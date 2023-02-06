import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import random
import shutil
import plotly
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')
import datetime
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
from scipy.stats import norm
import winsound
import warnings
warnings.filterwarnings('ignore')
from selenium.common.exceptions import WebDriverException
import pickle

# DL Missing Data

os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')

os.system('python player_box_scores.py')

os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')

os.system('python team_box_score_update.py')
### 2) Get Yesterday's Games and Odds
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')

# Get Yesterday's Games
os.system('python bigdataball_scrape.py')

### 3) Update Features of Yesterday's Games

os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')
os.system('python update_all_features_v2.py')


today = datetime.datetime.today().strftime('%Y-%m-%d')

### 4) Get Today's Games and Odds
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')

# Use draftkings scrape
url = 'https://sportsbook.draftkings.com/leagues/basketball/nba'
driver = webdriver.Chrome()
driver.get(url)

# find table (class sportsbook-table)
table = driver.find_element_by_class_name('sportsbook-table')
# get all html in table
table_html = table.get_attribute('innerHTML')
# convert to soup
soup = BeautifulSoup(table_html, 'html.parser')
# find all rows
rows = soup.find_all('tr')
# find all headers
headers = table.find_element_by_class_name('sportsbook-table__head')
headers = headers.find_elements_by_tag_name('th')
headers = [header.text for header in headers]

# find all rows
rows = table.find_elements_by_tag_name('tr')
# get all html in each row
rows_html = [row.get_attribute('innerHTML') for row in rows]
# convert to soup
rows_soup = [BeautifulSoup(row, 'html.parser') for row in rows_html]
# find all cells in each row
rows_cells = [row.find_all('td') for row in rows_soup]
# drop first row (headers)
rows_cells = rows_cells[1:]
# get text from each cell
rows_cells_text = [[cell.text for cell in row] for row in rows_cells]
names = table.find_elements_by_class_name('event-cell__name')
names = [name.text for name in names]

# add names to rows_cells_text
for i in range(len(rows_cells_text)):
    rows_cells_text[i].insert(0, names[i])

# convert to dataframe
rows_cells_text
df = pd.DataFrame(rows_cells_text, columns=headers)
df['spread_odds'] = df['SPREAD'].str[-4:]
df['SPREAD'] = df['SPREAD'].str[:-4]
df['total_odds'] = df['TOTAL'].str[-4:]
df['TOTAL'] = df['TOTAL'].str[:-4]

df.to_csv('data/team/aggregates/daily_updates/draftkings' + str(today) + '.csv', index=False)

print('Draftkings scrape complete')

### Create DF with today's games and odds
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')

print('Creating todays games df...')

os.system('python todays_games_df_Creation.py')

os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')

today_df = pd.read_csv('data/team/aggregates/daily_updates/today_df_features__' + str(today) + '.csv')

### Get Expected Minutes (Rotowire)
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')

os.system('python Rotowire_expected_minutes.py')

# load in rotowire data
today = datetime.datetime.today().strftime('%Y-%m-%d')
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')

expected_minutes = pd.read_csv('data/team/aggregates/daily_updates/player_minutes_projection_{}.csv'.format(today))
expected_minutes.head()
# get starters
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\4_Running_All')

os.system('python Rotowire_players_playing_today.py')

### Player Metric Additions
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')

season_averages = pd.read_csv('data/player/aggregates_of_aggregates/trad_season_averages_imputed.csv')
season_averages.drop_duplicates(inplace=True)
season_averages.head()
season_averages = season_averages[season_averages['trad_season'] == 2021]
# add player metrics from season averages to expected minutes
expected_minutes = expected_minutes.merge(season_averages, left_on= 'name', right_on='trad_player', how='left')
expected_minutes = expected_minutes.drop_duplicates(subset= ['name'])
expected_minutes.head()


expected_minutes['PM_TOV_Ratio_flipped'] = 1 - expected_minutes['PM_TOV_Rato']
expected_minutes['PM_Iso_Defense_flipped'] = 1 - expected_minutes['PM_Iso_Defense']
expected_minutes['PM_defensive_FG_flipped'] = 1 - expected_minutes['PM_defensive_FG']

expected_minutes['PM_Aggregate_Offensive_Rating'] = ((expected_minutes['PM_True_Shooting'] * .1) +
                                        (expected_minutes['PM_Open_3'] * .1) +
                                        (expected_minutes['PM_Ball_Handler'] * .1) +
                                        (expected_minutes['PM_Iso'] * .15) +
                                        (expected_minutes['PM_Shot_Creation'] * .1) +
                                        (expected_minutes['PM_Pressure_Scoring'] * .05) +
                                        (expected_minutes['PM_Driving_Offense'] * .05) +
                                        (expected_minutes['PM_Passing'] * .1) +
                                        (expected_minutes['PM_Catch_Shoot'] * .15) +
                                        (expected_minutes['PM_TOV_Ratio_flipped'] * .1))


