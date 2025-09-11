# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Custom names for links, nodes, subareas
#
# This is a sample notebook demonstrating how to use the `ShapefileToSwiftConverter` class from the `geosdhydro` package to convert a shapefile with custom names for links, nodes, and subareas into a JSON format compatible with the `swift2` hydrological modeling framework.

# %%
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString

from geosdhydro import ShapefileToSwiftConverter

# %% [markdown]
#
# ## Create synthetic test data
#
# Side note that even if string columns for IDS are preferable, the converter will convert them to string if they are not, as will be the case for ToNodeID below.
#
# We use the default column names for the required fields:

# %%
data = {
    "LinkID": ["1", "2", "3", "4", "5"],  # As strings
    "FromNodeID": ["2", "3", "4", "5", "6"],  # As strings
    "ToNodeID": [1, 2, 2, 2, 5],
    "SPathLen": [1000.0, 1500.0, 2000.0, 800.0, 1200.0],
    "DArea2": [3000000.0, 4000000.0, 2500000.0, -1.0, 3500000.0],  # Link 4 has negative area
    "geometry": [
        LineString([(2.1, 2.2), (1.1, 1.2)]),  # Link 1: node 2 -> node 1
        LineString([(3.1, 3.2), (2.1, 2.2)]),  # Link 2: node 3 -> node 2
        LineString([(4.1, 4.2), (2.1, 2.2)]),  # Link 3: node 4 -> node 2
        LineString([(5.1, 5.2), (2.1, 2.2)]),  # Link 4: node 5 -> node 2
        LineString([(6.1, 6.2), (5.1, 5.2)]),  # Link 5: node 6 -> node 5
    ],
}

# %% [markdown]
#
# That was the minimally required columns. We can add a few more to illustrate custom names:

# %%
custom_linkname_fieldname = "LinkName"
data[custom_linkname_fieldname] = [f"CustomLinkName_{i}" for i in range(5)]

# Custom names for subareas
custom_subarea_name_fieldname = "SubAreaName"
data[custom_subarea_name_fieldname] = [f"CustomSubAreaName_{i}" for i in range(5)]
gdf = gpd.GeoDataFrame(data)

gdf

# %%
# Custom node names
custom_nodenames = {str(i): f"CustomNodeName_{i}" for i in range(1, 7)}

# %%
converter = ShapefileToSwiftConverter(
    gdf,
    linkname_field=custom_linkname_fieldname,
    subarea_name_field=custom_subarea_name_fieldname,
    node_names=custom_nodenames,
)
result = converter.convert()


# %%
result.keys()

# %%
result["Nodes"][0]

# %%
result["Links"][0]

# %% [markdown]
# We check that one of the subarea is not present (area negative), even if a mapped name was specified:

# %%
[s['Name'] for s in  result["SubAreas"]]

# %%
