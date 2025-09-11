import unittest
from unittest.mock import Mock, patch
import ee
from ccdc_forest_detector import CCDCForestDetector


class TestCCDCForestDetector(unittest.TestCase):
    """Tests para CCDCForestDetector"""
    
    def setUp(self):
        """Setup para tests"""
        self.detector = CCDCForestDetector()
        
    def test_initialization(self):
        """Test inicialización básica"""
        self.assertIsNone(self.detector.study_area)
        self.assertIsNone(self.detector.s2_filtered)
        self.assertIsNone(self.detector.ccdc_result)
        self.assertEqual(len(self.detector.default_coords), 4)
        
    def test_set_study_area_with_coords(self):
        """Test establecer área de estudio con coordenadas"""
        coords = [-82.6150, 8.8900, -82.5850, 8.9100]
        
        with patch('ee.Geometry.Rectangle') as mock_rect, \
             patch('ee.FeatureCollection') as mock_fc, \
             patch('ee.Feature') as mock_feature:
            
            self.detector.set_study_area(coords=coords)
            mock_rect.assert_called_once_with(coords)
            
    def test_get_center_coordinates(self):
        """Test cálculo de coordenadas del centro"""
        coords = [-82.6150, 8.8900, -82.5850, 8.9100]
        center_lat, center_lon = self.detector.get_center_coordinates(coords)
        
        expected_lon = (-82.6150 + -82.5850) / 2
        expected_lat = (8.8900 + 8.9100) / 2
        
        self.assertEqual(center_lon, expected_lon)
        self.assertEqual(center_lat, expected_lat)
        
    def test_default_ccdc_params(self):
        """Test parámetros CCDC por defecto"""
        params = self.detector.default_ccdc_params
        
        self.assertEqual(params['minObservations'], 8)
        self.assertEqual(params['chiSquareProbability'], 0.90)
        self.assertEqual(params['minNumOfObservations'], 0.80)
        self.assertEqual(params['minNumOfSegments'], 2)
        self.assertEqual(params['recoveryThreshold'], 50)
        self.assertEqual(params['lambda_value'], 35000)
        
    @patch('ee.ImageCollection')
    def test_load_sentinel2_data_without_study_area(self, mock_collection):
        """Test cargar datos sin área de estudio definida"""
        with self.assertRaises(ValueError) as context:
            self.detector.load_sentinel2_data('2025-01-01', '2025-08-31')
        
        self.assertIn("área de estudio", str(context.exception))
        
    def test_run_ccdc_without_data(self):
        """Test ejecutar CCDC sin datos cargados"""
        with self.assertRaises(ValueError) as context:
            self.detector.run_ccdc()
        
        self.assertIn("datos Sentinel-2", str(context.exception))
        
    def test_get_change_layer_without_ccdc(self):
        """Test obtener capa de cambios sin ejecutar CCDC"""
        with self.assertRaises(ValueError) as context:
            self.detector.get_change_layer('2025-01-01', '2025-08-31')
        
        self.assertIn("ejecutar CCDC", str(context.exception))


if __name__ == '__main__':
    unittest.main()
