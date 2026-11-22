# Ficha del proyecto · Data Days Combustibles

| Dato | Valor |
| --- | --- |
| Repositorio | `vicente2121/datadays-combustibles-portfolio` (público) |
| Fuente | `vicente2121/DATADAYS_DP600/charla02/caso_02_historico_precios_combustibles` |
| Azure DevOps | No aplica: entrega directa solicitada para este portafolio, sin Épica ni historias |
| Modo de entrega | Directo a `main` |
| Workspace DEV | `DataDays-FabricApps-Portfolio-DEV` · `0245bb51-e0d1-40f1-b071-fcbbf1d7b155` |
| Carpeta Fabric | `02-Combustibles` · `b55f8c2f-a9df-4c0f-89f5-7d5f9b391648` |
| App Rayfin | `datadays-combustibles-portfolio` · `5e3a9b0c-6045-4c8b-9884-7d0997345e65` |
| Elementos de este caso | `DD02_LH_Combustibles`, `DD02_NB_Silver`, `DD02_NB_Gold`, `DD02_PL_EIA_Precios`, `DD02_SM_PreciosCombustibles`, `DD02_Informe_PreciosCombustibles` |
| Acceso | Fabric SSO; portafolio documental sin datos propios ni roles de app |
| Cuenta del desarrollador | `juanvicente@ajmvicente21hotmail.onmicrosoft.com` |
| Sincronización Git del workspace | Desactivada; las publicaciones se hacen con CLI/API y los repositorios se mantienen separados |

## Alcance de propiedad

Solo se crean o modifican los elementos enumerados arriba y la app de esta ficha. `case-source/` copia el material general y no se sincroniza con el workspace.

## Publicación

- [Fabric App](https://spicy-bloom-1cb1cf0b08-spaincentral.webapp.fabricapps.net)
- [Informe en Fabric](https://app.fabric.microsoft.com/groups/0245bb51-e0d1-40f1-b071-fcbbf1d7b155/reports/2410449a-d0d7-448d-9dd2-31c1d92a18f6)
- `fabric/` contiene las definiciones publicadas con IDs resueltos; `case-source/` conserva las plantillas originales.
- El informe publicado usa el JSON EIA de ejemplo incluido en el caso: Silver contiene 300 observaciones. La canalización Copy REST → Silver → Gold está creada, pero su ejecución viva requiere aportar `eia_api_key` al lanzar el pipeline.

| Elemento | ID |
| --- | --- |
| Lakehouse | `3130a9b4-c65e-427c-8cb3-c92c25d1aff4` |
| Notebooks Silver / Gold | `6416e872-f704-4fae-9cbc-60738619df46` / `432b5ba7-bb2f-4ba1-a336-5996817a372d` |
| Pipeline | `55716669-39a9-4fd4-a08e-b0f3297b4b9e` |
| Modelo Direct Lake | `348baba6-87d8-465e-9a40-ed582b2dbb80` |
| Informe | `2410449a-d0d7-448d-9dd2-31c1d92a18f6` |

## Riesgos para producción

- La clave EIA debe aportarse como parámetro seguro al ejecutar el pipeline; nunca se guarda en Git.
- El JSON incluido es una respuesta de ejemplo, no una conexión viva.
- La visibilidad de los datos del Lakehouse depende de los permisos del workspace; revisar antes de uso productivo.
