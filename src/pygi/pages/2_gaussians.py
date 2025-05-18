"""Streamlit app for Gaussian helpers
"""
import pandas as pd
import streamlit as st
from pygi import physics as ph
from pygi.dashboard import ureg
from pygi.helpers import add_equation

# Config
st.set_page_config(page_title="Gaussian Beam Calculator")

# CSS
st.write('''<style>

.stHorizontalBlock > .stColumn {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>''', unsafe_allow_html=True)

# Defaults
ul = ph.unit_list
input_values = {'w0': 50.0 * ureg('um'),
                'wz': 2.0 * ureg('mm'),
                'wvl': 532.0 * ureg('nm'),
                'z': 10.0 * ureg('cm'),
                'f': 100.0 * ureg('mm'),
                'm2': 1.0 * ureg('')}

# Session state
if 'initialized_gaussian' not in st.session_state:
    st.session_state['initialized_gaussian'] = True

    st.session_state['submitted_free_space'] = False
    st.session_state['submitted_lens_focus'] = False

    for k, v in input_values.items():
        st.session_state[k] = v


def main():
    """Main function to run the Streamlit page

    Shows Gaussian propagation and focusing calculator.
    """

    tab1, tab2 = st.tabs(['Free space propagation', 'Lens focusing'])

    with tab1:
        st.header('Free space propagation')
        form_free_space()

    with tab2:
        st.header('Focusing')
        form_lens_focus()


def input_row(label, quantity, key):
    """Create a row of input fields for the form.

    :param str label: Label for the input field.
    :param float value: Default value for the input field.
    :param str unit: Unit for the input field.
    :param str key: Key for the session state.
    """
    value = quantity.magnitude
    unit = quantity.units

    with st.container():
        col1, col2 = st.columns(2)
        return_number = col1.number_input(label, min_value=0.0, value=value, format='%.3f', key=key)
        return_unit = col2.selectbox('Units', ul, index=ul.index(f'{unit:~}'), key=f'{key}_unit')
        return_unit = ureg(return_unit)
    return return_number * return_unit


def form_free_space():
    """Create form for free space propagation of a Gaussian beam.
    """
    with st.form('form_free_space'):
        w0 = input_row('Beam waist radius', st.session_state['w0'], 'w0_FS')
        wvl = input_row('Wavelength', st.session_state['wvl'], 'wvl_FS')
        z = input_row('Propagation distance', st.session_state['z'], 'z_FS')
        m2 = st.number_input('M2 factor', min_value=1.0,
            value=st.session_state['m2'].magnitude, key='m2_FS')
        m2 = m2 * ureg('')

        # Every form must have a submit button.
        submitted_fs = st.form_submit_button("Submit",
            on_click=update_session_state, args=[['_FS', 'w0', 'wvl', 'z', 'm2']])

        add_equation(r'w_z = w_0 \sqrt{1 + \left( \frac{m^2 \lambda z}{\pi w_0^2} \right)^2}')

        add_beam_metrics(w0, wvl, m2)

        # Plotting
        z_array, wz_array = ph.caustic(w0, z, wvl, m2)
        add_plot(z_array, wz_array,
            xlabel='Propagation distance', ylabel='Beam size')

        if submitted_fs or st.session_state['submitted_free_space']:
            st.session_state['submitted_free_space'] = True

            wz = ph.beam_size(w0, z, wvl, m2)
            st.metric(
                label=f'Beam size at {z:#~P} from waist',
                value=f'{wz.to_compact():.2f~P}')


def form_lens_focus():
    """Create form for focusing of a Gaussian beam.
    """
    with st.form('form_lens_focus'):
        wz = input_row('Beam waist radius', st.session_state['wz'], 'wz_LF')
        wvl = input_row('Wavelength', st.session_state['wvl'], 'wvl_LF')
        f = input_row('Focal length', st.session_state['f'], 'f_LF')
        m2 = st.number_input('M2 factor', min_value=1.0, value=st.session_state['m2'].magnitude, key='m2_LF')
        m2 = m2 * ureg('')

        # Every form must have a submit button.
        submitted_lf = st.form_submit_button("Submit",
            on_click=update_session_state, args=[['_LF', 'wz', 'wvl', 'f', 'm2']])

        with st.expander('Equation', expanded=False):
            st.latex(r'w_\text{collimated}= M^2 \frac{\lambda f}{\pi w_0}')

        if submitted_lf or st.session_state['submitted_lens_focus']:
            st.session_state['submitted_lens_focus'] = True

            focus_radius = ph.lens_focusing(wz, f, wvl, m2)

            add_beam_metrics(focus_radius, wvl, m2)

            # Plotting
            z_array, wz_array = ph.caustic(focus_radius, -f, wvl, m2=m2)
            add_plot(z_array, wz_array,
                xlabel='Distance from lens', ylabel='Beam size')

            st.metric(label='Focused beam radius', value=f'{focus_radius.to_compact():.2f~P}')


def add_plot(x, y, xlabel=None, ylabel=None):
    """Add plot to the app.

    :param list x: X values.
    :param list y: Y values.
    :param str xlabel: X axis label.
    :param str ylabel: Y axis label.
    """
    with st.expander('Caustic', expanded=False):
        df = pd.DataFrame({'x': x.magnitude, 'y': y.magnitude})
        st.line_chart(df, x='x', x_label=f'{xlabel} ({x.units})', y_label=f'{ylabel} ({y.units})',
            use_container_width=True)


def add_beam_metrics(w0, wvl, m2):
    """Add additional beam metrics to the app.

    :param float w0: Beam waist radius.
    :param float wvl: Wavelength.
    :param float m2: M2 factor.
    """
    with st.expander('Beam metrics', expanded=False):
        st.metric(label='Divergence (half cone)',
            value=f'{ph.beam_divergence(w0, wvl, m2).to_compact():.2f~P}')
        st.metric(label='Rayleigh length (mm)',
            value=f'{ph.rayleigh_length(w0, wvl, m2).to_compact():.2f~P}')


def update_session_state(key_values):
    """Update input values from session state, so they carry between tabs.
    """
    suffix = key_values.pop(0)
    for arg in key_values:
        st.session_state[arg] = st.session_state[arg + suffix] * st.session_state[arg].units


main()
