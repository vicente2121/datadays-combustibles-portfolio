# Data Days · Combustibles

Fabric App tipo portafolio del caso 02 de DP-600: un histórico semanal de gasolina y diésel de la EIA que conserva la respuesta original, deduplica en Silver y sirve resúmenes Gold a un informe Direct Lake. La app describe el método y sus resultados; **no es un monitor de precios en directo**.

**Publicado:** [Fabric App](https://spicy-bloom-1cb1cf0b08-spaincentral.webapp.fabricapps.net) · [Informe Power BI](https://app.fabric.microsoft.com/groups/0245bb51-e0d1-40f1-b071-fcbbf1d7b155/reports/2410449a-d0d7-448d-9dd2-31c1d92a18f6) · workspace `DataDays-FabricApps-Portfolio-DEV` / carpeta `02-Combustibles`. El informe usa la muestra de 300 observaciones; la carga viva requiere clave EIA.

## Explora la solución

| Parte | Contenido |
| --- | --- |
| `packages/frontend/` | Fabric App Rayfin con arquitectura y preguntas del caso |
| [`case-source/docs/`](case-source/docs/) | Guía ilustrada y PDF de la clase |
| [`case-source/notebooks/`](case-source/notebooks/) | Notebooks de Silver y Gold, en `.ipynb` y `.py` |
| [`case-source/pipelines/`](case-source/pipelines/) | Plantilla Copy REST → Silver → Gold |
| [`case-source/powerbi/`](case-source/powerbi/) | PBIP con informe y modelo Direct Lake |
| [`fabric/`](fabric/) | Copias de despliegue con conexiones e identificadores resueltos |
| [`case-source/data/`](case-source/data/) | Respuesta EIA de ejemplo, no una fuente viva |
| [`docs/proyecto.md`](docs/proyecto.md) | Workspace, carpeta e inventario de recursos de esta app |

Los artefactos proceden del [repositorio general de Data Days](https://github.com/vicente2121/DATADAYS_DP600/tree/main/charla02/caso_02_historico_precios_combustibles). El workspace de Fabric **no está sincronizado con Git**.

## Lo que demuestra

- Bronze conserva una respuesta JSON por ejecución.
- Silver usa MERGE con grano serie y fecha para evitar duplicados.
- Gold prepara dimensiones, evolución mensual y último precio.
- El modelo Direct Lake da continuidad al análisis en Power BI.

## Reproducción y desarrollo

Para reproducir la ingesta viva se necesita una clave propia de EIA, introducida como parámetro seguro al ejecutar el pipeline. Nunca se guarda en este repositorio. La guía de réplica está en [`case-source/README.md`](case-source/README.md).

La app requiere Node.js 22.13 o posterior:

```powershell
npm install
npm run typecheck
npm run build
npm run dev
```

Consulta [`docs/rayfin-template.md`](docs/rayfin-template.md) para los comandos de la plantilla oficial.
