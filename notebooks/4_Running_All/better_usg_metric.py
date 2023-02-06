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

today = datetime.datetime.today().strftime('%Y-%m-%d')
# load updated player data
trad_player_data = pd.read_csv('data/player/aggregates/Trad&Adv_box_scores_GameView.csv')
# fix date so it is sortable
trad_player_data['trad_game date'] = pd.to_datetime(trad_player_data['trad_game date'])
# convert to just date
trad_player_data['trad_game date'] = trad_player_data['trad_game date'].dt.date
# to date
#trad_player_data['trad_game date'] = trad_player_data['trad_game date'].dt.strftime('%Y-%m-%d')
# sort by date
trad_player_data = trad_player_data.sort_values(by = ['trad_game date'], ascending = False)
# drop nan for trad_player
trad_player_data = trad_player_data.dropna(subset = ['trad_player'])
trad_player_data.head()
# add team totals for each game for points, rebounds, assists, turnovers, steals, free throws attempted, and shots attempted
trad_player_data = trad_player_data.merge(trad_player_data.groupby(['trad_game date', 'trad_team'])['trad_pts', 'trad_reb', 'trad_ast', 'trad_tov', 'trad_stl', 'trad_fta', 'trad_fga'].sum().reset_index().rename(columns={'trad_pts': 'trad_team_pts', 'trad_reb': 'trad_team_reb', 'trad_ast': 'trad_team_ast', 'trad_tov': 'trad_team_tov', 'trad_stl': 'trad_team_stl', 'trad_fta': 'trad_team_fta', 'trad_fga': 'trad_team_fga'}), how='left', left_on=['trad_game date', 'trad_team'], right_on=['trad_game date', 'trad_team'])

trad_player_data.head()
# add player_points_percentage, player_rebounds_percentage, player_assists_percentage, player_turnovers_percentage, player_steals_percentage, player_free_throws_percentage, and player_field_goal_percentage
trad_player_data['player_points_percentage'] = trad_player_data['trad_pts'] / trad_player_data['trad_team_pts']
trad_player_data['player_rebounds_percentage'] = trad_player_data['trad_reb'] / trad_player_data['trad_team_reb']
trad_player_data['player_assists_percentage'] = trad_player_data['trad_ast'] / trad_player_data['trad_team_ast']
trad_player_data['player_turnovers_percentage'] = trad_player_data['trad_tov'] / trad_player_data['trad_team_tov']
trad_player_data['player_steals_percentage'] = trad_player_data['trad_stl'] / trad_player_data['trad_team_stl']
trad_player_data['player_free_throws_attempted_percentage'] = trad_player_data['trad_fta'] / trad_player_data['trad_team_fta']
trad_player_data['player_field_goal_attepted_percentage'] = trad_player_data['trad_fga'] / trad_player_data['trad_team_fga']

# add per_min for each of the above
trad_player_data['player_points_percentage_per_min'] = trad_player_data['player_points_percentage'] / trad_player_data['trad_min'] * 100
trad_player_data['player_rebounds_percentage_per_min'] = trad_player_data['player_rebounds_percentage'] / trad_player_data['trad_min'] * 100
trad_player_data['player_assists_percentage_per_min'] = trad_player_data['player_assists_percentage'] / trad_player_data['trad_min'] * 100
trad_player_data['player_turnovers_percentage_per_min'] = trad_player_data['player_turnovers_percentage'] / trad_player_data['trad_min'] * 100
trad_player_data['player_steals_percentage_per_min'] = trad_player_data['player_steals_percentage'] / trad_player_data['trad_min'] * 100



# fix nans with 0
trad_player_data = trad_player_data.fillna(0)
# get this season averages
tpd22 = trad_player_data[trad_player_data['trad_game date'] >= datetime.date(2022, 10, 1)]
# get averages
tpd22_avg = tpd22.groupby(['trad_player'])['trad_pts', 'trad_reb', 'trad_ast', 'trad_tov', 'trad_stl', 'trad_fta', 'trad_fga', 'player_points_percentage', 'player_rebounds_percentage', 'player_assists_percentage', 'player_turnovers_percentage', 'player_steals_percentage', 'player_free_throws_attempted_percentage', 'player_field_goal_attepted_percentage', 'player_points_percentage_per_min', 'player_rebounds_percentage_per_min', 'player_assists_percentage_per_min', 'player_turnovers_percentage_per_min', 'player_steals_percentage_per_min'].mean().reset_index()

# rank by player_points_percentage_per_min
tpd22_avg = tpd22_avg.sort_values(by = ['player_field_goal_attepted_percentage'], ascending = False).round(2)

# keep just new columns
current_usg_metrics = tpd22_avg[['trad_player', 'player_points_percentage', 'player_rebounds_percentage', 
                                'player_assists_percentage', 'player_turnovers_percentage', 'player_steals_percentage', 
                                'player_free_throws_attempted_percentage', 'player_field_goal_attepted_percentage', 
                                'player_points_percentage_per_min', 'player_rebounds_percentage_per_min', 'player_assists_percentage_per_min', 
                                'player_turnovers_percentage_per_min', 'player_steals_percentage_per_min']]

# add percentiles for each metric
current_usg_metrics['player_points_percentage_percentile'] = current_usg_metrics['player_points_percentage'].rank(pct=True)
current_usg_metrics['player_rebounds_percentage_percentile'] = current_usg_metrics['player_rebounds_percentage'].rank(pct=True)
current_usg_metrics['player_assists_percentage_percentile'] = current_usg_metrics['player_assists_percentage'].rank(pct=True)
current_usg_metrics['player_turnovers_percentage_percentile'] = current_usg_metrics['player_turnovers_percentage'].rank(pct=True)
current_usg_metrics['player_steals_percentage_percentile'] = current_usg_metrics['player_steals_percentage'].rank(pct=True)
current_usg_metrics['player_free_throws_attempted_percentage_percentile'] = current_usg_metrics['player_free_throws_attempted_percentage'].rank(pct=True)
current_usg_metrics['player_field_goal_attepted_percentage_percentile'] = current_usg_metrics['player_field_goal_attepted_percentage'].rank(pct=True)
current_usg_metrics['player_points_percentage_per_min_percentile'] = current_usg_metrics['player_points_percentage_per_min'].rank(pct=True)
current_usg_metrics['player_rebounds_percentage_per_min_percentile'] = current_usg_metrics['player_rebounds_percentage_per_min'].rank(pct=True)
current_usg_metrics['player_assists_percentage_per_min_percentile'] = current_usg_metrics['player_assists_percentage_per_min'].rank(pct=True)
current_usg_metrics['player_turnovers_percentage_per_min_percentile'] = current_usg_metrics['player_turnovers_percentage_per_min'].rank(pct=True)
current_usg_metrics['player_steals_percentage_per_min_percentile'] = current_usg_metrics['player_steals_percentage_per_min'].rank(pct=True)
current_usg_metrics = current_usg_metrics.sort_values(by = ['player_points_percentage_percentile'], ascending = False).round(2)
current_usg_metrics.head(10)
# save as current usg metrics

current_usg_metrics.to_csv('data/player/aggregates/current_usg_metrics_'+ today +'.csv', index = False)