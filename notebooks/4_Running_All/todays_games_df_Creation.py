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
import time
import requests     
from scipy.stats import norm
import winsound
import warnings
warnings.filterwarnings('ignore')
today = datetime.date.today()
today = today.strftime('%Y-%m-%d')

today_df= pd.read_csv('data/team/aggregates/daily_updates/draftkings' + str(today) + '.csv')

# delete the O or U from the totals
today_df['TOTAL'] = today_df['TOTAL'].str.replace('O', '').str.strip()
today_df['TOTAL'] = today_df['TOTAL'].str.replace('U', '').str.strip()
today_df['TOTAL'] = today_df['TOTAL'].astype(float)

# convert names to nba-type names
# create a dictionary of names and their nba-type names
names_dict = {'ATL Hawks':'ATL',
                'BKN Nets':'BKN',
                'BOS Celtics':'BOS',
                'CHA Hornets':'CHA',
                'CHI Bulls':'CHI',
                'CLE Cavaliers':'CLE',
                'DAL Mavericks':'DAL',
                'DEN Nuggets':'DEN',
                'DET Pistons':'DET',
                'GS Warriors':'GSW',
                'HOU Rockets':'HOU',
                'IND Pacers':'IND',
                'LA Clippers':'LAC',
                'LA Lakers':'LAL',
                'MEM Grizzlies':'MEM',
                'MIA Heat':'MIA',
                'MIL Bucks':'MIL',
                'MIN Timberwolves':'MIN',
                'NO Pelicans':'NOP',
                'NY Knicks':'NYK',
                'OKC Thunder':'OKC',
                'ORL Magic':'ORL',
                'PHI 76ers':'PHI',
                'PHO Suns':'PHX',
                'POR Trail Blazers':'POR',
                'SAC Kings':'SAC',
                'SA Spurs':'SAS',
                'TOR Raptors':'TOR',
                'UTA Jazz':'UTA',
                'WAS Wizards':'WAS'}
                
today_df['trad_team'] = today_df['TODAY'].map(names_dict)
# reset index
today_df = today_df.reset_index(drop=False)
### Adding Features


#### Load Old_DF_Final (just like update_all_features)
old_df_final = pd.read_csv('data/team/All_Things_9.csv')

# sort by date
#old_df_final.trad_gamedate = pd.to_datetime(old_df_final.trad_gamedate)
old_df_final = old_df_final.sort_values(by=['trad_gamedate'], ascending=False)
old_df_final['trad_gamedate'] = pd.to_datetime(old_df_final['trad_gamedate'])

# drop unnamed columns
unnamed = [col for col in old_df_final.columns if 'Unnamed' in col]
old_df_final.drop(columns=unnamed, inplace=True)

print(f'old df final shape: {old_df_final.shape}')


# where index is even, matchup is next row. where index is odd, matchup is previous row
today_df['matchup'] = np.where(today_df.index % 2 == 0, today_df['trad_team'].shift(-1), today_df['trad_team'].shift(1))

today_df['AwayTeam'] = np.where(today_df.index % 2 == 0, today_df['trad_team'], today_df['matchup'].str[:3])
today_df['HomeTeam'] = np.where(today_df.index % 2 == 0, today_df['matchup'].str[:3], today_df['trad_team'])

today_df['trad_matchup'] = today_df['AwayTeam'] + ' @ ' + today_df['HomeTeam']
today_df['trad_season'] = 2022
today_df['team_2'] = np.where(today_df.AwayTeam == today_df.trad_team, today_df.HomeTeam, today_df.AwayTeam)
today_df['trad_gamedate'] = today



