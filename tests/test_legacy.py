"""Legacy compatibility checks; do not alter historical engineering calculations."""
import ast
import subprocess
import unittest
from pathlib import Path
import numpy as np
from scipy import signal
import app

BASE = "bb41e2874e480b739730a9dce97c4f58458ffcb1"

class LegacyRegressionTests(unittest.TestCase):
    def test_original_engine_and_chart_functions_unchanged(self):
        original = subprocess.check_output(["git", "show", BASE + ":app.py"], text=True)
        current = Path("app.py").read_text(encoding="utf-8")
        def functions(source):
            return {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}
        old, new = functions(original), functions(current)
        self.assertEqual(set(old), set(new))
        for name in old.keys() - {"main", "render_glass_metric_cards", "render_block_diagram_svg"}:
            self.assertEqual(old[name], new[name], name)
        begin = "    # --- INPUT VALIDATION & CONTROL ENGINE COMPUTATION ---"
        end = "    # --- MATHEMATICAL TRANSFER FUNCTION CONTAINERS ---"
        self.assertEqual(original.split(begin)[1].split(end)[0], current.split(begin)[1].split(end)[0])

    def test_default_pid_and_plots(self):
        num, den = np.array([1.]), np.array([1.,2.,10.])
        cn, cd, ln, ld = app.compute_closed_loop_tf(num, den, 8.,12.,1.5)
        np.testing.assert_allclose(cn, [1.5,8.,12.])
        np.testing.assert_allclose(cd, [1.,3.5,18.,12.])
        ol, cl, loop = (signal.TransferFunction(*coeffs) for coeffs in ((num,den),(cn,cd),(ln,ld)))
        t = np.linspace(0,12,1400)
        to, yo = signal.step(ol,T=t)
        tc, yc = signal.step(cl,T=t)
        self.assertTrue(np.isfinite(yc).all())
        metrics = app.calculate_step_metrics(tc,yc,np.roots(cd))
        self.assertTrue(metrics["stable"])
        for fig in (app.create_step_response_figure(to,yo,tc,yc,metrics), app.create_pole_zero_figure(np.roots(den),np.roots(num),np.roots(cd),np.roots(cn)), app.create_bode_figure(ol,loop,app.calculate_frequency_margins(loop))):
            self.assertGreater(len(fig.data), 0)
            self.assertTrue(fig.to_json())
        self.assertEqual(len(app.generate_csv_data(t,yo,yc).splitlines()),1401)
