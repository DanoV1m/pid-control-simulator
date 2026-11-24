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
