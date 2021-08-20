import numpy as np
from turbopy import Simulation
import matplotlib.pyplot as plt
import spring

class Uncertainty:
    def __init__(self, mean_K, mean_M, sd_K = 0,  sd_M = 0): # Initializes an Uncertainty object that can self randomize and run the turboPy Physics Module on itself.
        self.mean_K = mean_K
        self.mean_M = mean_M
        self.sd_K = sd_K
        self.sd_M = sd_M
        self.springConstant = np.random.normal(self.mean_K, self.sd_K)
        self.mass = np.random.normal(self.mean_M, self.sd_M)
    
    def randomizeVars(self):
        self.springConstant = np.random.normal(self.mean_K, self.sd_K)
        self.mass = np.random.normal(self.mean_M, self.sd_M)

    def run(self,t0,t1,steps): # Uses the turboPy Physics Module for the Block on Spring problem.
        problem_config = {
            "Grid": {"N": 2, "x_min": 0, "x_max": 1},
            "Clock": {"start_time": t0,
                    "end_time": t1,
                    "num_steps": steps},
            "PhysicsModules": {
                "BlockOnSpring": {
                    "mass": self.mass,
                    "spring_constant": self.springConstant,
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

        time = sim.diagnostics[0].csv._buffer
        momentum = sim.diagnostics[1].csv._buffer[:,1]
        position = sim.diagnostics[2].csv._buffer[:,1]

        retDct = {}
        for i in range(len(time)):
            retDct[time[i][0]] = (momentum[i],position[i])  # Stores everything in a dictionary witth the structure dict[time] = (momentum at time, position at time)
        return retDct

class MonteCarlo:
    def __init__(self,runner, n, t0 = 0, t1 = 12, steps = 1200):   #Runner is an object from the class Uncertainty and n is the number of runs
        dataDct = {}
        randMass = []
        randK = []
        for i in range(n):
            randMass += [runner.mass]
            randK += [runner.springConstant]
            dataDct[(runner.springConstant,runner.mass)] = runner.run(t0,t1,steps)
            runner.randomizeVars()
        
        self.dataDct = dataDct

    def displayMaxMomentum(self, title, xMin = 0, xMax = 0):  # xMin and xMax represent the range of the graph.

        histData = []
        for key in self.dataDct: # Simple max value finder for each iteration of mass and spring constant.
            tempMaxMomentum = -1
            for t in self.dataDct[key]:
                if(self.dataDct[key][t][0] > tempMaxMomentum):
                    tempMaxMomentum = self.dataDct[key][t][0]
            histData += [tempMaxMomentum]

        if(xMin != xMax):
            plt.hist(histData, 50, facecolor='blue', alpha=0.5, range=[xMin,xMax])

        else:
            plt.hist(histData, 50, facecolor='blue', alpha=0.5)

        plt.title(title)
        plt.xlabel('Momentum')
        plt.ylabel('Count')
        plt.show()
                