expected_minutes['PM_Aggregate_Defensive_Rating'] = ( (((expected_minutes['PM_matchup_difficulty'] * .15) /100) + 
                                        (expected_minutes['PM_Iso_Defense_flipped'] * .1) + 
                                        (expected_minutes['PM_loose_balls_recovered'] * .1) +
                                        (expected_minutes['PM_speed_score'] * .1) +
                                        (expected_minutes['PM_Adv_Rebounding'] * .0375) +
                                        (expected_minutes['PM_Trad_Rebounding'] * .0375) +
                                        (expected_minutes['PM_offensive_boxouts'] * .0375) +
                                        (expected_minutes['PM_defensive_boxouts'] * .0375) +
                                        (expected_minutes['PM_coverage_area'] * .2) +
                                        (expected_minutes['PM_defensive_FG_flipped'] * .2)))

expected_minutes['PM_Player_Metric'] = expected_minutes['PM_Aggregate_Offensive_Rating'] + expected_minutes['PM_Aggregate_Defensive_Rating']
keep_cols = ['name', 'minutes', 'OUT', 'GTD', 'team_x', 'PM_Aggregate_Offensive_Rating', 
                'PM_Aggregate_Defensive_Rating', 'PM_Player_Metric']

expected_minutes2 = expected_minutes[keep_cols]


# TODO: Impute the rookies scores
# Likely, will have to encorporate size, pick number, position, and stats so far this year (wait 20 games?)
# team dictionary (names to abbreviations)
team_dict = {'Hawks':'ATL',
                'Nets':'BKN',
                'Celtics':'BOS',
                'Hornets':'CHA',
                'Bulls':'CHI',
                'Cavaliers':'CLE',
                'Mavericks':'DAL',
                'Nuggets':'DEN',
                'Pistons':'DET',
                'Warriors':'GSW',
                'Rockets':'HOU',
                'Pacers':'IND',
                'Clippers':'LAC',
                'Lakers':'LAL',
                'Grizzlies':'MEM',
                'Heat':'MIA',
                'Bucks':'MIL',
                'Timberwolves':'MIN',
                'Pelicans':'NOP',
                'Knicks':'NYK',
                'Thunder':'OKC',
                'Magic':'ORL',
                '76ers':'PHI',
                'Suns':'PHX',
                'Trail Blazers':'POR',
                'Kings':'SAC',
                'Spurs':'SAS',
                'Raptors':'TOR',
                'Jazz':'UTA',
                'Wizards':'WAS'}


expected_minutes2['trad_team'] = expected_minutes2['team_x'].map(team_dict)

## All Together Now
#### Add Team Player Metrics

def get_net_score(team, matchup, cutoff):
    team_data = expected_minutes2[expected_minutes2['trad_team'] == team]
    team_data = team_data[team_data['minutes'] > 0]
    team_data = team_data.sort_values(by='PM_Player_Metric', ascending=False)
    team_data = team_data[:cutoff]
    # sum PM_Player_Metric
    team_score = team_data['PM_Player_Metric'].sum()

    matchup_data = expected_minutes2[expected_minutes2['trad_team'] == matchup]
    matchup_data = matchup_data[matchup_data['minutes'] > 0]
    matchup_data = matchup_data.sort_values(by='PM_Player_Metric', ascending=False)
    matchup_data = matchup_data[:cutoff]
    # sum PM_Player_Metric
    matchup_score = matchup_data['PM_Player_Metric'].sum()

    net_score = team_score - matchup_score
    return net_score

print('calculating net scores...')

today_df['net_score_top_4'] = today_df.apply(lambda x: get_net_score(x['trad_team'], x['matchup'], 4), axis=1)
today_df['net_score_top_5'] = today_df.apply(lambda x: get_net_score(x['trad_team'], x['matchup'], 5), axis=1)
today_df['net_score_top_6'] = today_df.apply(lambda x: get_net_score(x['trad_team'], x['matchup'], 6), axis=1)
today_df['net_score_top_7'] = today_df.apply(lambda x: get_net_score(x['trad_team'], x['matchup'], 7), axis=1)
today_df['net_score_top_8'] = today_df.apply(lambda x: get_net_score(x['trad_team'], x['matchup'], 8), axis=1)

