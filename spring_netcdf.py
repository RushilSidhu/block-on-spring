"""Use turboPy to compute the motion of a block on a spring

This version of the example app uses the turobPy `HistoryDiagnostic` to 
save the simulation output to a single netCDF format file.
"""
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from turbopy import Simulation, PhysicsModule, Diagnostic
from turbopy import CSVOutputUtility, ComputeTool


class BlockOnSpring(PhysicsModule):
    """Use turboPy to compute the motion of a block on a spring"""

    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.position = np.zeros((1, 3))
        self.momentum = np.zeros((1, 3))
        self.mass = input_data.get('mass', 1)
        self.spring_constant = input_data.get('spring_constant', 1)
        self.push = owner.find_tool_by_name(input_data["pusher"]).push

    def initialize(self):
        self.position[:] = np.array(self._input_data["x0"])

    def exchange_resources(self):
        self.publish_resource({"Block:position": self.position})
        self.publish_resource({"Block:momentum": self.momentum})

    def update(self):
        self.push(self.position, self.momentum,
                  self.mass, self.spring_constant)


class ForwardEuler(ComputeTool):
    """Implementation of the forward Euler algorithm

    y_{n+1} = y_n + h * f(t_n, y_n)
    """

    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.dt = None

    def initialize(self):
        self.dt = self._owner.clock.dt

    def push(self, position, momentum, mass, spring_constant):
        p0 = momentum.copy()
        momentum[:] = momentum - self.dt * spring_constant * position
        position[:] = position + self.dt * p0 / mass


class BackwardEuler(ComputeTool):
    """Implementation of the backward Euler algorithm

    y_{n+1} = y_n + h * f(t_{n+1}, y_{n+1})

    Since the position and momentum are separable for this problem, this
    algorithm can be rearranged to give
    alpha = (1 + h^2 * k / m)
    alpha * x_{n+1} = x_n + h * p_n / m
            p_{n+1} = p_n + h * (-k * x_{n+1})
    """

    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.dt = None

    def initialize(self):
        self.dt = self._owner.clock.dt

    def push(self, position, momentum, mass, spring_constant):
        factor = 1.0 / (1 + self.dt ** 2 * spring_constant / mass)
        position[:] = (position + self.dt * momentum / mass) * factor
        momentum[:] = momentum - self.dt * spring_constant * position


class Leapfrog(ComputeTool):
    """Implementation of the leapfrog algorithm

    x_{n+1} = x_n + h * fx(t_{n}, p_{n})
    p_{n+1} = p_n + h * fp(t_{n+1}, x_{n+1})
    """

    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.dt = None

    def initialize(self):
        self.dt = self._owner.clock.dt

    def push(self, position, momentum, mass, spring_constant):
        position[:] = position + self.dt * momentum / mass
        momentum[:] = momentum - self.dt * spring_constant * position


PhysicsModule.register("BlockOnSpring", BlockOnSpring)
ComputeTool.register("ForwardEuler", ForwardEuler)
ComputeTool.register("BackwardEuler", BackwardEuler)
ComputeTool.register("Leapfrog", Leapfrog)


if __name__ == "__main__":
    block_config = {
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
        },
        "Diagnostics": {
            # default values come first
            "directory": "output_leapfrog/",
            "histories": {
                "filename": "output.nc",
                "traces": [
                    {'name': 'Block:momentum',
                    'units': 'kg m/s',
                    'coords': ["dim0", "vector component"],
                    'long_name': 'Block Momentum'
                    },
                    {'name': 'Block:position',
                    'units': 'm',
                    'coords': ["dim0", "vector component"],
                    'long_name': 'Block Position'
                    },
                ]
            }
        }
    }

    sim = Simulation(block_config)
    sim.run()

    block_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "ForwardEuler"
    block_config["Diagnostics"]["directory"] = "output_euler/"

    sim = Simulation(block_config)
    sim.run()

    # Now plot the outputs
    lf_output = xr.load_dataset('output_leapfrog/output.nc')
    print(lf_output)
    lf_output['Block:position'][:,1].plot(x='time', label='Leapfrog')
    plt.show()

    fe_output = xr.load_dataset('output_euler/output.nc')
    print(fe_output)
    lf_output['Block:position'][:,1].plot(x='time', label='Leapfrog')
    fe_output['Block:position'][:,1].plot(x='time', label='Forward Euler')
    plt.legend()
    plt.grid()
    plt.show()
