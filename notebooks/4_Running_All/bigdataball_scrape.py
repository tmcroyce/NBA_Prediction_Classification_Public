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

# Check if updating is necessary
check_data = pd.read_csv('data/team/aggregates/bigdataball_team_boxes.csv')

# check last row of DATE
last_date = check_data['DATE'].iloc[-1]
print(f' Last date uploaded: {last_date}')
today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)
yesterday = yesterday.strftime('%m/%d/%Y')
print(f'Yesterday was: {yesterday}')


if last_date != yesterday:
    # if no driver is open, open one
    driver = None

    def check_and_open_driver(driver):
    # if driver is not open
        if driver == None:
            driver = webdriver.Chrome()
            # minimize
            driver.minimize_window()
        return driver

    driver = check_and_open_driver(driver)
    url = 'https://www.bigdataball.com/my-account/'
    driver.get(url)

    user_nm = os.environ.get('PRIMARY_EMAIL')

    # add user name
    username = '/html/body/div/div/div/div/article/div/div/div/form/p[1]/input'
    driver.find_element_by_xpath(username).send_keys(user_nm)

    passw = os.environ.get('COMMON_PWORD')

    pword = '/html/body/div/div/div/div/article/div/div/div/form/p[2]/span/input'
    driver.find_element_by_xpath(pword).send_keys(passw)

    # click login
    login = '/html/body/div/div/div/div/article/div/div/div/form/p[3]/button'
    driver.find_element_by_xpath(login).click()

    url = 'https://www.bigdataball.com/nba-stats-central/'

    driver.get(url)

    # wait 5 seconds
    time.sleep(3)
    # find div with class 'files no-breadcrumb'
    files = driver.find_element_by_class_name('list-container')
    # get all html in div
    files_html = files.get_attribute('innerHTML')
    # get links from html
    soup = BeautifulSoup(files_html, 'html.parser')
    links = soup.find_all('a')
    # get href from links
    hrefs = [link.get('href') for link in links]
    # click each link
    for href in hrefs:
        # click link
        try:
            driver.get(href)

        except: 
            print('error (two errors expected)')
            continue

    # get yesterdays date
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # put in month-day-year format
    yesterday = yesterday.strftime('%m-%d-%Y')
    yesterday
    file_name = 'C:\\Users\\Travis\\Downloads\\' + yesterday + '-nba-season-team-feed.xlsx'

    updated_df = pd.read_excel(file_name)


    ### Add Columns
    # open abbrev_interpretation
    abbrev_interpretation = pd.read_csv('data/team/bigdataball/Abbreviation_Interpreter.csv')
    abbrev_interpretation.head(3)

    def get_abbrev(team):
        abbrev = abbrev_interpretation.loc[abbrev_interpretation['SHORT NAME'] == team, 'INITIALS'].values[0]
        return abbrev

    updated_df['Team_Abrev'] = updated_df['TEAM'].apply(get_abbrev)

    def get_nba_abbrev(team):
        abbrev = abbrev_interpretation.loc[abbrev_interpretation['SHORT NAME'] == team, 'NBA_NAME'].values[0]
        return abbrev

    updated_df['Nba_com_team_Abbrev'] = updated_df['TEAM'].apply(get_nba_abbrev)

    def get_opp_abbrev(team, gameid):
        opp = updated_df.loc[(updated_df['GAME-ID'] == gameid) & (updated_df['TEAM'] != team), 'Team_Abrev'].values[0]
        return opp

    updated_df['Opp_Abbrev'] = updated_df.apply(lambda x: get_opp_abbrev(x['TEAM'], x['GAME-ID']), axis=1)

    def get_nba_opp_abbrev(team):
        abbrev = abbrev_interpretation.loc[abbrev_interpretation['INITIALS'] == team, 'NBA_NAME'].values[0]
        return abbrev

    updated_df['Nba_com_team_2_abbrev'] = updated_df.apply(lambda x: get_nba_opp_abbrev(x['Opp_Abbrev']), axis=1)

    updated_df['Date_underscore'] = updated_df['DATE'].astype(str).str.replace('/', '_')
    updated_df['HomeTeam'] = np.where(updated_df['VENUE'] == 'H', updated_df['Nba_com_team_Abbrev'], updated_df['Nba_com_team_2_abbrev'])
    updated_df['AwayTeam'] = np.where(updated_df['VENUE'] == 'R', updated_df['Nba_com_team_Abbrev'], updated_df['Nba_com_team_2_abbrev'])
    updated_df['Matchup_GameDate'] = updated_df['AwayTeam'] + ' @ ' + updated_df['HomeTeam'] + '_' + updated_df['Date_underscore']

    # save
    updated_df.to_csv('data/team/aggregates/bigdataball_team_boxes.csv', index=False)

    # close driver
    driver.close()

    print('2 errors are expected & do not matter. All Done!')

else:
    print("Already up to date")