features_to_work_with = ['trad_pts',
 'trad_fgm',
 'trad_fga',
 'trad_fg%',
 'trad_3pm',
 'trad_3pa',
 'trad_3p%',
 'trad_ftm',
 'trad_fta',
 'trad_ft%',
 'trad_oreb',
 'trad_dreb',
 'trad_reb',
 'trad_ast',
 'trad_tov',
 'trad_stl',
 'trad_blk',
 'trad_pf',
 'trad_+/-',
 'adv_offrtg',
 'adv_defrtg',
 'adv_netrtg',
 'adv_ast%',
 'adv_ast/to',
 'adv_astratio',
 'adv_oreb%',
 'adv_dreb%',
 'adv_reb%',
 'adv_tov%',
 'adv_efg%',
 'adv_ts%',
 'adv_pace',
 'adv_pie',
 'four_efg%',
 'four_ftarate',
 'four_tov%',
 'four_oreb%',
 'four_oppefg%',
 'four_oppfta\xa0rate',
 'four_opptov%',
 'four_opporeb%',
 'misc_ptsoff\xa0to',
 'misc_2ndpts',
 'misc_fbps',
 'misc_pitp',
 'misc_opp\xa0ptsoff\xa0to',
 'misc_opp2nd\xa0pts',
 'misc_oppfbps',
 'misc_opppitp',
 'score_%fga2pt',
 'score_%fga3pt',
 'score_%pts2pt',
 'score_%pts2pt\xa0mr',
 'score_%pts3pt',
 'score_%ptsfbps',
 'score_%ptsft',
 'score_%ptsoff\xa0to',
 'score_%ptspitp',
 'score_2fgm%ast',
 'score_2fgm%uast',
 'score_3fgm%ast',
 'score_3fgm%uast',
 'score_fgm%ast',
 'score_fgm%uast']

df = old_df_final

def get_avgs_by_game(team, season, game_date, metric):
    data = df[df['trad_team'] == team]
    data1 = data[data['trad_season'] == season]
    # filter by date
    data2 = data1[data1['trad_gamedate'] < game_date]
    # drop na
    data2 = data2.dropna(subset=[metric])
    metric_mean = data2[metric].mean()
    return metric_mean


for f in features_to_work_with:
    today_df['t1_running_' + f] = today_df.apply(lambda row: get_avgs_by_game(row['trad_team'], row['trad_season'], row['trad_gamedate'], f), axis=1)
for f in features_to_work_with:
    today_df['t2_running_' + f] = today_df.apply(lambda row: get_avgs_by_game(row['team_2'], row['trad_season'], row['trad_gamedate'], f), axis=1)

# add dif between teams
for f in features_to_work_with:
    today_df['running_t1-t2_' + f] = today_df['t1_running_' + f] - today_df['t2_running_' + f]
# Add all teams running averages

def get_league_avgs_by_game(season, game_date, metric):
    data = df[df['trad_season'] == season]
    # filter by date
    data = data[data['trad_gamedate'] < game_date]
    data = data.dropna(subset = [metric])
    metric_mean = data[metric].mean()
    return metric_mean

print('creating league running averages')

for f in features_to_work_with:
    today_df['league_running_' + f] = today_df.apply(lambda row: get_league_avgs_by_game(row['trad_season'], row['trad_gamedate'], f), axis=1)
# Team Running - League Running
for f in features_to_work_with:
    today_df['t1_league_delta_' + f] = today_df['t1_running_' + f] - today_df['league_running_' + f]

# team 2 - League
for f in features_to_work_with:
    today_df['t2_league_delta_' + f] = today_df['t2_running_' + f] - today_df['league_running_' + f]

# Team 1 - Team 2
for f in features_to_work_with:
    today_df['t1_delta_minus_t2_delta_' + f] = today_df['t1_league_delta_' + f] - today_df['t2_league_delta_' + f]
### 2b Update
games_df = df.copy()
games_df = games_df[games_df['trad_season'] >= 2012]
games_df['win?'] = np.where(games_df['trad_w/l'] == 'W', 1, 0)
#groupby team and trad_season to get win totals per year
df_wins = games_df.groupby(['trad_team','trad_season'])['win?'].sum()

dfw = pd.DataFrame(df_wins)

# all columns same level
dfw = dfw.reset_index()

def get_previous_trad_season_win_total(team, trad_season):
    season = 2021
    data = dfw[dfw['trad_team'] == team]
    data = data[data['trad_season'] == season]
    win_tot = data['win?'].values[0]
    return win_tot

# get list of trad_team
teams = dfw['trad_team'].unique()


today_df['team_wins_previous_season'] = today_df.apply(lambda row: get_previous_trad_season_win_total(row['trad_team'], row['trad_season']), axis=1)
today_df['team_win%_previous_season'] = today_df['team_wins_previous_season'] / 82
today_df['team_2_wins_previous_season'] = today_df.apply(lambda row: get_previous_trad_season_win_total(row['team_2'], row['trad_season']), axis=1)

