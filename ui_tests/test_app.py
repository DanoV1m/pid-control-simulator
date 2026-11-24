import unittest
from pathlib import Path

APP = str(Path(__file__).resolve().parents[1] / 'app.py')
from streamlit.testing.v1 import AppTest

class AppSmokeTests(unittest.TestCase):
    def test_default_tabs_and_modes(self):
        app=AppTest.from_file(APP, default_timeout=60).run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertEqual(len(app.tabs),7)
        mode=next(r for r in app.radio if "P-Only" in r.options)
        mode.set_value("P-Only").run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertEqual(len(app.tabs),7)
    def test_invalid_denominator(self):
        app=AppTest.from_file(APP,default_timeout=60).run()
        self.assertFalse(app.exception,str(app.exception))
        app.text_input[1].set_value("0").run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertTrue(app.error)

    def test_custom_markup_and_language(self):
        app=AppTest.from_file(APP, default_timeout=60).run()
        for language in ("English", "עברית"):
            app.radio[0].set_value(language).run()
            self.assertFalse(app.exception,str(app.exception))
            payloads=[element.proto.body for element in app.get("html")]
            self.assertEqual(sum(s.count('class="metric-glass-card"') for s in payloads),10)
            self.assertEqual(sum('class="block-diagram-container"' in s for s in payloads),1)
            self.assertEqual(sum('class="math-card"' in s for s in payloads),3)
            self.assertEqual(sum('class="sidebar-section-badge"' in s for s in payloads),3)
            self.assertTrue(any('class="hero-container"' in s for s in payloads))
            self.assertFalse(any('<div' in e.value or '<svg' in e.value for e in app.markdown))
            self.assertEqual(len(app.tabs),7)
