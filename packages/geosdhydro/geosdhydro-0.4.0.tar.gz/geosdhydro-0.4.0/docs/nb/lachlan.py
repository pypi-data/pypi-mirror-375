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
# # Catchment structure for the Lachlan valley
#
# Network definition for a shapefile with information on the Lachlan valley, as of ~8th August 2025. This is use case for customisable column names as well as being more liberal with the types of columns in the `geopandas` data frame resulting from reading the shapefile.
#

# %%
from pathlib import Path

import geopandas as gpd

from geosdhydro import ShapefileToSwiftConverter

# %%
fpath = Path.home() / "data"/"wnsw"/"Lachlan"/"Lachlan_links4swift.shp"

# %%
fpath.exists()

# %%
link_specs = gpd.read_file(fpath)

link_specs.head()

# %%
{x: link_specs[x].dtype for x in link_specs.columns}

# %% [markdown]
# Note that some of the input columns, LinkID, ToNodeID, FromNodeID, are integers, because of habits. It is preferable to have them as strings, but the converter will transparently convert them to string. Another thing is that there is a duplicated ID in the links:

# %%
gdf = link_specs
# Check for duplicates in the 'LinkID' column
duplicates = gdf["LinkID"][gdf["LinkID"].duplicated(keep=False)]

# Display the duplicated IDs
print(duplicates)

# %% [markdown]
# Let's see what happens:

# %%
link_specs = link_specs.drop(index=[3,17])

# %% [markdown]
# and now we expect the converter to do the job:

# %%

converter = ShapefileToSwiftConverter(
    gdf = link_specs,
    include_coordinates = True,
    linkid_field = "LinkID",
    fromnodeid_field = "FromNodeID",
    tonodeid_field = "ToNodeID",
    spathlen_field = "SPathLen",
    darea2_field = "DArea",
    geometry_field = "geometry",
)

# %%
result = converter.convert()

# %% [markdown]
# `result` is a python dictionary

# %% [markdown]
# As expected given that some areas were negative in the input file (i.e. links without a contributing subarea), we have less subareas than links

# %%
f"there are {len(result['Links'])} links, {len(result['Nodes'])} nodes, {len(result['SubAreas'])} subareas"

# %% [markdown]
# The object `converter` has a `save_to_file` method, or you can use the `json` module to save the above `result`:

# %%
import json

# %%
fp = Path.home() / "tmp" / "lachlan_swift.json"
with open(fp, "w") as f:
    json.dump(result, f, indent=2)


# %% [markdown]
# ## Checking the json output loads as a catchment structure

# %% [markdown]
# This can be done if you have `swift2` in your python env using the following.
#
# See [load_lachlan.ipynb](./load_lachlan.ipynb).
#

# %%

# from swift2.model_definitions import model_from_json_file
# sim = model_from_json_file(fp)
