"""Exercise actual rendered DOM at desktop and narrow widths; local server only."""
import unittest
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
                            page.get_by_text("Compare with Open-Loop Plant Performance",exact=True).click()
                            expect(page.locator(".metrics-grid").nth(1).locator(".metric-glass-card")).to_have_count(5)
                            expect(page.locator(".metrics-grid").nth(1)).to_be_visible()
                            page.get_by_text("System Architecture & Control Loop Block Diagram",exact=True).click()
                            svg=page.locator(".block-diagram-container svg")
                            expect(svg).to_be_visible()
                            expect(svg.locator("circle")).to_have_count(2)
                            expect(svg.locator("rect")).to_have_count(2)
                            expect(svg.locator("text").filter(has_text="PID Controller")).to_be_visible()
                            expect(svg.locator("text").filter(has_text="LTI Plant")).to_be_visible()
                            expect(svg.locator("marker#arrow")).to_have_count(1)
                            expect(page.locator(".math-card")).to_have_count(3)
                            self.assertEqual(page.locator(".metrics-grid").first.evaluate("(el) => getComputedStyle(el).display"),"grid")
                            self.assertEqual(page.locator("pre").filter(has_text="<div class=").count(),0)
                            self.assertEqual(page.locator("pre").filter(has_text="<circle").count(),0)
                            self.assertEqual(page.locator("pre").filter(has_text="<path").count(),0)
                            self.assertEqual(page.locator('[data-testid="stException"]').count(),0)
                        finally:
                            page.close()
            finally:
                browser.close()
