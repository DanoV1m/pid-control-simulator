import unittest
from streamlit.testing.v1 import AppTest

class LegacyAppTests(unittest.TestCase):
    def test_default_and_pid_update(self):
        at=AppTest.from_file("app.py",default_timeout=60).run()
        self.assertEqual(len(at.exception),0)
        self.assertEqual(len(at.tabs),4)
        self.assertEqual(len(at.get("plotly_chart")),3)
        before=at.get("plotly_chart")[0].proto.spec
        at.slider[0].set_value(12.0).run()
        self.assertEqual(len(at.exception),0)
        self.assertNotEqual(before,at.get("plotly_chart")[0].proto.spec)
    def test_hebrew_interface(self):
        at=AppTest.from_file("app.py",default_timeout=60).run()
        at.radio[0].set_value("עברית").run()
        self.assertEqual(len(at.exception),0)
        self.assertEqual(len(at.tabs),4)
        self.assertEqual(len(at.get("plotly_chart")),3)
