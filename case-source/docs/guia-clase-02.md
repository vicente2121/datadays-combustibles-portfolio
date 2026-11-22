# Clase 02/10 · Histórico acumulativo de precios de combustibles en Microsoft Fabric

**Serie:** Proyectos en un mes: 10 patrones de carga en Microsoft Fabric · Microsoft Data Days  
**Patrón:** Append Only con deduplicación e idempotencia  
**Fuente real:** EIA Open Data API v2, precios semanales de gasolina regular y diésel de Estados Unidos, en USD/galón.  
**Artefactos creados:** workspace `DataDays-Clase02-Combustibles-20261113`, Lakehouse `LH_PreciosCombustibles`, cuadernos `NB_ProcesarHistoricoEIA` y `NB_GoldResumenCombustibles`, canalización `PL_EIA_Precios_Append`, modelo `MD_PreciosCombustibles_Gold` e informe `INF_EvolucionPreciosCombustibles`.

**Para repetir la clase:** abre [cuadernos listos para copiar y pegar](../notebooks/LEEME_COPIAR_Y_PEGAR.md). Incluyen versiones importables sin los identificadores de este workspace y el código completo de cada celda.

Todas las imágenes de esta guía son **capturas reales** de la interfaz de Fabric y EIA tomadas durante la construcción de esta clase. Cada imagen muestra el estado antes o después de la acción indicada. La clave EIA no se muestra ni se guarda en este material.

## Lo que vamos a construir

Un *snapshot* representa los precios observados en una ejecución concreta. Cada archivo JSON de `Files/bronze/eia` es un snapshot de la respuesta EIA de ese momento. El histórico acumulativo reúne las observaciones de todas las ejecuciones en `silver.precios_combustibles_historico` sin borrar las fechas anteriores. Su clave natural es **serie EIA + fecha**. Si se repite la misma carga, el `MERGE` no inserta otra fila con esa clave.

| Capa | Objeto | Qué conserva |
|---|---|---|
| Bronze | `Files/bronze/eia/precios_<RunId>.json` | La respuesta copiada en cada ejecución, para rastrear el origen. |
| Silver | `silver.precios_combustibles_historico` | Una observación por serie y fecha, particionada por `anio` y `mes`. |
| Gold | `gold.dim_combustible`, `gold.dim_mes`, `gold.fact_precios_mensuales`, `gold.fact_ultimo_precio` | Dimensiones y resúmenes derivados de Silver para Power BI. |

Las series elegidas son `EMM_EPMR_PTE_NUS_DPG` (gasolina regular) y `EMD_EPD2D_PTE_NUS_DPG` (diésel). La consulta comienza en 2024-01-01, usa frecuencia semanal y solicita hasta 500 observaciones; EIA devolvió 300 para el periodo actual. La URL del origen está en [la plantilla del pipeline](../pipelines/PL_EIA_Precios_Append.template.json); el tratamiento de datos está en [NB_ProcesarHistoricoEIA.ipynb](../notebooks/NB_ProcesarHistoricoEIA.ipynb).

## Paso 0 · Conseguir una clave EIA

![Formulario oficial de registro de EIA](../output/playwright/clase02/00-registro-oficial-eia.png)

