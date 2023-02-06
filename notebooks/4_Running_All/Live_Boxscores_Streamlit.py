import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import sqlite3
import seaborn as sns
from matplotlib.pyplot import figure
from bs4 import BeautifulSoup
import time
import requests     
import shutil       
import datetime
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')
import requests
import json
import xgboost
from xgboost import XGBClassifier
from random import randint
import  random
import os
import plotly.graph_objs as go
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')
from cmath import nan
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.pipeline import Pipeline, make_pipeline, FeatureUnion
from sklearn.tree import plot_tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import make_column_selector as selector, ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
import pickle
from sklearn.metrics import fbeta_score
import winsound
from sklearn.linear_model import LinearRegression
from sklearn import tree, preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, plot_confusion_matrix, recall_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_curve, auc, f1_score, make_scorer, recall_score
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


### Get Live Games Boxscores

st.title('The Parlay Companion 1.0')

# get data
player_boxes = pd.read_csv('data/player/aggregates/Trad&Adv_box_scores_GameView.csv')

# get all players from this year
this_season_players = player_boxes[player_boxes['trad_season'] == 2022]
ts_players = this_season_players['trad_player'].unique()
ts_teams = this_season_players['trad_team'].unique()
st.sidebar.title('Select Team')
teams= st.sidebar.multiselect('Select Teams', ts_teams)

# get players on these teams
ts_players = this_season_players[this_season_players['trad_team'].isin(teams)]['trad_player'].unique()


st.sidebar.title('Select Players')
players = st.sidebar.multiselect('Select Players', ts_players)


# Get Games Today
nba_scoreboard = 'https://www.nba.com/games'
nba_scoreboard = requests.get(nba_scoreboard)
nba_scoreboard = BeautifulSoup(nba_scoreboard.content, 'html.parser')
# get all links
container = nba_scoreboard.find('div', class_ = 'GamesView_gameCardsContainer__c_9fB')
links = container.find_all('a')
# get hrefs for each link
hrefs = []
for link in links:
    hrefs.append(link.get('href'))

# keep all boxscore links
boxscore_links = []
for href in hrefs:
    if 'box' in href:
        boxscore_links.append(href)

boxes = pd.DataFrame(boxscore_links, columns = ['boxscore_link'])
boxes['boxscore_link'] = 'https://www.nba.com' + boxes['boxscore_link']
boxes['game'] = boxes['boxscore_link'].str.split('/').str[4]
boxes['away_team'] = boxes['game'].str.split('-').str[0]
boxes['home_team'] = boxes['game'].str.split('-').str[2]
boxes = boxes[['away_team', 'home_team', 'boxscore_link']]
st.write(boxes)

def isBrowserAlive(driver):
   try:
      driver.current_url
      # or driver.title
      return True
   except:
      return False

driver = None
if driver == None:
    driver = webdriver.Chrome()
    driver.minimize_window()

def get_nba_boxscore(url):

    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # get container
    #container = soup.find('div', class_ = 'MaxWidthContainer_mwc__ID5AG')
    # get all tables
    tables = soup.find_all('table')
    # open first table
    t1 = pd.read_html(str(tables[0]))[0]
    t1['Player'] = t1['PLAYER'].apply(lambda x: x.split('.')[0][:-1])
    # min to str
    t1['MIN'] = t1['MIN'].astype(str)
    # drop rows if string of MIN includes DNP
    t1 = t1[~t1['MIN'].str.contains('DNP')]
    cols = ['Player', 'MIN', 'PTS', 'FGM', 'FGA', 'PF', 'REB', 'AST','STL', '+/-']
    t1 = t1[cols]

    t2 = pd.read_html(str(tables[1]))[0]
    t2['Player'] = t2['PLAYER'].apply(lambda x: x.split('.')[0][:-1])
    # min to str
    t2['MIN'] = t2['MIN'].astype(str)
    # drop rows if string of MIN includes DNP
    t2 = t2[~t2['MIN'].str.contains('DNP')]
    t2 = t2[cols]

    # append t1 and t2
    t1['Team'] = 'Home'
    t2['Team'] = 'Away'
    t3 = t1.append(t2)
    

    return t3

# add sidebar for game selection
st.sidebar.title('NBA Game Selection')
games = st.sidebar.multiselect('Select Game', boxes['home_team'])

# get boxscore for selected games


all_boxes = pd.DataFrame()
for game in games:
    # check driver
    if isBrowserAlive(driver) == False:
        driver = webdriver.Chrome()
        driver.minimize_window()
    box = boxes[boxes['home_team'] == game]
    box_link = box['boxscore_link'].values[0]
    box_score = get_nba_boxscore(box_link)
    all_boxes = all_boxes.append(box_score)


# close driver
driver.close()



st.subheader('Player Stats')
st.write(all_boxes[all_boxes['Player'].isin(players)])

# add refresh button
refresh = st.sidebar.button('Refresh')
if refresh:
    driver = None
    if driver == None:
        driver = webdriver.Chrome()
        driver.minimize_window()
    for game in games:
        box = boxes[boxes['home_team'] == game]
        box_link = box['boxscore_link'].values[0]
        box_score = get_nba_boxscore(box_link)
        all_boxes = all_boxes.append(box_score)

    st.sidebar.write('Refreshed as of {}'.format(datetime.datetime.now()))


