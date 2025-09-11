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
#     display_name: geosdhydro
#     language: python
#     name: geosdhydro
# ---

# %% [markdown]
# # Getting started
#
# This is a sample notebook demonstrating how to use the `geosdhydro` package to convert a geopandas dataframe to a swift json file. A browsable form of this notebook should be at the [package documentation](https://csiro-hydroinformatics.github.io/geosdhydro/).

# %%
import geopandas as gpd

# %%
from pathlib import Path

# %%
from geosdhydro import ShapefileToSwiftConverter

# %%
fpath = Path.home() / "data/wnsw/Abercrombie/Abercrombie_links4swift.shp"

# %%
fpath.exists()

# %%
link_specs = gpd.read_file(fpath)

print(link_specs.head())

# %%
{x: link_specs[x].dtype for x in link_specs.columns}

# %% [markdown]
# Note that some of the input columns, LinkID, ToNodeID, FromNodeID, are integers, because of habits. It is preferable to have them as strings, but the converter will transparently convert them to string. Another thing is that there is a duplicated ID in the links:

# %%
gdf = link_specs
# Check for duplicates in the 'LinkID' column
duplicates = gdf['LinkID'][gdf['LinkID'].duplicated(keep=False)]

# Display the duplicated IDs
print(duplicates)

# %% [markdown]
# Let's see what happens:

# %%
# THere are default values for the expected columns names and whether to retrieve lat/lon coordinates:
# converter = ShapefileToSwiftConverter(link_specs)

# but let us be explicit in this example tutorial
converter = ShapefileToSwiftConverter(
    gdf = link_specs,
    include_coordinates = False,
    linkid_field = 'LinkID',
    fromnodeid_field = 'FromNodeID',
    tonodeid_field = 'ToNodeID',
    spathlen_field = 'SPathLen',
    darea2_field = 'DArea2',
    geometry_field = 'geometry',
)

# %%
link_specs.iloc[[3, 17]]

# %% [markdown]
# Not quite sure what was intended with the above. One of the entry has 1 meter-length links `SPathLen`, but a catchment area, the other is the other way around. I may have been a legacy workaround, or a data bug. Be it as it may, this is a useful way to illustrate the need to look at data, and the build-in checks in the package/features.
#
# For the sake of the example, let us just drop these.

# %%
link_specs = link_specs.drop(index=[3,17])

# %% [markdown]
# and now we expect the converter to do the job:

# %%

converter = ShapefileToSwiftConverter(
    gdf = link_specs,
    include_coordinates = False,
    linkid_field = 'LinkID',
    fromnodeid_field = 'FromNodeID',
    tonodeid_field = 'ToNodeID',
    spathlen_field = 'SPathLen',
    darea2_field = 'DArea2',
    geometry_field = 'geometry',
)

# %%
result = converter.convert()

# %% [markdown]
# `result` is a python dictionary

# %% [markdown]
# As expected given that some areas were negative in the input file (i.e. links without a contributing subarea), we have less subareas than links

# %%
f"there are {len(result["Links"])} links, {len(result["Nodes"])} nodes, {len(result["SubAreas"])} subareas"

# %% [markdown]
# The object `converter` has a `save_to_file` method, or you can use the `json` module to save the above `result`:

# %%
import json

# %%
fp = Path.home() / "tmp" / "abercrombie_swift.json"
# with open(fp, "w") as f:
#     json.dump(result, f, indent=2)


# %% [markdown]
# ## Checking the json output loads as a catchment structure

# %%
# This is be done if you have `swift2` in your python env using:

# from swift2.model_definitions import model_from_json_file
# sim = model_from_json_file(fp)

# %%