today_df['team2_win%_previous_season'] = today_df['team_2_wins_previous_season'] / 82
today_df['team1_prevwins_minus_team2_prevwins'] = today_df['team_wins_previous_season'] - today_df['team_2_wins_previous_season']
today_df['home_or_away'] = np.where(today_df['trad_team'] == today_df['HomeTeam'], 'home', 'away')
# NBA Champion by Year
champs = pd.read_csv('data/team/cleaned_finals_results.csv')


def champ_winner(team, trad_season):
    sz_to_check = trad_season - 1
    df = champs[champs['Yr'] == sz_to_check]
    if team in df['Winner_abv'].values:
        return 1
    else:
        return 0

today_df['prev_season_champ_winner'] = today_df.apply(lambda row: champ_winner(row['trad_team'], row['trad_season']), axis=1)
today_df['team2_prev_season_champ_winner'] = today_df.apply(lambda row: champ_winner(row['team_2'], row['trad_season']), axis=1)

# Team Salary
team_contracts = pd.read_csv('data/team/team_contracts/All_team_contracts.csv')


def get_salaries(team, trad_season):
    try:
        sz = str(trad_season)
        data = team_contracts[team_contracts['Team_Abbrev'] == team]
        val = data[sz].values[0]
        # get value for trad_season
        return val
    except:
        return np.nan


today_df['team_salary'] = today_df.apply(lambda row: get_salaries(row['trad_team'], row['trad_season']), axis=1)


# YOY Change in Salary
def get_yoy(team, trad_season):
    try:
        z = int(trad_season)
        sz = str(trad_season)
        sz1 = z - 1
        sz2 = str(sz1)
        colz = 'yoy_' + sz2[-2:] + '_' + sz[-2:]
        data = team_contracts[team_contracts['Team_Abbrev'] == team]
        val = data[colz].values[0]
        # get value for trad_season
        return val
    except:
        return np.nan


today_df['team_yoy_salary_change'] = today_df.apply(lambda row: get_yoy(row['trad_team'], row['trad_season']), axis=1)
today_df['team2_yoy_salary_change'] = today_df.apply(lambda row: get_yoy(row['team_2'], row['trad_season']), axis=1)

# REST
def get_rest_days(team, trad_season, gamedate):

    # rest days are days between game dates
    
    data = df[(df['trad_team'] == team) & (df['trad_season'] == trad_season)]
    data = df[df['trad_gamedate'] <= gamedate]
    data = data.sort_values(by=['trad_gamedate'], ascending=False)
    gameday1 = data.iloc[0]['trad_gamedate']
    gameday1 = pd.to_datetime(gameday1)
    gameday2 = data.iloc[2]['trad_gamedate']
    gameday2 = pd.to_datetime(gameday2)
    val = gameday1 - gameday2
    val = val.days
    # get value for trad_season
    return val


today_df['rest_days'] = today_df.apply(lambda row: get_rest_days(row['trad_team'], row['trad_season'], row['trad_gamedate']), axis=1)
today_df['team2_rest_days'] = today_df.apply(lambda row: get_rest_days(row['team_2'], row['trad_season'], row['trad_gamedate']), axis=1)


print('getting rest days')

### 2e Update
def get_game_avgs(team, season, date, metric, game_num, agg_metric):
    data = df[df['trad_team'] == team]
    # filter by date
    data = data[data['trad_gamedate'] < date]
    # only last 80 games
    data = data.sort_values('trad_gamedate', ascending = False)
    data = data.head(game_num)
    data = data.dropna(subset = [metric])
    if agg_metric == 'std':
        metric = data[metric].std()
    else:
        metric = data[metric].mean()
    return metric


