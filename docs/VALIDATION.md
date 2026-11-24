# Numerical validation

The calculation engine is separated from Streamlit. Strict left-half-plane classification, finite coefficients and DC-gain-based steady state have regression tests. Margins remain sampled approximations; exact pole-zero cancellation, negative responses, derivative filtering and robust settling guarantees require further work. Run `python -m unittest discover -s tests -v`. Do not claim physical or MATLAB validation until measured.

## Root locus and Nyquist
The new tabs show sampled roots of the compensated loop characteristic polynomial D+kN and mirrored frequency response. No automatic encirclement count or stability verdict is claimed; imaginary-axis poles require a full indented contour. Tests use analytic first-order reference cases.

## Actuator saturation
A separate first-order plant experiment compares conditional integration with ordinary integral action, using exact zero-order-hold plant propagation. It is not a nonlinear simulation of the selected transfer function. Tests check saturation, analytic propagation and integral windup.

## Frequency margins
Gain and phase crossings now use logarithmic-frequency interpolation on 10^-3 to 10^3 rad/s, including phase crossings at odd multiples of 180 degrees. Reported margins are the signed candidates closest to zero; they do not establish closed-loop stability. Tangencies and crossings outside the grid may be missed. Missing values mean no detected crossing, not infinite margin. Analytical first- and third-order tests cover reference frequencies and margins.

## UI regression
CI installs the full application requirements and runs Streamlit AppTest for all seven default analysis tabs, switching controller mode and rejecting an invalid denominator. This exercises Python UI execution, not visual browser rendering.

## Python runtime compatibility
The CI matrix checks Python 3.11 and 3.14 independently with fail-fast disabled. Each job installs binary wheels for the full application requirements, checks dependency consistency and imports, records resolved versions, compiles the application and executes numerical and Streamlit AppTest regressions. Binary-only installation deliberately rejects dependencies requiring a source build in this Linux CI environment. Application requirements now pin all 36 packages captured in both successful Linux CI runs for commit 13921e3, with Python-version markers for NumPy and SciPy. CI verifies all active package versions and tests browser rendering separately. Pins are not a hash-verified, cross-platform lockfile; additional platform-specific dependencies, operating system libraries, package availability and the actual hosted environment may differ. No CI step deploys the application.

## HTML and SVG rendering regression
All twelve custom HTML/CSS/SVG calls use Streamlit's dedicated st.html renderer (minimum Streamlit 1.33), not Markdown. Existing visual styles and metric computation are retained. Narrow metric grids can shrink to the container width; the SVG diagram scrolls horizontally within its card where necessary to maintain legibility. AppTest checks markup for both languages, and a Chromium CI test checks the actual DOM at desktop and narrow widths against a loopback-only Streamlit server. It does not deploy, compare pixel-perfect screenshots, or validate every browser or device. No user-provided HTML or JavaScript is enabled.

### Chromium follow-up
Initial browser runs passed the Python checks but did not locate the inline SVG in the rendered DOM and encountered sidebar interception at 390 px. The static, trusted SVG is now encoded as an image inside the existing HTML card, preserving its vector content without relying on inline SVG surviving the HTML sanitizer. The sidebar uses Streamlit's adaptive initial state. Browser checks require a decoded visible image, verify diagram geometry and labels in its SVG source, and exercise real expander clicks; the AppTest also decodes the same payload. No external deployment is involved in these local browser checks.

## Release dependency preparation
The exact package lists came from both successful push and PR runs (45413365383 and 45413376905). Playwright 1.65.2 and greenlet 3.5.6 are pinned separately in CI to avoid adding browser tooling to the deployed app. The browser install remains CI-only and uses a loopback server; system packages are not locked. Python 3.11 and 3.14 are the tested minor versions. Other Python versions are not supported by this dependency snapshot. Revalidate after updating any pin. The new snapshot requires a fresh CI run before release.
