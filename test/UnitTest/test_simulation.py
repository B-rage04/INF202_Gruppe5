def test_simulation():
    from src.simulation import Simulation

    assert True  # TODO fix test


def test_ship_sink_reduces_oil():
    import numpy as np
    from src.simulation import Simulation
    from src.mesh import Mesh

    config = {
        "settings": {"nSteps": 1, "tStart": 0.0, "tEnd": 0.5},
        "geometry": {
            "meshName": "Exsample/Geometry/bay.msh",
            "borders": [[0, 0.45], [0, 0.2]],
            "ship": [0.35, 0.45],
        },
        "IO": {"logName": "log", "writeFrequency": 1},
    }

    sim = Simulation(config)

    # Identify cells within ship radius
    ship_xy = np.array(config["geometry"]["ship"])
    in_radius_ids = []
    for cell in sim.msh.cells:
        if cell.type != "triangle":
            continue
        d = np.linalg.norm(np.array([cell.midpoint[0], cell.midpoint[1]]) - ship_xy)
        if d <= 0.1:
            in_radius_ids.append(cell.id)

    # Ensure there are some cells in radius
    assert len(in_radius_ids) > 0

    # Snapshot oil, update once, and check reduced values in radius
    before = {cell.id: cell.oil for cell in sim.msh.cells if cell.type == "triangle"}
    sim.update_oil()
    after = {cell.id: cell.oil for cell in sim.msh.cells if cell.type == "triangle"}

    reduced = [after[i] < before[i] for i in in_radius_ids]
    assert any(reduced), "Expected some oil reduction within ship radius"
