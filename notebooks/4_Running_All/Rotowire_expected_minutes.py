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
# Log in to Rotowire
driver = webdriver.Chrome()
login_url = 'https://www.rotowire.com/users/login.php'
username = os.environ.get('rot_login')
password = os.environ.get('COMMON_PWORD')

# go to login page
driver.get(login_url)
# enter username
username_field = driver.find_element_by_name('username')
username_field.send_keys(username)
# enter password
password_field = driver.find_element_by_name('password')
password_field.send_keys(password)
# click login button
login_xpath = '/html/body/div[1]/div/main/div/div[1]/form/button'

# click login button
login_button = driver.find_element_by_xpath(login_xpath)
login_button.click()


# Go to page
url = 'https://www.rotowire.com/basketball/nba-lineups.php'
driver.get(url)
# Same as above, but for all teams playing today
team_minutes = driver.find_elements_by_class_name(('see-proj-minutes'))

minutes_today = pd.DataFrame()

for teamz in team_minutes:
    teamz.click()
    time.sleep(2)
    # get all minutes
    minutes = driver.find_elements_by_class_name('minutes-meter__proj')
    minutes = [x.text for x in minutes]
    # get all names
    names = driver.find_elements_by_class_name('lineups-viz__player-name')
    names = [x.text for x in names]
    # if minutes is longer than names, drop the last element in minutes
    if len(minutes) > len(names):
        minutes = minutes[:-1]
    # make df
    df = pd.DataFrame({'name':names, 'minutes':minutes})
    df['minutes'] = df['minutes'].astype(float)

    # if last 3 digits in name are OUT, then OUT = 1
    df['OUT'] = df['name'].apply(lambda x: 1 if x[-3:] == 'OUT' else 0)
    df['GTD'] = df['name'].apply(lambda x: 1 if x[-3:] == 'GTD' else 0)

    # remove OUT and GTD from name
    df['name'].replace(to_replace='OUT', value='', regex=True, inplace=True)
    df['name'].replace(to_replace='GTD', value='', regex=True, inplace=True)
    df['name'].replace(to_replace='\n', value='', regex=True, inplace=True)

    team = driver.find_element_by_class_name('lineups-viz').text
    # get text to "Projected Minutes"
    team = team.split('Projected Minutes')[0]
    # get text
    team = team.replace('\n', '')
    df['team'] = team

    minutes_today = minutes_today.append(df)
    # click close button
    driver.find_element_by_class_name('lineups-viz__close').click()


minutes_today

today = datetime.datetime.today().strftime('%Y-%m-%d')
minutes_today.to_csv('data/team/aggregates/daily_updates/player_minutes_projection_{}.csv'.format(today), index=False)
# close driver
driver.close()

print('Job Done')