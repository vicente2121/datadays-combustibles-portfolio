# Definiciones publicadas · combustibles

Estas copias apuntan al workspace `DataDays-FabricApps-Portfolio-DEV`. `case-source/` conserva el material original. El workspace no tiene integración Git.

- `pipeline-content.json`: Copy REST EIA → Silver → Gold con IDs de los elementos publicados y conexiones REST/Lakehouse existentes. Requiere `eia_api_key` en cada ejecución viva; la clave no se guarda aquí.
- `SemanticModel/`: modelo TMDL Direct Lake dirigido a `DD02_LH_Combustibles`.
- `Report/`: PBIR enlazado al modelo publicado mediante `byConnection`, la forma de la API de Fabric.

Para comprobar el análisis sin clave EIA se cargó el JSON de ejemplo de `case-source/data/` en `Files/bronze/eia/`; luego se ejecutaron Silver y Gold. El modelo devolvió 300 observaciones Silver y 35 meses. El informe publicado refleja esta muestra hasta una nueva ejecución viva del pipeline.
