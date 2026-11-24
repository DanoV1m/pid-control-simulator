import unittest
import numpy as np
from scipy import signal
from control_engine import calculate_frequency_margins

class MarginsTest(unittest.TestCase):
    def test_first_order(self):
        m=calculate_frequency_margins(signal.TransferFunction([2],[1,1]))
        self.assertAlmostEqual(m['w_gc'],np.sqrt(3),places=3)
        self.assertAlmostEqual(m['pm'],120,places=2)
        self.assertIsNone(m['gm'])
    def test_third_order(self):
        m=calculate_frequency_margins(signal.TransferFunction([4],[1,3,3,1]))
        self.assertAlmostEqual(m['w_pc'],np.sqrt(3),places=3)
        self.assertAlmostEqual(m['gm'],20*np.log10(2),places=2)
    def test_no_crossing(self):
        m=calculate_frequency_margins(signal.TransferFunction([.1],[1,1]))
        self.assertIsNone(m['pm'])
        self.assertIsNone(m['w_gc'])
