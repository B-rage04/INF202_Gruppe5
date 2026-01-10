from src.flow import Flow


def test_flow_methods():  # Test just to chek the CI
    f = Flow()
    u = f.u0(0.35, 0.45)
    vx, vy = f.v(1.0, 2.0)
    assert isinstance(u, float)
    assert isinstance(vx, float) and isinstance(vy, float)
