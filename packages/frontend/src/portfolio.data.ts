const source = 'https://github.com/vicente2121/datadays-combustibles-portfolio';
const path = 'case-source';

export const caseStudy = {
  number: '02', motif: 'fuel', monogram: 'EIA',
  kicker: 'CASO 02 · HISTÓRICO DE PRECIOS DE COMBUSTIBLES',
  title: 'Del dato semanal a una historia legible.',
  intro: 'Un histórico reproducible de gasolina y diésel de la EIA: ingesta REST, Silver idempotente, resúmenes Gold y análisis en Direct Lake.',
  disclosure: 'Portafolio documental. Los precios del informe original dependen de la ejecución y no se muestran aquí en directo.',
  sourceUrl: `${source}/tree/main/${path}`,
  reportUrl: 'https://app.fabric.microsoft.com/groups/0245bb51-e0d1-40f1-b071-fcbbf1d7b155/reports/2410449a-d0d7-448d-9dd2-31c1d92a18f6',
  flow: 'EIA API → BRONZE → SILVER → GOLD → POWER BI',
  metrics: [
    { value: '2', label: 'series de combustible analizadas' },
    { value: '4', label: 'tablas Gold para el análisis' },
    { value: '1', label: 'histórico Silver deduplicado' },
  ],
  domain: 'ENERGÍA · SERIE TEMPORAL · DIRECT LAKE',
  challengeTitle: 'Acumular sin duplicar.',
  challenge: 'Una API semanal puede devolver observaciones ya vistas. Conservar cada respuesta es útil para auditoría, pero el histórico analítico necesita una única observación por serie y fecha. El caso separa ambas necesidades y convierte semanas en vistas mensuales y último precio para el informe.',
  takeaway: 'Dos ejecuciones pueden dejar dos JSON en Bronze y el mismo número de observaciones válidas en Silver.',
  stages: [
    { name: 'Bronze', short: 'Respuesta REST por ejecución', title: 'Cada corrida conserva su respuesta.', description: 'Una actividad Copy llama a la API de EIA y guarda el JSON bajo Files/bronze/eia con un nombre asociado al RunId.', points: ['Clave EIA introducida en la ejecución, fuera del repositorio', 'Entrada y salida seguras en la actividad de copia', 'Originales separados por corrida'], caption: 'PL_EIA_Precios_Append.template.json' },
    { name: 'Silver', short: 'Observación única por fecha', title: 'MERGE para un histórico idempotente.', description: 'El notebook procesa las respuestas, tipa fechas y valores, deduplica y actualiza silver.precios_combustibles_historico mediante MERGE.', points: ['Grano: serie de combustible y fecha', 'Particiones por año y mes', 'Una segunda ejecución no multiplica observaciones'], caption: 'COPIAR_PEGAR_01_Silver.ipynb' },
    { name: 'Gold', short: 'Resumen mensual y último valor', title: 'Datos listos para comparar.', description: 'El segundo notebook crea dimensiones de combustible y mes, un hecho de precios mensuales y un hecho de último precio.', points: ['gold.dim_combustible y gold.dim_mes', 'gold.fact_precios_mensuales', 'gold.fact_ultimo_precio'], caption: 'COPIAR_PEGAR_02_Gold.ipynb' },
    { name: 'Power BI', short: 'Lectura temporal en Direct Lake', title: 'Evolución sin exportaciones manuales.', description: 'El proyecto PBIP incluye un informe y un modelo semántico Direct Lake sobre las tablas Gold del Lakehouse.', points: ['Relaciones de combustible y mes', 'Visual de evolución mensual', 'Modelo e informe en el mismo proyecto PBIP'], caption: 'PreciosCombustibles.pbip' },
  ],
  resultsIntro: 'El material de la clase muestra el recorrido completo, desde la API hasta la lectura del histórico.',
  outcomes: [
    { question: '¿Cómo evoluciona cada combustible?', answer: 'El hecho mensual permite comparar las series en una línea temporal común.' },
    { question: '¿Cuál es el último precio disponible?', answer: 'Gold materializa una tabla específica de último valor por combustible.' },
    { question: '¿Qué ocurre al repetir la ingesta?', answer: 'Bronze añade una nueva evidencia; Silver conserva una observación por serie y fecha.' },
    { question: '¿Se puede rastrear el origen?', answer: 'El JSON por RunId permite revisar la respuesta que alimentó la transformación.' },
  ],
  limit: 'La clave de la API EIA es personal y no forma parte del repositorio. El informe publicado usa por ahora el JSON de ejemplo incluido; una ingesta viva puede incorporar más semanas. Las plantillas originales conservan marcadores para nuevas réplicas.',
  artifacts: [
    { title: 'Informe en Fabric', description: 'Histórico y evolución sobre el modelo publicado', href: 'https://app.fabric.microsoft.com/groups/0245bb51-e0d1-40f1-b071-fcbbf1d7b155/reports/2410449a-d0d7-448d-9dd2-31c1d92a18f6', kind: 'repo' },
    { title: 'Guía ilustrada', description: 'Pasos de la clase y comprobaciones', href: `${source}/blob/main/${path}/docs/guia-clase-02.md`, kind: 'guide' },
    { title: 'Notebooks', description: 'Procesamiento Silver y agregados Gold', href: `${source}/tree/main/${path}/notebooks`, kind: 'code' },
    { title: 'Pipeline', description: 'Plantilla Copy REST → Silver → Gold', href: `${source}/tree/main/${path}/pipelines`, kind: 'code' },
    { title: 'Proyecto Power BI', description: 'PBIR, TMDL y modelo Direct Lake', href: `${source}/tree/main/${path}/powerbi`, kind: 'repo' },
  ],
  replicaTitle: 'Repite la cadena en tu workspace.',
  replicaSteps: ['Crea un Lakehouse con esquemas y vincúlalo a los dos notebooks.', 'Crea la conexión REST y aporta tu clave EIA al ejecutar el pipeline.', 'Sustituye los seis identificadores de la plantilla del pipeline.', 'Conecta el modelo Direct Lake al Lakehouse nuevo y comprueba Silver y Gold.'],
  footer: 'CASO 02 / COMBUSTIBLES',
};
