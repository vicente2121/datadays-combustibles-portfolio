# Cuadernos listos para repetir la Clase 02

Puedes usarlos de dos maneras:

| Opción | Silver | Gold |
| --- | --- | --- |
| **Copiar y pegar** todo el código en una celda PySpark nueva | [COPIAR_PEGAR_01_Silver.py](COPIAR_PEGAR_01_Silver.py) | [COPIAR_PEGAR_02_Gold.py](COPIAR_PEGAR_02_Gold.py) |
| **Importar** un cuaderno con celdas y explicaciones | [COPIAR_PEGAR_01_Silver.ipynb](COPIAR_PEGAR_01_Silver.ipynb) | [COPIAR_PEGAR_02_Gold.ipynb](COPIAR_PEGAR_02_Gold.ipynb) |

Las copias `COPIAR_PEGAR` no llevan los identificadores del workspace ni del Lakehouse de esta ejecución y aceptan cualquier nombre de Lakehouse. Después de importarlas, debes vincular el Lakehouse nuevo manualmente. Los dos archivos `.py` contienen código completo y continuo: copia **todo** el archivo de cada uno en **una sola celda PySpark**, sin dividirlo.

## Orden exacto para repetirlo

1. Crea un workspace Fabric y un Lakehouse **con esquemas**. Puedes llamarlo `lk_historico`.
2. Prepara la actividad de copia REST del pipeline con [PL_EIA_Precios_Append.template.json](../pipelines/PL_EIA_Precios_Append.template.json) como referencia. La copia debe escribir un JSON de EIA en `Files/bronze/eia`. Introduce tu clave EIA en el parámetro `eia_api_key` solo al ejecutar; no la pegues en los cuadernos.
3. Crea `NB_ProcesarHistoricoEIA`, selecciona **PySpark**, vincula el Lakehouse como **Lakehouse predeterminado** y pega entero [COPIAR_PEGAR_01_Silver.py](COPIAR_PEGAR_01_Silver.py), o importa [COPIAR_PEGAR_01_Silver.ipynb](COPIAR_PEGAR_01_Silver.ipynb). Pulsa **Ejecutar todo**.
4. Comprueba `Tables → silver → precios_combustibles_historico`. El resumen del cuaderno debe decir `duplicados_en_silver: 0` y mostrar las particiones `anio`, `mes`.
5. Crea `NB_GoldResumenCombustibles`, vincula el mismo Lakehouse y pega entero [COPIAR_PEGAR_02_Gold.py](COPIAR_PEGAR_02_Gold.py), o importa [COPIAR_PEGAR_02_Gold.ipynb](COPIAR_PEGAR_02_Gold.ipynb). Pulsa **Ejecutar todo**.
6. Comprueba las cuatro tablas en `Tables → gold`. Gold debe imprimir los conteos y dos precios semanales recientes. En el pipeline, conecta el cuaderno Gold después del Silver con la condición **Succeeded**.

En una repetición futura las cantidades pueden cambiar porque EIA publica semanas nuevas. Las comprobaciones del código se basan en claves, relaciones y sumas; no exigen que vuelvan a salir exactamente 300 filas Silver o 70 Gold.

**Si sale «Vincula un Lakehouse con esquemas como predeterminado»**, abre el explorador del cuaderno, agrega el Lakehouse y márcalo como predeterminado antes de ejecutar. Si Silver indica que no hay JSON, ejecuta primero la copia REST del pipeline. Si sale `NameError: Path is not defined` en un cuaderno anterior, ejecuta de nuevo la celda de importaciones y luego **Ejecutar todo**. La copia reutilizable también importa `Path` dentro de la celda que lo usa.
