# CCDC Forest Change Detector

Una librería de Python para la detección de cambios forestales utilizando el algoritmo CCDC (Continuous Change Detection and Classification) con Google Earth Engine.

## Características

- Detección de cambios temporales en cobertura forestal usando CCDC
- Procesamiento de imágenes Sentinel-2 con enmascaramiento de nubes (Cloud Score Plus)
- Visualización interactiva con mapas duales
- Análisis de NDVI temporal
- Configuración flexible de áreas de estudio y parámetros
- Exportación de resultados y visualizaciones

## Instalación

```bash
pip install ccdc-forest-change-detector
```

## Requisitos previos

1. **Google Earth Engine**: Necesitas tener una cuenta de Google Earth Engine y autenticación configurada
2. **Jupyter Notebook/Lab**: Recomendado para visualizaciones interactivas

### Configuración de Google Earth Engine

```python
import ee
ee.Authenticate()  # Solo la primera vez
ee.Initialize(project='tu-proyecto-gee')  # Opcional: especifica tu proyecto
```

## Uso básico

### Ejemplo 1: Análisis completo con áreas predefinidas

```python
from ccdc_forest_detector import CCDCForestDetector, ForestVisualization
import ee

# Inicializar detector
detector = CCDCForestDetector(project_id='tu-proyecto-gee')
detector.initialize_ee()

# Cargar límites administrativos (opcional)
distritos = ee.FeatureCollection("projects/tu-proyecto/assets/Lim_Distrito")
corregimientos = ee.FeatureCollection("projects/tu-proyecto/assets/Lim_Corregimiento")

# Establecer área de estudio usando feature collections
detector.set_study_area(
    feature_collection=corregimientos,
    filter_field='LMCO_NOMB',
    filter_values=['Paso Ancho', 'Cerro Punta']
)

# Crear visualizador
visualizer = ForestVisualization(detector)

# Ejecutar análisis completo
display_widget = visualizer.create_complete_analysis_display(
    data_start_date='2023-01-01',
    data_end_date='2025-08-20',
    change_start_date='2025-01-01',
    change_end_date='2025-08-31',
    title="Detección de Cambios - Chiriquí (Paso Ancho | Cerro Punta)",
    distrito_fc=distritos,
    corregimiento_fc=corregimientos
)

# Mostrar visualización
display(display_widget)
```

### Ejemplo 2: Análisis con coordenadas personalizadas

```python
from ccdc_forest_detector import CCDCForestDetector, ForestVisualization

# Inicializar detector
detector = CCDCForestDetector()
detector.initialize_ee()

# Establecer área usando coordenadas [xmin, ymin, xmax, ymax]
coords = [-82.6150, 8.8900, -82.5850, 8.9100]
detector.set_study_area(coords=coords)

# Cargar datos Sentinel-2
detector.load_sentinel2_data(
    date_start='2023-01-01',
    date_end='2025-08-20',
    cloud_threshold=0.8
)

# Ejecutar CCDC con parámetros personalizados
ccdc_params = {
    'minObservations': 6,
    'chiSquareProbability': 0.95,
    'minNumOfObservations': 0.8,
    'minNumOfSegments': 2,
    'recoveryThreshold': 50,
    'lambda_value': 25000
}
detector.run_ccdc(ccdc_params)

# Obtener capa de cambios
change_layer = detector.get_change_layer('2025-01-01', '2025-08-31')

# Crear visualización
visualizer = ForestVisualization(detector)
layout, map1, map2 = visualizer.create_dual_map_display(
    coords=coords,
    zoom=12,
    title="Análisis de Cambios Personalizado"
)

# Agregar capas manualmente
visualizer.add_monthly_rgb_layers(map1, 2025, 1, 8)
visualizer.add_monthly_ndvi_layers(map2, 2025, 1, 8)
visualizer.add_change_layer(map1, change_layer, 2025, 1, 8)
visualizer.add_change_layer(map2, change_layer, 2025, 1, 8)

display(layout)
```

### Ejemplo 3: Análisis solo NDVI

```python
from ccdc_forest_detector import CCDCForestDetector, ForestVisualization

detector = CCDCForestDetector()
detector.initialize_ee()
detector.set_study_area(coords=[-82.6150, 8.8900, -82.5850, 8.9100])

# Cargar datos
detector.load_sentinel2_data('2025-01-01', '2025-08-31')

# Crear visualización solo NDVI
visualizer = ForestVisualization(detector)
ndvi_map = visualizer.create_simple_ndvi_display(
    year=2025, 
    start_month=1, 
    end_month=8,
    title="Análisis NDVI 2025"
)

ndvi_map
```

## Parámetros de configuración

### Parámetros CCDC

```python
ccdc_params = {
    'minObservations': 8,           # Mínimo de observaciones por segmento
    'chiSquareProbability': 0.90,   # Probabilidad chi-cuadrado
    'minNumOfObservations': 0.80,   # Proporción mínima de observaciones
    'minNumOfSegments': 2,          # Mínimo número de segmentos
    'recoveryThreshold': 50,        # Umbral de recuperación
    'lambda_value': 35000           # Parámetro lambda para regularización
}
```

### Parámetros de visualización

La librería incluye paletas de colores predefinidas:

- **RGB**: Visualización en color verdadero
- **NDVI**: Gradiente verde para índice de vegetación
- **Cambios**: 8 colores para diferentes meses de cambio

## Métodos principales

### CCDCForestDetector

- `initialize_ee()`: Inicializar Google Earth Engine
- `set_study_area()`: Establecer área de estudio
- `load_sentinel2_data()`: Cargar y procesar datos Sentinel-2
- `run_ccdc()`: Ejecutar análisis CCDC
- `get_change_layer()`: Obtener capa de cambios
- `monthly_rgb_median()`: Generar compuesto RGB mensual
- `monthly_ndvi_median()`: Generar compuesto NDVI mensual

### ForestVisualization

- `create_complete_analysis_display()`: Análisis completo automatizado
- `create_dual_map_display()`: Crear visualización con dos mapas
- `add_monthly_rgb_layers()`: Agregar capas RGB mensuales
- `add_monthly_ndvi_layers()`: Agregar capas NDVI mensuales
- `add_change_layer()`: Agregar capa de detección de cambios

## Casos de uso

1. **Monitoreo de deforestación**: Detectar pérdida de cobertura forestal
2. **Análisis temporal de vegetación**: Seguimiento de cambios estacionales
3. **Evaluación de recuperación forestal**: Identificar áreas de regeneración
4. **Estudios de impacto ambiental**: Análisis antes/después de intervenciones
5. **Planificación territorial**: Apoyo en toma de decisiones sobre uso del suelo

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear branch para nueva funcionalidad
3. Agregar tests
4. Enviar pull request

## Licencia

MIT License - ver archivo LICENSE para detalles.

## Soporte

- GitHub Issues: [Reportar problemas](https://github.com/tuusuario/ccdc-forest-change-detector/issues)
- Documentación: [Wiki del proyecto](https://github.com/tuusuario/ccdc-forest-change-detector/wiki)
- Google Earth Engine: [Documentación oficial](https://developers.google.com/earth-engine)

## Cita

Si usas esta librería en tu investigación, por favor cita:

```
Elvis Garcia (2025). CCDC Forest Change Detector: A Python library for forest change detection using Google Earth Engine. 
```
