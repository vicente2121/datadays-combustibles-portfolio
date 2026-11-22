import type { VisualizationSpec } from '@microsoft/fabric-visuals';
import primarySpecJson from './queries/report/primarySpec.visual.json';
import secondarySpecJson from './queries/report/secondarySpec.visual.json';
const primarySpec = primarySpecJson as unknown as VisualizationSpec;
const secondarySpec = secondarySpecJson as unknown as VisualizationSpec;
import type { ColumnMetadataMap } from './lib/to-data-table';
import overviewQuery from './queries/report/overview.dax?raw';
import primaryQuery from './queries/report/monthly.dax?raw';
import secondaryQuery from './queries/report/latest.dax?raw';

const primaryMetadata: ColumnMetadataMap = {
  'dim_mes[fecha_mes]': { name: 'Fecha', displayName: 'Mes' },
  'dim_combustible[combustible]': { name: 'Combustible', displayName: 'Combustible' },
  '[PrecioPromedio]': { name: 'PrecioPromedio', displayName: 'Precio mensual', format: '0.000' },
};
const secondaryMetadata: ColumnMetadataMap = {
  'dim_combustible[combustible]': { name: 'Combustible', displayName: 'Combustible' },
  '[UltimoPrecio]': { name: 'UltimoPrecio', displayName: 'Último precio', format: '0.000' },
  '[VariacionSemanal]': { name: 'VariacionSemanal', displayName: 'Variación semanal (%)', format: '0.00' },
};

export const report = {
  connection: 'fuelmodel',
  title: 'Dos combustibles, una tendencia.',
  intro: 'Precios mensuales y últimos valores de gasolina regular y diésel, leídos del modelo publicado.',
  overviewQuery,
  primaryQuery,
  secondaryQuery,
  secondarySource: 'secondary' as const,
  metrics: [
    { label: 'Observaciones', subtitle: 'Muestra EIA cargada', field: '[Observaciones]', format: '0', compact: false },
    { label: 'Meses', subtitle: 'Dimensión temporal', field: '[Meses]', format: '0', compact: false },
    { label: 'Series', subtitle: 'Gasolina y diésel', field: '[Series]', format: '0', compact: false },
    { label: 'Precio medio mensual', subtitle: 'USD por galón · muestra', field: '[PrecioMensualPromedio]', format: '0.000', compact: false },
  ],
  primaryTitle: 'Evolución mensual',
  primarySubtitle: 'Los 12 meses más recientes de la muestra',
  primarySpec,
  primaryMetadata,
  secondaryTitle: 'Último precio disponible',
  secondarySubtitle: 'Cada serie conserva su propia fecha de referencia',
  secondarySpec,
  secondaryMetadata,
  disclosure: 'Datos de ejemplo cargados en el Lakehouse: 300 observaciones. Una carga EIA nueva requiere una clave introducida al ejecutar el pipeline.',
};
