import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime


def get_season():
  current_month = datetime.now().month

  seasons = {
      (12, 1, 2): 'winter',
      (3, 4, 5): 'spring',
      (6, 7, 8): 'summer',
      (9, 10, 11): 'autumn'
  }

  return [s for months, s in seasons.items() if current_month in months][0]

def data_analysis(df):
    df = df.sort_values(['city', 'timestamp'])
    df['30_day_avg'] = df.groupby('city')['temperature'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    df['avg_temp_by_season_city'] = df.groupby(['season', 'city'])['temperature'].transform('mean')
    df['std_temp_by_season_city'] = df.groupby(['season', 'city'])['temperature'].transform('std')
    df['anomaly'] = ((df['temperature'] < (df['avg_temp_by_season_city'] - 2 * df['std_temp_by_season_city'])) |
                     (df['temperature'] > (df['avg_temp_by_season_city'] + 2 * df['std_temp_by_season_city']))).astype(int)
    df['year'] = pd.to_datetime(df['timestamp']).dt.year
    
    return df


def is_anomaly(df_interval, temperature, city):
    season = get_season()

    df_interval['left_interval'] = (df_interval['avg_temp_by_season_city'] - 2 * df_interval['std_temp_by_season_city'])
    df_interval['right_interval'] = (df_interval['avg_temp_by_season_city'] + 2 * df_interval['std_temp_by_season_city'])
    df_interval = df_interval[['city', 'season', 'left_interval', 'right_interval']].drop_duplicates().reset_index(drop=True)
    
    left_interval = df_interval.where((df_interval['season'] == season) & (df_interval['city'] == city)).dropna()['left_interval'].iloc[0]
    right_interval = df_interval.where((df_interval['season'] == season) & (df_interval['city'] == city)).dropna()['right_interval'].iloc[0]

    return (temperature <= left_interval or temperature >= right_interval, left_interval, right_interval, temperature)

def plot_value_between_borders(left_border, value, right_border):
    fig, ax = plt.subplots(figsize=(6, 1))
    ax.set_xlim(min(value, left_border) - 2, max(value, right_border) + 2)
    ax.set_ylim(-1, 1)

    ax.hlines(y=0, xmin=left_border, xmax=right_border, color='blue', linewidth=2)
    ax.text(left_border, 0.3, f'{round(left_border, 1)} °C', horizontalalignment='center', fontsize=10, color='blue')
    ax.text(right_border, 0.3, f'{round(right_border, 1)} °C', horizontalalignment='center', fontsize=10, color='blue')

    ax.plot(value, 0, 'ro')
    ax.text(value, -0.5, f'{round(value, 1)} °C', horizontalalignment='center', fontsize=10, color='red')

    ax.set_xlabel('Температура °C')

    plt.axhline(0, color='grey', lw=0.5)
    ax.set_yticks([])
    plt.grid(False)
    st.pyplot(fig)

def temp_plot(df, left_border, right_border):
    fig, ax = plt.subplots(figsize=(14, 8))
    plt.xlabel("Год")
    plt.ylabel("Температура °C")

    y = np.array(df['temperature'])
    x = pd.to_datetime(df['timestamp'])

    plt.plot(x, y, color='blue')

    plt.scatter(x[y < left_border], y[y < left_border], color='red') 
    plt.scatter(x[y > right_border], y[y > right_border], color='red')

    plt.grid(False)
    st.pyplot(plt)

def box_plot(df):
    plt.figure(figsize=(8, 4))
    plt.boxplot(df['temperature'], notch=True, patch_artist=True)
    plt.ylabel("Температура°C")
    plt.xticks([])
    plt.grid(axis='y')
    st.pyplot(plt)

def seasonal_profile(df):
    seasonal_profiles = df.groupby(['season']).agg(
        mean_temperature=('temperature', 'mean'),
        std_temperature=('temperature', 'std')
    ).reset_index()
    st.write(seasonal_profiles)

    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    sns.barplot(data=seasonal_profiles, x='season', y='mean_temperature', ax=ax[0])
    ax[0].set_title('Средняя температура по сезонам')
    ax[0].set_xlabel('Сезон')
    ax[0].set_ylabel('Средняя температура°C')

    sns.barplot(data=seasonal_profiles, x='season', y='std_temperature', ax=ax[1])
    ax[1].set_title('Среднее отклонение по сезонам')
    ax[1].set_xlabel('Сезон')
    ax[1].set_ylabel('Стандартное отклонение°C')
    ax[1].set_ylim(seasonal_profiles['std_temperature'].min() * 0.95, seasonal_profiles['std_temperature'].max() * 1.05)
    
    st.pyplot(plt)


st.title("Анализ данных по погоде")
st.sidebar.header("Настройки")

file = st.sidebar.file_uploader("Загрузите csv файл с историческими данными погоды", type="csv")
key = st.sidebar.text_input("Введите api токен для OpenWeatherMap")

if file is not None:
    df = pd.read_csv(file)
    df = data_analysis(df)
    city_list = list(df['city'].unique())
    city = st.sidebar.selectbox("Выберите город", city_list)
    min_year = min(pd.to_datetime(df[df['city'] == city]['timestamp']).dt.year)
    max_year = max(pd.to_datetime(df[df['city'] == city]['timestamp']).dt.year)

    if key:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric&lang=ru')
        response_data = response.json()

        if response.status_code == 200:
            current_temp = response_data['main']['temp']
            anomaly = is_anomaly(df, current_temp, city)

            text = f'Текущая температура в {city}: {current_temp:.1f}°C - '
            text += 'аномальная' if anomaly[0] else 'в норме'
            st.write(text)

            plot_value_between_borders(anomaly[1], anomaly[3], anomaly[2])

            st.text('')
            st.write(f'Описательная статистика по сезонам для {city}:')

            col1, col2 = st.columns(2)

            with col1:
                season = st.selectbox("Выберите сезон:", ['summer', 'autumn', 'winter', 'spring', 'all'])

            with col2:
                year = st.selectbox('Выберите год:', list(map(str, range(min_year, max_year + 1))) + ['all'])

            if season == 'all' and year == 'all':
                st.write(pd.DataFrame(df[df['city'] == city]['temperature'].describe()).T)
                box_plot(df[(df['city'] == city)])
            elif season != 'all' and year == 'all':
                st.write(pd.DataFrame(df[(df['city'] == city) & (df['season'] == season)]['temperature'].describe()).T)
                box_plot(df[(df['city'] == city) & (df['season'] == season)])
            elif season == 'all' and year != 'all':
                st.write(pd.DataFrame(df[(df['city'] == city) & (df['year'] == int(year))]['temperature'].describe()).T)
                box_plot(df[(df['city'] == city) & (df['year'] == int(year))])
            else:
                st.write(pd.DataFrame(df[(df['city'] == city) & (df['year'] == int(year))  & (df['season'] == season)]['temperature'].describe()).T)
                box_plot(df[(df['city'] == city) & (df['year'] == int(year)) & (df['season'] == season)])
            
            st.write(f'Температура с аномалиями за период: {min_year}-{max_year}')
            temp_plot(df[df['city'] == city][['timestamp', 'temperature', 'anomaly']], anomaly[1], anomaly[2])

            st.write(f'Сезонные профили для {city}:')
            seasonal_profile(df[df['city'] == city])

        else:
            error_message = {"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}
            st.error(error_message)
