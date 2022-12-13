import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from deta import Deta
from datetime import datetime



key =(DETA_KEY)



deta = Deta(key)

db = deta.Base('Trainingsdokumentation')

today = datetime.today().strftime('%d.%m.%y')
session_date = today


def insert_period(excercise, satz, rep, kg, rir, rel_load, mittl_ge):
    return db.put({'Datum': session_date, 'Übung': excercise, 'Satz': satz,
                   'rep': rep, 'kg': kg, 'rir': rir, 'Relative load': rel_load,
                   'Mittleres Hantelgewicht': mittl_ge})


def fetch_all_periods():
    res = db.fetch()
    return res.items


def get_period(date):
    return db.get(date)


def fetch_date(Datum):
    res2 = db.fetch({'Datum': Datum})
    return res2.items


layout = 'centered'

st.set_page_config(page_title=('Trainingsdokumentation'), layout=layout)
st.title('Trainingsdokumentation')

selected = option_menu(
    menu_title=None,
    options=('Eingabe: Einheit', 'Auswertung: Einhiet'),
    orientation='horizontal')

if selected == 'Eingabe: Einheit':
    with st.form('Trainingsdokumentation', clear_on_submit=True):

        # st.date_input('todays date', key = 'datum')

        st.text_input('What excercise are you going to perform?', key='ubung')
        st.radio('Wich set did you do?', (1, 2, 3, 4, 5, 6), key='satz')
        st.select_slider('How many repititions did you do?', options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                         key='rep')
        st.number_input('how much weight did you lift?', key='kg')
        st.select_slider('How many repitions in reserve?', options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                         key='rir')
        # st.text_input('comment about the set:', key = 'comment')

        '----'

        submitted = st.form_submit_button('Save Data')
        if submitted:
            # datum = str(st.session_state['datum'])
            excercise = str(st.session_state['ubung'])
            satz = str(st.session_state['satz'])
            rep = int(st.session_state['rep'])
            kg = int(st.session_state['kg'])
            rir = int(st.session_state['rir'])
            # comment = str(st.session_state['comment'])
            rel_load = rep / (rep + rir)
            mittl_ge = (rep * kg) / rep

            insert_period(excercise, satz, rep, kg, rir, rel_load, mittl_ge)

            st.success('workout saved!')

    # ----------

if selected == 'Auswertung: Einhiet':

    st.header('Auswertung')
    with st.form('Letzte Einheite'):
        datum_einheit = st.date_input('Datum der letzten Einheit: ')
        datum_einheit = str(datum_einheit.strftime('%d.%m.%y'))

        # datum_einheit = st.text_input('Datum der letzten Einheit (dd.mm.yy):')
        # period = st.selectbox('Einheit auswählen:', fetch_all_periods())
        submitted = st.form_submit_button('Einheit anschauen')
        if submitted:
            letzte_einheit = fetch_date(datum_einheit)
            df = pd.DataFrame(letzte_einheit)
            df = df.drop(['key', 'Datum'], axis=1)
            df = df.set_index(['Übung', 'Satz'])
            df = df.sort_values('Satz')

            st.write(df.to_html(), unsafe_allow_html=True)
