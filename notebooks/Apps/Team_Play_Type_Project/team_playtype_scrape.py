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
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')


def scrape_team_playtype_data(playtype, offense_or_defense):
    if playtype == 'isolation':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/isolation'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/isolation?TypeGrouping=defensive'
    elif playtype == 'postup':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/playtype-post-up'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/playtype-post-up?TypeGrouping=defensive'
    elif playtype == 'prb':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/ball-handler'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/ball-handler?TypeGrouping=defensive'
    elif playtype == 'spotup':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/spot-up'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/spot-up?TypeGrouping=defensive'
    elif playtype == 'handoff':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/hand-off'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/hand-off?TypeGrouping=defensive'
    elif playtype == 'cut':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/cut'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/cut?TypeGrouping=defensive'
    elif playtype == 'offscreen':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/off-screen'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/off-screen?TypeGrouping=defensive'
    elif playtype == 'transition':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/transition'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/transition?TypeGrouping=defensive'
    elif playtype == 'pnr':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/roll-man'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/roll-man?TypeGrouping=defensive'
    elif playtype == 'putbacks':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/putbacks'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/putbacks?TypeGrouping=defensive'
    elif playtype == 'misc':
        if offense_or_defense == 'offense':
            url = 'https://www.nba.com/stats/teams/misc'
        elif offense_or_defense == 'defense':
            url = 'https://www.nba.com/stats/teams/misc?TypeGrouping=defensive'

    driver = None
    if driver is None:
        driver = webdriver.Chrome()
        # minimize
        driver.minimize_window()
    driver.get(url)
    time.sleep(5)
    src = driver.page_source
    parser = BeautifulSoup(src, 'lxml')
    table = parser.find("div", attrs = {"class":"Crom_base__f0niE"})
    headers = table.findAll('th')
    headerlist = [h.text.strip() for h in headers[0:]] 
    row_names = table.findAll('a')                          
    row_list = [b.text.strip() for b in row_names[0:]] 
    rows = table.findAll('tr')[0:]
    player_stats = [[td.getText().strip() for td in rows[i].findAll('td')[0:]] for i in range(len(rows))]
    tot_cols = len(player_stats[1])                           #set the length to ignore hidden columns
    headerlist = headerlist[:tot_cols] 
    stats = pd.DataFrame(player_stats, columns = headerlist)
    # close driver
    driver.close()

    return stats


today = datetime.date.today()
today = today.strftime('%Y-%m-%d')

files = os.listdir('data/team/Playtypes/defensive_playtypes/')
files = [f for f in files if f.endswith('.csv')]
# drop csv extension
files = [f[:-4] for f in files]

if today in files:
    print('Already scraped today')
else:
    playtype_list = ['isolation', 'postup', 'prb', 'pnr', 'spotup', 'handoff', 'cut', 'offscreen', 'transition', 'putbacks', 'misc']
    offense_or_defense_list = ['offense', 'defense']

    for playtype in playtype_list:
        for offense_or_defense in offense_or_defense_list:
            df = scrape_team_playtype_data(playtype, offense_or_defense)
            df.to_csv('data/team/Playtypes/' + playtype + '_' + offense_or_defense + today + '.csv', index = False)

    files = os.listdir('data/team/Playtypes')
    off_files = [f for f in files if 'offense' in f]
    off_files = [f for f in off_files if today in f]
    def_files = [f for f in files if 'defense' in f]
    def_files = [f for f in def_files if today in f]


    # make master df of all playtypes
    df = pd.DataFrame()
    for file in off_files:
        data = pd.read_csv('data/team/Playtypes/' + file)
        data['play_type'] = file.split('_')[0]
        df = df.append(data)

    df.to_csv('data/team/Playtypes/offensive_playtypes/'+ today + '.csv', index = False)

    # defensive
    df = pd.DataFrame()
    for file in def_files:
        data = pd.read_csv('data/team/Playtypes/' + file)
        data['play_type'] = file.split('_')[0]
        df = df.append(data)

    df.to_csv('data/team/Playtypes/defensive_playtypes/'+ today + '.csv', index = False)

print('Job Done')