# Ficha del proyecto · Data Days Combustibles

| Dato | Valor |
| --- | --- |
| Repositorio | `vicente2121/datadays-combustibles-portfolio` (público) |
| Fuente | `vicente2121/DATADAYS_DP600/charla02/caso_02_historico_precios_combustibles` |
| Azure DevOps | No aplica: entrega directa solicitada para este portafolio, sin Épica ni historias |
| Modo de entrega | Directo a `main` |
| Workspace DEV | `DataDays-FabricApps-Portfolio-DEV` · `0245bb51-e0d1-40f1-b071-fcbbf1d7b155` |
| Carpeta Fabric | `02-Combustibles` · `b55f8c2f-a9df-4c0f-89f5-7d5f9b391648` |
| App Rayfin | `datadays-combustibles-portfolio` · identificador único en `rayfin/rayfin.yml` |
| Elementos de este caso | `DD02_LH_Combustibles`, `DD02_NB_Silver`, `DD02_NB_Gold`, `DD02_PL_EIA`, `DD02_SM_PreciosCombustibles`, `DD02_Informe_PreciosCombustibles` |
| Acceso | Fabric SSO; portafolio documental sin datos propios ni roles de app |
| Cuenta del desarrollador | `juanvicente@ajmvicente21hotmail.onmicrosoft.com` |
| Sincronización Git del workspace | Desactivada; las publicaciones se hacen con CLI/API y los repositorios se mantienen separados |

## Alcance de propiedad

Solo se crean o modifican los elementos enumerados arriba y la app de esta ficha. `case-source/` copia el material general y no se sincroniza con el workspace.

## Riesgos para producción

- La clave EIA debe aportarse como parámetro seguro al ejecutar el pipeline; nunca se guarda en Git.
- El JSON incluido es una respuesta de ejemplo, no una conexión viva.
- La visibilidad de los datos del Lakehouse depende de los permisos del workspace; revisar antes de uso productivo.
