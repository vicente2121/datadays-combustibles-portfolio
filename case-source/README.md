# Data Days · Clase 02/10 · Precios de combustibles

Construimos un histórico semanal de gasolina regular y diésel de la EIA en Microsoft Fabric: copia REST a Bronze, deduplicación en Silver, agregados Gold y un informe Power BI con modelo Direct Lake.

## Descargar y recorrer el caso

- [Guía ilustrada paso a paso](docs/guia-clase-02.md) y [versión PDF](docs/guia-clase-02.pdf).
- [Notebooks listos para importar o copiar](notebooks/LEEME_COPIAR_Y_PEGAR.md): Silver y Gold, en `.ipynb` y `.py`. Los archivos `NB_*.ipynb` son la captura de la clase; para otro workspace usa `COPIAR_PEGAR_*.ipynb`.
- [Plantilla completa del pipeline](pipelines/PL_EIA_Precios_Append.template.json): copia REST → Silver → Gold, con sus dependencias y el parámetro `eia_api_key`.
- [Proyecto Power BI](powerbi/PreciosCombustibles.pbip): definición PBIR del informe y TMDL del modelo semántico.
- [Respuesta de EIA de ejemplo](data/precios_eia_para_bronze.json), útil para revisar el formato de Bronze. Los resultados actuales pueden contener más semanas.

Las imágenes de la guía están en `output/playwright/clase02/`.

## Reproducirlo en tu workspace

1. Crea un workspace en una capacidad Fabric y un Lakehouse **con esquemas**.
2. Obtén tu propia clave de la [API de EIA](https://www.eia.gov/opendata/register.php). Crea en Fabric una conexión REST a `https://api.eia.gov/` y una conexión al Lakehouse. No guardes la clave en el repositorio.
3. Importa `COPIAR_PEGAR_01_Silver.ipynb` y `COPIAR_PEGAR_02_Gold.ipynb`. Vincula el Lakehouse nuevo como predeterminado en ambos notebooks.
4. Usa la plantilla del pipeline como referencia para crear `PL_EIA_Precios_Append`. Sustituye los seis marcadores `<WORKSPACE_ID>`, `<LAKEHOUSE_ID>`, `<NOTEBOOK_SILVER_ID>`, `<NOTEBOOK_GOLD_ID>`, `<REST_CONNECTION_ID>` y `<LAKEHOUSE_CONNECTION_ID>` por los identificadores de tus elementos y conexiones. La plantilla contiene la definición de Fabric Data Pipeline; la guía muestra cómo configurar cada actividad desde la interfaz.
5. Ejecuta el pipeline con el valor de `eia_api_key` introducido en el diálogo de ejecución. Comprueba que aparecen `Files/bronze/eia`, `silver.precios_combustibles_historico` y las cuatro tablas Gold.
6. En `powerbi/PreciosCombustibles.SemanticModel/definition/expressions.tmdl`, sustituye `<WORKSPACE_ID>` y `<LAKEHOUSE_ID>` por los identificadores de tu workspace y Lakehouse. Abre `PreciosCombustibles.pbip` en Power BI Desktop y publica el modelo y el informe en tu workspace. El informe usa una referencia local `byPath` al modelo, por lo que ambos directorios deben permanecer juntos.

El pipeline y el modelo tienen marcadores deliberados: no se conectan al workspace de la demostración al descargarlos. El modelo y el informe se exportaron del workspace `DataDays-Clase02-Combustibles-20261113`; sus tablas, relaciones, medida y visual son los de la charla.

La clave EIA se pide en cada ejecución y no está incluida. Las opciones `secureInput` y `secureOutput` están activadas en la actividad de copia; consulta la nota de seguridad de la guía sobre errores del conector REST.
