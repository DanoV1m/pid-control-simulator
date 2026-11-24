# Numerical validation

The calculation engine is separated from Streamlit. Strict left-half-plane classification, finite coefficients and DC-gain-based steady state have regression tests. Margins remain sampled approximations; exact pole-zero cancellation, negative responses, derivative filtering and robust settling guarantees require further work. Run `python -m unittest discover -s tests -v`. Do not claim physical or MATLAB validation until measured.
