import pandas as pd
import geopandas
import streamlit as st
import folium
import plotly.express as px
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import numpy as np


@st.cache
def get_data(path):
    data = pd.read_csv(path)
    data.drop_duplicates(subset=['id'], inplace=True, keep='first')
    data = data.reset_index(drop=True)
    

    ##agrupar por zipcode para analisar e criar a coluna median_by_zipcode! (primeiro padrao para compra)
    zipc = data[['price', 'zipcode']].groupby('zipcode').median().reset_index()
    zipc.rename(columns={'price': 'median_price', 'zipcode': 'zipcode'}, inplace=True)
    for i in range(len(data)):
        for k in range(len(zipc)):
            if data.loc[i, 'zipcode'] == zipc.loc[k, 'zipcode']:
                data.loc[i, 'median_by_zipcode'] = zipc.loc[k, 'median_price']
    # tratar os dados iniciais (add o q precisar)
    # resell min = 1.1 do valor de compra (a empresa que estabeleceu)
    
    data.rename(columns={'long': 'lon'}, inplace=True)
    data['date'] = pd.to_datetime(data['date'])
    data['price_m2'] = data['price'] / data['sqft_lot']
    data['renovated'] = data['yr_renovated'].apply(lambda x: 'no' if x == 0 else 'yes')
    data['month'] = pd.to_datetime(data['date']).dt.month
    data['season'] = data['month'].apply(lambda x: 'summer' if (x > 5) & (x < 8) else
    'spring' if (x > 2) & (x < 5) else
    'fall' if (x > 8) & (x < 12) else
    'winter')

    ##analisar agrupar por zipcode para criar season_to_sell
    ##basicamente tive que selecionar a temporada com a  maior mediana by zipcode para ser o melhor momento para venda
    x = data[['price', 'zipcode', 'season']].groupby(['zipcode', 'season']).median().reset_index()
    x.rename(columns={'zipcode': 'zipcode', 'season': 'season', 'price': 'median_price'}, inplace=True)
    ziphigh = []
    for i in range(3, len(x), 4):
        zipcode = x.loc[i, 'zipcode']
        ziphigh.append(x.loc[i - 3, 'median_price'])
        ziphigh.append(x.loc[i - 2, 'median_price'])
        ziphigh.append(x.loc[i - 1, 'median_price'])
        ziphigh.append(x.loc[i, 'median_price'])
        x.loc[i - 3, 'max_price'] = max(ziphigh)
        x.loc[i - 2, 'max_price'] = max(ziphigh)
        x.loc[i - 1, 'max_price'] = max(ziphigh)
        x.loc[i, 'max_price'] = max(ziphigh)
        if len(ziphigh) == 4:
            p = 0
            s = str(x.loc[(x['median_price'] == max(ziphigh)) & (x['zipcode'] == zipcode), 'season'])
            season_max = s.split()[1]
            for k in range(len(data)):
                if data.loc[k, 'zipcode'] == zipcode:
                    data.loc[k, 'season_to_sell'] = season_max
                    f = list(x.loc[x['zipcode']==zipcode,'max_price'])
                    data.loc[k,'season_max_price'] = f[0]
            for j in range(4):

                x.loc[i - j, 'season_max'] = season_max
                p = p + 1
                if p == 4:
                    ziphigh = []
    # limpar os outliers
    data['bedrooms'].max()
    data = data.drop([15870]).reset_index()
    # se for menor q a mediana da regiao e condicao maior igual 3 = pode comprar
    for i in range(len(data)):
        if data.loc[i, 'price'] < data.loc[i,'season_max_price']:
            data.loc[i, 'resell_min'] = data.loc[i, 'season_max_price'] 
        else:
            data.loc[i, 'resell_min'] = data.loc[i, 'price'] * 1.1
        data.loc[i, 'profit'] = data.loc[i,'resell_min'] - data.loc[i, 'price']



    for i in range(len(data)):
        if (data.loc[i, 'price'] < data.loc[i, 'median_by_zipcode']) & (data.loc[i, 'condition'] >= 3):
            data.loc[i, 'situation'] = 'to_buy'
        else:
            data.loc[i, 'situation'] = 'not_to_buy'
    return data


@st.cache
def get_geofile():
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
    geofile = geopandas.read_file(url)
    return geofile


