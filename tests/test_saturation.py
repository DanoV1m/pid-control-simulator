import unittest
import numpy as np
from control_engine import simulate_saturated_pid

class SaturationTests(unittest.TestCase):
    def test_exact_first_step(self):
        t,y,u,i=simulate_saturated_pid(2,0,0,1,.5,dt=.01,duration=.1)
        self.assertAlmostEqual(y[1],.5*(1-np.exp(-.01)))
        self.assertLessEqual(np.max(np.abs(u)),.5)
    def test_windup(self):
        _,_,_,a=simulate_saturated_pid(2,2,0,1,.5,anti_windup=False)
        _,_,_,b=simulate_saturated_pid(2,2,0,1,.5,anti_windup=True)
        self.assertGreater(a[-1],1)
        self.assertAlmostEqual(b[-1],0)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            simulate_saturated_pid(1,1,1,0,1)
