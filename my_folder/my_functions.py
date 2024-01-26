def my_create_project(my_folder, project_name):
    """
    Create a new project, set title, and save.

    :param my_folder: Path: Folder where the project will be saved.
    :param project_name: str: Name of the project.
    :return: QgsProject: Created project instance.
    """
    my_project = QgsProject.instance()  # QgsProject
    my_project.clear()  # Clear project
    my_project.setTitle(project_name)
    project_file = str(my_folder / project_name) + '.qgz'
    # Save project to file
    my_project.write(project_file)
    return my_project  # Return the created project


def my_add_vector_layer_from_shapefile(fn, ln):
    """
    Add and name a vector layer from a file.

    :param fn: str: Path to the file.
    :param ln: str: Output layer name.
    :return: QgsVectorLayer: Added vector layer.
    """
    mylayer = QgsVectorLayer(str(fn), "", "ogr")
    # set encoding to utf-8
    provider = mylayer.dataProvider()
    if provider.encoding() != 'UTF-8':
        mylayer.dataProvider().setEncoding('UTF-8')
    # set name
    mylayer.setName(ln)
    QgsProject.instance().addMapLayer(mylayer)
    return mylayer


def my_processing_run_vector_clip(operation, ln_input, ln_overlay, dict_params, layer_name):
    """
    Run vector clip operation using specified parameters.

    :param operation: str: Processing algorithm to run.
    :param ln_input: QgsVectorLayer: Input vector layer.
    :param ln_overlay: QgsVectorLayer: Overlay vector layer.
    :param dict_params: dict: Dictionary of algorithm parameters.
    :param layer_name: str: Name of the resulting layer.
    :return: QgsVectorLayer: Resulting clipped layer.
    """
    dict_params['INPUT'] = ln_input
    dict_params['OVERLAY'] = ln_overlay
    dict_params['OUTPUT'] = QgsProcessing.TEMPORARY_OUTPUT
    mylayer = processing.run(operation, dict_params)['OUTPUT']
    if isinstance(mylayer, QgsVectorLayer):
        mylayer.setName(layer_name)
        QgsProject().instance().addMapLayer(mylayer)
        return mylayer


def toggle_layer_visibility(project, layer_name, visibility):
    """
    Toggle layer visibility in the project.

    :param project: QgsProject: Project instance.
    :param layer_name: str: Name of the layer to toggle visibility.
    :param visibility: bool: Visibility state (True for visible, False for invisible).
    """
    my_layers = project.mapLayersByName(layer_name)
    if my_layers:
        # my_layer is the first in the returned list
        my_layer = my_layers[0]
        # get the layer id
        my_layer_id = my_layer.id()
        # access layerTree
        root = project.layerTreeRoot()  # QgsLayerTree
        # identify tree layer: QgsLayerTreeLayer
        my_tree_layer = root.findLayer(my_layer_id)  # QgsLayerTreeLayer

        # make it not visible or visible based on the 'visibility' parameter
        my_tree_layer.setItemVisibilityChecked(visibility)


def my_join_attributes_by_location(layer1, layer2, join_fields, output_layer_name, predicate=[4, 5], method=2, discard_nonmatching=False, prefix='', output='TEMPORARY_OUTPUT'):
    """
    Join attributes by location using native:joinattributesbylocation algorithm.

    :param layer1: QgsVectorLayer: First input vector layer.
    :param layer2: QgsVectorLayer: Second input vector layer.
    :param join_fields: list: Fields to join.
    :param output_layer_name: str: Name of the output layer.
    :param predicate: list: Predicate for the join. Default is [4, 5].
    :param method: int: Join method. Default is 2.
    :param discard_nonmatching: bool: Whether to discard non-matching features. Default is False.
    :param prefix: str: Prefix for the output fields. Default is an empty string.
    :param output: str: Output type. Default is 'TEMPORARY_OUTPUT'.
    :return: QgsVectorLayer: Resulting joined layer.
    """
    dict_params = {
        'INPUT': layer1,
        'PREDICATE': predicate,
        'JOIN': layer2,
        'JOIN_FIELDS': join_fields,
        'METHOD': method,
        'DISCARD_NONMATCHING': discard_nonmatching,
        'PREFIX': prefix,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT 
    }

    joined_layer = processing.run('native:joinattributesbylocation', dict_params)['OUTPUT']

    if isinstance(joined_layer, QgsVectorLayer):
        joined_layer.setName(output_layer_name)
        QgsProject().instance().addMapLayer(joined_layer)
        return joined_layer


