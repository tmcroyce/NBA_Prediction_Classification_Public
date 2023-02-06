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

today = datetime.date.today()
today = today.strftime('%Y-%m-%d')

# check if today's dl already exists
if os.path.exists('data/team/aggregates/daily_updates/defense_vs_position' + str(today) + '.csv'):
    pass
else:
    # Log in to Rotowire
    driver = None
    if driver is None:
        driver = webdriver.Chrome()
        # minimize
        driver.minimize_window()
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

    # wait 3 seconds for page to load
    time.sleep(3)

    pg_url = 'https://www.rotowire.com/daily/nba/defense-vspos.php'
    driver.get(pg_url)

    # download the csv
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # wait 2 seconds
    time.sleep(3)

    # csv_link = soup.find('button', class_ = 'export-button is-csv hovering')
    # csv_link.click()

    csv_xpath = '//*[@id="NBAPlayers"]/div[3]/div[2]/button[2]'
    csv_link = driver.find_element_by_xpath(csv_xpath)
    csv_link.click()
    # close browser
    driver.close()
    d_vs_position_files = pd.DataFrame()

    # check files in folder that match
    folder = os.listdir('C:\\Users\\Travis\\Downloads')
    for file in folder:
        if file.startswith('rotowire-NBA-defense-vs-pos'):
            # add to dataframe
            d_vs_position_files = d_vs_position_files.append({'file_name': file}, ignore_index = True)


    # identify file with highest number
    d_vs_position_files['file_number'] = d_vs_position_files['file_name'].str[-6:-5]
    # if file_number is not a number, make it 0
    d_vs_position_files['file_number'] = d_vs_position_files['file_number'].apply(lambda x: 0 if x.isnumeric() == False else x)
    d_vs_position_files['file_number'] = d_vs_position_files['file_number'].astype(int)
    # select file with highest number
    newest_file = d_vs_position_files[d_vs_position_files['file_number'] == d_vs_position_files['file_number'].max()]
    newest_file = newest_file['file_name'].values
    # read file
    d_vs_position = pd.read_csv('C:\\Users\\Travis\\Downloads\\' + newest_file[0])

    d_vs_position.to_csv('data/team/aggregates/daily_updates/defense_vs_position' + str(today) + '.csv', index = False)