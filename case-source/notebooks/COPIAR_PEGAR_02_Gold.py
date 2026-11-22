# Clase 02/10 · Capa Gold: resumen listo para Power BI.
# Silver conserva cada observación; Gold reúne métricas de lectura rápida.

from pyspark.sql import functions as F
from pyspark.sql.window import Window


# 1. Leer el histórico Silver y comprobar su clave natural.
contexto = notebookutils.runtime.context
assert contexto.get("defaultLakehouseName"), (
    "Vincula un Lakehouse con esquemas como predeterminado."
)
historico = spark.table("silver.precios_combustibles_historico")
filas_silver = historico.count()
assert filas_silver > 0, "Silver está vacía: ejecuta antes la carga EIA."
duplicados_silver = historico.groupBy("serie_eia", "fecha").count() \
    .where(F.col("count") > 1).count()
assert duplicados_silver == 0, "Silver tiene series y fechas repetidas."
print(f"Silver: {filas_silver} observaciones válidas, {duplicados_silver} duplicados")


# 2. Dimensiones: combustible y mes. Las claves son estables y únicas.
dim_combustible = historico.select(
    "serie_eia", "combustible", "region", "unidad"
).distinct()
assert dim_combustible.groupBy("serie_eia").count().where(F.col("count") > 1).count() == 0

base_mes = historico.select(
    F.trunc(F.col("fecha"), "MM").alias("fecha_mes")
).distinct()
dim_mes = base_mes.select(
    "fecha_mes",
    F.year("fecha_mes").alias("anio"),
    F.month("fecha_mes").alias("mes"),
    F.date_format("fecha_mes", "yyyy-MM").alias("etiqueta_mes"),
    F.quarter("fecha_mes").alias("trimestre"),
)


# 3. Hecho mensual. Una fila por combustible y mes; el promedio no sustituye
# las 300 observaciones semanales originales, que siguen en Silver.
mensual = historico.withColumn("fecha_mes", F.trunc(F.col("fecha"), "MM")) \
    .groupBy("serie_eia", "fecha_mes") \
    .agg(
        F.round(F.avg("precio_usd_galon"), 3).alias("precio_promedio_usd_galon"),
        F.min("precio_usd_galon").alias("precio_minimo_usd_galon"),
        F.max("precio_usd_galon").alias("precio_maximo_usd_galon"),
        F.count("*").cast("int").alias("semanas_observadas"),
    )
ventana_mes = Window.partitionBy("serie_eia").orderBy("fecha_mes")
mensual = mensual.withColumn(
    "precio_mes_anterior_usd_galon",
    F.lag("precio_promedio_usd_galon").over(ventana_mes),
).withColumn(
    "variacion_mensual_pct",
    F.when(F.col("precio_mes_anterior_usd_galon") > 0,
           F.round(100 * (F.col("precio_promedio_usd_galon") /
                          F.col("precio_mes_anterior_usd_galon") - 1), 2)),
).select(
    "serie_eia", "fecha_mes", "precio_promedio_usd_galon",
    "precio_minimo_usd_galon", "precio_maximo_usd_galon",
    "semanas_observadas", "precio_mes_anterior_usd_galon",
    "variacion_mensual_pct",
)


# 4. Hecho de último precio semanal para las tarjetas KPI del informe.
ventana_ultima = Window.partitionBy("serie_eia").orderBy(F.col("fecha").desc())
ultimo = historico.withColumn("posicion", F.row_number().over(ventana_ultima)) \
    .withColumn("precio_anterior_usd_galon", F.lead("precio_usd_galon").over(ventana_ultima)) \
    .where(F.col("posicion") == 1) \
    .withColumn(
        "variacion_semanal_pct",
        F.when(F.col("precio_anterior_usd_galon") > 0,
               F.round(100 * (F.col("precio_usd_galon") /
                              F.col("precio_anterior_usd_galon") - 1), 2)),
    ).select(
        "serie_eia", "fecha", "precio_usd_galon",
        "precio_anterior_usd_galon", "variacion_semanal_pct",
    )


# 5. Materializar Gold. Es una capa derivada: se reconstruye desde Silver en
# cada ejecución para incorporar la nueva semana en el promedio del mes.
spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
salidas = {
    "gold.dim_combustible": dim_combustible,
    "gold.dim_mes": dim_mes,
    "gold.fact_precios_mensuales": mensual,
    "gold.fact_ultimo_precio": ultimo,
}
for nombre, datos in salidas.items():
    datos.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(nombre)


# 6. Validaciones para explicar Gold con cifras, no solo con un diagrama.
conteos = {nombre: spark.table(nombre).count() for nombre in salidas}
assert conteos["gold.dim_combustible"] == 2
assert conteos["gold.fact_ultimo_precio"] == 2
assert spark.table("gold.fact_precios_mensuales").agg(
    F.sum("semanas_observadas")
).first()[0] == filas_silver
assert spark.table("gold.fact_precios_mensuales").groupBy(
    "serie_eia", "fecha_mes"
).count().where(F.col("count") > 1).count() == 0
print("Silver:", filas_silver, "filas")
print("Gold:", conteos)
print("Ejemplo de KPI semanal:")
spark.table("gold.fact_ultimo_precio").join(
    spark.table("gold.dim_combustible"), "serie_eia"
).select("combustible", "fecha", "precio_usd_galon", "variacion_semanal_pct") \
    .orderBy("combustible").show(truncate=False)
print("Últimos seis meses por combustible:")
spark.table("gold.fact_precios_mensuales").join(
    spark.table("gold.dim_combustible"), "serie_eia"
).select("combustible", "fecha_mes", "precio_promedio_usd_galon",
         "semanas_observadas", "variacion_mensual_pct") \
    .orderBy(F.col("fecha_mes").desc(), "combustible").show(12, truncate=False)