def add_area_column(layer, column_name=None):
    """
    Adds a new column to the attribute table with the area of each polygon.

    :param layer: QgsVectorLayer: Input vector layer.
    :param column_name: str: Name of the new column. Default is 'Buildings_Area'.
    :return: QgsVectorLayer: Input layer with the new column.
    """
    # Check if the layer is valid
    if not layer or not layer.isValid():
        print("Invalid layer.")
        return None

    # Check if the 'Add Attributes' capability is available
    if "Add Attributes" in layer.dataProvider().capabilitiesString():
        # Add a new attribute named 'Buildings_Area' to the layer
        area_field = QgsField(column_name, QVariant.Double, len=10)
        with edit(layer):
            layer.addAttribute(area_field)
            layer.updateFields()

        # Update the attribute values with the area of each polygon
        with edit(layer):
            for feature in layer.getFeatures():
                area = feature.geometry().area()
                feature.setAttribute(column_name, area)
                layer.updateFeature(feature)


def my_aggregate_function(input_layer, group_by, aggregates, output_layer_name):
    """
    Aggregate function using native:aggregate algorithm.

    :param input_layer: QgsVectorLayer: Input vector layer.
    :param group_by: str: Grouping field.
    :param aggregates: list: List of dictionaries defining aggregates.
    :param output_layer_name: str: Name of the output layer. Default is 'aggregate_result'.
    :return: QgsVectorLayer: Resulting aggregate layer.
    """
    dict_params = {
        'INPUT': input_layer,
        'GROUP_BY': group_by,
        'AGGREGATES': aggregates,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }

    result_layer = processing.run("native:aggregate", dict_params)['OUTPUT']

    if isinstance(result_layer, QgsVectorLayer):
        result_layer.setName(output_layer_name)
        QgsProject().instance().addMapLayer(result_layer)
        return result_layer


def my_join_attributes_by_field_value(input_layer1, input_layer2, field1, field2, fields_to_copy, method=1, discard_nonmatching=False, prefix='', output_layer_name=None):
    """
    Join attributes table function using native:joinattributestable algorithm.

    :param input_layer1: QgsVectorLayer: First input

 vector layer.
    :param input_layer2: QgsVectorLayer: Second input vector layer.
    :param field1: str: Field from the first input layer for the join.
    :param field2: str: Field from the second input layer for the join.
    :param fields_to_copy: list: Fields to copy from the second layer.
    :param method: int: Join method (1 for inner join, 0 for left join). Default is 1.
    :param discard_nonmatching: bool: Whether to discard non-matching features. Default is False.
    :param prefix: str: Prefix for the output fields. Default is an empty string.
    :param output_layer_name: str: Name of the output layer. If None, a default name will be used.
    :return: QgsVectorLayer: Resulting joined layer.
    """
    if output_layer_name is None:
        output_layer_name = 'join_result'  # Default output layer name if not provided

    dict_params = {
        'INPUT': input_layer1,
        'FIELD': field1,
        'INPUT_2': input_layer2,
        'FIELD_2': field2,
        'FIELDS_TO_COPY': fields_to_copy,
        'METHOD': method,
        'DISCARD_NONMATCHING': discard_nonmatching,
        'PREFIX': prefix,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }

    joined_layer = processing.run("native:joinattributestable", dict_params)['OUTPUT']

    if isinstance(joined_layer, QgsVectorLayer):
        joined_layer.setName(output_layer_name)
        QgsProject().instance().addMapLayer(joined_layer)
        return joined_layer


def update_area_attribute(layer):
    """
    Update the 'Buildings_Area' attribute in the provided layer.

    :param layer: QgsVectorLayer: Input vector layer.
    """
    # Ensure the layer is valid
    if not layer or not layer.isValid():
        print("Invalid layer.")
        return

    # Get the field index for the 'Buildings_Area' attribute
    area_field_index = layer.fields().indexFromName('Buildings_Area')

    # Create an expression to update the 'Area' attribute
    expression = QgsExpression('if("Buildings_Area" is NULL, 0, "Buildings_Area")')

    # Set the expression context for the layer
    QgsExpressionContextUtils.setLayerVariable(layer, 'expression', expression)

    # Update the 'Buildings_Area' attribute for each feature in the layer
    with edit(layer):
        for feature in layer.getFeatures():
            expression_context = QgsExpressionContext()
            expression_context.appendScope(QgsExpressionContextUtils.globalScope())
            expression_context.appendScope(QgsExpressionContextUtils.layerScope(layer))
            expression_context.setFeature(feature)

            area_value = expression.evaluate(expression_context)
            feature.setAttribute(area_field_index, area_value)
            layer.updateFeature(feature)


