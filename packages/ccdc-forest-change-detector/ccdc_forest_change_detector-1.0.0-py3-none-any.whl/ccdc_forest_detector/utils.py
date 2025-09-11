import ee


class CloudScorePlus:
    """Utilidad para aplicar Cloud Score Plus a colecciones de imágenes"""
    
    @staticmethod
    def apply_cloud_score_plus(img_col, roi, start, end, qa_band='cs_cdf', threshold=0.8):
        """
        Aplicar Cloud Score Plus para enmascarar nubes
        
        Args:
            img_col (ee.ImageCollection): Colección de imágenes
            roi (ee.FeatureCollection): Región de interés
            start (str): Fecha de inicio
            end (str): Fecha de fin
            qa_band (str): Banda de calidad a usar
            threshold (float): Umbral para enmascaramiento
            
        Returns:
            ee.ImageCollection: Colección con máscaras aplicadas
        """
        cs_plus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED') \
            .filterBounds(roi).filterDate(start, end)

        joined = ee.Join.inner().apply(
            primary=img_col,
            secondary=cs_plus,
            condition=ee.Filter.equals(leftField='system:index', rightField='system:index')
        )

        def merge_and_mask(pair):
            primary = ee.Image(pair.get('primary'))
            score = ee.Image(pair.get('secondary')).select(qa_band)
            return primary.updateMask(score.gte(threshold))

        return ee.ImageCollection(joined.map(merge_and_mask))


class DateUtils:
    """Utilidades para manejo de fechas"""
    
    @staticmethod
    def generate_date_range(start_date, end_date, frequency='monthly'):
        """
        Generar rango de fechas
        
        Args:
            start_date (str): Fecha de inicio
            end_date (str): Fecha de fin
            frequency (str): Frecuencia ('monthly', 'weekly', 'daily')
            
        Returns:
            list: Lista de tuplas (año, mes) si frequency='monthly'
        """
        from datetime import datetime, timedelta
        import calendar
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        dates = []
        
        if frequency == 'monthly':
            current = start.replace(day=1)
            while current <= end:
                dates.append((current.year, current.month))
                # Avanzar al siguiente mes
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        
        return dates


class GeometryUtils:
    """Utilidades para manejo de geometrías"""
    
    @staticmethod
    def create_rectangle_from_coords(coords):
        """
        Crear rectángulo de Earth Engine desde coordenadas
        
        Args:
            coords (list): [xmin, ymin, xmax, ymax]
            
        Returns:
            ee.Geometry.Rectangle: Geometría rectangular
        """
        return ee.Geometry.Rectangle(coords)
    
    @staticmethod
    def get_bounds_from_feature_collection(feature_collection):
        """
        Obtener límites de una colección de características
        
        Args:
            feature_collection (ee.FeatureCollection): Colección de características
            
        Returns:
            ee.Geometry: Geometría de los límites
        """
        return feature_collection.geometry().bounds()


class VisualizationParams:
    """Parámetros de visualización predefinidos"""
    
    RGB_VIS = {'min': 0, 'max': 3000, 'bands': ['B4', 'B3', 'B2']}
    
    NDVI_VIS = {
        'min': 0,
        'max': 1,
        'palette': ['#FFFFFF', '#CE7E45', '#DF923D', '#F1B555', '#FCD163', '#99B718',
                   '#74A901', '#66A000', '#529400', '#3E8601', '#207401', '#056201',
                   '#004C00', '#023B01', '#012E01', '#011D01', '#011301']
    }
    
    CHANGE_PALETTE = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', 
                     '#ff7f00', '#ffff33', '#a65628', '#a50026']
    
    @classmethod
    def get_change_vis_params(cls, min_year_month, max_year_month):
        """
        Obtener parámetros de visualización para cambios
        
        Args:
            min_year_month (int): Año-mes mínimo (ej: 202501)
            max_year_month (int): Año-mes máximo (ej: 202508)
            
        Returns:
            dict: Parámetros de visualización
        """
        return {
            'min': min_year_month,
            'max': max_year_month,
            'palette': cls.CHANGE_PALETTE
        }
    
    @classmethod
    def generate_month_labels(cls, year, start_month, end_month):
        """
        Generar etiquetas de meses
        
        Args:
            year (int): Año
            start_month (int): Mes de inicio
            end_month (int): Mes de fin
            
        Returns:
            list: Lista de etiquetas de meses
        """
        return [f"{year}-{str(m).zfill(2)}" for m in range(start_month, end_month + 1)]
