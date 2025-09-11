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
#     display_name: hydrofc
#     language: python
#     name: hydrofc
# ---

# %% [markdown]
# # Load the Lachlan model structure
#
# Checks that the json file(s) produced can be loaded by swift

# %%
import swift2 as s

# %%
from pathlib import Path

fn = Path.home() / "tmp" / "lachlan_swift.json"
assert fn.exists(), "File does not exist: {fn}"


# %%

lachlan = s.classes.Simulation.from_json_file(fn)

# %%
lachlan.describe()
