from turbopy import Simulation
import spring

problem_config = {
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
