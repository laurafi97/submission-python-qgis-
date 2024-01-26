# test_project.py

import unittest
from unittest.mock import patch
from pathlib import Path
from qgis.core import QgsProject, QgsVectorLayer
from qgis.gui import QgsMapCanvas
from qgis.utils import iface
from PyQt5.QtWidgets import QAction
from project import main

class TestProjectScript(unittest.TestCase):

    def setUp(self):
        # Mock QgsProject methods
        self.mock_clear = patch.object(QgsProject.instance(), 'clear').start()
        self.mock_addRasterLayer = patch.object(iface, 'addRasterLayer').start()
        self.mock_mapLayersByName = patch.object(QgsProject.instance(), 'mapLayersByName').start()
        self.mock_setCrs = patch.object(QgsProject.instance(), 'setCrs').start()

        # Mock QgsVectorLayer methods
        self.mock_dataProvider = patch.object(QgsVectorLayer, 'dataProvider').start()
        self.mock_setEncoding = patch.object(QgsVectorLayer, 'setEncoding').start()
        self.mock_setName = patch.object(QgsVectorLayer, 'setName').start()
        self.mock_addMapLayer = patch.object(QgsProject.instance(), 'addMapLayer').start()
        self.mock_extent = patch.object(QgsVectorLayer, 'extent').start()

        # Mock QgsMapCanvas methods
        self.mock_setExtent = patch.object(QgsMapCanvas, 'setExtent').start()
        self.mock_refresh = patch.object(QgsMapCanvas, 'refresh').start()

        # Mock QgsProcessing methods
        self.mock_processing_run = patch('project.processing.run').start()

        # Mock iface methods
        self.mock_mainWindow = patch.object(iface, 'mainWindow').start()
        self.mock_findChild = patch.object(self.mock_mainWindow, 'findChild').start()
        self.mock_trigger = patch.object(self.mock_findChild.return_value, 'trigger').start()

    def tearDown(self):
        # Stop patching after each test
        patch.stopall()

    def test_main(self):
        # Call the main function
        main()

        # Assert that QgsProject methods are called
        self.mock_clear.assert_called_once()
        self.mock_addRasterLayer.assert_called_once()
        self.mock_mapLayersByName.assert_called()
        self.mock_setCrs.assert_called_once()

        # Assert that QgsVectorLayer methods are called
        self.mock_dataProvider.assert_called()
        self.mock_setEncoding.assert_called_once()
        self.mock_setName.assert_called()
        self.mock_addMapLayer.assert_called()

        # Assert that QgsMapCanvas methods are called
        self.mock_setExtent.assert_called_once()
        self.mock_refresh.assert_called_once()

        # Assert that QgsProcessing methods are called
        self.mock_processing_run.assert_called()

        # Assert that iface methods are called
        self.mock_mainWindow.assert_called_once()
        self.mock_findChild.assert_called()
        self.mock_trigger.assert_called_once()

if __name__ == '__main__':
    unittest.main()
