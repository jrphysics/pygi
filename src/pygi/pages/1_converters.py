import re
import streamlit as st
from pygi.dashboard import ureg
from pygi.helpers import add_equation
from pygi.physics import pulse_avg_power, pulse_peak_power


# Config
st.set_page_config(page_title="Converters")

# Session state
if 'initialized_converter' not in st.session_state:
    st.session_state['initialized_converter'] = True

    st.session_state['ratio_dB'] = None
    st.session_state['ratio_%'] = None

    st.session_state['power_dBm'] = None
    st.session_state['power_W'] = None

    st.session_state['pulse_time'] = '1 ns'
    st.session_state['pulse_frequency'] = '1 kHz'
    st.session_state['pulse_energy'] = '1 mJ'


def main():
    """Main function to run the Streamlit page

    Shows the multiple converters.
    """
    tab1, tab2 = st.tabs(['Pulsed Laser Power', 'dB converter'])

    with tab1:
        st.header('Pulsed Laser Power')
        pulsed_cw(tab=tab1)


    with tab2:
        st.header('dB converter')
        db_converter(tab=tab2)

        st.header('dBm converter')
        dbm_converter(tab=tab2)


def pulsed_cw(tab: st.tabs = None):
    st.text_input(label="Pulse energy", key='pulse_energy', placeholder="1 mJ",
        on_change=text_to_pint, kwargs={'input_key': 'pulse_energy', 'tab': tab})

    st.text_input(label="Pulse width", key='pulse_time', placeholder="1 ns",
        on_change=text_to_pint, kwargs={'input_key': 'pulse_time', 'tab': tab})

    st.text_input(label="Pulse repetition frequency", key='pulse_frequency', placeholder="1 KHz",
        on_change=text_to_pint, kwargs={'input_key': 'pulse_frequency', 'tab': tab})

    for k in ['pulse_energy', 'pulse_time', 'pulse_frequency']:
        text_to_pint(input_key=k, tab=tab)

    show_pulse_power(tab=tab)
    add_equation(r'''P_\text{avg} = E \cdot f \quad \text{W}
        \\ -------- \\
        P_\text{peak} = \frac{E}{\tau} \quad \text{W}
        ''')


def text_to_pint(input_key: str = '', tab: st.tabs = None):
    regex = r'^(?P<number>[0-9]?+\.?[0-9]?+)\s?(?P<unit>\w+)?$'
    default_units = {'[time]': 's', '[frequency]': 'Hz', '[energy]': 'J', '[power]': 'W'}
    user_input = st.session_state[input_key]
    dimension = f'[{input_key.split('_')[-1]}]'

    re_match = re.match(regex, user_input)

    if user_input == '':
        return

    number = re_match.group('number')
    unit = re_match.group('unit')

    if re_match is None or not number:
        with tab:
            st.error('Invalid input format. Please use the format: <number> <unit>.')
        return

    value = float(number)
    if not unit:
        # Default unit is Joules (SI)
        unit = ureg(default_units[dimension])
    else:
        unit = ureg(unit)

    if not unit.check(dimension):
        with tab:
            st.error(f'Invalid unit: {unit}. Please use a valid {dimension} unit.')

    st.session_state[f'{input_key}_pint'] = value * unit


def show_pulse_power(tab: st.tabs = None):
    pulse_time = st.session_state['pulse_time_pint']
    pulse_energy = st.session_state['pulse_energy_pint']
    pulse_frequency = st.session_state['pulse_frequency_pint']

    power_avg = pulse_avg_power(pulse_energy, pulse_frequency)
    power_peak = pulse_peak_power(pulse_energy, pulse_time)
    with tab:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label='Average power', value=f'{power_avg.to('W').to_compact():.2f~#P}')
        with col2:
            st.metric(label='Peak power', value=f'{power_peak.to('W').to_compact():.2f~#P}')


def update_input_boxes(leading_value: str = None, keys_to_update: list = None, tab=None):
    """Updates the relevant input boxes if one changes

    :param str leading_value: _description_, defaults to None
    :param list keys_to_update: _description_, defaults to None
    :param _type_ tab: The streamlit tab object to place the input boxes in
    """
    value = st.session_state[leading_value]
    unit = ureg(leading_value.split('_')[-1])

    if 'dB' not in str(unit.units):
        if value == 0:
            with tab:
                st.error(f'0{str(unit.units)} cannot be converted to dB')
            value = None

    for k in keys_to_update:
        if k != leading_value:
            if value is None:
                st.session_state[k] = None
            else:
                value_unit = value * unit
                st.session_state[k] = value_unit.to(k.split('_')[-1]).magnitude


def generate_input_box(label: str = '', key: str = '', keys_to_update: list = None, value: float = None, number_format: str = '%.2f', tab: st.tabs = None):
    """Generate input box for the converters page

    Parameters
    ----------
    label : str, optional
        _description_, by default ''
    key : str, optional
        _description_, by default ''
    keys_to_update : list, optional
        _description_, by default None
    value : float, optional
        _description_, by default None
    number_format : str, optional
        _description_, by default '%.2f'
    tab : st.tabs, optional
        The streamlit tab object to place the input boxes in
    """
    st.number_input(
        label=label,
        value=value,
        format=number_format,
        key=key,
        on_change=update_input_boxes,
        kwargs={'leading_value': key, 'keys_to_update': keys_to_update, 'tab': tab},
    )


def db_converter(tab: st.tabs = None):
    """Converter between dB and percentage

    Parameters
    ----------
    tab : st.tabs, optional
        The streamlit tab object to place the input boxes in
    """
    input_boxes = ['ratio_dB', 'ratio_%']
    generate_input_box(label="Ratio (dB)", key="ratio_dB",
        keys_to_update=input_boxes, number_format="%.2f", tab=tab)
    generate_input_box(label="Ratio (%)", key="ratio_%",
        keys_to_update=input_boxes, number_format="%.2f", tab=tab)

    add_equation(r'''R_\text{\%} = 100 \cdot 10^{\frac{R_\text{dB}}{10}} \quad \text{\%}
        \\ - \\
        R_\text{dB} = 10 \cdot \log_{10}\left(\frac{R_\text{\%}}{100}\right) \quad \text{dB}''')


def dbm_converter(tab: st.tabs = None):
    """Converter between dBm and W

    Parameters
    ----------
    tab : st.tabs, optional
        The streamlit tab object to place the input boxes in
    """
    input_boxes = ['power_dBm', 'power_W']
    generate_input_box(label="Input power (dBm)", key="power_dBm",
        keys_to_update=input_boxes, number_format="%.2f", tab=tab)
    generate_input_box(label="Input power (W)", key="power_W",
        keys_to_update=input_boxes, number_format="%.2E", tab=tab)

    add_equation(r'''P_\text{W} = 10^{\frac{P_\text{dBm} - 30}{10}} \quad \text{W}
        \\ -------- \\
        P_\text{dBm} = 10 \cdot \log_{10}(P_\text{W}) + 30 \quad \text{dBm}''')


main()
