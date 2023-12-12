import streamlit as st
import folium
import numpy as np
import plotly.express as px
import pandas as pd

def app(df):
    # Analisis Geográfico
    st.header('Analisis Geográfico')
    # Create a select box for the tabs
    tab = st.selectbox('Seleccione', ['Mapa de Incidencias', 'Gráfico de incidencias por distrito según el año '])

    if tab == 'Mapa de Incidencias':
        def get_color(fatalities):
            if fatalities > 5000:
                return 'darkred'
            elif fatalities > 1000:
                return 'red'
            elif fatalities > 500:
                return 'orange'
            else:
                return 'green'


        

        # Create a base map centered around the region
        district_coords = {
            'Gaza': [31.5, 34.466667],
            'Hebron': [31.532569, 35.095388],
            'Jenin': [32.457336, 35.286865],
            'Nablus': [32.221481, 35.254417],
            'Ramallah': [31.902922, 35.206209],
            'Bethlehem': [31.705791, 35.200657],
            'Tulkarm': [32.308628, 35.028537],
            'Jericho': [31.857163, 35.444362],
            'Rafah': [31.296866, 34.245536],
            'Khan Yunis': [31.346201, 34.306286]
        }

        district_fatalities = df.groupby('event_location_district').size()

        # Create a base map centered around the region
        my_map = folium.Map(location=[31.5, 34.75], zoom_start=8, tiles='OpenStreetMap')

        # Add markers and circles for districts
        for district, coords in district_coords.items():
            fatalities = district_fatalities.get(district, 0)
            folium.Marker(
                location=coords,
                tooltip=f'{district}: {fatalities} fatalities',
                icon=None
            ).add_to(my_map)
            folium.Circle(
                location=coords,
                radius=np.sqrt(fatalities) * 100,  
                color=get_color(fatalities),  
                fill=True,
                fill_color=get_color(fatalities),
                fill_opacity=0.6,
            ).add_to(my_map)

        # Convert Folium map to HTML
        map_html = my_map._repr_html_()

        # Use Streamlit to display the map
        st.components.v1.html(map_html, width=800, height=500, scrolling=True)

        st.write("""
        Este mapa representa la distribución geográfica de las fatalidades por distrito. Cada círculo representa un distrito, 
        y su tamaño es proporcional a la cantidad de fatalidades en ese distrito. El color de cada círculo representa la cantidad 
        de fatalidades, con un gradiente de verde a rojo oscuro.
        """)

        # Display the results of the attacks per district
        results = district_fatalities.reset_index()
        results.columns = ['district', 'fatalities']
        
        st.subheader('Número de fatalidades por distrito')
        # Create four columns for the results
        cols = st.columns(4)
        for i in range(len(results)):
            with cols[i % 4]:  # Use modulus operation to cycle through the four columns
                cols[i % 4].subheader(f"{results.iloc[i, 0]}")
                st.info(f"{results.iloc[i, 1]} ")

    elif tab == 'Gráfico de incidencias por distrito según el año ':
        # Converting 'date_of_event' to datetime
        df['date_of_event'] = pd.to_datetime(df['date_of_event'])

        # Extracting the year from the date
        df['year'] = df['date_of_event'].dt.year

        # Grouping df by year and region
        year_region_fatalities = df.groupby(['year', 'event_location_region']).size().unstack(fill_value=0).reset_index()

        # Melt the DataFrame for Plotly
        year_region_fatalities_melted = pd.melt(year_region_fatalities, id_vars=['year'], var_name='Region', value_name='Fatalities')

        # Create a Streamlit app
        st.title('Fatalidades durante los años por regiones')
        

        # Create a dropdown widget to select the region
        region_options = ['All'] + list(year_region_fatalities_melted['Region'].unique())
        selected_region = st.selectbox('Selecciona la región', region_options)

        # Filter the data based on the selected region
        if selected_region == 'All':
            filtered_data = year_region_fatalities_melted
            title = 'Fatalidades durante los años Todos'
        else:
            filtered_data = year_region_fatalities_melted[year_region_fatalities_melted['Region'] == selected_region]
            title = f'Fatalidades durante los años  {selected_region}'

        # Create an interactive line plot using Plotly
        fig = px.line(filtered_data, x='year', y='Fatalities', color='Region',
                    labels={'year': 'Year', 'Fatalities': 'Number of Fatalities'},
                    title=title)
        fig.update_xaxes(tickangle=45)

        # Show the interactive plot within Streamlit
        st.plotly_chart(fig)