# add predicted_winner
today_df['top_4_predicted_winner'] = np.where(today_df['net_score_top_4'] > 0, 1, 0)
today_df['top_5_predicted_winner'] = np.where(today_df['net_score_top_5'] > 0, 1, 0)
today_df['top_6_predicted_winner'] = np.where(today_df['net_score_top_6'] > 0, 1, 0)
today_df['top_7_predicted_winner'] = np.where(today_df['net_score_top_7'] > 0, 1, 0)
today_df['top_8_predicted_winner'] = np.where(today_df['net_score_top_8'] > 0, 1, 0)


# check pre-processed data
ppd = pd.read_csv('data/team/aggregates/Pre-processed_data.csv')

# check columns in ppd that are not in today_df
ppd_cols = ppd.columns
today_df_cols = today_df.columns
ppd_cols.difference(today_df_cols)

today_df['CLOSING\nODDS'] = today_df['MONEYLINE']
today_df['OPENING ODDS'] = today_df['MONEYLINE']
today_df['CLOSING SPREAD'] = today_df['SPREAD']
today_df['OPENING SPREAD'] = today_df['SPREAD']
today_df['CLOSING TOTAL'] = today_df['TOTAL']
today_df['OPENING TOTAL'] = today_df['TOTAL']
today_df['TEAM\nREST DAYS'] = today_df['rest_days']


today_df.to_csv('data/team/aggregates/daily_updates/today_df_'+str(today)+'.csv', index=False)
ppd_cols = ppd.columns
today_df_cols = today_df.columns
ppd_cols.difference(today_df_cols)


os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')
# load model

print('loading model...')

with open('pickle_models/pipe_1.pkl', 'rb') as f:
    model = pickle.load(f)
data = pd.read_csv('data/team/aggregates/Pre-processed_data.csv')
data.head()

