"""Landing page"""
import streamlit as st
from pint import UnitRegistry


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

# Defaults
ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
ureg.formatter.default_format = '~'

st.write("# Welcome to ...")

