import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import sqlite3
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests   
import shutil      
import datetime
from scipy.stats import norm
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
import os
import winsound
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')
import warnings
warnings.filterwarnings('ignore')
from selenium.common.exceptions import WebDriverException
import re

driver = webdriver.Chrome()
# minimize
driver.minimize_window()
url = 'https://www.rotowire.com/basketball/nba-lineups.php'


driver.get(url)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# find div class = 'lineups'. This is the div that contains all the lineups.
# The lineups are split by 'lineup is-nba' class

tot_lineup_df = pd.DataFrame()

lineups = soup.find_all('div', class_='lineup__box')
# get rid of last 2 lineups
lineups = lineups[:-2]

for lineup in lineups:
    # wait for page to load
    time.sleep(2)

    away_team = lineup.find('ul', class_= 'lineup__list is-visit').text.strip().replace('\n', ' ')
    home_team = lineup.find('ul', class_= 'lineup__list is-home').text.strip().replace('\n', ' ')

         # split into three lists by 'Expected Lineup'
    away_team_name = lineup.find('a', class_='lineup__team is-visit').text.strip()
    home_team_name = lineup.find('a', class_='lineup__team is-home').text.strip()

    away_team_pg = away_team[away_team.find('PG')+3:away_team.find('SG')-1]
    away_team_sg = away_team[away_team.find('SG')+3:away_team.find('SF')-1]
    away_team_sf = away_team[away_team.find('SF')+3:away_team.find('PF')-1]
    away_team_pf = away_team[away_team.find('PF')+3:away_team.find(' C ')]
    away_team_c = away_team[away_team.find(' C ')+2:away_team.find('Pro')-1]

    home_team_pg = home_team[home_team.find('PG')+3:home_team.find('SG')-1]
    home_team_sg = home_team[home_team.find('SG')+3:home_team.find('SF')-1]
    home_team_sf = home_team[home_team.find('SF')+3:home_team.find('PF')-1]
    home_team_pf = home_team[home_team.find('PF')+3:home_team.find(' C ')]
    home_team_c = home_team[home_team.find(' C ')+2:home_team.find('Pro')-1]

    away_status = away_team[0:away_team.find('PG')-2]
    home_status = home_team[0:home_team.find('PG')-2]

    # create dataframe
    lineup_df = pd.DataFrame({'Away_Team': away_team_name, 'Home_Team': home_team_name, 'Away_PG': away_team_pg, 'Away_SG': away_team_sg, 'Away_SF': away_team_sf, 'Away_PF': away_team_pf, 'Away_C': away_team_c, 'Home_PG': home_team_pg, 'Home_SG': home_team_sg, 'Home_SF': home_team_sf, 'Home_PF': home_team_pf, 'Home_C': home_team_c, 'Away_Status': away_status, 'Home_Status': home_status}, index=[0])

    tot_lineup_df = pd.concat([tot_lineup_df, lineup_df], axis=0)

tot_lineup_df = tot_lineup_df.reset_index(drop=True)

today = datetime.datetime.now().strftime('%Y-%m-%d')

tot_lineup_df.to_csv('data/team/aggregates/daily_updates/starting_lineups_{}.csv'.format(today), index=False)

driver.close()