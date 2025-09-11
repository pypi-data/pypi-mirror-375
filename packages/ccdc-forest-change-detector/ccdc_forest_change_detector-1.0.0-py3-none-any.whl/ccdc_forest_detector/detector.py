import ee
import geemap
import datetime
import ipywidgets as widgets
import pandas as pd
from IPython.display import display
from .utils import CloudScorePlus


class CCDCForestDetector:
    """
    Clase principal para detección de cambios forestales usando CCDC
    """
    
    def __init__(self, project_id=None):
        """
        Inicializar el detector CCDC
        
        Args:
            project_id (str, optional): ID del proyecto de Google Earth Engine
        """
        self.project_id = project_id
        self.study_area = None
        self.s2_filtered = None
        self.ccdc_result = None
        self.year_month = None
        
        # Configuraciones por defecto
        self.default_coords = [-82.6150, 8.8900, -82.5850, 8.9100]
        self.default_ccdc_params = {
            'minObservations': 8,
            'chiSquareProbability': 0.90,
            'minNumOfObservations': 0.80,
            'minNumOfSegments': 2,
            'recoveryThreshold': 50,
            'lambda_value': 35000
        }
        
        # Paletas de colores
        self.change_palette = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', 
                              '#ff7f00', '#ffff33', '#a65628', '#a50026']
        
        self.ndvi_palette = ['#FFFFFF', '#CE7E45', '#DF923D', '#F1B555', '#FCD163', '#99B718',
                            '#74A901', '#66A000', '#529400', '#3E8601', '#207401', '#056201',
                            '#004C00', '#023B01', '#012E01', '#011D01', '#011301']
    
    def initialize_ee(self):
        """Inicializar Google Earth Engine"""
        try:
            if self.project_id:
                ee.Initialize(project=self.project_id)
            else:
                ee.Initialize()
        except Exception as e:
            print(f"Error inicializando Earth Engine: {e}")
            print("Ejecutando autenticación...")
            ee.Authenticate()
            if self.project_id:
                ee.Initialize(project=self.project_id)
            else:
                ee.Initialize()
    
    def set_study_area(self, feature_collection=None, filter_field=None, 
                      filter_values=None, coords=None):
        """
        Establecer área de estudio
        
        Args:
            feature_collection (ee.FeatureCollection, optional): Colección de características
            filter_field (str, optional): Campo para filtrar
            filter_values (list, optional): Valores para filtrar
            coords (list, optional): Coordenadas [xmin, ymin, xmax, ymax]
        """
        if feature_collection and filter_field and filter_values:
            self.study_area = feature_collection.filter(
                ee.Filter.inList(filter_field, filter_values)
            )
        elif coords:
            # Crear geometría a partir de coordenadas
            xmin, ymin, xmax, ymax = coords
            geometry = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax])
            self.study_area = ee.FeatureCollection([ee.Feature(geometry)])
        else:
            # Usar coordenadas por defecto
            xmin, ymin, xmax, ymax = self.default_coords
            geometry = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax])
            self.study_area = ee.FeatureCollection([ee.Feature(geometry)])
    
    def load_sentinel2_data(self, date_start, date_end, cloud_threshold=0.8):
        """
        Cargar y procesar datos Sentinel-2
        
        Args:
            date_start (str): Fecha de inicio (formato 'YYYY-MM-DD')
            date_end (str): Fecha de fin (formato 'YYYY-MM-DD')
            cloud_threshold (float): Umbral para Cloud Score Plus
        """
        if not self.study_area:
            raise ValueError("Debe establecer el área de estudio primero")
        
        # Sentinel-2 SR
        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(self.study_area) \
            .filterDate(date_start, date_end)
        
        # Recortar
        s2_clipped = s2.map(lambda img: img.clip(self.study_area))
        
        # Aplicar Cloud Score Plus
        cloud_scorer = CloudScorePlus()
        self.s2_filtered = cloud_scorer.apply_cloud_score_plus(
            s2_clipped, self.study_area, date_start, date_end, threshold=cloud_threshold
        )
    
    def add_ndvi(self, img):
        """Agregar banda NDVI a imagen"""
        ndvi = img.normalizedDifference(['B8', 'B12']).multiply(10000).int16().rename('ndvi')
        return img.addBands(ndvi)
    
    def run_ccdc(self, ccdc_params=None):
        """
        Ejecutar análisis CCDC
        
        Args:
            ccdc_params (dict, optional): Parámetros para CCDC
        """
        if not self.s2_filtered:
            raise ValueError("Debe cargar los datos Sentinel-2 primero")
        
        if ccdc_params is None:
            ccdc_params = self.default_ccdc_params
        
        # Agregar NDVI
        s2_ndvi = self.s2_filtered.map(self.add_ndvi)
        
        # Ejecutar CCDC
        self.ccdc_result = ee.Algorithms.TemporalSegmentation.Ccdc(
            s2_ndvi.select(['ndvi', 'B5', 'B12']),
            ['ndvi', 'B5', 'B12'],
            ['B5', 'B12'],
            ccdc_params['minObservations'],
            ccdc_params['chiSquareProbability'],
            ccdc_params['minNumOfObservations'],
            ccdc_params['minNumOfSegments'],
            ccdc_params['recoveryThreshold'],
            ccdc_params['lambda_value']
        )
    
    def get_change_layer(self, filter_start_date, filter_end_date):
        """
        Obtener capa de cambios filtrada por fechas
        
        Args:
            filter_start_date (str): Fecha inicio filtro (formato 'YYYY-MM-DD')
            filter_end_date (str): Fecha fin filtro (formato 'YYYY-MM-DD')
        
        Returns:
            ee.Image: Imagen con cambios codificados por año-mes
        """
        if not self.ccdc_result:
            raise ValueError("Debe ejecutar CCDC primero")
        
        # Último cambio (ruptura)
        tbreak = self.ccdc_result.select('tBreak')
        argmax = tbreak.arrayArgmax()
        argmax_scalar = argmax.arrayFlatten([['argmax_array']])
        last_break = tbreak.arrayGet(argmax_scalar).focal_min(1).focal_max(1)
        
        # Filtrar por fechas
        start_millis = ee.Date(filter_start_date).millis()
        end_millis = ee.Date(filter_end_date).millis()
        filtered = last_break.updateMask(
            last_break.gte(start_millis).And(last_break.lte(end_millis))
        )
        
        # Convertir a año y mes
        year = filtered.divide(1000 * 60 * 60 * 24 * 365.25).add(1970).floor()
        months_since_1970 = filtered.divide(1000 * 60 * 60 * 24 * 30.44).floor()
        month = months_since_1970.subtract(year.subtract(1970).multiply(12)).mod(12).add(1)
        self.year_month = year.multiply(100).add(month).rename('year_month')
        
        return self.year_month
    
    def monthly_rgb_median(self, year, month):
        """
        Obtener mediana RGB mensual
        
        Args:
            year (int): Año
            month (int): Mes
            
        Returns:
            ee.Image: Imagen RGB mediana del mes
        """
        if not self.s2_filtered:
            raise ValueError("Debe cargar los datos Sentinel-2 primero")
        
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, 'month')
        
        monthly_collection = self.s2_filtered.filterDate(start, end).filterBounds(self.study_area)
        return monthly_collection.median().select(['B4', 'B3', 'B2','B8','B8A','B5','B12']).clip(self.study_area)
    
    def monthly_ndvi_median(self, year, month):
        """
        Obtener mediana NDVI mensual
        
        Args:
            year (int): Año
            month (int): Mes
            
        Returns:
            ee.Image: Imagen NDVI mediana del mes
        """
        if not self.s2_filtered:
            raise ValueError("Debe cargar los datos Sentinel-2 primero")
        
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, 'month')
        monthly = self.s2_filtered.filterDate(start, end).median()
        ndvi = monthly.normalizedDifference(['B8', 'B12']).rename('NDVI')
        return ndvi.clip(self.study_area)
    
    def get_center_coordinates(self, coords=None):
        """
        Obtener coordenadas del centro del área de estudio
        
        Args:
            coords (list, optional): Coordenadas [xmin, ymin, xmax, ymax]
            
        Returns:
            tuple: (center_lat, center_lon)
        """
        if coords is None:
            coords = self.default_coords
        
        xmin, ymin, xmax, ymax = coords
        center_lon = (xmin + xmax) / 2
        center_lat = (ymin + ymax) / 2
        
        return center_lat, center_lon
