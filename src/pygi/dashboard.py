"""Landing page"""
import streamlit as st
from pint import UnitRegistry


st.set_page_config(
    page_title="pyGI",
    page_icon="👋",
)

# Defaults
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
ureg.formatter.default_format = '~'

st.write("# Welcome to pyGI")
st.write('Your single stop for all your laser needs!')

st.write('What do you need?')
st.page_link("pages/1_converters.py", label="Converters across units")
st.page_link("pages/2_gaussians.py", label="Gaussian beam calculator")
