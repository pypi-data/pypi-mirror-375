from functools import partial

import geopandas as gpd
import pytest
from gerrychain import (
    GeographicPartition,
    Graph,
    MarkovChain,
    Partition,
    accept,
    constraints,
    updaters,
)
from gerrychain.proposals import recom

from gerrytools.geometry import (
    dataframe,
    dispersion_updater_closure,
    dissolve,
    dualgraph,
    invert,
    unitmap,
)

from .utils import remotegraphresource, remoteresource


@pytest.mark.xfail(
    reason="Documentation and call signature do not match; clarification needed."
)
def test_dispersion_calc():
    gdf = gpd.read_file("./test-resources/test-vtds/")
    gdf["CONGRESS"] = gdf["CONGRESS"].astype(int)
    graph = Graph.from_json("./test-resources/IN-vtds.json")

    my_updaters = {
        "population": updaters.Tally("TOTPOP", alias="population"),
        "dispersion": dispersion_updater_closure(gdf, "CONGRESS", "TOTPOP"),
    }

    initial_partition = GeographicPartition(
        graph, assignment="CONGRESS", updaters=my_updaters
    )

    ideal_population = sum(initial_partition["population"].values()) / len(
        initial_partition
    )

    proposal = partial(
        recom,
        pop_col="TOTPOP",
        pop_target=ideal_population,
        epsilon=0.10,
        node_repeats=2,
    )

    pop_constraint = constraints.within_percent_of_ideal_population(
        initial_partition, 0.02
    )

    chain = MarkovChain(
        proposal=proposal,
        constraints=[pop_constraint],
        accept=accept.always_accept,
        initial_state=initial_partition,
        total_steps=100,
    )

    total_dispersion_over_run = 0
    for count, partition in enumerate(chain):
        if count == 0:
            assert partition["dispersion"] == 0

        total_dispersion_over_run += partition["dispersion"]

    assert total_dispersion_over_run


def test_dissolve():
    # Read in geometric data.
    districts = gpd.read_file(remoteresource("test-vtds.geojson"))

    # Assign half the units to district 0, the other half to district 1; create
    # a "name" column and do the same.
    districts = districts[["geometry", "G20PREDBID"]]

    keep = ["G20PREDBID"]
    districts["DISTRICT"] = [0] * (len(districts) // 2) + [1] * (
        len(districts) - len(districts) // 2
    )
    dissolved = dissolve(districts, by="DISTRICT", keep=keep)
    dissolved["NAME"] = ["A", "B"]

    # Assert that we have two distinct geometries.
    assert len(dissolved) == 2

    # Assert that the sum of the kept column is the same as the sum of the original.
    assert dissolved["G20PREDBID"].sum() == districts["G20PREDBID"].sum()


def test_dualgraph():
    # Read in geometric data and get centroids.
    districts = gpd.read_file(remoteresource("test-districts.geojson"))
    districts["x"] = districts["geometry"].apply(lambda c: c.centroid.coords[0][0])
    districts["y"] = districts["geometry"].apply(lambda c: c.centroid.coords[0][1])
    districts = districts[["DISTRICT", "geometry", "G20PREDBID", "x", "y", "NAME"]]

    # Create default dual graph.
    default = dualgraph(districts, index="DISTRICT")

    # Create an adjusted dual graph.
    adjusted = dualgraph(
        districts, index="DISTRICT", edges_to_add=[(1, 1)], edges_to_cut=[(0, 1)]
    )

    # Create another adjusted dual graph, this time with more things mucked up.
    nameadjusted = dualgraph(districts, index="NAME", colmap={"G20PREDBID": "BIDEN"})

    # Check that there are different edges in `default` and `adjusted`, and that
    # edges were added and cut.
    assert set(default.edges()) != set(adjusted.edges())
    assert (1, 1) in set(adjusted.edges())
    assert (0, 1) not in set(adjusted.edges())

    # Assert that reindexing and renaming happened.
    assert set(default.nodes()) != set(nameadjusted.nodes())
    for _, data in nameadjusted.nodes(data=True):
        assert data.get("BIDEN", False)


def test_unitmap():
    # Read in some test dataframes.
    vtds = gpd.read_file(remoteresource("test-vtds.geojson"))
    counties = gpd.read_file(remoteresource("test-counties.geojson"))

    # Make an assignment!
    umap = unitmap((vtds, "GEOID20"), (counties, "COUNTYFP20"))

    # Assert that the type is a dict and that it has the right number of keys.
    assert type(umap) is dict
    assert len(umap) == len(vtds)

    # Invert it!
    inverse = invert(umap)

    # Assert that we have a dict and that it has as many keys as counties.
    assert type(inverse) is dict
    assert len(inverse) == len(counties)


def test_dataframe():
    G = remotegraphresource("test-graph.json")

    P = Partition(
        graph=G, assignment={v: d["COUNTYFP20"] for v, d in G.nodes(data=True)}
    )
    df = dataframe(P, assignment="COUNTYFP20")
    df = df.rename({"id": "GEOID20"}, axis=1)

    # Assert the right number of "districts."
    len(P.parts) == 92


if __name__ == "__main__":
    test_dataframe()
    # test_dualgraph()
    # test_dissolve()
    # test_unitmap()
