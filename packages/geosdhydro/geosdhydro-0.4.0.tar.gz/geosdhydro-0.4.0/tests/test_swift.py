import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString

from geosdhydro import ShapefileToSwiftConverter


def test_one_link_two_nodes_one_subarea() -> None:
    """Test conversion with one link, two nodes, and one subarea."""
    # Create test data
    data = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": [1000.0],
        "DArea2": [5000000.0],  # 5 km² in m²
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf = gpd.GeoDataFrame(data)

    converter = ShapefileToSwiftConverter(gdf)
    result = converter.convert()

    # Test structure
    assert len(result["Links"]) == 1
    assert len(result["Nodes"]) == 2
    assert len(result["SubAreas"]) == 1

    # Test link details
    link = result["Links"][0]
    assert link["ID"] == "1"
    assert link["UpstreamNodeID"] == "1"
    assert link["DownstreamNodeID"] == "2"
    assert link["Length"] == 1000.0
    assert link["Name"] == "1"

    # Test nodes
    node_ids = {node["ID"] for node in result["Nodes"]}
    assert node_ids == {"1", "2"}

    # Test subarea
    subarea = result["SubAreas"][0]
    assert subarea["ID"] == "1"
    assert subarea["LinkID"] == "1"
    assert subarea["AreaKm2"] == 5.0
    assert subarea["Name"] == "Subarea_1"


def test_one_link_two_nodes_no_subarea() -> None:
    """Test conversion with one link, two nodes, and no subarea."""
    # Create test data with negative DArea2 (no subarea)
    data = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": [1500.0],
        "DArea2": [-1.0],  # Negative value means no subarea
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf = gpd.GeoDataFrame(data)

    converter = ShapefileToSwiftConverter(gdf)
    result = converter.convert()

    # Test structure
    assert len(result["Links"]) == 1
    assert len(result["Nodes"]) == 2
    assert len(result["SubAreas"]) == 0  # No subareas expected

    # Test link details
    link = result["Links"][0]
    assert link["ID"] == "1"
    assert link["UpstreamNodeID"] == "1"
    assert link["DownstreamNodeID"] == "2"
    assert link["Length"] == 1500.0

    # Test nodes exist
    node_ids = {node["ID"] for node in result["Nodes"]}
    assert node_ids == {"1", "2"}


def test_coordinates_included() -> None:
    """Test conversion with coordinates included in nodes."""
    # Create test data
    data = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": [1000.0],
        "DArea2": [5000000.0],
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf = gpd.GeoDataFrame(data)

    converter = ShapefileToSwiftConverter(gdf, include_coordinates=True)
    result = converter.convert()

    # Find nodes by ID
    nodes_by_id = {node["ID"]: node for node in result["Nodes"]}

    # Test node 1 coordinates (start point)
    node1 = nodes_by_id["1"]
    assert "Longitude" in node1
    assert "Latitude" in node1
    assert node1["Longitude"] == 1.1
    assert node1["Latitude"] == 1.2

    # Test node 2 coordinates (end point)
    node2 = nodes_by_id["2"]
    assert node2["Longitude"] == 2.1
    assert node2["Latitude"] == 2.2


