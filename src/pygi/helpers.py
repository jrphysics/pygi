import streamlit as st


def add_equation(equation):
    """Add equation to the app.

    :param str equation: Equation to add.
    """
    with st.expander('Equation', expanded=False):
        st.latex(equation)
