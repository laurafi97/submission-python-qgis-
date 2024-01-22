# Project Report

## Project Title: Calculation of Urban Density with QGIS and Python
**Student:** Laura Fischer  
**Course:** Introduction to Python Course + QGIS with Python, ISA, ULIsboa, 2023/24  
**Instructor:** Manuel Campagnolo

### Introduction:
The project focuses on conducting an urban planning analysis using QGIS and Python scripting. The primary objective is to calculate the building-land ratio, a crucial metric in urban planning, for a designated area in the City of Ebelsbach, Germany. The project leverages the QGIS software along with Python scripts (`project.py` and `my_functions.py`) to automate various geospatial processes.

### Project Components:
- **Data Sources:**
  - Digital Field Map Data: The dataset is obtained from the Bavarian Geodata Portal ([https://geodaten.bayern.de/opengeodata](https://geodaten.bayern.de/opengeodata)).
    - `land_parcel.shp`: Parcel boundaries in the city.
    - `buildings.shp`: Building footprints.
    - `area_of_interest.shp`: Region of interest within the city.
- **Scripts:**
  - `my_functions.py`: A Python script containing reusable functions for handling vector layers, attribute joins, and various geoprocessing tasks.
  - `project.py`: The main script orchestrating the entire analysis, utilizing functions from `my_functions.py`.
  - `test_project.py`: A script containing unit tests for the `project.py` script.

### Analysis Workflow:
- **Project Creation:**
  - The project begins by creating a new QGIS project (`my_create_project` function) and setting the title.
- **Data Loading:**
  - The script loads relevant shapefiles (`land_parcel`, `buildings`, `area_of_interest`) using the `my_load_shapefile` function.
- **Preprocessing:**
  - Layers are cropped to the area of interest (`my_crop_vector_layer`), and visibility is toggled accordingly.
- **Attribute Joins:**
  - Building footprints are joined with land parcel data (`my_join_attributes_by_location`), enhancing the dataset.
- **Aggregation:**
  - Building areas are aggregated by parcel ID (`my_aggregate_function`), providing a summary for each land parcel.
- **Further Analysis:**
  - Additional columns are added for building and land parcel areas (`add_area_column`).
  - The building-land ratio is calculated (`calculate_building_land_ratio`).
- **Visualization:**
  - The resulting layer is styled using graduated symbology (`set_graduated_symbology`).
- **Export:**
  - Temporary layers are hidden, and the final result is saved, including its style (`my_export_layer_as_file`).

### Language Considerations:
- The attribute table in the German city dataset uses German words, reflecting the local context. This language specificity is accounted for in the script.

### Significance of Building-Land Ratio:
The building-land ratio is a critical metric in urban planning, representing the proportion of built-up area (buildings) to the total land area within a defined boundary. A higher ratio indicates more intensive land use and can influence zoning decisions, density planning, and infrastructure requirements. Understanding this ratio helps planners balance urban development, green spaces, and infrastructure needs for sustainable city growth.

### Potential Improvements:
- **Code Modularity:**
  - The script could be further modularized to enhance code readability and maintainability.
- **Error Handling:**
  - Implementing more robust error handling mechanisms can improve the script's resilience to unexpected inputs or errors during execution.
- **User Interface:**
  - Introducing a user interface for parameter input and result visualization could enhance the script's usability.
- **Reduce Temporary Layers:**
  - The script could be improved by minimizing the creation of unnecessary temporary layers. Consolidating steps and reusing existing layers where possible would enhance efficiency and reduce the complexity of the project.


### Conclusion:
The project successfully demonstrates an automated workflow for urban planning analysis using QGIS and Python. By calculating the building-land ratio, it provides valuable insights for sustainable urban development in the City of Ebelsbach. The script serves as a foundation for further enhancements and customization in the field of geospatial analysis.