data.columns.to_list()
test_cols = ['trad_season',
 't1_running_trad_pts',
 't1_running_trad_fgm',
 't1_running_trad_fga',
 't1_running_trad_fg%',
 't1_running_trad_3pm',
 't1_running_trad_3pa',
 't1_running_trad_3p%',
 't1_running_trad_ftm',
 't1_running_trad_fta',
 't1_running_trad_ft%',
 't1_running_trad_oreb',
 't1_running_trad_dreb',
 't1_running_trad_reb',
 't1_running_trad_ast',
 't1_running_trad_tov',
 't1_running_trad_stl',
 't1_running_trad_blk',
 't1_running_trad_pf',
 't1_running_trad_+/-',
 't1_running_adv_offrtg',
 't1_running_adv_defrtg',
 't1_running_adv_netrtg',
 't1_running_adv_ast%',
 't1_running_adv_ast/to',
 't1_running_adv_astratio',
 't1_running_adv_oreb%',
 't1_running_adv_dreb%',
 't1_running_adv_reb%',
 't1_running_adv_tov%',
 't1_running_adv_efg%',
 't1_running_adv_ts%',
 't1_running_adv_pace',
 't1_running_adv_pie',
 't1_running_four_efg%',
 't1_running_four_ftarate',
 't1_running_four_tov%',
 't1_running_four_oreb%',
 't1_running_four_oppefg%',
 't1_running_four_oppfta\xa0rate',
 't1_running_four_opptov%',
 't1_running_four_opporeb%',
 't1_running_misc_ptsoff\xa0to',
 't1_running_misc_2ndpts',
 't1_running_misc_fbps',
 't1_running_misc_pitp',
 't1_running_misc_opp\xa0ptsoff\xa0to',
 't1_running_misc_opp2nd\xa0pts',
 't1_running_misc_oppfbps',
 't1_running_misc_opppitp',
 't1_running_score_%fga2pt',
 't1_running_score_%fga3pt',
 't1_running_score_%pts2pt',
 't1_running_score_%pts2pt\xa0mr',
 't1_running_score_%pts3pt',
 't1_running_score_%ptsfbps',
 't1_running_score_%ptsft',
 't2_running_trad_pts',
 't2_running_trad_fgm',
 't2_running_trad_fga',
 't2_running_trad_fg%',
 't2_running_trad_3pm',
 't2_running_trad_3pa',
 't2_running_trad_3p%',
 't2_running_trad_ftm',
 't2_running_trad_fta',
 't2_running_trad_ft%',
 't2_running_trad_oreb',
 't2_running_trad_dreb',
 't2_running_trad_reb',
 't2_running_trad_ast',
 't2_running_trad_tov',
 't2_running_trad_stl',
 't2_running_trad_blk',
 't2_running_trad_pf',
 't2_running_trad_+/-',
 't2_running_adv_offrtg',
 't2_running_adv_defrtg',
 't2_running_adv_netrtg',
 't2_running_adv_ast%',
 't2_running_adv_ast/to',
 't2_running_adv_astratio',
 't2_running_adv_oreb%',
 't2_running_adv_dreb%',
 't2_running_adv_reb%',
 't2_running_adv_tov%',
 't2_running_adv_efg%',
 't2_running_adv_ts%',
 't2_running_adv_pace',
 't2_running_adv_pie',
 't2_running_four_efg%',
 't2_running_four_ftarate',
 't2_running_four_tov%',
 't2_running_four_oreb%',
 't2_running_four_oppefg%',
 't2_running_four_oppfta\xa0rate',
 't2_running_four_opptov%',
 't2_running_four_opporeb%',
 't2_running_misc_ptsoff\xa0to',
 't2_running_misc_2ndpts',
 't2_running_misc_fbps',
 't2_running_misc_pitp',
 't2_running_misc_opp\xa0ptsoff\xa0to',
 't2_running_misc_opp2nd\xa0pts',
 't2_running_misc_oppfbps',
 't2_running_misc_opppitp',
 't2_running_score_%fga2pt',
 't2_running_score_%fga3pt',
 't2_running_score_%pts2pt',
 't2_running_score_%pts2pt\xa0mr',
 't2_running_score_%pts3pt',
 't2_running_score_%ptsfbps',
 't2_running_score_%ptsft',
 'running_t1-t2_trad_pts',
 'running_t1-t2_trad_fgm',
 'running_t1-t2_trad_fga',
 'running_t1-t2_trad_fg%',
 'running_t1-t2_trad_3pm',
 'running_t1-t2_trad_3pa',
 'running_t1-t2_trad_3p%',
 'running_t1-t2_trad_ftm',
 'running_t1-t2_trad_fta',
 'running_t1-t2_trad_ft%',
 'running_t1-t2_trad_oreb',
 'running_t1-t2_trad_dreb',
 'running_t1-t2_trad_reb',
 'running_t1-t2_trad_ast',
 'running_t1-t2_trad_tov',
 'running_t1-t2_trad_stl',
 'running_t1-t2_trad_blk',
 'running_t1-t2_trad_pf',
 'running_t1-t2_trad_+/-',
 'running_t1-t2_adv_offrtg',
 'running_t1-t2_adv_defrtg',
 'running_t1-t2_adv_netrtg',
 'running_t1-t2_adv_ast%',
 'running_t1-t2_adv_ast/to',
 'running_t1-t2_adv_astratio',
 'running_t1-t2_adv_oreb%',
 'running_t1-t2_adv_dreb%',
 'running_t1-t2_adv_reb%',
 'running_t1-t2_adv_tov%',
 'running_t1-t2_adv_efg%',
 'running_t1-t2_adv_ts%',
 'running_t1-t2_adv_pace',
 'running_t1-t2_adv_pie',
 'running_t1-t2_four_efg%',
 'running_t1-t2_four_ftarate',
 'running_t1-t2_four_tov%',
 'running_t1-t2_four_oreb%',
 'running_t1-t2_four_oppefg%',
 'running_t1-t2_four_oppfta\xa0rate',
 'running_t1-t2_four_opptov%',
 'running_t1-t2_four_opporeb%',
 'running_t1-t2_misc_ptsoff\xa0to',
 'running_t1-t2_misc_2ndpts',
 'running_t1-t2_misc_fbps',
 'running_t1-t2_misc_pitp',
 'running_t1-t2_misc_opp\xa0ptsoff\xa0to',
 'running_t1-t2_misc_opp2nd\xa0pts',
 'running_t1-t2_misc_oppfbps',
 'running_t1-t2_misc_opppitp',
 'running_t1-t2_score_%fga2pt',
 'running_t1-t2_score_%fga3pt',
 'running_t1-t2_score_%pts2pt',
 'running_t1-t2_score_%pts2pt\xa0mr',
 'running_t1-t2_score_%pts3pt',
 'running_t1-t2_score_%ptsfbps',
 'running_t1-t2_score_%ptsft',
 't1_league_delta_trad_pts',
 't1_league_delta_trad_fgm',
 't1_league_delta_trad_fga',
 't1_league_delta_trad_fg%',
 't1_league_delta_trad_3pm',
 't1_league_delta_trad_3pa',
 't1_league_delta_trad_3p%',
 't1_league_delta_trad_ftm',
 't1_league_delta_trad_fta',
 't1_league_delta_trad_ft%',
 't1_league_delta_trad_oreb',
 't1_league_delta_trad_dreb',
 't1_league_delta_trad_reb',
 't1_league_delta_trad_ast',
 't1_league_delta_trad_tov',
 't1_league_delta_trad_stl',
 't1_league_delta_trad_blk',
 't1_league_delta_trad_pf',
 't1_league_delta_trad_+/-',
 't1_league_delta_adv_offrtg',
 't1_league_delta_adv_defrtg',
 't1_league_delta_adv_netrtg',
 't1_league_delta_adv_ast%',
 't1_league_delta_adv_ast/to',
 't1_league_delta_adv_astratio',
 't1_league_delta_adv_oreb%',
 't1_league_delta_adv_dreb%',
 't1_league_delta_adv_reb%',
 't1_league_delta_adv_tov%',
 't1_league_delta_adv_efg%',
 't1_league_delta_adv_ts%',
 't1_league_delta_adv_pace',
 't1_league_delta_adv_pie',
 't1_league_delta_four_efg%',
 't1_league_delta_four_ftarate',
 't1_league_delta_four_tov%',
 't1_league_delta_four_oreb%',
 't1_league_delta_four_oppefg%',
 't1_league_delta_four_oppfta\xa0rate',
 't1_league_delta_four_opptov%',
 't1_league_delta_four_opporeb%',
 't1_league_delta_misc_ptsoff\xa0to',
 't1_league_delta_misc_2ndpts',
 't1_league_delta_misc_fbps',
 't1_league_delta_misc_pitp',
 't1_league_delta_misc_opp\xa0ptsoff\xa0to',
 't1_league_delta_misc_opp2nd\xa0pts',
 't1_league_delta_misc_oppfbps',
 't1_league_delta_misc_opppitp',
 't1_league_delta_score_%fga2pt',
 't1_league_delta_score_%fga3pt',
 't1_league_delta_score_%pts2pt',
 't1_league_delta_score_%pts2pt\xa0mr',
 't1_league_delta_score_%pts3pt',
 't1_league_delta_score_%ptsfbps',
 't2_league_delta_trad_pts',
 't2_league_delta_trad_fgm',
 't2_league_delta_trad_fga',
 't2_league_delta_trad_fg%',
 't2_league_delta_trad_3pm',
 't2_league_delta_trad_3pa',
 't2_league_delta_trad_3p%',
 't2_league_delta_trad_ftm',
 't2_league_delta_trad_fta',
 't2_league_delta_trad_ft%',
 't2_league_delta_trad_oreb',
 't2_league_delta_trad_dreb',
 't2_league_delta_trad_reb',
 't2_league_delta_trad_ast',
 't2_league_delta_trad_tov',
 't2_league_delta_trad_stl',
 't2_league_delta_trad_blk',
 't2_league_delta_trad_pf',
 't2_league_delta_trad_+/-',
 't2_league_delta_adv_offrtg',
 't2_league_delta_adv_defrtg',
 't2_league_delta_adv_netrtg',
 't2_league_delta_adv_ast%',
 't2_league_delta_adv_ast/to',
 't2_league_delta_adv_astratio',
 't2_league_delta_adv_oreb%',
 't2_league_delta_adv_dreb%',
 't2_league_delta_adv_reb%',
 't2_league_delta_adv_tov%',
 't2_league_delta_adv_efg%',
 't2_league_delta_adv_ts%',
 't2_league_delta_adv_pace',
 't2_league_delta_adv_pie',
 't2_league_delta_four_efg%',
 't2_league_delta_four_ftarate',
 't2_league_delta_four_tov%',
 't2_league_delta_four_oreb%',
 't2_league_delta_four_oppefg%',
 't2_league_delta_four_oppfta\xa0rate',
 't2_league_delta_four_opptov%',
 't2_league_delta_four_opporeb%',
 't2_league_delta_misc_ptsoff\xa0to',
 't2_league_delta_misc_2ndpts',
 't2_league_delta_misc_fbps',
 't2_league_delta_misc_pitp',
 't2_league_delta_misc_opp\xa0ptsoff\xa0to',
 't2_league_delta_misc_opp2nd\xa0pts',
 't2_league_delta_misc_oppfbps',
 't2_league_delta_misc_opppitp',
 't2_league_delta_score_%fga2pt',
 't2_league_delta_score_%fga3pt',
 't2_league_delta_score_%pts2pt',
 't2_league_delta_score_%pts2pt\xa0mr',
 't2_league_delta_score_%pts3pt',
 't2_league_delta_score_%ptsfbps',
 't1_delta_minus_t2_delta_trad_pts',
 't1_delta_minus_t2_delta_trad_fgm',
 't1_delta_minus_t2_delta_trad_fga',
 't1_delta_minus_t2_delta_trad_fg%',
 't1_delta_minus_t2_delta_trad_3pm',
 't1_delta_minus_t2_delta_trad_3pa',
 't1_delta_minus_t2_delta_trad_3p%',
 't1_delta_minus_t2_delta_trad_ftm',
 't1_delta_minus_t2_delta_trad_fta',
 't1_delta_minus_t2_delta_trad_ft%',
 't1_delta_minus_t2_delta_trad_oreb',
 't1_delta_minus_t2_delta_trad_dreb',
 't1_delta_minus_t2_delta_trad_reb',
 't1_delta_minus_t2_delta_trad_ast',
 't1_delta_minus_t2_delta_trad_tov',
 't1_delta_minus_t2_delta_trad_stl',
 't1_delta_minus_t2_delta_trad_blk',
 't1_delta_minus_t2_delta_trad_pf',
 't1_delta_minus_t2_delta_trad_+/-',
 't1_delta_minus_t2_delta_adv_offrtg',
 't1_delta_minus_t2_delta_adv_defrtg',
 't1_delta_minus_t2_delta_adv_netrtg',
 't1_delta_minus_t2_delta_adv_ast%',
 't1_delta_minus_t2_delta_adv_ast/to',
 't1_delta_minus_t2_delta_adv_astratio',
 't1_delta_minus_t2_delta_adv_oreb%',
 't1_delta_minus_t2_delta_adv_dreb%',
 't1_delta_minus_t2_delta_adv_reb%',
 't1_delta_minus_t2_delta_adv_tov%',
 't1_delta_minus_t2_delta_adv_efg%',
 't1_delta_minus_t2_delta_adv_ts%',
 't1_delta_minus_t2_delta_adv_pace',
 't1_delta_minus_t2_delta_adv_pie',
 't1_delta_minus_t2_delta_four_efg%',
 't1_delta_minus_t2_delta_four_ftarate',
 't1_delta_minus_t2_delta_four_tov%',
 't1_delta_minus_t2_delta_four_oreb%',
 't1_delta_minus_t2_delta_four_oppefg%',
 't1_delta_minus_t2_delta_four_oppfta\xa0rate',
 't1_delta_minus_t2_delta_four_opptov%',
 't1_delta_minus_t2_delta_four_opporeb%',
 't1_delta_minus_t2_delta_misc_ptsoff\xa0to',
 't1_delta_minus_t2_delta_misc_2ndpts',
 't1_delta_minus_t2_delta_misc_fbps',
 't1_delta_minus_t2_delta_misc_pitp',
 't1_delta_minus_t2_delta_misc_opp\xa0ptsoff\xa0to',
 't1_delta_minus_t2_delta_misc_opp2nd\xa0pts',
 't1_delta_minus_t2_delta_misc_oppfbps',
 't1_delta_minus_t2_delta_misc_opppitp',
 't1_delta_minus_t2_delta_score_%fga2pt',
 't1_delta_minus_t2_delta_score_%fga3pt',
 't1_delta_minus_t2_delta_score_%pts2pt',
 't1_delta_minus_t2_delta_score_%pts2pt\xa0mr',
 't1_delta_minus_t2_delta_score_%pts3pt',
 't1_delta_minus_t2_delta_score_%ptsfbps',
 'team_wins_previous_season',
 'team_win%_previous_season',
 'team_2_wins_previous_season',
 'team2_win%_previous_season',
 'team1_prevwins_minus_team2_prevwins',
 'home_or_away',
 'prev_season_champ_winner',
 'team2_prev_season_champ_winner',
 'team_salary',
 'team_yoy_salary_change',
 'team2_yoy_salary_change',
 'rest_days',
 'team2_rest_days',
 'net_score_top_4',
 'net_score_top_5',
 'net_score_top_6',
 'net_score_top_7',
 'net_score_top_8',
 'top_4_predicted_winner',
 'top_5_predicted_winner',
 'top_6_predicted_winner',
 'top_7_predicted_winner',
 'top_8_predicted_winner',
 'tm1_80_game_avg_offrtg',
 'tm1_80_game_std_offrtg',
 'tm1_80_game_avg_defrtg',
 'tm1_80_game_std_defrtg',
 'tm1_80_game_avg_pace',
 'tm1_80_game_std_pace',
 'tm2_80_game_avg_offrtg',
 'tm2_80_game_std_offrtg',
 'tm2_80_game_avg_defrtg',
 'tm2_80_game_std_defrtg',
 'tm2_80_game_avg_pace',
 'tm2_80_game_std_pace',
 'tm1_40_gm_avg_offrtg',
 'tm1_40_gm_std_offrtg',
 'tm1_40_gm_avg_defrtg',
 'tm1_40_gm_std_defrtg',
 'tm1_40_gm_avg_pace',
 'tm1_40_gm_std_pace',
 'tm2_40_gm_avg_offrtg',
 'tm2_40_gm_std_offrtg',
 'tm2_40_gm_avg_defrtg',
 'tm2_40_gm_std_defrtg',
 'tm2_40_gm_avg_pace',
 'tm2_40_gm_std_pace',
 'tm1_20_gm_avg_offrtg',
 'tm1_20_gm_std_offrtg',
 'tm1_20_gm_avg_defrtg',
 'tm1_20_gm_std_defrtg',
 'tm1_20_gm_avg_pace',
 'tm1_20_gm_std_pace',
 'tm2_20_gm_avg_offrtg',
 'tm2_20_gm_std_offrtg',
 'tm2_20_gm_avg_defrtg',
 'tm2_20_gm_std_defrtg',
 'tm2_20_gm_avg_pace',
 'tm2_20_gm_std_pace',
 'tm1_10_gm_avg_offrtg',
 'tm1_10_gm_std_offrtg',
 'tm1_10_gm_avg_defrtg',
 'tm1_10_gm_std_defrtg',
 'tm1_10_gm_avg_pace',
 'tm1_10_gm_std_pace',
 'tm2_10_gm_avg_offrtg',
 'tm2_10_gm_std_offrtg',
 'tm2_10_gm_avg_defrtg',
 'tm2_10_gm_std_defrtg',
 'tm2_10_gm_avg_pace',
 'tm2_10_gm_std_pace',
 'nba_80_gm_avg_offrtg',
 'nba_80_gm_std_offrtg',
 'nba_80_gm_avg_defrtg',
 'nba_80_gm_std_defrtg',
 'nba_80_gm_avg_pace',
 'nba_80_gm_std_pace',
 'nba_40_gm_avg_offrtg',
 'nba_40_gm_std_offrtg',
 'nba_40_gm_avg_defrtg',
 'nba_40_gm_std_defrtg',
 'nba_40_gm_avg_pace',
 'nba_40_gm_std_pace',
 'nba_20_gm_avg_offrtg',
 'nba_20_gm_std_offrtg',
 'nba_20_gm_avg_defrtg',
 'nba_20_gm_std_defrtg',
 'nba_20_gm_avg_pace',
 'nba_20_gm_std_pace',
 'nba_10_gm_avg_offrtg',
 'nba_10_gm_std_offrtg',
 'nba_10_gm_avg_defrtg',
 'nba_10_gm_std_defrtg',
 'nba_10_gm_avg_pace',
 'nba_10_gm_std_pace',
 '80gm_tm1_minus_nba_avg_offrtg',
 '80gm_tm1_minus_nba_std_offrtg',
 '80gm_tm1_minus_nba_avg_defrtg',
 '80gm_tm1_minus_nba_std_defrtg',
 '80gm_tm1_minus_nba_avg_pace',
 '80gm_tm1_minus_nba_std_pace',
 '80gm_tm2_minus_nba_avg_offrtg',
 '80gm_tm2_minus_nba_std_offrtg',
 '80gm_tm2_minus_nba_avg_defrtg',
 '80gm_tm2_minus_nba_std_defrtg',
 '80gm_tm2_minus_nba_avg_pace',
 '80gm_tm2_minus_nba_std_pace',
 '40gm_tm1_minus_nba_avg_offrtg',
 '40gm_tm1_minus_nba_std_offrtg',
 '40gm_tm1_minus_nba_avg_defrtg',
 '40gm_tm1_minus_nba_std_defrtg',
 '40gm_tm1_minus_nba_avg_pace',
 '40gm_tm1_minus_nba_std_pace',
 '40gm_tm2_minus_nba_avg_offrtg',
 '40gm_tm2_minus_nba_std_offrtg',
 '40gm_tm2_minus_nba_avg_defrtg',
 '40gm_tm2_minus_nba_std_defrtg',
 '40gm_tm2_minus_nba_avg_pace',
 '40gm_tm2_minus_nba_std_pace',
 '20gm_tm1_minus_nba_avg_offrtg',
 '20gm_tm1_minus_nba_std_offrtg',
 '20gm_tm1_minus_nba_avg_defrtg',
 '20gm_tm1_minus_nba_std_defrtg',
 '20gm_tm1_minus_nba_avg_pace',
 '20gm_tm1_minus_nba_std_pace',
 '20gm_tm2_minus_nba_avg_offrtg',
 '20gm_tm2_minus_nba_std_offrtg',
 '20gm_tm2_minus_nba_avg_defrtg',
 '20gm_tm2_minus_nba_std_defrtg',
 '20gm_tm2_minus_nba_avg_pace',
 '20gm_tm2_minus_nba_std_pace',
 '10gm_tm1_minus_nba_avg_offrtg',
 '10gm_tm1_minus_nba_std_offrtg',
 '10gm_tm1_minus_nba_avg_defrtg',
 '10gm_tm1_minus_nba_std_defrtg',
 '10gm_tm1_minus_nba_avg_pace',
 '10gm_tm1_minus_nba_std_pace',
 '10gm_tm2_minus_nba_avg_offrtg',
 '10gm_tm2_minus_nba_std_offrtg',
 '10gm_tm2_minus_nba_avg_defrtg',
 '10gm_tm2_minus_nba_std_defrtg',
 '10gm_tm2_minus_nba_avg_pace',
 '10gm_tm2_minus_nba_std_pace',
 'Tm1_Points_Estimate_80gm',
 'Tm2_Points_Estimate_80gm',
 'Estimate_Points_Difference_80gm',
 'Tm1_Points_Estimate_40gm',
 'Tm2_Points_Estimate_40gm',
 'Estimate_Points_Difference_40gm',
 'Tm1_Points_Estimate_20gm',
 'Tm2_Points_Estimate_20gm',
 'Estimate_Points_Difference_20gm',
 'Tm1_Points_Estimate_Weighted',
 'Tm2_Points_Estimate_Weighted',
 'Estimate_Points_Difference_Weighted',
 'TEAM\nREST DAYS',
 'OPENING ODDS',
 'OPENING SPREAD',
 'OPENING TOTAL',
 'CLOSING\nODDS',
 'CLOSING SPREAD',
 'CLOSING TOTAL',
 'MONEYLINE']

