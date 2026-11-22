# Clase 02/10 · Histórico acumulativo de precios de combustibles.
# Fuente: EIA Open Data API v2, copiada previamente a Files/bronze/eia.

from datetime import date, datetime, timezone
from pathlib import Path
import json

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window


# 1. Comprobar contexto y archivos Bronze. Cada ejecución del pipeline deja
# un archivo distinto. Volver a leerlos todos hace la demostración reproducible;
# MERGE impide que vuelvan a entrar las fechas ya presentes en Silver.
contexto = notebookutils.runtime.context
assert contexto.get("defaultLakehouseName") == "LH_PreciosCombustibles", (
    "Vincula LH_PreciosCombustibles como Lakehouse predeterminado."
)
carpeta_bronze = Path("/lakehouse/default/Files/bronze/eia")
archivos = sorted(carpeta_bronze.glob("*.json"))
if not archivos:
    raise FileNotFoundError("No hay JSON de EIA en Files/bronze/eia. Ejecuta antes la copia del pipeline.")
print(f"Archivos Bronze encontrados: {len(archivos)}")


# 2. La copia REST puede escribir un documento JSON o líneas JSON. Este lector
# acepta las dos formas y extrae response.data de la respuesta oficial de EIA.
def extraer_registros(objeto):
    if isinstance(objeto, list):
        for elemento in objeto:
            yield from extraer_registros(elemento)
    elif isinstance(objeto, dict):
        if "period" in objeto and "value" in objeto:
            yield objeto
        else:
            for clave in ("response", "data", "rows"):
                if clave in objeto:
                    valor = objeto[clave]
                    if isinstance(valor, str):
                        try:
                            valor = json.loads(valor)
                        except json.JSONDecodeError:
                            continue
                    yield from extraer_registros(valor)


def leer_archivo(ruta):
    contenido = ruta.read_text(encoding="utf-8-sig").strip()
    if not contenido:
        return []
    try:
        return list(extraer_registros(json.loads(contenido)))
    except json.JSONDecodeError:
        registros = []
        for numero, linea in enumerate(contenido.splitlines(), start=1):
            if linea.strip():
                try:
                    registros.extend(extraer_registros(json.loads(linea)))
                except json.JSONDecodeError as error:
                    raise ValueError(f"JSON inválido en {ruta.name}, línea {numero}") from error
        return registros


series = {
    "EMM_EPMR_PTE_NUS_DPG": "Gasolina regular",
    "EMD_EPD2D_PTE_NUS_DPG": "Diésel",
}
filas = []
invalidas = 0
for archivo in archivos:
    capturado_en = datetime.fromtimestamp(archivo.stat().st_mtime, timezone.utc)
    for registro in leer_archivo(archivo):
        serie = registro.get("series")
        try:
            fecha = date.fromisoformat(str(registro["period"])[:10])
            precio = float(registro["value"])
            if serie not in series or precio <= 0:
                raise ValueError("Serie o precio fuera de alcance")
        except (KeyError, ValueError, TypeError):
            invalidas += 1
            continue
        filas.append((serie, series[serie], "Estados Unidos", fecha, precio,
                      "USD/galón", capturado_en, archivo.name, fecha.year, fecha.month))

if not filas:
    raise ValueError("Los archivos Bronze no contienen observaciones válidas de las dos series EIA.")


# 3. Deduplicar dentro de la entrada. La clave natural es (serie EIA, fecha).
# Si un archivo posterior trae una corrección, este histórico append conserva
# el primer valor incorporado; las correcciones requieren una política aparte.
esquema = T.StructType([
    T.StructField("serie_eia", T.StringType(), False),
    T.StructField("combustible", T.StringType(), False),
    T.StructField("region", T.StringType(), False),
    T.StructField("fecha", T.DateType(), False),
    T.StructField("precio_usd_galon", T.DoubleType(), False),
    T.StructField("unidad", T.StringType(), False),
    T.StructField("capturado_en_utc", T.TimestampType(), False),
    T.StructField("archivo_origen", T.StringType(), False),
    T.StructField("anio", T.IntegerType(), False),
    T.StructField("mes", T.IntegerType(), False),
])
entrada = spark.createDataFrame(filas, schema=esquema)
ventana = Window.partitionBy("serie_eia", "fecha").orderBy(
    F.col("capturado_en_utc").asc(), F.col("archivo_origen").asc()
)
unicas = entrada.withColumn("orden", F.row_number().over(ventana)) \
    .where(F.col("orden") == 1).drop("orden")
total_entrada = entrada.count()
total_unicas = unicas.count()


# 4. Crear Silver Delta una sola vez, particionada por año y mes, y agregar
# exclusivamente las claves todavía ausentes. Repetir la carga es idempotente.
tabla = "silver.precios_combustibles_historico"
spark.sql("CREATE SCHEMA IF NOT EXISTS silver")
spark.sql("""
CREATE TABLE IF NOT EXISTS silver.precios_combustibles_historico (
    serie_eia STRING, combustible STRING, region STRING, fecha DATE,
    precio_usd_galon DOUBLE, unidad STRING, capturado_en_utc TIMESTAMP,
    archivo_origen STRING, anio INT, mes INT
) USING DELTA PARTITIONED BY (anio, mes)
""")
antes = spark.table(tabla).count()
DeltaTable.forName(spark, tabla).alias("destino").merge(
    unicas.alias("origen"),
    "destino.serie_eia = origen.serie_eia AND destino.fecha = origen.fecha"
).whenNotMatchedInsertAll().execute()
despues = spark.table(tabla).count()


# 5. Controles que se pueden repetir en directo durante la clase.
duplicados_silver = spark.table(tabla).groupBy("serie_eia", "fecha") \
    .count().where(F.col("count") > 1).count()
if duplicados_silver:
    raise AssertionError(f"Silver tiene {duplicados_silver} claves duplicadas")
particiones = spark.sql(f"DESCRIBE DETAIL {tabla}").select("partitionColumns").first()[0]
assert particiones == ["anio", "mes"], f"Particiones inesperadas: {particiones}"

resumen = {
    "archivos_bronze": len(archivos),
    "filas_leidas": total_entrada,
    "filas_invalidas": invalidas,
    "claves_unicas_en_bronze": total_unicas,
    "filas_silver_antes": antes,
    "filas_nuevas": despues - antes,
    "filas_silver_despues": despues,
    "duplicados_en_silver": duplicados_silver,
    "particiones": particiones,
}
print(json.dumps(resumen, ensure_ascii=False, indent=2))
spark.table(tabla).groupBy("combustible").agg(
    F.count("*").alias("observaciones"),
    F.min("fecha").alias("primera_fecha"),
    F.max("fecha").alias("ultima_fecha")
).orderBy("combustible").show(truncate=False)
