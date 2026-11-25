import unittest
import base64
import re
import xml.etree.ElementTree as ET
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
            diagrams=[s for s in payloads if 'class="block-diagram-container"' in s]
            self.assertEqual(len(diagrams),1)
            encoded=re.search(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)',diagrams[0])
            self.assertIsNotNone(encoded)
            svg=ET.fromstring(base64.b64decode(encoded.group(1)))
            ns={"s":"http://www.w3.org/2000/svg"}
            self.assertEqual(len(svg.findall(".//s:circle",ns)),2)
            self.assertEqual(len(svg.findall(".//s:rect",ns)),2)
            self.assertTrue(any(e.get("id")=="arrow" for e in svg.findall(".//s:marker",ns)))
            self.assertEqual(sum('class="math-card"' in s for s in payloads),3)
            self.assertEqual(sum('class="sidebar-section-badge"' in s for s in payloads),3)
            self.assertTrue(any('class="hero-container"' in s for s in payloads))
            self.assertFalse(any('<div' in e.value or '<svg' in e.value for e in app.markdown))
            self.assertEqual(len(app.tabs),7)
