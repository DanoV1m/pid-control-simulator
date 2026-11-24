import unittest
import numpy as np
from control_engine import parse_coefficients, compute_closed_loop_tf, calculate_step_metrics, dc_gain

class EngineTests(unittest.TestCase):
    def test_nonfinite_and_zero(self):
        self.assertIsNone(parse_coefficients("nan,1"))
        self.assertIsNone(parse_coefficients("inf"))
        np.testing.assert_array_equal(parse_coefficients("0"), [0])
    def test_p_control(self):
        n,d,_,_=compute_closed_loop_tf(np.array([1]),np.array([1,1]),2,0,0)
        np.testing.assert_allclose(n,[2])
        np.testing.assert_allclose(d,[1,3])
        self.assertAlmostEqual(dc_gain(n,d),2/3)
    def test_boundary_poles(self):
        for pole in [0,1e-9,1j]:
            self.assertFalse(calculate_step_metrics(np.array([0,1]),np.array([0,1]),np.array([pole]))["stable"])
    def test_short_window(self):
        t=np.linspace(0,5,100)
        result=calculate_step_metrics(t,1-np.exp(-t/10),np.array([-.1]),final_value=1)
        self.assertEqual(result["steady_state"],1)
        self.assertIsNone(result["settling_time"])
        self.assertIsNone(result["rise_time"])
if __name__ == "__main__":
    unittest.main()
