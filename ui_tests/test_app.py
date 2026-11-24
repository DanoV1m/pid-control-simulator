import unittest
from streamlit.testing.v1 import AppTest

class AppSmokeTests(unittest.TestCase):
    def test_default_tabs_and_modes(self):
        app=AppTest.from_file("app.py", default_timeout=60).run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertEqual(len(app.tabs),7)
        mode=next(r for r in app.radio if "P-Only" in r.options)
        mode.set_value("P-Only").run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertEqual(len(app.tabs),7)
    def test_invalid_denominator(self):
        app=AppTest.from_file("app.py",default_timeout=60).run()
        self.assertFalse(app.exception,str(app.exception))
        app.text_input[1].set_value("0").run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertTrue(app.error)
