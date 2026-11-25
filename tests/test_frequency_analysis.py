import unittest
import numpy as np
from control_engine import root_locus_samples, nyquist_samples

class FrequencyTests(unittest.TestCase):
    def test_first_order_locus(self):
        roots = root_locus_samples([1], [1, 1], [0, 1, 3])
        np.testing.assert_allclose(np.array(roots).ravel(), [-1, -2, -4])
    def test_singular_gain(self):
        with self.assertRaises(ValueError):
            root_locus_samples([-1], [1], [1])
    def test_nyquist_mirror(self):
        w = np.array([0.1, 1, 10])
        p, n = nyquist_samples([1], [1,1], w)
        np.testing.assert_allclose(p, 1/(1+1j*w))
        np.testing.assert_allclose(n, p[::-1].conj())
