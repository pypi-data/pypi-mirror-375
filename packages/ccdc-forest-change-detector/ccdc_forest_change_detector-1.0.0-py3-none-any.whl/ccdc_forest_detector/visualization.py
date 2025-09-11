import geemap
import ipywidgets as widgets
from IPython.display import display
import ee
from .utils import VisualizationParams, DateUtils


class ForestVisualization:
    """Clase para crear visualizaciones de detección de cambios forestales"""
    
    def __init__(self, detector):
        """
        Inicializar visualización
        
        Args:
            detector (CCDCForestDetector): Instancia del detector
        """
        self.detector = detector
        self.vis_params = VisualizationParams()
    
    def create_dual_map_display(self, coords=None, zoom=12, title=None,
                               distrito_fc=None, corregimiento_fc=None):
        """
        Crear visualización con dos mapas lado a lado
        
        Args:
            coords (list, optional): Coordenadas del área
            zoom (int): Nivel de zoom
            title (str, optional): Título personalizado
            distrito_fc (ee.FeatureCollection, optional): Límites de distritos
            corregimiento_fc (ee.FeatureCollection, optional): Límites de corregimientos
        
        Returns:
            widgets.VBox: Widget con la visualización completa
        """
        # Obtener coordenadas del centro
        center_lat, center_lon = self.detector.get_center_coordinates(coords)
        
        # Crear mapas
        map1 = geemap.Map(center=[center_lat, center_lon], zoom=zoom)
        map2 = geemap.Map(center=[center_lat, center_lon], zoom=zoom)
        
        # Agregar mapas base
        map1.add_basemap('HYBRID')
        map2.add_basemap('HYBRID')
        
        # Título por defecto
        if title is None:
            title = "Detección de Cambios (CCDC) - Análisis Temporal"
        
        # Agregar límites administrativos si se proporcionan
        if distrito_fc and self.detector.study_area:
            distrito_styled = distrito_fc.style(**{
                'fillColor': '00000000', 'color': 'black', 'width': 2
            }).visualize(**{'opacity': 0.8})
            map1.addLayer(distrito_styled.clip(self.detector.study_area), {}, 'Límite - Distritos')
        
        if corregimiento_fc and self.detector.study_area:
            corregimiento_styled = corregimiento_fc.style(**{
                'fillColor': '00000000', 'color': 'black', 'width': 2
            }).visualize(**{'opacity': 0.8})
            map1.addLayer(corregimiento_styled.clip(self.detector.study_area), {}, 'Límite - Corregimientos')
        
        # Crear título widget
        titulo_widget = widgets.HTML(
            value=f"<h3 style='text-align:center;'>{title}</h3>"
        )
        
        # Crear contenedor de mapas
        mapas = widgets.HBox([map1, map2])
        
        # Layout final
        layout = widgets.VBox([titulo_widget, mapas])
        
        return layout, map1, map2
    
    def add_monthly_rgb_layers(self, map_widget, year, start_month, end_month):
        """
        Agregar capas RGB mensuales al mapa
        
        Args:
            map_widget: Widget del mapa
            year (int): Año
            start_month (int): Mes de inicio
            end_month (int): Mes de fin
        """
        for month in range(start_month, end_month + 1):
            rgb_img = self.detector.monthly_rgb_median(year, month)
            layer_name = f'RGB {year}-{str(month).zfill(2)}'
            map_widget.addLayer(rgb_img, self.vis_params.RGB_VIS, layer_name)
    
    def add_monthly_ndvi_layers(self, map_widget, year, start_month, end_month):
        """
        Agregar capas NDVI mensuales al mapa
        
        Args:
            map_widget: Widget del mapa
            year (int): Año
            start_month (int): Mes de inicio
            end_month (int): Mes de fin
        """
        for month in range(start_month, end_month + 1):
            ndvi_img = self.detector.monthly_ndvi_median(year, month)
            layer_name = f'NDVI {year}-{str(month).zfill(2)}'
            map_widget.addLayer(ndvi_img, self.vis_params.NDVI_VIS, layer_name)
    
    def add_change_layer(self, map_widget, change_image, year, start_month, end_month,
                        layer_name="Cambios mensuales"):
        """
        Agregar capa de cambios al mapa
        
        Args:
            map_widget: Widget del mapa
            change_image (ee.Image): Imagen con cambios
            year (int): Año
            start_month (int): Mes de inicio
            end_month (int): Mes de fin
            layer_name (str): Nombre de la capa
        """
        min_year_month = year * 100 + start_month
        max_year_month = year * 100 + end_month
        
        vis_params = self.vis_params.get_change_vis_params(min_year_month, max_year_month)
        map_widget.addLayer(change_image, vis_params, layer_name)
        
        # Agregar leyenda
        labels = self.vis_params.generate_month_labels(year, start_month, end_month)
        map_widget.add_legend(
            title="Mes del cambio",
            labels=labels,
            colors=self.vis_params.CHANGE_PALETTE[:len(labels)],
            position='bottomleft'
        )
    
    def create_complete_analysis_display(self, 
                                       data_start_date, data_end_date,
                                       change_start_date, change_end_date,
                                       rgb_year=2025, rgb_start_month=1, rgb_end_month=8,
                                       ndvi_year=2025, ndvi_start_month=1, ndvi_end_month=8,
                                       coords=None, zoom=12,
                                       distrito_fc=None, corregimiento_fc=None,
                                       title=None, cloud_threshold=0.8,
                                       ccdc_params=None):
        """
        Crear análisis completo con visualización
        
        Args:
            data_start_date (str): Fecha inicio datos ('YYYY-MM-DD')
            data_end_date (str): Fecha fin datos ('YYYY-MM-DD')
            change_start_date (str): Fecha inicio filtro cambios ('YYYY-MM-DD')
            change_end_date (str): Fecha fin filtro cambios ('YYYY-MM-DD')
            rgb_year (int): Año para capas RGB
            rgb_start_month (int): Mes inicio RGB
            rgb_end_month (int): Mes fin RGB
            ndvi_year (int): Año para capas NDVI
            ndvi_start_month (int): Mes inicio NDVI
            ndvi_end_month (int): Mes fin NDVI
            coords (list, optional): Coordenadas área de estudio
            zoom (int): Nivel de zoom
            distrito_fc (ee.FeatureCollection, optional): Límites distritos
            corregimiento_fc (ee.FeatureCollection, optional): Límites corregimientos
            title (str, optional): Título personalizado
            cloud_threshold (float): Umbral para Cloud Score Plus
            ccdc_params (dict, optional): Parámetros CCDC personalizados
        
        Returns:
            widgets.VBox: Visualización completa
        """
        # Cargar datos
        self.detector.load_sentinel2_data(data_start_date, data_end_date, cloud_threshold)
        
        # Ejecutar CCDC
        self.detector.run_ccdc(ccdc_params)
        
        # Obtener capa de cambios
        change_layer = self.detector.get_change_layer(change_start_date, change_end_date)
        
        # Crear visualización
        layout, map1, map2 = self.create_dual_map_display(
            coords, zoom, title, distrito_fc, corregimiento_fc
        )
        
        # Agregar capas RGB al primer mapa
        self.add_monthly_rgb_layers(map1, rgb_year, rgb_start_month, rgb_end_month)
        
        # Agregar capas NDVI al segundo mapa
        self.add_monthly_ndvi_layers(map2, ndvi_year, ndvi_start_month, ndvi_end_month)
        
        # Agregar capa de cambios a ambos mapas
        change_start_year = int(change_start_date[:4])
        change_start_month_num = int(change_start_date[5:7])
        change_end_month_num = int(change_end_date[5:7])
        
        self.add_change_layer(
            map1, change_layer, change_start_year, 
            change_start_month_num, change_end_month_num,
            f"Cambios {change_start_date[:7]} - {change_end_date[:7]}"
        )
        
        self.add_change_layer(
            map2, change_layer, change_start_year,
            change_start_month_num, change_end_month_num,
            f"Cambios {change_start_date[:7]} - {change_end_date[:7]}"
        )
        
        return layout
    
    def create_simple_rgb_display(self, year, start_month, end_month, 
                                 coords=None, zoom=12, title=None):
        """
        Crear visualización simple solo con capas RGB
        
        Args:
            year (int): Año
            start_month (int): Mes de inicio
            end_month (int): Mes de fin
            coords (list, optional): Coordenadas
            zoom (int): Nivel de zoom
            title (str, optional): Título
        
        Returns:
            geemap.Map: Mapa con capas RGB
        """
        center_lat, center_lon = self.detector.get_center_coordinates(coords)
        
        map_widget = geemap.Map(center=[center_lat, center_lon], zoom=zoom)
        map_widget.add_basemap('HYBRID')
        
        self.add_monthly_rgb_layers(map_widget, year, start_month, end_month)
        
        if title:
            print(f"=== {title} ===")
        
        return map_widget
    
    def create_simple_ndvi_display(self, year, start_month, end_month,
                                  coords=None, zoom=12, title=None):
        """
        Crear visualización simple solo con capas NDVI
        
        Args:
            year (int): Año
            start_month (int): Mes de inicio
            end_month (int): Mes de fin
            coords (list, optional): Coordenadas
            zoom (int): Nivel de zoom
            title (str, optional): Título
        
        Returns:
            geemap.Map: Mapa con capas NDVI
        """
        center_lat, center_lon = self.detector.get_center_coordinates(coords)
        
        map_widget = geemap.Map(center=[center_lat, center_lon], zoom=zoom)
        map_widget.add_basemap('HYBRID')
        
        self.add_monthly_ndvi_layers(map_widget, year, start_month, end_month)
        
        if title:
            print(f"=== {title} ===")
        
        return map_widget