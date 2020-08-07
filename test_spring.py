"""Tests for block-on-spring turboPy app"""
import numpy as np
import pytest
from turbopy import Simulation, PhysicsModule
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


def bos_run():
    block_config = {
        "Grid": {"N": 2, "x_min": 0, "x_max": 1},
        "Clock": {"start_time": 0,
                  "end_time": 10,
                  "num_steps": 100},
        "PhysicsModules": {
            "BlockOnSpring": {
                "mass": 1,
                "spring_constant": 1,
                "pusher": "Leapfrog",
                "x0": [0, 1, 0],
            }
        },
        "Tools": {
            "Leapfrog": {},
            "ForwardEuler": {},
            "BackwardEuler": {}
        },
        "Diagnostics": {
            # default values come first
            "directory": "test_output/",
            "output_type": "csv",
            "clock": {"filename": "time.csv"},
            "BlockDiagnostic": [
                {'component': 'momentum', 'filename': 'block_p.csv'},
                {'component': 'position', 'filename': 'block_x.csv'}
            ]
        }
    }

    block_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "ForwardEuler"
    block_config["Diagnostics"]["directory"] = "test_data/test_output/output_euler/"
    sim = Simulation(block_config)
    sim.run()

    block_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "Leapfrog"
    block_config["Diagnostics"]["directory"] = "test_data/test_output/output_leapfrog/"
    sim = Simulation(block_config)
    sim.run()

    block_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "BackwardEuler"
    block_config["Diagnostics"]["directory"] = "test_data/test_output/output_backward_euler/"
    sim = Simulation(block_config)
    sim.run()


bos_run()


def test_bos_forwardeuler():
    """Tests block_on_spring app with ForwardEuler ComputeTool and compares to
    output files with a "good" output.
    """

    for filename in ['block_p', 'block_x', 'time']:
        ref_data = np.genfromtxt(f'test_data/reference_output/output_euler/{filename}.csv',
                                 delimiter=',')
        tmp_data = np.genfromtxt(f'test_data/test_output/output_euler/{filename}.csv',
                                 delimiter=',')
        assert np.allclose(ref_data, tmp_data, rtol=1e-05, atol=1e-08)


def test_bos_backwardeuler():
    """Tests block_on_spring app with BackwardEuler ComputeTool and compares to
    output files with a "good" output.
    """

    for filename in ['block_p', 'block_x', 'time']:
        ref_data = np.genfromtxt(f'test_data/reference_output/output_backward_euler/{filename}.csv',
                                 delimiter=',')
        tmp_data = np.genfromtxt(f'test_data/test_output/output_backward_euler/{filename}.csv',
                                 delimiter=',')
        assert np.allclose(ref_data, tmp_data, rtol=1e-05, atol=1e-08)


def test_bos_leapfrog():
    """Tests block_on_spring app with LeapFrog ComputeTool and compares to
    output files with a "good" output.
    """

    for filename in ['block_p', 'block_x', 'time']:
        ref_data = np.genfromtxt(f'test_data/reference_output/output_leapfrog/{filename}.csv',
                                 delimiter=',')
        tmp_data = np.genfromtxt(f'test_data/test_output/output_leapfrog/{filename}.csv',
                                 delimiter=',')
        assert np.allclose(ref_data, tmp_data, rtol=1e-05, atol=1e-08)