En el [registro oficial de EIA](https://www.eia.gov/opendata/register.php), indica nombre, apellido, correo y categoría; revisa sus términos antes de enviarlo. EIA envía la clave al correo indicado. Durante la ejecución de Fabric introducirás esa clave en el parámetro `eia_api_key`. No la escribas en el cuaderno, el JSON exportado ni las capturas.

![Confirmación real de reenvío de clave EIA](../output/playwright/clase02/28-eia-clave-reenviada.png)

Si EIA indica que el correo ya existe, abre **Forgot My API Key**, solicita el reenvío y revisa tu bandeja. En esta preparación, EIA confirmó que envió la clave al correo registrado.

## 1 · Crear el espacio de trabajo y el Lakehouse

### Paso 1. Abrir Fabric

![Inicio real de Fabric](../output/playwright/clase02/01-inicio-fabric.png)

En la página inicial de Fabric, entra en **Áreas de trabajo** y pulsa **Nueva área de trabajo**. Todos los artefactos de esta clase quedarán juntos en ese espacio.

### Paso 2. Elegir nombre y capacidad

![Formulario de workspace y capacidad](../output/playwright/clase02/02-workspace-formulario-capacidad.png)

Escribe `DataDays-Clase02-Combustibles-20261113` y selecciona una capacidad Fabric activa. La capacidad es necesaria para ejecutar la canalización y el cuaderno Spark.

### Paso 3. Comprobar el workspace vacío

![Workspace recién creado](../output/playwright/clase02/03-workspace-creado.png)

La lista todavía no tiene elementos: empezamos desde cero. Pulsa **Nuevo elemento** para crear el Lakehouse.

### Paso 4. Encontrar Lakehouse en el catálogo

![Catálogo de nuevos elementos](../output/playwright/clase02/04-nuevo-elemento-lakehouse.png)

Busca **Lakehouse** en el catálogo. Este elemento alojará archivos sin transformar en `Files` y la tabla Delta final en `Tables`.

### Paso 5. Crear un Lakehouse con esquemas

![Formulario de Lakehouse](../output/playwright/clase02/05-lakehouse-formulario-esquemas.png)

Nómbralo `LH_PreciosCombustibles` y activa los **esquemas**. Usaremos el esquema `silver` para distinguir la tabla validada de los archivos Bronze.

### Paso 6. Reconocer Files y Tables

![Lakehouse creado](../output/playwright/clase02/06-lakehouse-creado.png)

El Lakehouse ya existe. `Files` recibirá el JSON de la API; `Tables` mostrará la tabla Delta tras la primera ejecución correcta del cuaderno.

## 2 · Crear el cuaderno de tratamiento

### Paso 7. Seleccionar Cuaderno

![Catálogo con Cuaderno](../output/playwright/clase02/07-nuevo-elemento-cuaderno.png)

Vuelve a **Nuevo elemento** y elige **Cuaderno**. El cuaderno aplica la regla de negocio que la actividad de copia no resuelve: validar, deduplicar e insertar solo claves nuevas.

### Paso 8. Darle un nombre fácil de reconocer

![Formulario de Cuaderno](../output/playwright/clase02/08-cuaderno-formulario.png)

Escribe `NB_ProcesarHistoricoEIA`. El nombre aparecerá después en el selector de la actividad **Bloc de notas** del pipeline.

### Paso 9. Vincular el Lakehouse predeterminado

![Cuaderno creado](../output/playwright/clase02/09-cuaderno-creado.png)

Vincula `LH_PreciosCombustibles` como Lakehouse predeterminado. Así el código puede leer `/lakehouse/default/Files/bronze/eia` y escribir `silver.precios_combustibles_historico`.

## 3 · Construir la canalización de ingesta

### Paso 10. Elegir Canalización

![Catálogo con Canalización](../output/playwright/clase02/10-nuevo-elemento-canalizacion.png)

En **Nuevo elemento**, selecciona **Canalización**. Orquestará la copia EIA → Bronze y, después, el cuaderno Bronze → Silver.

### Paso 11. Crear la canalización

![Formulario de Canalización](../output/playwright/clase02/11-canalizacion-formulario.png)

Ponle `PL_EIA_Precios_Append`. El nombre recuerda el patrón: añadir observaciones nuevas sin reemplazar la tabla histórica.

### Paso 12. Partir de un lienzo vacío

![Lienzo de canalización vacío](../output/playwright/clase02/12-canalizacion-creada.png)

Abre la canalización creada. Desde el lienzo, agrega una actividad **Copiar datos**.

### Paso 13. Agregar la actividad de copia

![Menú de actividad de copia](../output/playwright/clase02/13-copy-actividad-agregada.png)

En la barra de actividades, elige **Agregar actividad de copia de datos** y llama a la actividad `Copiar_EIA_Bronze`. El nombre describe el movimiento, sin mezclar todavía la transformación.

### Paso 14. Escoger REST como origen

![Selector REST](../output/playwright/clase02/14-origen-rest.png)

En la pestaña **Origen** de la copia, elige **REST**. EIA publica los precios en un endpoint HTTPS que responde JSON.

### Paso 15. Crear la conexión EIA

![Nueva conexión REST EIA](../output/playwright/clase02/15-conexion-eia-formulario.png)

Usa URL base `https://api.eia.gov`, autenticación **Anónimo** y nombre `EIA_OpenData_REST_Clase02`. La autenticación anónima corresponde al conector; la autorización de la API se enviará como parámetro seguro en la URL relativa.

### Paso 16. Seleccionar la conexión

![Origen con conexión elegida](../output/playwright/clase02/16-origen-rest-conexion-creada.png)

Comprueba que **Origen** ya muestra la conexión REST. La URL relativa se configura separadamente para que el mismo conector pueda reutilizarse.

### Paso 17. Configurar el destino Bronze

![Destino Lakehouse JSON](../output/playwright/clase02/17-destino-lakehouse-json.png)

En **Destino**, selecciona `LH_PreciosCombustibles` → **Archivos**, carpeta `bronze/eia`, formato **JSON**. El nombre `precios_@{pipeline().RunId}.json` crea un archivo por ejecución; evita sobrescribir el snapshot anterior.

### Paso 18. Declarar la clave como parámetro seguro

![Parámetro EIA de tipo Cadena sin valor predeterminado](../output/playwright/clase02/18-parametro-eia-seguro.png)

En los parámetros del pipeline crea `eia_api_key` de tipo **Cadena (`String`)**, sin valor predeterminado. En esta configuración verificada, el conector REST recibe la clave al evaluar la URL. Un primer intento con `SecureString` no se interpoló como una clave válida; por eso se cambió el tipo. Quien ejecute el pipeline introduce la clave en ese momento.

### Paso 19. Formar la petición semanal EIA

![URL relativa EIA con parámetro](../output/playwright/clase02/19-origen-eia-url-parametrizada.png)

En **Origen → URL relativa** usa la expresión dinámica de [la plantilla del pipeline](../pipelines/PL_EIA_Precios_Append.template.json): el endpoint `v2/petroleum/pri/gnd/data/`, `api_key`, frecuencia semanal, las dos series, fecha inicial y límite de 500. Fabric evalúa `@{pipeline().parameters.eia_api_key}` al ejecutar. La solicitud REST tiene 180 segundos de espera y dos reintentos para tolerar respuestas temporales `504` de EIA.

### Paso 20. Proteger entrada y salida de la copia

![Opciones de entrada y salida seguras](../output/playwright/clase02/20-entrada-salida-seguras.png)

En **General → Avanzadas**, activa **Entrada segura** y **Salida segura**. Esto oculta la entrada y salida habituales de la actividad. **Límite observado:** una respuesta `504` del conector incluyó la URL completa en el mensaje de error de la ejecución, incluso con estas opciones activas. La clave gratuita de EIA debe tratarse como visible para quien pueda consultar esos errores; no la uses como secreto de mayor sensibilidad en este patrón.

### Paso 21. Añadir el cuaderno

![Actividad de cuaderno configurada](../output/playwright/clase02/21-notebook-actividad-configurada.png)

Agrega una actividad **Bloc de notas**, llámala `Procesar_y_deduplicar_Silver` y selecciona el cuaderno `NB_ProcesarHistoricoEIA` en el mismo workspace.

## 4 · Entender y ejecutar el cuaderno

### Paso 22. Leer el propósito del cuaderno

![Cuaderno con Lakehouse asociado](../output/playwright/clase02/22-cuaderno-codigo-y-lakehouse.png)

El explorador muestra el Lakehouse vinculado. El cuaderno se divide en celdas para poder explicar importaciones, lectura Bronze, reglas de calidad, deduplicación, escritura Delta y comprobaciones por separado.

### Paso 23. Quitar duplicados de la entrada

![Código de deduplicación](../output/playwright/clase02/23-cuaderno-deduplicacion.png)

El código agrupa por `(serie_eia, fecha)` y asigna `row_number()`. Conserva la primera observación de cada clave dentro de los archivos Bronze. Una misma fecha de gasolina y diésel son **dos** claves distintas.

### Paso 24. Crear Silver particionada y hacer MERGE

![Código Delta y particiones](../output/playwright/clase02/24-cuaderno-merge-silver-particion.png)

`CREATE TABLE ... USING DELTA PARTITIONED BY (anio, mes)` organiza físicamente los datos por año y mes. `MERGE ... WHEN NOT MATCHED INSERT` agrega únicamente claves ausentes. Una segunda ejecución con los mismos archivos debe indicar `filas_nuevas: 0`.

### Paso 25. Unir las actividades en orden

![DAG de copia a cuaderno](../output/playwright/clase02/25-pipeline-dependencia-copia-cuaderno.png)

La flecha verde une **éxito de copia** con **inicio del cuaderno**. Esto evita procesar archivos incompletos si falla la llamada REST.

### Paso 26. Validar antes de ejecutar

![Validación sin errores](../output/playwright/clase02/26-validacion-pipeline-sin-errores.png)

Pulsa **Validar**. Fabric mostró **«Se validó su canalización. No se ha encontrado ningún error»**. Esta comprobación valida la configuración, no sustituye una ejecución real con clave.

### Paso 27. Ejecutar con la clave EIA

![Diálogo de ejecución sin clave](../output/playwright/clase02/27-dialogo-ejecucion-sin-clave.png)

Pulsa **Ejecutar**, pega tu clave en `eia_api_key` y confirma. La captura se tomó **antes** de introducirla. No hagas capturas del cuadro una vez escrito el secreto.

![Ejecución real de la canalización](../output/playwright/clase02/29-pipeline-ejecucion-real.png)

Al aceptar, la pestaña **Salida** muestra el ID de ejecución y el estado **En curso**. La copia corre primero; el cuaderno espera la marca de éxito de la flecha verde.

### Paso 28. Verificar la ejecución terminada

![Canalización completada con ambas actividades correctas](../output/playwright/clase02/31-pipeline-ejecucion-completada.png)

La ejecución terminó **Correcto** y el cuaderno también aparece **Correcto**. EIA devolvió temporalmente un `504`; por eso la copia muestra una cruz roja de un intento fallido antes de un intento correcto. Los dos reintentos configurados permitieron completar la carga.

### Paso 29. Reconocer las dos zonas del Lakehouse

![Estructura Bronze y Silver en Lakehouse](../output/playwright/clase02/32-lakehouse-bronze-silver.png)

En el explorador aparecen `Files/bronze` y el esquema `silver`. Bronze guarda el JSON de origen y Silver publica la tabla consultable. Tener ambos permite explicar de dónde salió cada fila.

### Paso 30. Abrir la tabla histórica

![Vista previa de Silver con 300 filas](../output/playwright/clase02/33-lakehouse-tabla-silver.png)

Abre `Tables → silver → precios_combustibles_historico`. La vista previa real muestra **300 filas** y columnas como `serie_eia`, `combustible`, `fecha` y `precio_usd_galon`. No es un fichero aislado de la última ejecución: es la tabla Delta acumulativa.

### Paso 31. Localizar el JSON de la ejecución

![Archivo JSON real en Bronze](../output/playwright/clase02/34-bronze-json-ejecucion.png)

Abre `Files → bronze → eia`. El archivo `precios_<RunId>.json` ocupa aproximadamente 89 KB. Su nombre enlaza el snapshot de origen con el ID que mostró la canalización.

### Paso 32. Repetir el cuaderno y leer la prueba de idempotencia

![Resumen real del cuaderno con cero filas nuevas](../output/playwright/clase02/35-cuaderno-ejecucion-idempotente.png)

Al ejecutar de nuevo el cuaderno con el mismo Bronze, el resumen mostró `filas_silver_antes: 300`, `filas_nuevas: 0`, `filas_silver_despues: 300`, `duplicados_en_silver: 0` y particiones `anio`, `mes`. Esta es la prueba concreta de que una repetición no duplica precios.

### Paso 33. Comprobar cobertura temporal por combustible

![Rango de fechas de las dos series](../output/playwright/clase02/36-rango-fechas-por-combustible.png)

La tabla de resultados muestra **150 observaciones de diésel** y **150 de gasolina regular**, desde **2024-01-01** hasta **2026-11-09**. Esta comprobación también detectaría si una serie no llegara desde EIA.

### Paso 34. Repetir la canalización completa

![Segunda ejecución real correcta](../output/playwright/clase02/37-segunda-ejecucion-pipeline-correcta.png)

Vuelve a pulsar **Ejecutar** con la misma clave EIA. En la segunda ejecución real, **Copiar_EIA_Bronze** y **Procesar_y_deduplicar_Silver** terminaron **Correcto**. Así se comprueba la idempotencia del flujo completo, no solo del cuaderno aislado.

### Paso 35. Comparar los snapshots Bronze

![Dos archivos JSON tras dos ejecuciones](../output/playwright/clase02/38-dos-json-bronze.png)

Bronze ahora muestra **dos archivos JSON** de 89 KB, cada uno con su `RunId`. Ningún snapshot reemplazó al anterior: se conserva la trazabilidad de ambas llamadas a EIA.

### Paso 36. Confirmar que Silver no se duplicó

![Silver sigue con 300 filas tras dos pipelines](../output/playwright/clase02/39-silver-sigue-300-filas.png)

Vuelve a abrir la tabla Silver. La vista previa sigue mostrando **300 filas**, aunque Bronze ya tiene dos snapshots de 300 observaciones. El `MERGE` insertó cero claves nuevas en la segunda ejecución.

### Paso 37. Explicar la deduplicación con cifras reales

![Dos snapshots de 300 filas reducidos a 300 claves únicas](../output/playwright/clase02/40-dos-snapshots-deduplicados.png)

El resumen del cuaderno tras ambas ejecuciones da el ejemplo para explicar en directo: **2 archivos Bronze → 600 filas leídas → 300 claves únicas → 0 filas nuevas → 300 filas Silver → 0 duplicados**. La tabla conserva una fila por combustible y semana, aunque el origen se haya consultado dos veces.

## Parte 3 · De Silver a Gold

**Idea para explicar en directo:** Silver tiene el grano **una serie EIA y una fecha semanal**; es el histórico acumulativo. Cada JSON Bronze es una fotografía de una ejecución. Gold no reemplaza ese histórico: calcula tablas derivadas para responder preguntas de negocio rápidamente. Si se vuelve a ejecutar, Gold se reconstruye desde Silver, por lo que la misma semana no suma dos veces.

### Paso 38. Crear el cuaderno de Gold

![Creación real del cuaderno Gold en Fabric](../output/playwright/clase02/41-nuevo-cuaderno-gold.png)

En el mismo workspace, crea `NB_GoldResumenCombustibles`. Separar este cuaderno del de Silver deja clara la responsabilidad de cada paso: el primero incorpora y deduplica observaciones; el segundo calcula resúmenes. No se necesita una segunda llamada a EIA.

### Paso 39. Vincular el Lakehouse predeterminado

![Cuaderno Gold con el Lakehouse vinculado](../output/playwright/clase02/42-cuaderno-gold-vinculado.png)

Vincula `LH_PreciosCombustibles` como Lakehouse predeterminado. El código completo está en [`NB_GoldResumenCombustibles.ipynb`](../notebooks/NB_GoldResumenCombustibles.ipynb). Lee `silver.precios_combustibles_historico`, comprueba que existe información y que no hay claves `(serie_eia, fecha)` repetidas.

### Paso 40. Transformar las observaciones semanales

![Tablas Gold visibles en el Lakehouse](../output/playwright/clase02/45-lakehouse-capa-gold.png)

El cuaderno crea el esquema `gold` y cuatro tablas Delta. `dim_combustible` describe las dos series; `dim_mes` contiene los 35 meses; `fact_precios_mensuales` resume 70 combinaciones combustible-mes; `fact_ultimo_precio` guarda la última semana de cada combustible. La dimensión da contexto a los hechos, sin repetir nombres en cada fila del resumen.

### Paso 41. Interpretar el hecho mensual

![Vista previa real de 70 filas del hecho mensual](../output/playwright/clase02/46-gold-hecho-mensual.png)

Abre `Tables → gold → fact_precios_mensuales`. Una fila representa **un combustible en un mes**. Las columnas muestran precio promedio, mínimo y máximo en USD por galón, número de semanas observadas, promedio del mes anterior y variación mensual porcentual. La vista previa muestra **70 filas**: 35 meses por dos combustibles. El total de `semanas_observadas` debe sumar las 300 filas de Silver.

### Paso 42. Encadenar Gold después de Silver

![Pipeline de tres actividades: Bronze, Silver y Gold](../output/playwright/clase02/44-pipeline-bronze-silver-gold.png)

En `PL_EIA_Precios_Append`, la actividad `Construir_Gold_PowerBI` ejecuta el cuaderno Gold únicamente si `Procesar_y_deduplicar_Silver` terminó correctamente. La flecha expresa una dependencia de datos: Power BI leerá un resumen actualizado después de cada carga válida.

### Paso 43. Probar la cadena completa

![Ejecución real con las tres actividades correctas](../output/playwright/clase02/52-ejecucion-completa-correcta.png)

Ejecuta la canalización con `eia_api_key` y abre **Salida**. En la captura real aparecen las tres actividades en **Correcto**. Esta prueba verifica la orquestación completa, no solo la ejecución manual de cada cuaderno. Repetirla conserva 300 claves semanales en Silver y vuelve a producir el mismo resumen Gold mientras EIA no publique otra semana.

## Parte 4 · Modelo semántico y Power BI

**Pregunta de negocio para el directo:** ¿cómo evolucionó el precio medio mensual del diésel frente a la gasolina regular? El hecho mensual Gold responde con una fila por combustible y mes. El modelo semántico conecta las dimensiones y ofrece una medida reutilizable. El informe dibuja ambas series desde ese modelo.

### Paso 44. Iniciar un modelo Direct Lake

![Diálogo real para crear un modelo semántico Direct Lake](../output/playwright/clase02/47-nuevo-modelo-direct-lake.png)

Desde el Lakehouse, pulsa **Nuevo modelo semántico** y escribe `MD_PreciosCombustibles_Gold`. Direct Lake consulta las tablas Delta de OneLake sin preparar una copia importada para esta demostración. El modelo es la capa de nombres, relaciones y medidas que consume Power BI.

### Paso 45. Seleccionar las tablas

![Selección de Gold y Silver para el modelo](../output/playwright/clase02/48-seleccion-tablas-modelo.png)

Selecciona las cuatro tablas `gold` y `silver.precios_combustibles_historico`, y pulsa **Confirmar**. Silver queda disponible para preguntas semanales detalladas; Gold se usa para el informe mensual. Si una tabla no aparece, comprueba que el cuaderno Gold terminó y actualiza la lista de tablas.

### Paso 46. Reconocer las cinco tablas en el modelo

![Modelo semántico Direct Lake creado en Fabric](../output/playwright/clase02/49-modelo-semantico-direct-lake.png)

En la vista de modelo aparecen dos dimensiones (`dim_combustible`, `dim_mes`), dos hechos Gold y el histórico Silver. Antes de dibujar visuales, crea las relaciones; compartir un campo llamado `serie_eia` no conecta automáticamente las tablas.

### Paso 47. Crear la relación de combustible

![Diálogo real de relación varios a uno por serie EIA](../output/playwright/clase02/50-relacion-mensual-combustible.png)

Relaciona `fact_precios_mensuales[serie_eia]` con `dim_combustible[serie_eia]`. La cardinalidad es **varios a uno**: un combustible aparece en muchos meses, pero tiene una sola fila en la dimensión. Usa filtro en una sola dirección, desde la dimensión hacia el hecho.

### Paso 48. Completar las relaciones del modelo

![Cuatro relaciones reales del modelo semántico](../output/playwright/clase02/51-cuatro-relaciones-modelo.png)

Añade `fact_precios_mensuales[fecha_mes] → dim_mes[fecha_mes]`, `fact_ultimo_precio[serie_eia] → dim_combustible[serie_eia]` y `precios_combustibles_historico[serie_eia] → dim_combustible[serie_eia]`. La vista **Administrar relaciones** muestra cuatro relaciones activas. La medida `Precio mensual promedio = AVERAGE('fact_precios_mensuales'[precio_promedio_usd_galon])` calcula el valor por mes y combustible según el filtro del visual.

### Paso 49. Abrir el editor de informes

![Editor real de Power BI con el modelo conectado](../output/playwright/clase02/53-informe-powerbi-editor.png)

Desde el modelo, abre **Archivo → Crear nuevo informe**. La derecha muestra las cinco tablas conectadas. Inserta un **Gráfico de líneas**; al principio el lienzo está vacío y Power BI aún no sabe qué fecha ni qué valor debe representar.

### Paso 50. Dibujar la evolución mensual

![Gráfico real con precio mensual de diésel y gasolina](../output/playwright/clase02/54-linea-precio-mensual-combustible.png)

Arrastra `dim_mes[fecha_mes]` al eje X, la medida `Precio mensual promedio` al eje Y y `dim_combustible[combustible]` a **Leyenda**. Ajusta el tamaño en **Formato visual → General → Propiedades** para ocupar el lienzo. Las dos curvas se separan por combustible y recorren enero de 2024 a noviembre de 2026. La curva del diésel supera los 6 USD/galón hacia el final; es una lectura del dato, no un valor inventado para el gráfico.

### Paso 51. Guardar y comprobar el informe

![Informe Power BI guardado y abierto en modo lectura](../output/playwright/clase02/55-informe-guardado-precio-mensual.png)

Guarda el informe como `INF_EvolucionPreciosCombustibles` en el workspace de la clase. Ábrelo en modo lectura y comprueba que ambas líneas aparecen con datos reales. Para explicar el resultado, señala que la línea resume **meses** de Gold; las **semanas originales** siguen en Silver y se pueden analizar por separado sin perder detalle.

## Comprobaciones para el directo

Tras una ejecución correcta, abre `LH_PreciosCombustibles`. En `Files/bronze/eia` debe aparecer un JSON con el ID de la ejecución. En `Tables/silver` debe aparecer `precios_combustibles_historico`.

En el cuaderno o en el SQL analytics endpoint, comprueba el número de observaciones por combustible y el rango de fechas:

```sql
SELECT combustible, COUNT(*) AS observaciones,
       MIN(fecha) AS primera_fecha, MAX(fecha) AS ultima_fecha
FROM silver.precios_combustibles_historico
GROUP BY combustible
ORDER BY combustible;
```

Para demostrar que no hay claves repetidas:

```sql
SELECT serie_eia, fecha, COUNT(*) AS veces
FROM silver.precios_combustibles_historico
GROUP BY serie_eia, fecha
HAVING COUNT(*) > 1;
```

El segundo resultado debe estar vacío. Ejecuta la canalización otra vez con la misma clave y compara el total: la cantidad de filas Silver debe quedar igual y el resumen del cuaderno debe indicar cero filas nuevas. Cuando EIA publique una semana nueva, la siguiente ejecución añadirá esa fecha sin perder las anteriores.

**Regla de correcciones:** este ejemplo preserva el primer valor insertado para cada serie y fecha. Si EIA corrigiera un precio pasado, habría que definir una política explícita de correcciones antes de actualizarlo. Esa decisión es distinta de la deduplicación de un histórico Append Only.

**Mantenimiento:** se puede considerar `OPTIMIZE` o `VACUUM` cuando crezca el volumen. No es necesario para estas dos series semanales ni conviene ejecutar `VACUUM` durante la demostración inicial porque altera la retención de versiones Delta.