today_df_2 = today_df[test_cols]
today_df_2.head(3)
# convert OPENING ODDS to numeric... problem because it has plus and minus signs
today_df_2['OPENING ODDS'] = today_df_2['OPENING ODDS'].astype(str).str.strip()
today_df_2['OPENING ODDS'] = today_df_2['OPENING ODDS'].str.replace('+', '')
today_df_2['OPENING ODDS'] = today_df_2['OPENING ODDS'].str.replace('−', '-')
# to float
today_df_2['OPENING ODDS'] = today_df_2['OPENING ODDS'].astype(float)

today_df_2['CLOSING\nODDS'] = today_df_2['CLOSING\nODDS'].astype(str).str.strip()
today_df_2['CLOSING\nODDS'] = today_df_2['CLOSING\nODDS'].str.replace('+', '')
today_df_2['CLOSING\nODDS'] = today_df_2['CLOSING\nODDS'].str.replace('−', '-')
# to float
today_df_2['CLOSING\nODDS'] = today_df_2['CLOSING\nODDS'].astype(float)

today_df_2['MONEYLINE'] = today_df_2['MONEYLINE'].astype(str).str.strip()
today_df_2['MONEYLINE'] = today_df_2['MONEYLINE'].str.replace('+', '')
today_df_2['MONEYLINE'] = today_df_2['MONEYLINE'].str.replace('−', '-')
# to float
today_df_2['MONEYLINE'] = today_df_2['MONEYLINE'].astype(float)

today_df_2.head()
# check for non numeric dtypes only
today_df_2.select_dtypes(exclude=['int64', 'float64'])
today_df_2['home?']= np.where(today_df_2['home_or_away'] == 'home', 1, 0)
today_df_2.fillna(0, inplace=True)

prediction =model.predict(today_df_2)

# get the predicted probabilities
probs = model.predict_proba(today_df_2)

# add the probabilities to the dataframe
today_df['probs'] = probs[:,1]
today_df['prediction'] = prediction

today = datetime.datetime.today().strftime('%Y-%m-%d')
today_df.to_csv('data/team/aggregates/daily_updates/predictions_today_'+ str(today) +'.csv', index=False)
print('predictions saved to csv')
print(today_df)