def calculate_building_land_ratio(layer, building_area_field, land_area_field, ratio_field_name):
    """
    Calculate the ratio of building area to land area and add a new field to the layer.

    :param layer: QgsVectorLayer: Input vector layer.
    :param building_area_field: str: Name of the field representing building area.
    :param land_area_field: str: Name of the field representing land area.
    :param ratio_field_name: str: Name of the new ratio field to be added.
    :return: QgsVectorLayer: Input layer with the new ratio field.
    """
    # Check if the layer is valid
    if not layer or not layer.isValid():
        print("Invalid layer.")
        return None

    # Check if the 'Add Attributes' capability is available
    if "Add Attributes" in layer.dataProvider().capabilitiesString():
        # Add a new attribute for the ratio to the layer
        ratio_field = QgsField(ratio_field_name, QVariant.Double, len=3)
        with edit(layer):
            layer.addAttribute(ratio_field)
            layer.updateFields()

        # Calculate the ratio using the provided expression
    calculate_ratio_expression = f'if("{land_area_field}" = 0, 0, "{building_area_field}" / "{land_area_field}")'
    with edit(layer):
        expression = QgsExpression(calculate_ratio_expression)
        expression_context = QgsExpressionContext()
        expression_context.appendScope(QgsExpressionContextUtils.globalScope())
        expression_context.appendScope(QgsExpressionContextUtils.layerScope(layer))

        for feature in layer.getFeatures():
            expression_context.setFeature(feature)
            ratio_value = expression.evaluate(expression_context)
            
            # Set the precision of the ratio to 1 decimal places
            ratio_value = round(ratio_value, 1)

            feature.setAttribute(ratio_field_name, ratio_value)
            layer.updateFeature(feature)

    return layer


def my_zoom_to_layer(layer_name):
    """
    Zoom to the specified layer in the project.

    :param layer_name: str: Name of the layer to zoom to.
    """
    # Access layer in project if it exists
    mylayers = QgsProject().instance().mapLayersByName(layer_name)
    # mylayer is the first in the returned list
    if mylayers:
        mylayer = mylayers[0]
        # determine CRS
        my_crs = mylayer.crs()
        QgsProject.instance().setCrs(my_crs)
        # Determine extent
        extent = mylayer.extent()
        iface.mapCanvas().setExtent(extent) 
        iface.mapCanvas().refresh()


def set_graduated_symbology(layer, field_name, num_classes=5, ramp_name='Spectral'):
    """
    Set graduated symbology for the given layer based on the specified field.

    :param layer: QgsVectorLayer: Input vector layer.
    :param field_name: str: Name of the field for symbology.
    :param num_classes: int: Number of classes for the graduated symbology. Default is 5.
    :param ramp_name: str: Name of the color ramp to be used. Default is 'Spectral'.
    """
    # Define the classification method
    classification_method = QgsClassificationJenks()

    # Change format settings as necessary
    format = QgsRendererRangeLabelFormat()
    format.setFormat("%1 - %2")
    format.setPrecision(2)
    format.setTrimTrailingZeroes(True)

    # Get the default style and color ramp
    default_style = QgsStyle().defaultStyle()
    color_ramp = default_style.colorRamp(ramp_name)

    # Create graduated symbol renderer
    my_renderer = QgsGraduatedSymbolRenderer()
    my_renderer.setClassAttribute(field_name)
    my_renderer.setClassificationMethod(classification_method)
    my_renderer.setLabelFormat(format)
    my_renderer.updateClasses(layer, num_classes)
    my_renderer.updateColorRamp(color_ramp)

    # Set renderer to the layer
    layer.setRenderer(my_renderer)

    # Refresh the layer
    layer.triggerRepaint()


def my_export_layer_as_file(mylayer, fn, save_style=True):
    """ 
    Save QgsVectorLayer as file and optionally save the layer style as a QML file.
    
    :param mylayer: QgsVectorLayer: Input vector layer.
    :param fn: str or Path: File name to save the layer.
    :param save_style: bool: Whether to save the layer style as a QML file. Default is True.
    """
    if isinstance(mylayer, QgsVectorLayer):
        # Save the layer as a file
        processing.run("native:savefeatures", {'INPUT': mylayer, 'OUTPUT': str(fn)})

        # Save layer style as QML file if save_style is True
        if save_style:
            fn_qml = Path(str(fn)).with_suffix(".qml")
            mylayer.saveNamedStyle(str(fn_qml))