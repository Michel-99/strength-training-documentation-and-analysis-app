import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import supabase
from supabase import create_client, Client
from datetime import datetime, timedelta
import numpy as np
import plotly.express as ff

headers={
    "authorization":st.secrets["url", "key"]}

key =st.secrets["key"]
url = st.secrets["url"]

supabase = create_client(url, key)
response = supabase.table("Training").select("*").execute()

#print(response)



layout = 'wide'

st.set_page_config(page_title=('Trainingsdokumentation'), layout=layout)
st.title('Trainingsdokumentation')

selected =option_menu(None,['Eingabe: Einheit', 'letzte Einheit','Auswertung: Einheit', 'test'], orientation='horizontal')



if selected == 'Eingabe: Einheit':

    uebung = supabase.table("Übungsdatenbank").select("Übung").execute()
    listue = uebung.data
    uebung_pd = pd.DataFrame(data = listue)

    with st.form('Trainingsdokumentation', clear_on_submit=True):

        st.selectbox("What excercise did you perform?", uebung_pd, key = 'ubung')
        st.radio('Wich set did you do?', (1, 2, 3, 4, 5, 6), key='set')
        st.select_slider('How many repititions did you do?', options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                         key='rep')
        st.number_input('how much weight did you lift?', key='kg')
        st.select_slider('How many repitions in reserve?', options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                         key='rir')
        
        
        #######
        submitted = st.form_submit_button('Save Data')
        if submitted:
            excercise = str(st.session_state['ubung'])
            satz = int(st.session_state['set'])
            rep = int(st.session_state['rep'])
            kg = int(st.session_state['kg'])
            rir = int(st.session_state['rir'])
            relload = rep / (rep + rir)
            mihg = (rep * kg) / rep

            data, count = supabase.table('Training').insert({'Übung': excercise,'Satz' : satz,'Wiederholungen':rep,'Gewicht': kg, 'RIR':rir, 'Mittleres-Hantelgewicht': mihg, 'Relative_Load':relload}).execute()

        
            st.success('set saved!')

###############---------------------------------

if selected == 'letzte Einheit':
    
    
    with st.form('Trainingsdokumentation'):
    
        date = st.date_input('Wann war deine letzte Einheit?', format = 'YYYY-MM-DD', key = 'date')
        uebung2 = supabase.table("Übungsdatenbank").select("Übung").execute()
        listue2 = uebung2.data
        uebung_pd2 = pd.DataFrame(data = listue2)
        uebung = st.selectbox('Welche Übung möchtest du dir anschauen', uebung_pd2)
        
        submitted = st.form_submit_button('Einheit anschauen')

        if submitted:
        
            tr_data = supabase.table('Training').select('*').execute()
            tr_data = pd.DataFrame(data = tr_data.data)
            date = date.strftime('%Y-%m-%d')
            data_df = tr_data[tr_data['Datum'] == date]
            data_df = data_df[data_df['Übung'] == uebung]
            data_df = data_df.drop(columns=['id', 'created_at', 'Übung', 'Datum'])
            mitl_hg = data_df['Mittleres-Hantelgewicht']
            #
            st.dataframe(data_df, hide_index = True)
            #
            col1, col2, = st.columns(2)
            #
            with col1: 
                st.subheader('test')
                mitl_hg = mitl_hg.sum()
                rows = np.shape(data_df)[0]
                MHG = mitl_hg/rows
                st.write('Mittleres Hantelgewicht: ')
                st.write(MHG, 'kg')


            with col2: 
                st.subheader('test')
                df_chart = data_df.drop(columns=['RIR', 'Mittleres-Hantelgewicht'])
                st.line_chart(df_chart, x = 'Satz', y = ['Gewicht', 'Relative_Load'])
            
            





###############----------------------------------            

          
if selected == 'Auswertung: Einheit':
     # load 'Training' table and put it in a pd DataFrame + list of headers
     tr = supabase.table('Training').select('*').execute()
     list_tr = tr.data
     df_tr = pd.DataFrame(data = list_tr)
     tr_hea = df_tr.columns.tolist()
     tr_hea = tr_hea[2:]
     
     ue = supabase.table('Übungsdatenbank').select('Übung').execute()
     list_ue = ue.data
     df_ue = pd.DataFrame(data = list_ue)
     


     with st.form('Trainingsdokumentation'):
         
         y_param = st.selectbox('what paramter?',tr_hea, key='y' )

         xy_param = st.selectbox('Für welche Übung', df_ue, key = 'xy' )

         x = st.radio('Welchen Zeitraum möchtest du dir anschauen?', ['100', '150', '300'], key = 'x', horizontal= True)
         x = int(x)
         submitted = st.form_submit_button('GO!')

         if submitted:
            start_date = datetime.now() - timedelta(days = x)
            end_date = datetime.now()
            df_tr['Datum'] = pd.to_datetime(df_tr['Datum'], format='%Y-%m-%d')
            date_df = df_tr[(df_tr['Datum'] >= start_date) & (df_tr['Datum'] <= end_date)]
            #y_param aus selectbox heruasfiltern
            filtered_df = date_df[date_df['Übung'].str.contains(xy_param)]
            filtered_df['Satz'] = filtered_df['Satz'].astype(str)
           
            fig2 = ff.line(filtered_df, x = 'Datum', y = y_param, color = 'Satz', markers = True)
            st.plotly_chart(fig2, use_container_width=True, theme = 'streamlit')
            #st.scatter_chart(filtered_df, x = 'Datum', y = y_param)
            st.dataframe(filtered_df)
            





if selected =='test':

    test = supabase.table('Training').select('*').execute()
    list_tr = test.data
    df_tr = pd.DataFrame(data = list_tr)
    tr_hea = df_tr.columns.tolist()
    tr_hea = tr_hea[2:]

    uebung = supabase.table('Übungsdatenbank').select('*').execute()
    uebung_li = uebung.data
    df_ueb = pd.DataFrame(data = uebung_li)
    df_region = df_ueb['Körperregion']
    df_region = df_region.drop_duplicates()

    df_merged = pd.merge(df_tr, df_ueb, on='Übung')
    df_merged = df_merged.drop(columns=['id_x', 'created_at_x', 'id_y', 'created_at_y'])
    
    with st.form('test'):
        y_param2 = st.selectbox('what paramter?',tr_hea, key='y2')
        x_param = st.selectbox('welche Körperregion', df_region)
        st.dataframe(df_merged)
