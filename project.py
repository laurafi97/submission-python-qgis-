# QGIS with Python
# ISA, ULIsboa, 2023
# Instructor: Manuel Campagnolo

# digital field map data form the City Ebelsbach - Germany
# (source: https://geodaten.bayern.de/opengeodata/index.html 2023)

import os
from pathlib import Path
from console.console import _console
from PyQt5.QtWidgets import QAction
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsProcessing,
    QgsExpression, QgsExpressionContext, QgsExpressionContextUtils,
    QgsStyle, QgsGraduatedSymbolRenderer, QgsClassificationJenks,
    QgsRendererRangeLabelFormat
)
from qgis.gui import QgsMapCanvas
from qgis.utils import iface
from PyQt5.QtCore import QVariant


# Constants

fn_land_parcel = 'land_parcel.shp'
fn_buildings = 'buildings.shp'
fn_area_of_interest = 'area_of_interest.shp'

crs = 'EPSG:4326'  # WGS 84

# project and data folders
project_name = 'space_ratio_calculation'
input_subfolder = 'input'
output_subfolder = 'output'
# basemap: OpenStreetMap
uri_OSM = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0'



class ProjectProcessor:
    def __init__(self, project_name='space_ratio_calculation', input_subfolder='input', output_subfolder='output'):
        self.project_name = project_name
        self.input_subfolder = input_subfolder
        self.output_subfolder = output_subfolder

    def create_project(self):
        my_folder = self._get_script_folder()
        my_project = self._create_project_instance(my_folder, self.project_name)
        return my_project

    def _get_script_folder(self):
        script_path = Path(_console.console.tabEditorWidget.currentWidget().path)
        return script_path.parent

    def _create_project_instance(self, my_folder, project_name):
        my_project = QgsProject.instance()
        my_project.clear()
        my_project.setTitle(project_name)
        project_file = str(my_folder / project_name) + '.qgz'
        my_project.write(project_file)
        return my_project
        
# load my_functions.py
exec(Path(my_folder/ "my_functions.py").read_text())

    def main(self):
        my_folder = self._get_script_folder()
        
        
        my_project = self.create_project()

        if my_project is None:
            print("Error: Unable to create the project.")
            return
              
        # add basemap
        QgsProject.instance().clear()
        iface.addRasterLayer(uri_OSM, "OpenStreetMap", "wms")

        # load shapefiles
        fn = my_folder / self.input_subfolder / fn_land_parcel
        land_parcel = my_add_vector_layer_from_shapefile(fn, 'land_parcel')

        fn = my_folder / self.input_subfolder / fn_buildings
        buildings = my_add_vector_layer_from_shapefile(fn, 'buildings')

        fn = my_folder / self.input_subfolder / fn_area_of_interest
        area_of_interest = my_add_vector_layer_from_shapefile(fn, 'area_of_interest')

        # zoom to layer
        my_zoom_to_layer('area_of_interest')

        # Crop layers to area of interest
        dict_params = {'INPUT': land_parcel, 'OVERLAY': area_of_interest, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        crop_land_parcel = my_processing_run_vector_clip("native:clip", land_parcel, area_of_interest, dict_params,
                                                        'land_parcel_crop')

        dict_params = {'INPUT': buildings, 'OVERLAY': area_of_interest, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        crop_buildings = my_processing_run_vector_clip("native:clip", buildings, area_of_interest, dict_params,
                                                      'buildings_crop')

        # Toggle layer visibility
        toggle_layer_visibility(my_project, 'land_parcel', False)
        toggle_layer_visibility(my_project, 'buildings', False)

        # Join attributes by location
        output_layer_name = 'buldings_parcelID'
        join_fields = ['idflurst']
        joined_layer = my_join_attributes_by_location(crop_buildings, crop_land_parcel, join_fields,
                                                      output_layer_name)

        # Add area column to the joined layer
        add_area = add_area_column(joined_layer, column_name='Buildings_Area')

        # Aggregate the 'Buildings_Area' attribute by parcel ID (idflurst)
        aggregate_layer = 'buildings_aggregated'
        aggregate_result = my_aggregate_function(joined_layer, '"idflurst"', [
            {'aggregate': 'first_value', 'delimiter': ',', 'input': '"idflurst"', 'length': 16, 'name': 'idflurst',
             'precision': 0, 'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'aggregate': 'sum', 'delimiter': ',', 'input': '"Buildings_Area"', 'length': 10, 'name': 'Buildings_Area',
             'precision': 0, 'sub_type': 0, 'type': 6, 'type_name': 'double precision'}
        ], output_layer_name=aggregate_layer)

        # Join aggregated results back to the cropped land parcel
        joined_by_field_value = 'land_parcel_buildings_area'
        join_result = my_join_attributes_by_field_value(crop_land_parcel, aggregate_result, 'idflurst', 'idflurst',
                                                        ['Buildings_Area'], output_layer_name=joined_by_field_value)

        # Update the 'Buildings_Area' attribute in the joined layer
        update_area_attribute(join_result)

        # Add Land parcel area to the layer
        add_area = add_area_column(join_result, column_name='LandParcel_Area')

        # Calculate building-to-land ratio
        building_area_field = 'Buildings_Area'
        land_area_field = 'LandParcel_Area'
        ratio_field_name = 'Building_Land_Ratio'
        calculate_building_land_ratio(join_result, building_area_field, land_area_field, ratio_field_name)

        # Set graduated symbology for the 'land_parcel_buildings_area' layer
        set_graduated_symbology(join_result, ratio_field_name, num_classes=5, ramp_name='Reds')

        # Toggle layer visibility of the temporary layers
        toggle_layer_visibility(my_project, 'area_of_interest', False)
        toggle_layer_visibility(my_project, 'land_parcel_crop', False)
        toggle_layer_visibility(my_project, 'buildings_crop', False)
        toggle_layer_visibility(my_project, 'buldings_parcelID', False)
        toggle_layer_visibility(my_project, 'buildings_aggregated', False)

        # Save layer in output folder with style as default
        fn_land_parcel_buildings_area = my_folder / self.output_subfolder / 'land_parcel_buildings_area.shp'
        my_export_layer_as_file(join_result, fn_land_parcel_buildings_area)

        # save project
        iface.mainWindow().findChild(QAction, 'mActionSaveProject').trigger()


if __name__ == '__console__':
    processor = ProjectProcessor()
    processor.main()
