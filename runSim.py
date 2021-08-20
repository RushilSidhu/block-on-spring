from turbopy import Simulation
import matplotlib.pyplot as plt
import spring
import Uncertainty

problem_config = {
    "Grid": {"N": 2, "x_min": 0, "x_max": 1},
    "Clock": {"start_time": 0,
              "end_time": 100,
              "num_steps": 1000},
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

problem_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "ForwardEuler"
problem_config["Diagnostics"]["directory"] = "output_euler/"

sim = Simulation(problem_config)
sim.run()

mc = Uncertainty.Uncertainty(1,1,10,10)

print(mc.getMonteCarlo())

time = sim.diagnostics[0].csv._buffer
momentum = sim.diagnostics[1].csv._buffer[:,1]
position = sim.diagnostics[2].csv._buffer[:,1]
plt.plot(position, momentum)
plt.xlabel('time')
plt.ylabel('position')
plt.show()