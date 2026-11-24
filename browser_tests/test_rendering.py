"""Exercise actual rendered DOM at desktop and narrow widths; local server only."""
import unittest
import re
from playwright.sync_api import sync_playwright, expect

class BrowserRenderingTests(unittest.TestCase):
    def test_desktop_and_narrow_markup(self):
        with sync_playwright() as p:
            browser=p.chromium.launch()
            try:
                for width in (1440, 390):
                    with self.subTest(width=width):
                        page=browser.new_page(viewport={"width":width,"height":900})
                        try:
                            page.goto("http://127.0.0.1:8501",wait_until="domcontentloaded")
                            expect(page.locator(".hero-container")).to_be_visible(timeout=60000)
                            expect(page.locator(".metrics-grid").first.locator(".metric-glass-card")).to_have_count(5,timeout=60000)
                            if width==390:
                                sidebar=page.get_by_test_id("stSidebar")
                                if sidebar.get_attribute("data-collapsed")=="false":
                                    sidebar.get_by_test_id("stSidebarCollapseButton").click()
                                    expect(sidebar).to_have_attribute("data-collapsed","true")
                            page.get_by_text("Compare with Open-Loop Plant Performance",exact=True).click()
                            expect(page.locator(".metrics-grid").nth(1).locator(".metric-glass-card")).to_have_count(5)
                            expect(page.locator(".metrics-grid").nth(1)).to_be_visible()
                            page.get_by_text("System Architecture & Control Loop Block Diagram",exact=True).click()
                            image=page.locator(".block-diagram-container img.control-loop-image")
                            expect(image).to_be_visible(timeout=15000)
                            expect(image).to_have_attribute("src",re.compile(r"^data:image/svg\+xml;base64,"))
                            page.wait_for_function("() => { const img=document.querySelector('.control-loop-image'); return img && img.complete && img.naturalWidth>0 && img.naturalHeight>0; }",timeout=15000)
                            result=image.evaluate("""async el => {
                                const xml=await (await fetch(el.src)).text();
                                const svg=new DOMParser().parseFromString(xml,'image/svg+xml');
                                return {circles:svg.querySelectorAll('circle').length,
                                    rects:svg.querySelectorAll('rect').length,
                                    paths:svg.querySelectorAll('path').length,
                                    arrow:!!svg.querySelector('marker#arrow'),
                                    labels:svg.documentElement.textContent};
                            }""")
                            self.assertEqual(result["circles"],2)
                            self.assertEqual(result["rects"],2)
                            self.assertGreaterEqual(result["paths"],6)
                            self.assertTrue(result["arrow"])
                            self.assertIn("PID Controller",result["labels"])
                            self.assertIn("LTI Plant",result["labels"])
                            expect(page.locator(".math-card")).to_have_count(3)
                            expect(page.get_by_role("tab")).to_have_count(4)
                            for label in ("Step Response (Time Domain)", "s-Plane Pole-Zero Map", "Frequency Response (Bode Plot)"):
                                page.get_by_role("tab",name=label,exact=True).click()
                                plot=page.get_by_role("tabpanel").filter(visible=True).locator(".js-plotly-plot")
                                expect(plot).to_be_visible(timeout=30000)
                                page.wait_for_function("() => Array.from(document.querySelectorAll('.js-plotly-plot')).some(el => el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0 && el.data && el.data.length > 0 && el.querySelector('.main-svg'))",timeout=30000)
                            page.get_by_role("tab",name="Pole Telemetry & Damping Analysis",exact=True).click()
                            expect(page.get_by_test_id("stDataFrame")).to_be_visible()
                            self.assertEqual(page.locator(".metrics-grid").first.evaluate("(el) => getComputedStyle(el).display"),"grid")
                            self.assertEqual(page.locator("pre").filter(has_text="<div class=").count(),0)
                            self.assertEqual(page.locator("pre").filter(has_text="<circle").count(),0)
                            self.assertEqual(page.locator("pre").filter(has_text="<path").count(),0)
                            self.assertEqual(page.locator('[data-testid="stException"]').count(),0)
                        finally:
                            page.close()
            finally:
                browser.close()
