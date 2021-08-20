from turbopy import Simulation
import matplotlib.pyplot as plt
import spring
import Uncertainty as UQ


meanSpringConstant = 3 # mean (center) of the spring constant graph.
meanMass = 1
stdSpringConstant = 0.05 # standard deviation of the spring constant
stdMass = 0.05

runner = UQ.Uncertainty(meanSpringConstant, meanMass, stdSpringConstant, stdMass)

mc = UQ.MonteCarlo(runner, 1000)

mc.displayMaxMomentum("Test")





# Below this is just a display of the block on spring problem with no uncertainty.



problem_config = {
    "Grid": {"N": 2, "x_min": 0, "x_max": 1},
    "Clock": {"start_time": 0,
            "end_time": 12,
            "num_steps": 1200},
    "PhysicsModules": {
        "BlockOnSpring": {
            "mass": meanMass,
            "spring_constant": meanSpringConstant,
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


problem_config["PhysicsModules"]["BlockOnSpring"]["pusher"] = "ForwardEuler"
problem_config["Diagnostics"]["directory"] = "output_euler/"

sim = Simulation(problem_config)
sim.run()



time = sim.diagnostics[0].csv._buffer
momentum = sim.diagnostics[1].csv._buffer[:,1]
position = sim.diagnostics[2].csv._buffer[:,1]
plt.plot(time, momentum)
plt.plot(time, position)
plt.xlabel('time')
plt.title('position (orange) , momentum (blue)')
plt.show()

