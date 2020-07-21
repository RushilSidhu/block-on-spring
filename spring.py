"""Use turboPy to compute the motion of a block on a spring"""
import numpy as np
# import xarray as xr
# import matplotlib.pyplot as plt

from turbopy import Simulation, PhysicsModule, Diagnostic
from turbopy import CSVDiagnosticOutput, ComputeTool


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
        self.position[:] = np.array(self.input_data["x0"])

    def exchange_resources(self):
        self.publish_resource({"Block:position": self.position})
        self.publish_resource({"Block:momentum": self.momentum})
    
    def update(self):
        self.push(self.position, self.momentum,
                  self.mass, self.spring_constant)


class BlockDiagnostic(Diagnostic):
    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.data = None
        self.component = input_data.get("component", 1)
        self.output_function = None
        
    def inspect_resource(self, resource):
        if "Block:" + self.component in resource:
            self.data = resource["Block:" + self.component]
    
    def diagnose(self):
        self.output_function(self.data[0, :])

    def initialize(self):
        # setup output method
        functions = {"stdout": self.print_diagnose,
                     "csv": self.csv_diagnose,
                     }
        self.output_function = functions[self.input_data["output_type"]]
        if self.input_data["output_type"] == "csv":
            diagnostic_size = (self.owner.clock.num_steps + 1, 3)
            self.csv = CSVDiagnosticOutput(self.input_data["filename"], diagnostic_size)

    def finalize(self):
        self.diagnose()
        if self.input_data["output_type"] == "csv":
            self.csv.finalize()

    def print_diagnose(self, data):
        print(data)

    def csv_diagnose(self, data):
        self.csv.append(data)


class ForwardEuler(ComputeTool):
    def __init__(self, owner: Simulation, input_data: dict):
        super().__init__(owner, input_data)
        self.dt = None
        
    def initialize(self):
        self.dt = self.owner.clock.dt
    
    def push(self, position, momentum, mass, spring_constant):
        p0 = momentum.copy()
        momentum[:] = momentum - self.dt * spring_constant * position
        position[:] = position + self.dt * p0 / mass


PhysicsModule.register("BlockOnSpring", BlockOnSpring)
Diagnostic.register("BlockDiagnostic", BlockDiagnostic)
ComputeTool.register("ForwardEuler", ForwardEuler)

problem_config = {
    # Note: grid isn't used, but "gridless" sims aren't an option yet
    "Grid": {"N": 2, "x_min": 0, "x_max": 1},
    "Clock": {"start_time": 0,
              "end_time": 10,
              "num_steps": 100},
    "PhysicsModules": {
        "BlockOnSpring": {
            "mass": 1,
            "spring_constant": 1,
            "pusher": "ForwardEuler",
            "x0": [0, 1, 0],
        }
    },
    "Tools": {
        "ForwardEuler": {}
    },
    "Diagnostics": {
        # default values come first
        "directory": "output/",
        "output_type": "csv",
        "clock": {"filename": "time.csv"},
        "BlockDiagnostic": [
            {'component': 'momentum', 'filename': 'block_p.csv'},
            {'component': 'position', 'filename': 'block_x.csv'}
        ]
    }
}

sim = Simulation(problem_config)
sim.run()
