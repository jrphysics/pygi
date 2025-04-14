"""Streamlit app for Gaussian helpers
"""
import streamlit as st
from pygi import physics as ph

# Config
st.set_page_config(layout='wide')

# Defaults
input_values = {'w0': 1.0, 'w0_unit': 'mm',
                'wvl': 1.0, 'wvl_unit': 'um'}

# Session state
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True

    st.session_state['submitted_free_space'] = False
    st.session_state['submitted_lens_focus'] = False


def main():
    """Main function to run the Streamlit app

    Shows Gaussian propagation and focusing calculator.
    """
    st.title('Gaussian Beam Calculator')

    col_left, col_right = st.columns(2)

    with col_left:
        st.header('Free space propagation')
        form_free_space()

    with col_right:
        st.header('Focusing')
        form_lens_focus()


def form_free_space():
    """Create form for free space propagation of a Gaussian beam.
    """
    # If user already entered values, reuse them
    for k in input_values:
        if k in st.session_state:
            input_values[k] = st.session_state[k]

    with st.form('form_free_space'):
        col1, col2 = st.columns(2)
        w0 = col1.number_input('Beam waist radius', min_value=0.0, value=input_values['w0'], format='%.3f')
        w0_unit = col2.selectbox(
            'Units', ph.unit_list,
            index=ph.unit_list.index(input_values['w0_unit']),
            key='w0_unit_free_space')

        wvl = col1.number_input('Wavelength', min_value=0.0, value=input_values['wvl'], format='%.3f')
        wvl_unit = col2.selectbox(
            'Units', ph.unit_list,
            index=ph.unit_list.index(input_values['wvl_unit']),
            key='wvl_unit_free_space')

        z = col1.number_input('Propagation distance', min_value=0.0, value=1.0, format='%.3f')
        z_unit = col2.selectbox(
            'Units', ph.unit_list,
            index=0, key='z_unit_free_space')

        m2 = st.number_input('M2 factor', min_value=1.0, value=1.0)

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")

        with st.expander('Equation', expanded=False):
            st.latex(r'w_z = w_0 \sqrt{1 + \left( \frac{m^2 \lambda z}{\pi w_0^2} \right)^2}')

        if submitted or st.session_state['submitted_free_space']:
            st.session_state['submitted_free_space'] = True

            # Save input values
            # st.session_state['w0'] = w0
            # st.session_state['w0_unit'] = w0_unit
            st.session_state['wvl'] = wvl
            st.session_state['wvl_unit'] = wvl_unit

            wz = ph.beam_size(
                w0 * ph.unit(w0_unit),
                z * ph.unit(z_unit),
                wvl * ph.unit(wvl_unit), m2)
            st.metric(
                label=f'Beam size at {z:.2f}{z_unit} from waist ({w0_unit})',
                value=round(wz / ph.unit(w0_unit), 2))


def form_lens_focus():
    """Create form for focusing of a Gaussian beam.
    """
    # If user already entered values, reuse them
    for k in input_values:
        if k in st.session_state:
            input_values[k] = st.session_state[k]

    with st.form('form_lens_focus'):
        col1, col2 = st.columns(2)
        w0 = col1.number_input('Collimated beam radius', min_value=0.0, value=input_values['w0'], format='%.3f')
        w0_unit = col2.selectbox(
            'Units', ph.unit_list,
            index=ph.unit_list.index(input_values['w0_unit']), key='w0_unit_lens_focus')

        wvl = col1.number_input('Wavelength', min_value=0.0, value=input_values['wvl'], format='%.3f')
        wvl_unit = col2.selectbox(
            'Units', ph.unit_list,
            index=ph.unit_list.index(input_values['wvl_unit']), key='wvl_unit_lens_focus')

        f = col1.number_input('Focal length', min_value=0.0, value=100.0, format='%.3f')
        f_unit = col2.selectbox(
            'Units', ph.unit_list,
            index=2, key='f_unit_lens_focus')

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")

        with st.expander('Equation', expanded=False):
            st.latex(r'w_\text{collimated}= \frac{\lambda f}{\pi w_0}')

        if submitted or st.session_state['submitted_lens_focus']:
            st.session_state['submitted_lens_focus'] = True

            # Save input values
            # st.session_state['w0'] = w0
            # st.session_state['w0_unit'] = w0_unit
            st.session_state['wvl'] = wvl
            st.session_state['wvl_unit'] = wvl_unit

            focus_radius = ph.lens_focusing(
                w0 * ph.unit(w0_unit),
                f * ph.unit(f_unit),
                wvl * ph.unit(wvl_unit))
            st.metric(label='Focused beam radius', value=round(focus_radius / ph.unit('um'), 2))


if __name__ == "__main__":
    main()