def get_maps(x):
    genre_map = st.radio('Choose a Map', ('Price Density Map', 'Street View Map'))

    c1, c2 = st.columns((1, 1))
    c1.header = ('Portfolio Density')

    if genre_map == 'Street View Map':
        st.map(x)


    elif genre_map == 'Price Density Map':
        geofile = get_geofile()
        ids_map = folium.Map(location=[x['lat'].mean(), x['lon'].mean()], default_zoom_start=15)

        make_cluster = MarkerCluster().add_to(ids_map)
        df = x[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        folium.Choropleth(data=x, geo_data=geofile, columns=['zipcode', 'price'], key_on='feature.properties.ZIP',
                          fill_color='YlOrRd', fill_opacity=0.7, line_opacity=0.2, legend_name='AVG PRICE').add_to(
            ids_map)
        for name, row in x.iterrows():
            tooltip = 'Click me for more info!'

            folium.Marker(location=[row['lat'], row['lon']],
                          popup="\ {0}\n\ ID:{1}\n\ Price:U${2}\n\ ZIP Median Price: U${3}\n\n\ Yr built:{4}\n\ Yr renovated:{5}\n Sqft lot:{6}\n\ Condition: {7}\n\ Floors:{8}\n\ ".format(
                              row['situation'], row['id'], row['price'], row['median_by_zipcode'], row['yr_built'],
                              row['yr_renovated'], row['sqft_lot'], row['condition'], row['floors']),
                          tooltip='click me for more info!').add_to(make_cluster)
        with c1:
            folium_static(ids_map)
    return None


def filter_data(data, price_filter, bedroom_filter, bathroom_filter, floors_filter, waterfront_filter=None):
    if waterfront_filter == 1:
        df2 = data.loc[(data['price'] <= price_filter) & (data['bedrooms'] <= bedroom_filter) & (
                    data['bathrooms'] <= bathroom_filter) & (data['waterfront'] == 1)]
    else:
        df2 = data.loc[(data['price'] <= price_filter) & (data['bedrooms'] <= bedroom_filter) & (
                    data['bathrooms'] <= bathroom_filter)]

    if bool(floors_filter) == False:
        df1 = df2
    else:
        df1 = df2.loc[df2['floors'].isin(floors_filter)]

    return df1


def get_bars_one(data):
    st.subheader("1) WHAT HOUSES ARE THE BEST OPPORTUNITIES TO BUY? ")
    dados_analise = data.groupby(['zipcode', 'situation'], as_index=False, sort=True).size().reset_index()
    excluded = []
    opportunities = []
    profit = []
    try:  ##vai executar todos os dados incluindo os nao profit
        for i in range(len(dados_analise)):
            if not dados_analise.loc[i, 'zipcode'] in excluded:
                excluded.append(dados_analise.loc[i, 'zipcode'])
                dados_analise.loc[i, 'total'] = dados_analise.loc[i, 'size'] + dados_analise.loc[i + 1, 'size']
                percent = dados_analise.loc[i, 'size'] / dados_analise.loc[i, 'total']
                dados_analise.loc[i, 'percent'] = "{:.0%}".format(percent)
                dados_analise.loc[i, 'zipcode'] = str(dados_analise.loc[i, 'zipcode'])
            else:
                dados_analise.loc[i, 'total'] = dados_analise.loc[i - 1, 'total']
                dados_analise.loc[i, 'zipcode'] = str(dados_analise.loc[i, 'zipcode'])
                percent = dados_analise.loc[i, 'size'] / dados_analise.loc[i, 'total']
                dados_analise.loc[i, 'percent'] = "{:.0%}".format(percent)
                opportunities.append(dados_analise.loc[i, 'size'])
    except:  # vai executar se marcarem o box de apenas os profit!
        for i in range(len(dados_analise)):
            percent = dados_analise.loc[i, 'size'] / dados_analise.loc[i, 'size']
            dados_analise.loc[i, 'percent'] = "{:.0%}".format(percent)
            opportunities.append(dados_analise.loc[i, 'size'])
    finally:
        percents = len(data.loc[data['situation'] == 'to_buy']) / dados_analise['size'].sum()
        if 'not_to_buy' in list(data['situation']):
            fig = px.bar(dados_analise, x="zipcode", y='size', color='situation', text_auto='.2s',
                         color_discrete_sequence=["red", "lightgreen"])
        else:
            fig = px.bar(dados_analise, x="zipcode", y='size', color='situation', text_auto='.2s',
                         color_discrete_sequence=["lightgreen"])
        fig.update_traces(textfont_size=100, textangle=0, textposition="auto", cliponaxis=False)
        fig.update_layout(width=1000, height=400, bargap=0.1)
        col1, col2 = st.columns([1, 1])
        col2.metric(label='Opportunities',
                    value='{0} / {1}'.format(len(data.loc[data['situation'] == 'to_buy']), dados_analise['size'].sum()),
                    delta="{:.0%}".format(percents))
        col1.metric(label="Currently Estimated Profit", value='U$ {:,} '.format(data.loc[data['situation']=='to_buy','profit'].sum()))
        st.header("SIZE OF OPPORTUNITIES BY ZIPCODE")
        st.plotly_chart(fig, use_container_width=True)

    return None


def get_profit_info(data):
    prof2 = data.loc[data['situation'] == 'to_buy', ['zipcode', 'profit']].groupby('zipcode').sum().reset_index()
    prof = prof2.astype({'zipcode': 'string'})
    fig = px.bar(prof, x="zipcode", y="profit", color_discrete_sequence=["lightgreen"])
    fig.update_traces(textfont_size=100, textangle=0, textposition="auto", cliponaxis=False)
    fig.update_layout(width=1000, height=400, bargap=0.001)
    dataframe = st.checkbox('Display dataframe')
    if dataframe:
        st.dataframe(prof, width=1000)
    st.plotly_chart(fig)

    return None


def get_bars_two(data):
    st.subheader('2) WHAT IS THE BEST MOMENT TO SELL HOUSES?')
    zips_list = np.unique(data['zipcode']).tolist()
    zips_list.append('All zipcodes distribution')
    zips = st.selectbox('Choose a zipcode >', (zips_list))
    if zips == 'All zipcodes distribution':
        x = data[['price', 'zipcode', 'season']].groupby(['zipcode', 'season']).median().reset_index()
        x.rename(columns={'zipcode': 'zipcode', 'season': 'season', 'price': 'median_price'}, inplace=True)
        ziphigh = []
        for i in range(3, len(x), 4):
            zipcode = x.loc[i, 'zipcode']
            ziphigh.append(x.loc[i - 3, 'median_price'])
            ziphigh.append(x.loc[i - 2, 'median_price'])
            ziphigh.append(x.loc[i - 1, 'median_price'])
            ziphigh.append(x.loc[i, 'median_price'])
            x.loc[i - 3, 'max_median_price'] = max(ziphigh)
            x.loc[i - 2, 'max_median_price'] = max(ziphigh)
            x.loc[i - 1, 'max_median_price'] = max(ziphigh)
            x.loc[i, 'max_median_price'] = max(ziphigh)
            if len(ziphigh) == 4:
                p = 0
                s = str(x.loc[(x['median_price'] == max(ziphigh)) & (x['zipcode'] == zipcode), 'season'])
                season_max = s.split()[1]
                for k in range(len(data)):
                    if data.loc[k, 'zipcode'] == zipcode:
                        data.loc[k, 'season_to_sell'] = season_max
                for j in range(4):
                    x.loc[i - j, 'season_max'] = season_max
                    p = p + 1
                    if p == 4:
                        ziphigh = []
        a = x[['zipcode', 'max_median_price', 'season_max']].drop_duplicates()
        fig = px.scatter(a, x="season_max", y='max_median_price', hover_name="zipcode")
        fig.update_layout(width=1000, height=400, bargap=0.1)
        st.plotly_chart(fig)
    else:
        h = data[['price', 'zipcode', 'season']].groupby(['zipcode', 'season']).median().reset_index()
        f = h.loc[h['zipcode'] == zips]
        x = f['season']
        y = f['price']
        fig = px.line(f, x=x, y=y, color_discrete_sequence=["lightgreen"])
        fig.update_layout(width=1000, height=400, bargap=0.1)

        st.plotly_chart(fig)
    return None


def get_insights(data):
    st.subheader('3) INSIGHTS ')
    insights = st.radio('', ('Basement insight', 'Floors insight', 'Renovated buildings insight', 'Profit zipcodes'))
    if insights == 'Basement insight':
        pd.set_option('display.float_format', lambda x: '%.2f' % x)
        base_off = data.loc[data['sqft_basement'] == 0]
        base_off_grouped = base_off[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        base_on = data.loc[data['sqft_basement'] > 0]
        base_on_grouped = base_on[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        all_mean = pd.merge(base_off_grouped, base_on_grouped, on='zipcode', how='inner')
        all_mean.rename(columns={'zipcode': 'zipcode', 'price_x': 'without_basement', 'price_y': 'with_basement'},
                        inplace=True)
        df = {'basement': ['0', '1'],
              'mean_price': [all_mean['without_basement'].mean(), all_mean['with_basement'].mean()]}
        df2 = pd.DataFrame(df)
        fig = px.bar(df2, x="basement", y="mean_price", color_discrete_sequence=["lightgreen"])
        fig.update_layout(width=1000, height=400, bargap=0.1)
        dataframe = st.checkbox('Display dataframe')
        if dataframe:
            st.dataframe(all_mean, width=1000)
        st.plotly_chart(fig)
    elif insights == 'Floors insight':
        pd.set_option('display.float_format', lambda x: '%.2f' % x)
        floors = data.loc[data['floors'] == 1]
        floors_grouped = floors[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        floors_high = data.loc[data['floors'] > 1]
        floors_grouped_two = floors_high[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        all_mean = pd.merge(floors_grouped, floors_grouped_two, on='zipcode', how='inner')
        all_mean.rename(columns={'zipcode': 'zipcode', 'price_x': 'one_floor', 'price_y': 'two_or_more_floors'},
                        inplace=True)
        df = {'floors': ['1', '1>'],
              'mean_price': [all_mean['one_floor'].mean(), all_mean['two_or_more_floors'].mean()]}
        df2 = pd.DataFrame(df)
        fig = px.bar(df2, x="floors", y="mean_price", color_discrete_sequence=["lightgreen"])
        fig.update_layout(width=1000, height=400, bargap=0.1)
        dataframe = st.checkbox('Display dataframe')
        if dataframe:
            st.dataframe(all_mean, width=1000)
        st.plotly_chart(fig)

    elif insights == 'Renovated buildings insight':
        pd.set_option('display.float_format', lambda x: '%.2f' % x)
        not_renovated = data.loc[data['renovated'] == 'no']
        not_renovated_grouped = not_renovated[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        renovated = data.loc[data['renovated'] == 'yes']
        renovated_grouped = renovated[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        all_mean = pd.merge(not_renovated_grouped, renovated_grouped, on='zipcode', how='inner')
        all_mean.rename(
            columns={'zipcode': 'zipcode', 'price_x': 'not_renovated_price_mean', 'price_y': 'renovated_price_mean'},
            inplace=True)
        df = {'renovated': ['no', 'yes'],
              'mean_price': [all_mean['not_renovated_price_mean'].mean(), all_mean['renovated_price_mean'].mean()]}
        df2 = pd.DataFrame(df)
        fig = px.bar(df2, x="renovated", y="mean_price", color_discrete_sequence=["lightgreen"])
        fig.update_layout(width=1000, height=400, bargap=0.1)
        dataframe = st.checkbox('Display dataframe')
        if dataframe:
            st.dataframe(all_mean, width=1000)
        st.plotly_chart(fig)
    else:
        get_profit_info(data)

    return None


def streamlit_site(data):
    st.set_page_config(
        page_title="dbb_app01",
        page_icon="🧊",
        layout="wide", )
    st.title('🏡KC Home Sales Data Overview')
    dataf = get_data(data)
    st.sidebar.title('Filters')
    alldata_display = st.sidebar.checkbox(label='Use all data')
    profit_display = st.sidebar.checkbox(label='Show only profit items')
    dataframe_display = st.sidebar.checkbox(label='Show the dataframe')
    if profit_display:
        data_real = dataf.loc[dataf['situation'] == 'to_buy']
        print(data_real.shape)
    else:
        data_real = dataf

    if dataframe_display:
        st.dataframe(data_real, width=1000)

    price_min = int(data_real['price'].min())
    price_max = int(data_real['price'].max())
    price_avg = int(data_real['price'].mean())

    max_cama = int(data_real['bedrooms'].max())
    min_cama = int(data_real['bedrooms'].min())
    media_cama = int(data_real['bedrooms'].mean())

    min_bath = int(data_real['bathrooms'].min())
    max_bath = int(data_real['bathrooms'].max())
    avg_bath = int(data_real['bathrooms'].mean())

    floors_list = list(set(data_real['floors']))
    floors_list.sort()

    price_filter = st.sidebar.slider(label='Maximum Price', min_value=price_min, max_value=price_max, value=price_max)
    floors_filter = st.sidebar.multiselect('Floors Number', floors_list)
    bedroom_filter = st.sidebar.slider(label='Bedrooms', min_value=min_cama, max_value=max_cama, value=max_cama)
    bathroom_filter = st.sidebar.slider(label='Bathrooms', min_value=min_bath, max_value=max_bath, value=max_bath)
    ischeck = st.sidebar.checkbox(label='Only waterfront houses')

    if ischeck:
        df1 = filter_data(data_real, price_filter, bedroom_filter, bathroom_filter, floors_filter, waterfront_filter=1)
    else:
        df1 = filter_data(data_real, price_filter, bedroom_filter, bathroom_filter, floors_filter)

    if not alldata_display:
        df1 = df1.head(500)

    get_bars_one(df1)
    get_maps(df1)
    get_bars_two(dataf)
    get_insights(dataf)

    return None


if __name__ == "__main__":
    streamlit_site('kc_house_data.csv')

     
   
























