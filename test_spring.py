"""Tests for block-on-spring turboPy app"""
import numpy as np
from turbopy import PhysicsModule, Simulation
from spring import BlockOnSpring

# Need a "Simulation" object. Maybe need to mock it?
input_data = {
    "Tools": {"ForwardEuler": {}},
    "Grid": {"min": 1, "max": 2, "N": 3},
    "Clock": {"start_time": 0, "end_time": 1, "dt": 1},
    "PhysicsModules": {},
    "Diagnostics": {},
    }
sim = Simulation(input_data)
sim.prepare_simulation()


def test_sim_config():
    assert sim.find_tool_by_name("ForwardEuler") is not None


def test_BlockOnSpring_subclass():
    """Test main PhysicsModule class"""
    assert issubclass(BlockOnSpring, PhysicsModule)


def test_BlockOnSpring_instance():
    """Test instantiating a BlockOnSpring object"""
    min_config = {"pusher": "ForwardEuler"}
    b = BlockOnSpring(sim, min_config)
    assert isinstance(b, BlockOnSpring)


def test_BlockOnSpring_attributes():
    """Test setting attributes for a BlockOnSpring"""
    config = {
                "mass": 1,
                "spring_constant": 1,
                "pusher": "ForwardEuler",
                "x0": [[0, 1, 0]],
            }
    b = BlockOnSpring(sim, config)
    # These attributes get set in __init__()
    assert b.mass == 1
    assert b.spring_constant == 1
    np.testing.assert_allclose(b.position, [[0, 0, 0]])

    b.initialize()
    # These attributes get set in initialize()
    np.testing.assert_allclose(b.position, config["x0"])