def test_complex_catchment_structure() -> None:
    """Test conversion with complex catchment: 5 links, 6 nodes, 4 subareas."""
    # Create test data
    data = {
        "LinkID": [1, 2, 3, 4, 5],
        "FromNodeID": [2, 3, 4, 5, 6],
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
    gdf = gpd.GeoDataFrame(data)

    converter = ShapefileToSwiftConverter(gdf)
    result = converter.convert()

    # Test structure
    assert len(result["Links"]) == 5
    assert len(result["Nodes"]) == 6
    assert len(result["SubAreas"]) == 4  # Links 1,2,3,5 have subareas

    # Test nodes exist
    node_ids = {node["ID"] for node in result["Nodes"]}
    assert node_ids == {"1", "2", "3", "4", "5", "6"}

    # Test subareas (should be for links 1,2,3,5 only)
    subarea_link_ids = {subarea["LinkID"] for subarea in result["SubAreas"]}
    assert subarea_link_ids == {"1", "2", "3", "5"}

    # Verify link 4 has no subarea
    assert "4" not in subarea_link_ids



def test_invalid_spathlen_type() -> None:
    """Test that an exception is raised when spathlen is not a numeric type."""
    # Create test data with ToNodeID as float
    data = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": ["2"],
        "SPathLen": ["1000.0"], # valid, but wrong type, cannot be converted to float
        "DArea2": [5000000.0],
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf = gpd.GeoDataFrame(data)

    # Expect a TypeError due to wrong column type
    with pytest.raises(TypeError):
        ShapefileToSwiftConverter(gdf)


def test_invalid_spathlenname_type() -> None:
    """Test that an exception is raised when SPathLen column is not default expected name."""
    data = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": ["2"],
        "SPathLen_WrongName": [1000.0],
        "DArea2": [5000000.0],
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf = gpd.GeoDataFrame(data)

    # Expect a TypeError due to wrong column type
    with pytest.raises(ValueError):  # noqa: PT011
        ShapefileToSwiftConverter(gdf)

def test_duplicate_link_ids() -> None:
    """Test that an exception is raised when LinkID column contains duplicate values."""
    # Create test data with duplicate LinkID values
    data = {
        "LinkID": [1, 2, 1, 3, 2, 2],  # LinkID 1 and 2 are duplicated
        "FromNodeID": [1, 2, 1, 3, 2, 2],
        "ToNodeID": [2, 3, 2, 4, 3, 3],
        "SPathLen": [1000.0, 1500.0, 1000.0, 2000.0, 1500.0, 1500.0],
        "DArea2": [5000000.0, 4000000.0, 5000000.0, 3000000.0, 4000000.0, 4000000.0],
        "geometry": [
            LineString([(1.1, 1.2), (2.1, 2.2)]),
            LineString([(2.1, 2.2), (3.1, 3.2)]),
            LineString([(1.1, 1.2), (2.1, 2.2)]),
            LineString([(3.1, 3.2), (4.1, 4.2)]),
            LineString([(2.1, 2.2), (3.1, 3.2)]),
            LineString([(2.1, 2.2), (3.1, 3.2)]),
        ],
    }
    gdf = gpd.GeoDataFrame(data)

    # Expect a ValueError due to duplicate LinkID values
    with pytest.raises(ValueError) as excinfo:  # noqa: PT011
        ShapefileToSwiftConverter(gdf)

    # Check the error message
    assert "Column 'LinkID' contains duplicate values: ['2', '1'] at indices" in str(excinfo.value)

def test_valid_numeric_types() -> None:
    """Test that valid numeric types for SPathLen and DArea2 columns are accepted."""
    # Create test data with various numeric types
    for t in [float, np.float32, np.int32, np.uint16]:
        data = {
            "LinkID": [1],
            "FromNodeID": [1],
            "ToNodeID": [2],
            "SPathLen": [t(1000)],
            "DArea2": [t(64000)],  # Valid numeric type, small enough to fit in uint16
            "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
        }
        gdf = gpd.GeoDataFrame(data)

        # Should successfully create converter without errors
        converter = ShapefileToSwiftConverter(gdf)
        result = converter.convert()

        # Verify data was properly converted to float64
        links = result["Links"]
        assert len(links) == 1

        # Check that values match expected (all converted to float64)
        assert links[0]["Length"] == 1000.0

        # Check subareas (DArea2 converted to km²)
        subareas = result["SubAreas"]
        assert len(subareas) == 1
        assert subareas[0]["AreaKm2"] == 0.064


def test_invalid_numeric_types() -> None:
    """Test that invalid types for SPathLen and DArea2 columns raise appropriate errors."""
    # Test 1: Non-numeric string in SPathLen
    data1 = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": ["not-a-number"],  # String that can't be converted to float
        "DArea2": [5000000.0],
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf1 = gpd.GeoDataFrame(data1)
    with pytest.raises(TypeError):
        ShapefileToSwiftConverter(gdf1)
    # Test 2: Boolean in DArea2
    data2 = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": [1000.0],
        "DArea2": [True],  # Boolean value
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf2 = gpd.GeoDataFrame(data2)
    with pytest.raises(TypeError):
        ShapefileToSwiftConverter(gdf2)
    # Test 3: Object with mixed types
    data3 = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": [1000.0],
        "DArea2": [pd.Series([1, 2, 3])],  # A pandas Series object
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf3 = gpd.GeoDataFrame(data3)
    with pytest.raises(TypeError):
        ShapefileToSwiftConverter(gdf3)
    # Test 4: Date/time object
    data4 = {
        "LinkID": [1],
        "FromNodeID": [1],
        "ToNodeID": [2],
        "SPathLen": [np.datetime64("2023-01-01")],  # Datetime object
        "DArea2": [5000000.0],
        "geometry": [LineString([(1.1, 1.2), (2.1, 2.2)])],
    }
    gdf4 = gpd.GeoDataFrame(data4)

    with pytest.raises(TypeError):
        ShapefileToSwiftConverter(gdf4)

def test_element_names() -> None:
    """Test default/custom names for the elements."""
    # Create test data, first without custom names
    data = {
        "LinkID": [1, 2, 3, 4, 5],
        "FromNodeID": [2, 3, 4, 5, 6],
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
    gdf = gpd.GeoDataFrame(data)

    # Test default names
    converter = ShapefileToSwiftConverter(gdf)
    result = converter.convert()

    # Default names for links
    assert all(link["Name"] == str(link["ID"]) for link in result["Links"])

    # Default names for nodes
    assert all(node["Name"] == f"Node_{node['ID']}" for node in result["Nodes"])

    # Default names for subareas
    assert all(subarea["Name"] == f"Subarea_{subarea['ID']}" for subarea in result["SubAreas"])

    # Custom names for links
    custom_linkname_fieldname = "LinkName"
    data[custom_linkname_fieldname] = [f"CustomLinkName_{i}" for i in range(5)]

    # Custom names for subareas
    custom_subarea_name_fieldname = "SubAreaName"
    data[custom_subarea_name_fieldname] = [f"CustomSubAreaName_{i}" for i in range(5)]
    gdf = gpd.GeoDataFrame(data)

    # Custom node names
    some_dict = {str(i): f"CustomNodeName_{i}" for i in range(1, 7)}

    converter = ShapefileToSwiftConverter(
        gdf,
        linkname_field=custom_linkname_fieldname,
        subarea_name_field=custom_subarea_name_fieldname,
        node_names=some_dict,
    )
    result = converter.convert()

    # Assertions for custom link names
    assert all(link["Name"] == f"CustomLinkName_{int(link['ID'])-1}" for link in result["Links"])

    # Assertions for custom node names
    assert all(node["Name"] == f"CustomNodeName_{node['ID']}" for node in result["Nodes"])

    # Assertions for custom subarea names
    assert all(subarea["Name"] == f"CustomSubAreaName_{int(subarea['ID'])-1}" for subarea in result["SubAreas"])