today_df['tm1_80_game_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs( row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'avg'), axis=1)
today_df['tm1_80_game_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'std'), axis=1)
today_df['tm1_80_game_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'avg'), axis=1)
today_df['tm1_80_game_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'std'), axis=1)
today_df['tm1_80_game_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'avg'), axis=1)
today_df['tm1_80_game_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'std'), axis=1)
today_df['tm2_80_game_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'avg'), axis=1)
today_df['tm2_80_game_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'std'), axis=1)
today_df['tm2_80_game_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'avg'), axis=1)
today_df['tm2_80_game_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'std'), axis=1)
today_df['tm2_80_game_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'avg'), axis=1)
today_df['tm2_80_game_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'std'), axis=1)
today_df['tm1_40_gm_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'avg'), axis=1)
today_df['tm1_40_gm_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'std'), axis=1)
today_df['tm1_40_gm_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'avg'), axis=1)
today_df['tm1_40_gm_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'std'), axis=1)
today_df['tm1_40_gm_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'avg'), axis=1)
today_df['tm1_40_gm_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'std'), axis=1)

today_df['tm2_40_gm_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'avg'), axis=1)
today_df['tm2_40_gm_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'std'), axis=1)
today_df['tm2_40_gm_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'avg'), axis=1)
today_df['tm2_40_gm_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'std'), axis=1)
today_df['tm2_40_gm_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'avg'), axis=1)
today_df['tm2_40_gm_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'std'), axis=1)

today_df['tm1_20_gm_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'avg'), axis=1)
today_df['tm1_20_gm_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'std'), axis=1)
today_df['tm1_20_gm_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'avg'), axis=1)
today_df['tm1_20_gm_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'std'), axis=1)
today_df['tm1_20_gm_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'avg'), axis=1)
today_df['tm1_20_gm_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'std'), axis=1)

today_df['tm2_20_gm_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'avg'), axis=1)
today_df['tm2_20_gm_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'std'), axis=1)
today_df['tm2_20_gm_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'avg'), axis=1)
today_df['tm2_20_gm_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'std'), axis=1)
today_df['tm2_20_gm_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'avg'), axis=1)
today_df['tm2_20_gm_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'std'), axis=1)

today_df['tm1_10_gm_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'avg'), axis=1)
today_df['tm1_10_gm_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'std'), axis=1)
today_df['tm1_10_gm_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'avg'), axis=1)
today_df['tm1_10_gm_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'std'), axis=1)
today_df['tm1_10_gm_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'avg'), axis=1)
today_df['tm1_10_gm_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['trad_team'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'std'), axis=1)

today_df['tm2_10_gm_avg_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'avg'), axis=1)
today_df['tm2_10_gm_std_offrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'std'), axis=1)
today_df['tm2_10_gm_avg_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'avg'), axis=1)
today_df['tm2_10_gm_std_defrtg'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'std'), axis=1)
today_df['tm2_10_gm_avg_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'avg'), axis=1)
today_df['tm2_10_gm_std_pace'] = today_df.apply(lambda row: get_game_avgs(row['team_2'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'std'), axis=1)

def get_NBA_avgs( season, date, metric, game_num, agg_metric):
    # filter by date
    data = df[df['trad_gamedate'] < date]
    # only last 80 games
    data = data.sort_values('trad_gamedate', ascending = False)
    gamess = game_num * 30 # for each team
    data = data.head(gamess)
    data = data.dropna(subset = [metric])
    if agg_metric == 'std':
        metric = data[metric].std()
    else:
        metric = data[metric].mean()
    return metric

print('Calculating NBA Averages')

today_df['nba_80_gm_avg_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'avg'), axis=1)
today_df['nba_80_gm_std_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'std'), axis=1)
today_df['nba_80_gm_avg_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'avg'), axis=1)
today_df['nba_80_gm_std_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'std'), axis=1)
today_df['nba_80_gm_avg_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'avg'), axis=1)
today_df['nba_80_gm_std_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'std'), axis=1)

today_df['nba_40_gm_avg_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'avg'), axis=1)
today_df['nba_40_gm_std_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'std'), axis=1)
today_df['nba_40_gm_avg_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'avg'), axis=1)
today_df['nba_40_gm_std_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'std'), axis=1)
today_df['nba_40_gm_avg_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'avg'), axis=1)
today_df['nba_40_gm_std_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'std'), axis=1)

today_df['nba_20_gm_avg_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'avg'), axis=1)
today_df['nba_20_gm_std_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'std'), axis=1)
today_df['nba_20_gm_avg_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'avg'), axis=1)
today_df['nba_20_gm_std_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'std'), axis=1)
today_df['nba_20_gm_avg_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'avg'), axis=1)
today_df['nba_20_gm_std_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'std'), axis=1)

today_df['nba_10_gm_avg_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'avg'), axis=1)
today_df['nba_10_gm_std_offrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'std'), axis=1)
today_df['nba_10_gm_avg_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'avg'), axis=1)
today_df['nba_10_gm_std_defrtg'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'std'), axis=1)
today_df['nba_10_gm_avg_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'avg'), axis=1)
today_df['nba_10_gm_std_pace'] = today_df.apply(lambda row: get_NBA_avgs(row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'std'), axis=1)

today_df['80gm_tm1_minus_nba_avg_offrtg'] = today_df['tm1_80_game_avg_offrtg'] - today_df['nba_80_gm_avg_offrtg']
today_df['80gm_tm1_minus_nba_std_offrtg'] = today_df['tm1_80_game_std_offrtg'] - today_df['nba_80_gm_std_offrtg']
today_df['80gm_tm1_minus_nba_avg_defrtg'] = today_df['tm1_80_game_avg_defrtg'] - today_df['nba_80_gm_avg_defrtg']
today_df['80gm_tm1_minus_nba_std_defrtg'] = today_df['tm1_80_game_std_defrtg'] - today_df['nba_80_gm_std_defrtg']
today_df['80gm_tm1_minus_nba_avg_pace'] = today_df['tm1_80_game_avg_pace'] - today_df['nba_80_gm_avg_pace']
today_df['80gm_tm1_minus_nba_std_pace'] = today_df['tm1_80_game_std_pace'] - today_df['nba_80_gm_std_pace']
today_df['80gm_tm2_minus_nba_avg_offrtg'] = today_df['tm2_80_game_avg_offrtg'] - today_df['nba_80_gm_avg_offrtg']
today_df['80gm_tm2_minus_nba_std_offrtg'] = today_df['tm2_80_game_std_offrtg'] - today_df['nba_80_gm_std_offrtg']
today_df['80gm_tm2_minus_nba_avg_defrtg'] = today_df['tm2_80_game_avg_defrtg'] - today_df['nba_80_gm_avg_defrtg']
today_df['80gm_tm2_minus_nba_std_defrtg'] = today_df['tm2_80_game_std_defrtg'] - today_df['nba_80_gm_std_defrtg']
today_df['80gm_tm2_minus_nba_avg_pace'] = today_df['tm2_80_game_avg_pace'] - today_df['nba_80_gm_avg_pace']
today_df['80gm_tm2_minus_nba_std_pace'] = today_df['tm2_80_game_std_pace'] - today_df['nba_80_gm_std_pace']

today_df['40gm_tm1_minus_nba_avg_offrtg'] = today_df['tm1_40_gm_avg_offrtg'] - today_df['nba_40_gm_avg_offrtg']
today_df['40gm_tm1_minus_nba_std_offrtg'] = today_df['tm1_40_gm_std_offrtg'] - today_df['nba_40_gm_std_offrtg']
today_df['40gm_tm1_minus_nba_avg_defrtg'] = today_df['tm1_40_gm_avg_defrtg'] - today_df['nba_40_gm_avg_defrtg']
today_df['40gm_tm1_minus_nba_std_defrtg'] = today_df['tm1_40_gm_std_defrtg'] - today_df['nba_40_gm_std_defrtg']
today_df['40gm_tm1_minus_nba_avg_pace'] = today_df['tm1_40_gm_avg_pace'] - today_df['nba_40_gm_avg_pace']
today_df['40gm_tm1_minus_nba_std_pace'] = today_df['tm1_40_gm_std_pace'] - today_df['nba_40_gm_std_pace']

today_df['40gm_tm2_minus_nba_avg_offrtg'] = today_df['tm2_40_gm_avg_offrtg'] - today_df['nba_40_gm_avg_offrtg']
today_df['40gm_tm2_minus_nba_std_offrtg'] = today_df['tm2_40_gm_std_offrtg'] - today_df['nba_40_gm_std_offrtg']
today_df['40gm_tm2_minus_nba_avg_defrtg'] = today_df['tm2_40_gm_avg_defrtg'] - today_df['nba_40_gm_avg_defrtg']
today_df['40gm_tm2_minus_nba_std_defrtg'] = today_df['tm2_40_gm_std_defrtg'] - today_df['nba_40_gm_std_defrtg']
today_df['40gm_tm2_minus_nba_avg_pace'] = today_df['tm2_40_gm_avg_pace'] - today_df['nba_40_gm_avg_pace']
today_df['40gm_tm2_minus_nba_std_pace'] = today_df['tm2_40_gm_std_pace'] - today_df['nba_40_gm_std_pace']

today_df['20gm_tm1_minus_nba_avg_offrtg'] = today_df['tm1_20_gm_avg_offrtg'] - today_df['nba_20_gm_avg_offrtg']
today_df['20gm_tm1_minus_nba_std_offrtg'] = today_df['tm1_20_gm_std_offrtg'] - today_df['nba_20_gm_std_offrtg']
today_df['20gm_tm1_minus_nba_avg_defrtg'] = today_df['tm1_20_gm_avg_defrtg'] - today_df['nba_20_gm_avg_defrtg']
today_df['20gm_tm1_minus_nba_std_defrtg'] = today_df['tm1_20_gm_std_defrtg'] - today_df['nba_20_gm_std_defrtg']
today_df['20gm_tm1_minus_nba_avg_pace'] = today_df['tm1_20_gm_avg_pace'] - today_df['nba_20_gm_avg_pace']
today_df['20gm_tm1_minus_nba_std_pace'] = today_df['tm1_20_gm_std_pace'] - today_df['nba_20_gm_std_pace']

today_df['20gm_tm2_minus_nba_avg_offrtg'] = today_df['tm2_20_gm_avg_offrtg'] - today_df['nba_20_gm_avg_offrtg']
today_df['20gm_tm2_minus_nba_std_offrtg'] = today_df['tm2_20_gm_std_offrtg'] - today_df['nba_20_gm_std_offrtg']
today_df['20gm_tm2_minus_nba_avg_defrtg'] = today_df['tm2_20_gm_avg_defrtg'] - today_df['nba_20_gm_avg_defrtg']
today_df['20gm_tm2_minus_nba_std_defrtg'] = today_df['tm2_20_gm_std_defrtg'] - today_df['nba_20_gm_std_defrtg']
today_df['20gm_tm2_minus_nba_avg_pace'] = today_df['tm2_20_gm_avg_pace'] - today_df['nba_20_gm_avg_pace']
today_df['20gm_tm2_minus_nba_std_pace'] = today_df['tm2_20_gm_std_pace'] - today_df['nba_20_gm_std_pace']

today_df['10gm_tm1_minus_nba_avg_offrtg'] = today_df['tm1_10_gm_avg_offrtg'] - today_df['nba_10_gm_avg_offrtg']
today_df['10gm_tm1_minus_nba_std_offrtg'] = today_df['tm1_10_gm_std_offrtg'] - today_df['nba_10_gm_std_offrtg']
today_df['10gm_tm1_minus_nba_avg_defrtg'] = today_df['tm1_10_gm_avg_defrtg'] - today_df['nba_10_gm_avg_defrtg']
today_df['10gm_tm1_minus_nba_std_defrtg'] = today_df['tm1_10_gm_std_defrtg'] - today_df['nba_10_gm_std_defrtg']
today_df['10gm_tm1_minus_nba_avg_pace'] = today_df['tm1_10_gm_avg_pace'] - today_df['nba_10_gm_avg_pace']
today_df['10gm_tm1_minus_nba_std_pace'] = today_df['tm1_10_gm_std_pace'] - today_df['nba_10_gm_std_pace']

today_df['10gm_tm2_minus_nba_avg_offrtg'] = today_df['tm2_10_gm_avg_offrtg'] - today_df['nba_10_gm_avg_offrtg']
today_df['10gm_tm2_minus_nba_std_offrtg'] = today_df['tm2_10_gm_std_offrtg'] - today_df['nba_10_gm_std_offrtg']
today_df['10gm_tm2_minus_nba_avg_defrtg'] = today_df['tm2_10_gm_avg_defrtg'] - today_df['nba_10_gm_avg_defrtg']
today_df['10gm_tm2_minus_nba_std_defrtg'] = today_df['tm2_10_gm_std_defrtg'] - today_df['nba_10_gm_std_defrtg']
today_df['10gm_tm2_minus_nba_avg_pace'] = today_df['tm2_10_gm_avg_pace'] - today_df['nba_10_gm_avg_pace']
today_df['10gm_tm2_minus_nba_std_pace'] = today_df['tm2_10_gm_std_pace'] - today_df['nba_10_gm_std_pace']

today_df['Tm1_Points_Estimate_80gm'] = ((today_df['tm1_80_game_avg_pace'] + today_df['tm2_80_game_avg_pace'])/2) * ((today_df['tm1_80_game_avg_offrtg'] - (today_df['tm1_80_game_avg_defrtg'] - today_df['nba_80_gm_avg_defrtg'])))/100
today_df['Tm2_Points_Estimate_80gm'] = ((today_df['tm1_80_game_avg_pace'] + today_df['tm2_80_game_avg_pace'])/2) * ((today_df['tm2_80_game_avg_offrtg'] - (today_df['tm2_80_game_avg_defrtg'] - today_df['nba_80_gm_avg_defrtg'])))/100
today_df['Estimate_Points_Difference_80gm'] = today_df['Tm1_Points_Estimate_80gm'] - today_df['Tm2_Points_Estimate_80gm']

today_df['Tm1_Points_Estimate_40gm'] = ((today_df['tm1_40_gm_avg_pace'] + today_df['tm2_40_gm_avg_pace'])/2) * ((today_df['tm1_40_gm_avg_offrtg'] - (today_df['tm1_40_gm_avg_defrtg'] - today_df['nba_40_gm_avg_defrtg'])))/100
today_df['Tm2_Points_Estimate_40gm'] = ((today_df['tm1_40_gm_avg_pace'] + today_df['tm2_40_gm_avg_pace'])/2) * ((today_df['tm2_40_gm_avg_offrtg'] - (today_df['tm2_40_gm_avg_defrtg'] - today_df['nba_40_gm_avg_defrtg'])))/100
today_df['Estimate_Points_Difference_40gm'] = today_df['Tm1_Points_Estimate_40gm'] - today_df['Tm2_Points_Estimate_40gm']

today_df['Tm1_Points_Estimate_20gm'] = ((today_df['tm1_20_gm_avg_pace'] + today_df['tm2_20_gm_avg_pace'])/2) * ((today_df['tm1_20_gm_avg_offrtg'] - (today_df['tm1_20_gm_avg_defrtg'] - today_df['nba_20_gm_avg_defrtg'])))/100
today_df['Tm2_Points_Estimate_20gm'] = ((today_df['tm1_20_gm_avg_pace'] + today_df['tm2_20_gm_avg_pace'])/2) * ((today_df['tm2_20_gm_avg_offrtg'] - (today_df['tm2_20_gm_avg_defrtg'] - today_df['nba_20_gm_avg_defrtg'])))/100
today_df['Estimate_Points_Difference_20gm'] = today_df['Tm1_Points_Estimate_20gm'] - today_df['Tm2_Points_Estimate_20gm']

today_df['Tm1_Points_Estimate_10gm'] = ((today_df['tm1_10_gm_avg_pace'] + today_df['tm2_10_gm_avg_pace'])/2) * ((today_df['tm1_10_gm_avg_offrtg'] - (today_df['tm1_10_gm_avg_defrtg'] - today_df['nba_10_gm_avg_defrtg'])))/100
today_df['Tm2_Points_Estimate_10gm'] = ((today_df['tm1_10_gm_avg_pace'] + today_df['tm2_10_gm_avg_pace'])/2) * ((today_df['tm2_10_gm_avg_offrtg'] - (today_df['tm2_10_gm_avg_defrtg'] - today_df['nba_10_gm_avg_defrtg'])))/100
today_df['Estimate_Points_Difference_10gm'] = today_df['Tm1_Points_Estimate_10gm'] - today_df['Tm2_Points_Estimate_10gm']

# Weighted Average of the 4 estimates
today_df['Tm1_Points_Estimate_Weighted'] = today_df['Tm1_Points_Estimate_80gm'] * 0.17 + today_df['Tm1_Points_Estimate_40gm'] * 0.22 + today_df['Tm1_Points_Estimate_20gm'] * 0.28 + today_df['Tm1_Points_Estimate_10gm'] * 0.33
today_df['Tm2_Points_Estimate_Weighted'] = today_df['Tm2_Points_Estimate_80gm'] * 0.17 + today_df['Tm2_Points_Estimate_40gm'] * 0.22 + today_df['Tm2_Points_Estimate_20gm'] * 0.28 + today_df['Tm2_Points_Estimate_10gm'] * 0.33


today_df['Estimate_Points_Difference_Weighted'] = today_df['Tm1_Points_Estimate_Weighted'] - today_df['Tm2_Points_Estimate_Weighted']


today_df.to_csv('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\data\\team\\aggregates\\daily_updates\\today_df_features__' + str(today) + '.csv', index=False)
print('saved data/team/aggregates/daily_updates/today_df_features__' + str(today) + '.csv')  
print('Job Done!')