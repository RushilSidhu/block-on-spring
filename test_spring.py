"""Tests for block-on-spring turboPy app"""
import numpy as np
import pytest
from turbopy import PhysicsModule, Simulation
from spring import BlockOnSpring


@pytest.fixture(name="sim")
def simulation_fixture():
    """Creates a simulation object used to create a B.O.S. object"""
    input_data = {
        "Tools": {"ForwardEuler": {}},
        "Grid": {"min": 1, "max": 2, "N": 3},
        "Clock": {"start_time": 0, "end_time": 1, "dt": 1},
        "PhysicsModules": {},
        "Diagnostics": {},
        }
    simulation = Simulation(input_data)
    simulation.prepare_simulation()
    return simulation


def test_sim_config(sim):
    """Test tool configuration"""
    assert sim.find_tool_by_name("ForwardEuler") is not None


def test_subclass():
    """Test main PhysicsModule class"""
    assert issubclass(BlockOnSpring, PhysicsModule)


def test_instance(sim):
    """Test instantiating a BlockOnSpring object"""
    min_config = {"pusher": "ForwardEuler"}
    block_instance = BlockOnSpring(sim, min_config)
    assert isinstance(block_instance, BlockOnSpring)


def test_attributes(sim):
    """Test setting attributes for a BlockOnSpring"""
    config = {
        "mass": 1,
        "spring_constant": 1,
        "pusher": "ForwardEuler",
        "x0": [[0, 1, 0]],
        }
    block = BlockOnSpring(sim, config)
    # These attributes get set in __init__()
    assert block.mass == 1
    assert block.spring_constant == 1
    np.testing.assert_allclose(block.position, [[0, 0, 0]])
    block.initialize()
    # These attributes get set in initialize()
    np.testing.assert_allclose(block.position, config["x0"])


@pytest.fixture(name="bos_config")
def bos_fixture():
    """Returns a dictionary of input data to create a B.O.S object"""
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

    return block_config


def test_bos_forwardeuler(bos_config):
    """Tests block_on_spring app with ForwardEuler ComputeTool and compares to
    output files with a "good" output.
    """
    bos_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "ForwardEuler"
    bos_config["Diagnostics"]["directory"] = "test_data/test_output/"\
        "output_ForwardEuler/"
    sim = Simulation(bos_config)
    sim.run()
    for filename in ['block_p', 'block_x', 'time']:
        ref_data = np.genfromtxt('test_data/reference_output/'
                                 f'output_ForwardEuler/{filename}.csv',
                                 delimiter=',')
        tmp_data = np.genfromtxt('test_data/test_output/'
                                 f'output_ForwardEuler/{filename}.csv',
                                 delimiter=',')
        assert np.allclose(ref_data, tmp_data)


def test_bos_backwardeuler(bos_config):
    """Tests block_on_spring app with BackwardEuler ComputeTool and compares to
    output files with a "good" output.
    """
    bos_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "BackwardEuler"
    bos_config["Diagnostics"]["directory"] = "test_data/test_output/"\
        "output_BackwardEuler/"
    sim = Simulation(bos_config)
    sim.run()
    for filename in ['block_p', 'block_x', 'time']:
        ref_data = np.genfromtxt('test_data/reference_output/'
                                 f'output_BackwardEuler/{filename}.csv',
                                 delimiter=',')
        tmp_data = np.genfromtxt('test_data/test_output/'
                                 f'output_BackwardEuler/{filename}.csv',
                                 delimiter=',')
        assert np.allclose(ref_data, tmp_data)


def test_bos_leapfrog(bos_config):
    """Tests block_on_spring app with LeapFrog ComputeTool and compares to
    output files with a "good" output.
    """
    bos_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "Leapfrog"
    bos_config["Diagnostics"]["directory"] = "test_data/test_output/"\
        "output_Leapfrog/"
    sim = Simulation(bos_config)
    sim.run()
    for filename in ['block_p', 'block_x', 'time']:
        ref_data = np.genfromtxt('test_data/reference_output/'
                                 f'output_Leapfrog/{filename}.csv',
                                 delimiter=',')
        tmp_data = np.genfromtxt('test_data/test_output/'
                                 f'output_Leapfrog/{filename}.csv',
                                 delimiter=',')
        assert np.allclose(ref_data, tmp_data)
