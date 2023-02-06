import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import random
import shutil
import plotly
import warnings
import datetime
# ignore warnings
warnings.filterwarnings('ignore')

os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1')
df = pd.read_csv('data/team/aggregates/Both_Team_Boxscores_ALL_with_Trad_Difs.csv')


df.trad_gamedate = pd.to_datetime(df.trad_gamedate)
df.trad_gamedate = df.trad_gamedate.dt.date

# sort by date
df = df.sort_values(by=['trad_gamedate'], ascending=False)
# drop duplicates
df.drop_duplicates(subset = ['trad_matchup'], inplace=True)
# reset index
df.reset_index(drop=True, inplace=True)

df['days_since_dec_1'] = (df.trad_gamedate - datetime.date(2022, 12, 1)).dt.days

today = datetime.datetime.today().strftime('%Y-%m-%d')

# get LATEST Updated_All_Things file
files = os.listdir('data/team/aggregates/daily_updates')
files = [n for n in files if 'Updated_All_Things' in n]
files = [n for n in files if '.csv' in n]
files = pd.DataFrame(files)
files.columns = ['file_name']
files['date'] = files.file_name.str.split('_').str[3]
files['date'] = files.date.str.split('.').str[0]
files['date'] = pd.to_datetime(files['date'])
files = files.sort_values(by=['date'], ascending=False)
most_recent_file = files.file_name.values[0]
# Print most recent file name
print('most recent file is: ', most_recent_file)

old_df_final = pd.read_csv('data/team/aggregates/daily_updates/' + most_recent_file)


# sort by date
#old_df_final.trad_gamedate = pd.to_datetime(old_df_final.trad_gamedate)
old_df_final = old_df_final.sort_values(by=['trad_gamedate'], ascending=False)
old_df_final['trad_gamedate'] = pd.to_datetime(old_df_final['trad_gamedate'])
print(old_df_final.shape)
old_df_final.head(1)

latest_game = pd.to_datetime(old_df_final['trad_gamedate'].values[0])
# turn latest_game to timestamp
latest_game = latest_game.date()

latest_game_days_since_dec1 = ((latest_game) - datetime.date(2022, 12, 1)).days
print(latest_game_days_since_dec1)
missing_games = df[df['days_since_dec_1'] > latest_game_days_since_dec1]
missing_games = missing_games.drop_duplicates(subset=['trad_matchup'])
missing_games
print(f' You have {missing_games.shape[0]} games to add to your dataset')


# # if missing games is empty, then stop here
# if missing_games.shape[0] == 0:
#     print('You have no missing games')
#     # stop here

today = datetime.datetime.today().strftime('%Y-%m-%d')
file_should_be = 'data/team/aggregates/daily_updates/'+ today + '.csv'

if os.path.exists(file_should_be):
    print('file already exists')
# if not empty, then continue
else:
    all_cols = list(missing_games.columns)
    all_cols = [n for n in all_cols if 'Unnamed' not in n]
    all_cols = [n for n in all_cols if 'unnamed' not in n]
    all_cols = [n for n in all_cols if 't1' not in n]
    all_cols = [n for n in all_cols if 't2' not in n]
    all_cols = [n for n in all_cols if 'tm2' not in n]
    all_cols = [n for n in all_cols if 'tm1' not in n]
    all_cols = [n for n in all_cols if 'team' not in n]
    all_cols = [n for n in all_cols if 'date' not in n]
    all_cols = [n for n in all_cols if 'season' not in n]
    all_cols = [n for n in all_cols if 'matchup' not in n]
    all_cols = [n for n in all_cols if 'wins' not in n]
    all_cols = [n for n in all_cols if 'game' not in n]
    all_cols = [n for n in all_cols if 'w/l' not in n]
    all_cols = [n for n in all_cols if 'min' not in n]
    all_cols
    def get_avgs_by_game(team, season, game_date, metric):
        data = df[df['trad_team'] == team]
        data1 = data[data['trad_season'] == season]
        # filter by date
        data2 = data1[data1['trad_gamedate'] < game_date]
        # drop na
        data2 = data2.dropna(subset=[metric])
        metric_mean = data2[metric].mean()
        return metric_mean
    # First for team 1
    features_to_work_with = all_cols


    for f in features_to_work_with:
        missing_games['t1_running_' + f] = missing_games.apply(lambda row: get_avgs_by_game(row['trad_team'], row['trad_season'], row['trad_gamedate'], f), axis=1)
    

    for f in features_to_work_with:
        missing_games['t2_running_' + f] = missing_games.apply(lambda row: get_avgs_by_game( row['team_2'], row['trad_season'], row['trad_gamedate'], f), axis=1)

    # Add dif between teams
    for f in features_to_work_with:
        missing_games['running_t1-t2_' + f] = missing_games['t1_running_' + f] - missing_games['t2_running_' + f]
    
    # Add all teams running averages

    def get_league_avgs_by_game(season, game_date, metric):
        data = df[df['trad_season'] == season]
        # filter by date
        data = data[data['trad_gamedate'] < game_date]
        data = data.dropna(subset = [metric])
        metric_mean = data[metric].mean()
        return metric_mean
    
    # check nas
    missing = missing_games.isna().sum()
    missing[missing > 0]
    for f in features_to_work_with:
        missing_games['league_running_'+ f] = missing_games.apply(lambda row: get_league_avgs_by_game(row['trad_season'], row['trad_gamedate'], f), axis=1)
    
    # now add team running - league_running
    for f in features_to_work_with:
        missing_games['t1_league_delta_' + f] = missing_games['t1_running_' + f] - missing_games['league_running_'+ f]

    # team2 - league
    for f in features_to_work_with:
        missing_games['t2_league_delta_' + f] = missing_games['t2_running_' + f] - missing_games['league_running_'+ f]

    # team1 - team2
    for f in features_to_work_with:
        missing_games['t1_delta_minus_t2_delta_' + f] = missing_games['t1_league_delta_' + f] - missing_games['t2_league_delta_' + f]

  
    #### 2b update

    full_boxes = pd.DataFrame()

    team_box_files = os.listdir('data/team/team_boxscores/')
    team_box_files = [n for n in team_box_files if 'csv' in n]
    team_trad_box_files = [n for n in team_box_files if 'trad' in n]
    # drop the .csv


    for f in team_trad_box_files:
        # open each, add season, season type, and append
        data = pd.read_csv('data/team/team_boxscores/' + f)
        data['trad_season'] = f[-11:-7]
        if 'Regular' in f:
            data['trad_season_type'] = 'Regular'
        else:
            data['trad_season_type'] = 'Playoffs'
        full_boxes = full_boxes.append(data)

    full_boxes['GAME DATE'] = pd.to_datetime(full_boxes['GAME DATE'])
    # sort by game date
    full_boxes = full_boxes.sort_values(by='GAME DATE', ascending=False)
    # drop nan when in TEAM
    full_boxes = full_boxes.dropna(subset=['TEAM'])
    full_boxes['trad_season'] = full_boxes['trad_season'].astype(int)


    games_df = full_boxes.copy()
    games_df = games_df[games_df['trad_season'] >= 2012]
    games_df = games_df[games_df['trad_season_type'] == 'Regular']
    games_df['win?'] = np.where(games_df['W/L'] == 'W', 1, 0)
    #groupby team and trad_season to get win totals per year
    df_wins = games_df.groupby(['TEAM','trad_season'])['win?'].sum()


    dfw = pd.DataFrame(df_wins)


    def get_previous_trad_season_win_total(team, trad_season):
        return dfw.loc[(team, trad_season-1)]
    

    missing_games['team_wins_previous_season'] = missing_games.apply(lambda row: get_previous_trad_season_win_total(row['trad_team'], row['trad_season']), axis=1)
    missing_games['team_win%_previous_season'] = missing_games['team_wins_previous_season'] / 82
    missing_games['team_2_wins_previous_season'] = missing_games.apply(lambda row: get_previous_trad_season_win_total(row['team_2'], row['trad_season']), axis=1)


    missing_games['team2_win%_previous_season'] = missing_games['team_2_wins_previous_season'] / 82
    missing_games['team1_prevwins_minus_team2_prevwins'] = missing_games['team_wins_previous_season'] - missing_games['team_2_wins_previous_season']
    # Home or away
    missing_games['home_or_away'] = np.where(missing_games['trad_matchup'].str.contains('@'), 'away', 'home')


    # NBA Champion by Year
    champs = pd.read_csv('data/team/cleaned_finals_results.csv')

    def champ_winner(team, trad_season):
        sz_to_check = trad_season - 1
        df = champs[champs['Yr'] == sz_to_check]
        if team in df['Winner_abv'].values:
            return 1
        else:
            return 0

    missing_games['prev_season_champ_winner'] = missing_games.apply(lambda row: champ_winner(row['trad_team'], row['trad_season']), axis=1)
    missing_games['team2_prev_season_champ_winner'] = missing_games.apply(lambda row: champ_winner(row['team_2'], row['trad_season']), axis=1)
    
    # Team Salary
    salaries= pd.read_csv('data/team/aggregates/Team_Salaries_Through_2022.csv')


    def find_team_salary(team, year, change=False):
        try:
            if change:
                return salaries[salaries['team_abv'] == team][str(year)+'_change'].values[0]
            else:
                return salaries[salaries['team_abv'] == team][str(year)].values[0]
        except:
            return np.nan

    missing_games['team_yoy_salary_change'] = missing_games.apply(lambda row: find_team_salary(row['trad_team'], row['trad_season'],change= True), axis=1)
    missing_games['team__salary'] = missing_games.apply(lambda row: find_team_salary(row['trad_team'], row['trad_season'], change = False), axis=1)
    missing_games['team_2_yoy_salary_change'] = missing_games.apply(lambda row: find_team_salary(row['team_2'], row['trad_season'],change= True), axis=1)
    missing_games['team_2__salary'] = missing_games.apply(lambda row: find_team_salary(row['team_2'], row['trad_season'], change = False), axis=1)


    # REST
    def get_rest_days(team, trad_season, gamedate):

        # rest days are days between game dates
        gd = pd.to_datetime(gamedate)
        data = games_df[(games_df['TEAM'] == team) & (games_df['trad_season'] == trad_season)]
        data = data[data['GAME DATE'] < gd]
        most_recent_game = data['GAME DATE'].values[0]
        most_recent_game = pd.to_datetime(most_recent_game)
        gamedate_obj = pd.to_datetime(gamedate)

        rest_days = (gamedate_obj - most_recent_game).days
        # get value for trad_season
        return rest_days

    missing_games['rest_days'] = missing_games.apply(lambda row: get_rest_days(row['trad_team'], row['trad_season'], row['trad_gamedate']), axis=1)
    missing_games['team2_rest_days'] = missing_games.apply(lambda row: get_rest_days(row['team_2'], row['trad_season'], row['trad_gamedate']), axis=1)

    # Injuries by Game
    player_trad_boxscores = pd.read_csv('data/player/aggregates/Trad&Adv_box_scores_GameView.csv')


    # Part 1
    cols = []
    data = player_trad_boxscores
    data['team_player'] = data['trad_team'] + '_' + data['trad_player']
    home_games = data.loc[data['trad_match up'].astype(str).str.contains('vs')]
    away_games = data.loc[data['trad_match up'].astype(str).str.contains('@')]

    # Fix so all games have the same format
    home_games['trad_match up'] = home_games['trad_match up'].astype(str).str[-3:] + ' @ ' + home_games['trad_match up'].astype(str).str[0:3]
    print(f' The shape of the DF: {home_games.shape}')

    data2 = pd.concat([home_games, away_games])


    # Add matchup_gamedate to data
    data2['Matchup_GameDate'] = data2['trad_match up'].astype(str) + '_' + data2['trad_game date'].astype(str).str.replace('/', '_')

    # Part 2
    # Get unique player names
    player_team_namez = data2['team_player'].unique()   

    # Add players as columns     
    for player_team in player_team_namez:                       
        data2[str(player_team) + '_played'] = np.where( data2['team_player'] == str(player_team), 1, 0)
        data2[str(player_team) + '_min'] = np.where( data2['team_player'] == str(player_team), data2['trad_min'], 0)
        cols2 = str(player_team) + '_min'
        cols.append(cols2)

    grouped = data2.groupby('Matchup_GameDate')[cols].sum()
    grouped.to_csv('data/player/aggregates/players_minutes_played_GBG.csv')

    grouped = grouped.reset_index()
    grouped = grouped.loc[:,~grouped.columns.duplicated()].copy()

    minutes_df = pd.read_csv('data/player/aggregates/players_minutes_played_GBG.csv')

    
    
    def get_matchup_gamedate(matchup, gamedate):

        # change gamedate to date
        gamedate = pd.to_datetime(gamedate)
        # change to MM_DD_YYYY
        gamedate = gamedate.strftime('%m_%d_%Y')

        gamedate = str(gamedate)

        if 'vs.' in matchup:
            matchup1 = matchup.replace('vs.', ' @ ')
            matchup2 = matchup1.replace('-', '_')
            gamedatey = gamedate.replace('-', '_')
            tm1 = matchup2.split(' @ ')[0]
            tm2 = matchup2.split(' @ ')[1]
            tm2 = tm2.replace(' ', '')
            tm1 = tm1.replace(' ', '')
            new_matchup = tm2 + ' @ ' + tm1 +'_' + gamedatey

        else:
            gamedate1 = gamedate.replace('-', '_')
            new_matchup = matchup + '_' + gamedate1
            
        return new_matchup
    
    missing_games['Matchup_GameDate'] = missing_games.apply(lambda row: get_matchup_gamedate(row['trad_matchup'], row['trad_gamedate']), axis=1)

    
    #### 2c update -- not much necessary
    trad_season_averages = pd.read_csv('data/player/aggregates_of_aggregates/trad_season_averages_imputed.csv')
    min_df = pd.read_csv('data/player/aggregates/players_minutes_played_GBG.csv')
    pm_df = pd.read_csv('data/player/aggregates_of_aggregates/Season_Averages_With_Player_Metric.csv')
    
    # date is last 10 digits of matchup gamedate
    min_df['date'] = min_df['Matchup_GameDate'].str[-10:]
    min_df['date'] = min_df['date'].astype(str).replace('_', '/', regex=True)
    min_df['date'] = pd.to_datetime(min_df['date'])
    min_df= min_df.sort_values(by=['date'], ascending=False)


    def get_home_minutes(matchup):

        #id matchup in min_df
        home_min = min_df[min_df['Matchup_GameDate'] == matchup]

        # get columns
        colz = home_min.columns

        # identify home team
        home_team = matchup[6:9]

        # get player columns for home team
        team_id = [col for col in colz if home_team in col]
        home_cols = ['Matchup_GameDate'] + team_id 
        home_min = home_min[home_cols]

        # change nans to 0
        home_min = home_min.fillna(0)


        # drop cols with 0's (i.e., player did not play)
        zeros = home_min.loc[:, (home_min == 0).any(axis=0)]
        home_min = home_min.drop(columns = zeros)
        
        # rename cols to get rid of team and min portions of the cols
        home_min.columns = [col.split('_')[1] for col in home_min.columns]

        # Add "Matchup_" back to Gamedate column name
        home_min.rename(columns={'GameDate': 'Matchup_GameDate'}, inplace=True)
        
        return home_min

    def get_away_minutes(matchup):
        
            #id matchup in min_df
            away_min = min_df[min_df['Matchup_GameDate'] == matchup]
            colz = away_min.columns
        
            # identify home team
            away_team = matchup[:3]
        
            # get player columns for home team
            team_id = [col for col in colz if away_team in col]
            away_cols = ['Matchup_GameDate'] + team_id 
            away_min = away_min[away_cols]
        
            # change NaNs to 0
            away_min = away_min.fillna(0)
        
            # drop cols with 0's (i.e., player did not play)
            zeros = away_min.loc[:, (away_min == 0).any(axis=0)]
            away_min = away_min.drop(columns = zeros)
            
            # rename cols to get rid of team and min portions of the cols
            away_min.columns = [col.split('_')[1] for col in away_min.columns]

            
            # Add "Matchup_" back to Gamedate column name
            away_min.rename(columns={'GameDate': 'Matchup_GameDate'}, inplace=True)

            return away_min

    def get_player_score(player, season):

        # ID Season
        season = int(season)
        get_season = season - 1

        # ID Player
        median_player_score = pm_df['PM_Player_Metric'].median()
        player_score = pm_df[pm_df['trad_player'] == player]
        player_score = player_score[player_score['trad_season'] == get_season]

        if player_score.empty:
            return median_player_score 
        else:
            player_score = player_score['PM_Player_Metric'].values[0]
            return round(player_score,2)


    # change trad_gamedate to mdy style
    missing_games['trad_gamedate_mdy'] = pd.to_datetime(missing_games['trad_gamedate'])
    missing_games['trad_gamedate_mdy'] = missing_games['trad_gamedate_mdy'].dt.strftime('%m/%d/%Y')
    missing_games['Matchup_GameDate_2'] = missing_games['trad_matchup'] + '_' + missing_games['trad_gamedate_mdy'].astype(str).str.replace('/','_')
    
    
    def score_home(matchup, cutoff):
        #Get home team minutes
        home_min = get_home_minutes(matchup)

        # Get matchup_gamedate value
        matchup_df = missing_games[missing_games['Matchup_GameDate'] == matchup].reset_index()

        # Get season
        season = matchup_df['trad_season'].values[0]
        get_season = int(season)
        home_player_cols = list(home_min.columns[1:])
        
        # for each player find score from previous year
        for col in home_player_cols:
            player = col
            home_min[col + '_score'] = get_player_score(player, get_season)
        
        # calculate final score
        # keep the top 8 scoring players
        score_cols = [col for col in home_min.columns if col.endswith('_score')]
        mincolz = home_min[score_cols]
        score_cols_df = pd.DataFrame(mincolz)
        score_cols_df = score_cols_df.T
        score_cols_df.columns = ['score']
        score_cols_df = score_cols_df.sort_values(by='score', ascending=False)
        # the cutoff is the number of players to include in the data
        score_cols_df = score_cols_df.head(cutoff)
        home_score = score_cols_df.sum()

        return home_score.values[0]


    missing_games.trad_season
    missing_games.Matchup_GameDate



    def score_away(matchup, cutoff):

        
            #Get away team minutes
            away_min = get_away_minutes(matchup)
        
            # Get matchup_gamedate value
            matchup_gdate  = away_min['Matchup_GameDate'].values[0]
            date_df = missing_games[missing_games['Matchup_GameDate'] == matchup_gdate].reset_index()
        
            # Get season
            season = date_df['trad_season'].values[0]
            get_season = int(season)
            away_player_cols = list(away_min.columns[1:])
            
            # for each player find score from previous year
            for col in away_player_cols:
                player = col
                away_min[col + '_score'] = get_player_score(player, get_season)
        
            # calculate final score
            # keep the top 8 scoring players
            score_cols = [col for col in away_min.columns if col.endswith('_score')]
            mincolz = away_min[score_cols]
            score_cols_df = pd.DataFrame(mincolz)
            score_cols_df = score_cols_df.T
            score_cols_df.columns = ['score']
            score_cols_df = score_cols_df.sort_values(by='score', ascending=False)
            # the cutoff is the number of players to include in the data
            score_cols_df = score_cols_df.head(cutoff)
            away_score = score_cols_df.sum()
        
            return away_score.values[0]


    def score_game(matchup, cutoff):
        try:
            if 'vs' in matchup:
                home_team = matchup[0:3]
                home_team = str(home_team)
                away_team = matchup[8:11]
                away_team = str(away_team)
                date = matchup[-10:]
                date = str(date)
                new_matchup = away_team + ' @ ' + home_team + '_' + date
                new_matchup = str(new_matchup)
                home_score = score_home(new_matchup, cutoff)
                away_score = score_away(new_matchup, cutoff)
                if home_score > away_score:
                    winner = home_team
                else:
                    winner = away_team
            else:
                home_team = matchup[6:9]
                home_team = str(home_team)
                away_team = matchup[0:3]
                away_team = str(away_team)
                home_score = score_home(matchup, cutoff)
                away_score = score_away(matchup, cutoff)
                if home_score > away_score:
                    winner = home_team
                else:
                    winner = away_team
            return winner
        except:
            return np.nan


    def get_net_score(team, matchup, cutoff):
        try:
            if 'vs' in matchup:
                home_team = matchup[0:3]
                home_team = str(home_team)
                away_team = matchup[8:11]
                away_team = str(away_team)
                date = matchup[-10:]
                date = str(date)
                new_matchup = away_team + ' @ ' + home_team + '_' + date
                new_matchup = str(new_matchup)
                home_score = score_home(new_matchup, cutoff)
                away_score = score_away(new_matchup, cutoff)

                if team == home_team:
                    net_score = home_score - away_score
                elif team == away_team:
                    net_score = away_score - home_score
                
                return net_score
            
            else:
                home_team = matchup[6:9]
                home_team = str(home_team)
                away_team = matchup[0:3]
                away_team = str(away_team)
                home_score = score_home(matchup, cutoff)
                away_score = score_away(matchup, cutoff)
                if team == home_team:
                    net_score = home_score - away_score
                elif team == away_team:
                    net_score = away_score - home_score
            return net_score

        except:
            return np.nan

    
    missing_games['net_score_top_4'] = missing_games.apply(lambda row: get_net_score(row['trad_team'], row['Matchup_GameDate'], 4), axis=1)
    # check nan
    missing_games[missing_games['net_score_top_4'].isna()]
    missing_games['net_score_top_4'] = missing_games.apply(lambda row: get_net_score(row['trad_team'], row['Matchup_GameDate'], 4), axis=1)
    missing_games['net_score_top_5'] = missing_games.apply(lambda row: get_net_score(row['trad_team'], row['Matchup_GameDate'], 5), axis=1)
    missing_games['net_score_top_6'] = missing_games.apply(lambda row: get_net_score(row['trad_team'], row['Matchup_GameDate'], 6), axis=1)
    missing_games['net_score_top_7'] = missing_games.apply(lambda row: get_net_score(row['trad_team'], row['Matchup_GameDate'], 7), axis=1)
    missing_games['net_score_top_8'] = missing_games.apply(lambda row: get_net_score(row['trad_team'], row['Matchup_GameDate'], 8), axis=1)
    missing_games
    missing_games['top_4_predicted_winner'] = np.where(missing_games['net_score_top_4'] > 0, 1, 0)
    missing_games['top_5_predicted_winner'] = np.where(missing_games['net_score_top_5'] > 0, 1, 0)
    missing_games['top_6_predicted_winner'] = np.where(missing_games['net_score_top_6'] > 0, 1, 0)
    missing_games['top_7_predicted_winner'] = np.where(missing_games['net_score_top_7'] > 0, 1, 0)
    missing_games['top_8_predicted_winner'] = np.where(missing_games['net_score_top_8'] > 0, 1, 0)
    # find colluns with date in them
    date_cols = [col for col in missing_games.columns if 'date' in col]



    ### 2d -- Needs NO updates
    ### 2e update
    df['trad_gamedate'] = pd.to_datetime(df['trad_gamedate'])
    missing_games['trad_gamedate'] = pd.to_datetime(missing_games['trad_gamedate'])

    def get_game_avgs(my_gameid, team, season, date, metric, game_num, agg_metric):
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

    
    missing_games['tm1_80_game_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 80, 'avg'), axis=1)
    missing_games['tm1_80_game_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 80, 'std'), axis=1)
    missing_games['tm1_80_game_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 80, 'avg'), axis=1)
    missing_games['tm1_80_game_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 80, 'std'), axis=1)
    missing_games['tm1_80_game_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 80, 'avg'), axis=1)
    missing_games['tm1_80_game_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 80, 'std'), axis=1)
    missing_games['tm2_80_game_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 80, 'avg'), axis=1)
    missing_games['tm2_80_game_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 80, 'std'), axis=1)
    missing_games['tm2_80_game_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 80, 'avg'), axis=1)
    missing_games['tm2_80_game_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 80, 'std'), axis=1)
    missing_games['tm2_80_game_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 80, 'avg'), axis=1)
    missing_games['tm2_80_game_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 80, 'std'), axis=1)
    missing_games['tm1_40_gm_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 40, 'avg'), axis=1)
    missing_games['tm1_40_gm_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 40, 'std'), axis=1)
    missing_games['tm1_40_gm_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 40, 'avg'), axis=1)
    missing_games['tm1_40_gm_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 40, 'std'), axis=1)
    missing_games['tm1_40_gm_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 40, 'avg'), axis=1)
    missing_games['tm1_40_gm_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 40, 'std'), axis=1)

    missing_games['tm2_40_gm_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 40, 'avg'), axis=1)
    missing_games['tm2_40_gm_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 40, 'std'), axis=1)
    missing_games['tm2_40_gm_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 40, 'avg'), axis=1)
    missing_games['tm2_40_gm_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 40, 'std'), axis=1)
    missing_games['tm2_40_gm_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 40, 'avg'), axis=1)
    missing_games['tm2_40_gm_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 40, 'std'), axis=1)

    missing_games['tm1_20_gm_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 20, 'avg'), axis=1)
    missing_games['tm1_20_gm_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 20, 'std'), axis=1)
    missing_games['tm1_20_gm_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 20, 'avg'), axis=1)
    missing_games['tm1_20_gm_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 20, 'std'), axis=1)
    missing_games['tm1_20_gm_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 20, 'avg'), axis=1)
    missing_games['tm1_20_gm_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 20, 'std'), axis=1)

    missing_games['tm2_20_gm_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 20, 'avg'), axis=1)
    missing_games['tm2_20_gm_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 20, 'std'), axis=1)
    missing_games['tm2_20_gm_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 20, 'avg'), axis=1)
    missing_games['tm2_20_gm_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 20, 'std'), axis=1)
    missing_games['tm2_20_gm_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 20, 'avg'), axis=1)
    missing_games['tm2_20_gm_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 20, 'std'), axis=1)

    missing_games['tm1_10_gm_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 10, 'avg'), axis=1)
    missing_games['tm1_10_gm_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 10, 'std'), axis=1)
    missing_games['tm1_10_gm_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 10, 'avg'), axis=1)
    missing_games['tm1_10_gm_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 10, 'std'), axis=1)
    missing_games['tm1_10_gm_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 10, 'avg'), axis=1)
    missing_games['tm1_10_gm_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 10, 'std'), axis=1)

    missing_games['tm2_10_gm_avg_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 10, 'avg'), axis=1)
    missing_games['tm2_10_gm_std_offrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_offrtg', 10, 'std'), axis=1)
    missing_games['tm2_10_gm_avg_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 10, 'avg'), axis=1)
    missing_games['tm2_10_gm_std_defrtg'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_defrtg', 10, 'std'), axis=1)
    missing_games['tm2_10_gm_avg_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 10, 'avg'), axis=1)
    missing_games['tm2_10_gm_std_pace'] = missing_games.apply(lambda row: get_game_avgs(row['Matchup_GameDate'], row['trad_team'], row['trad_season'], row['trad_gamedate_mdy'], 'adv_pace', 10, 'std'), axis=1)

    def get_NBA_avgs(my_gameid, season, date, metric, game_num, agg_metric):
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

    
    missing_games['nba_80_gm_avg_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'avg'), axis=1)
    missing_games['nba_80_gm_std_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 80, 'std'), axis=1)
    missing_games['nba_80_gm_avg_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'avg'), axis=1)
    missing_games['nba_80_gm_std_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 80, 'std'), axis=1)
    missing_games['nba_80_gm_avg_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'avg'), axis=1)
    missing_games['nba_80_gm_std_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 80, 'std'), axis=1)

    missing_games['nba_40_gm_avg_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'avg'), axis=1)
    missing_games['nba_40_gm_std_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 40, 'std'), axis=1)
    missing_games['nba_40_gm_avg_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'avg'), axis=1)
    missing_games['nba_40_gm_std_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 40, 'std'), axis=1)
    missing_games['nba_40_gm_avg_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'avg'), axis=1)
    missing_games['nba_40_gm_std_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 40, 'std'), axis=1)

    missing_games['nba_20_gm_avg_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'avg'), axis=1)
    missing_games['nba_20_gm_std_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 20, 'std'), axis=1)
    missing_games['nba_20_gm_avg_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'],  row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'avg'), axis=1)
    missing_games['nba_20_gm_std_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 20, 'std'), axis=1)
    missing_games['nba_20_gm_avg_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'],  row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'avg'), axis=1)
    missing_games['nba_20_gm_std_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'],  row['trad_season'], row['trad_gamedate'], 'adv_pace', 20, 'std'), axis=1)

    missing_games['nba_10_gm_avg_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'avg'), axis=1)
    missing_games['nba_10_gm_std_offrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_offrtg', 10, 'std'), axis=1)
    missing_games['nba_10_gm_avg_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'avg'), axis=1)
    missing_games['nba_10_gm_std_defrtg'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_defrtg', 10, 'std'), axis=1)
    missing_games['nba_10_gm_avg_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'avg'), axis=1)
    missing_games['nba_10_gm_std_pace'] = missing_games.apply(lambda row: get_NBA_avgs(row['Matchup_GameDate'], row['trad_season'], row['trad_gamedate'], 'adv_pace', 10, 'std'), axis=1)

    missing_games['80gm_tm1_minus_nba_avg_offrtg'] = missing_games['tm1_80_game_avg_offrtg'] - missing_games['nba_80_gm_avg_offrtg']
    missing_games['80gm_tm1_minus_nba_std_offrtg'] = missing_games['tm1_80_game_std_offrtg'] - missing_games['nba_80_gm_std_offrtg']
    missing_games['80gm_tm1_minus_nba_avg_defrtg'] = missing_games['tm1_80_game_avg_defrtg'] - missing_games['nba_80_gm_avg_defrtg']
    missing_games['80gm_tm1_minus_nba_std_defrtg'] = missing_games['tm1_80_game_std_defrtg'] - missing_games['nba_80_gm_std_defrtg']
    missing_games['80gm_tm1_minus_nba_avg_pace'] = missing_games['tm1_80_game_avg_pace'] - missing_games['nba_80_gm_avg_pace']
    missing_games['80gm_tm1_minus_nba_std_pace'] = missing_games['tm1_80_game_std_pace'] - missing_games['nba_80_gm_std_pace']
    missing_games['80gm_tm2_minus_nba_avg_offrtg'] = missing_games['tm2_80_game_avg_offrtg'] - missing_games['nba_80_gm_avg_offrtg']
    missing_games['80gm_tm2_minus_nba_std_offrtg'] = missing_games['tm2_80_game_std_offrtg'] - missing_games['nba_80_gm_std_offrtg']
    missing_games['80gm_tm2_minus_nba_avg_defrtg'] = missing_games['tm2_80_game_avg_defrtg'] - missing_games['nba_80_gm_avg_defrtg']
    missing_games['80gm_tm2_minus_nba_std_defrtg'] = missing_games['tm2_80_game_std_defrtg'] - missing_games['nba_80_gm_std_defrtg']
    missing_games['80gm_tm2_minus_nba_avg_pace'] = missing_games['tm2_80_game_avg_pace'] - missing_games['nba_80_gm_avg_pace']
    missing_games['80gm_tm2_minus_nba_std_pace'] = missing_games['tm2_80_game_std_pace'] - missing_games['nba_80_gm_std_pace']

    missing_games['40gm_tm1_minus_nba_avg_offrtg'] = missing_games['tm1_40_gm_avg_offrtg'] - missing_games['nba_40_gm_avg_offrtg']
    missing_games['40gm_tm1_minus_nba_std_offrtg'] = missing_games['tm1_40_gm_std_offrtg'] - missing_games['nba_40_gm_std_offrtg']
    missing_games['40gm_tm1_minus_nba_avg_defrtg'] = missing_games['tm1_40_gm_avg_defrtg'] - missing_games['nba_40_gm_avg_defrtg']
    missing_games['40gm_tm1_minus_nba_std_defrtg'] = missing_games['tm1_40_gm_std_defrtg'] - missing_games['nba_40_gm_std_defrtg']
    missing_games['40gm_tm1_minus_nba_avg_pace'] = missing_games['tm1_40_gm_avg_pace'] - missing_games['nba_40_gm_avg_pace']
    missing_games['40gm_tm1_minus_nba_std_pace'] = missing_games['tm1_40_gm_std_pace'] - missing_games['nba_40_gm_std_pace']

    missing_games['40gm_tm2_minus_nba_avg_offrtg'] = missing_games['tm2_40_gm_avg_offrtg'] - missing_games['nba_40_gm_avg_offrtg']
    missing_games['40gm_tm2_minus_nba_std_offrtg'] = missing_games['tm2_40_gm_std_offrtg'] - missing_games['nba_40_gm_std_offrtg']
    missing_games['40gm_tm2_minus_nba_avg_defrtg'] = missing_games['tm2_40_gm_avg_defrtg'] - missing_games['nba_40_gm_avg_defrtg']
    missing_games['40gm_tm2_minus_nba_std_defrtg'] = missing_games['tm2_40_gm_std_defrtg'] - missing_games['nba_40_gm_std_defrtg']
    missing_games['40gm_tm2_minus_nba_avg_pace'] = missing_games['tm2_40_gm_avg_pace'] - missing_games['nba_40_gm_avg_pace']
    missing_games['40gm_tm2_minus_nba_std_pace'] = missing_games['tm2_40_gm_std_pace'] - missing_games['nba_40_gm_std_pace']

    missing_games['20gm_tm1_minus_nba_avg_offrtg'] = missing_games['tm1_20_gm_avg_offrtg'] - missing_games['nba_20_gm_avg_offrtg']
    missing_games['20gm_tm1_minus_nba_std_offrtg'] = missing_games['tm1_20_gm_std_offrtg'] - missing_games['nba_20_gm_std_offrtg']
    missing_games['20gm_tm1_minus_nba_avg_defrtg'] = missing_games['tm1_20_gm_avg_defrtg'] - missing_games['nba_20_gm_avg_defrtg']
    missing_games['20gm_tm1_minus_nba_std_defrtg'] = missing_games['tm1_20_gm_std_defrtg'] - missing_games['nba_20_gm_std_defrtg']
    missing_games['20gm_tm1_minus_nba_avg_pace'] = missing_games['tm1_20_gm_avg_pace'] - missing_games['nba_20_gm_avg_pace']
    missing_games['20gm_tm1_minus_nba_std_pace'] = missing_games['tm1_20_gm_std_pace'] - missing_games['nba_20_gm_std_pace']

    missing_games['20gm_tm2_minus_nba_avg_offrtg'] = missing_games['tm2_20_gm_avg_offrtg'] - missing_games['nba_20_gm_avg_offrtg']
    missing_games['20gm_tm2_minus_nba_std_offrtg'] = missing_games['tm2_20_gm_std_offrtg'] - missing_games['nba_20_gm_std_offrtg']
    missing_games['20gm_tm2_minus_nba_avg_defrtg'] = missing_games['tm2_20_gm_avg_defrtg'] - missing_games['nba_20_gm_avg_defrtg']
    missing_games['20gm_tm2_minus_nba_std_defrtg'] = missing_games['tm2_20_gm_std_defrtg'] - missing_games['nba_20_gm_std_defrtg']
    missing_games['20gm_tm2_minus_nba_avg_pace'] = missing_games['tm2_20_gm_avg_pace'] - missing_games['nba_20_gm_avg_pace']
    missing_games['20gm_tm2_minus_nba_std_pace'] = missing_games['tm2_20_gm_std_pace'] - missing_games['nba_20_gm_std_pace']

    missing_games['10gm_tm1_minus_nba_avg_offrtg'] = missing_games['tm1_10_gm_avg_offrtg'] - missing_games['nba_10_gm_avg_offrtg']
    missing_games['10gm_tm1_minus_nba_std_offrtg'] = missing_games['tm1_10_gm_std_offrtg'] - missing_games['nba_10_gm_std_offrtg']
    missing_games['10gm_tm1_minus_nba_avg_defrtg'] = missing_games['tm1_10_gm_avg_defrtg'] - missing_games['nba_10_gm_avg_defrtg']
    missing_games['10gm_tm1_minus_nba_std_defrtg'] = missing_games['tm1_10_gm_std_defrtg'] - missing_games['nba_10_gm_std_defrtg']
    missing_games['10gm_tm1_minus_nba_avg_pace'] = missing_games['tm1_10_gm_avg_pace'] - missing_games['nba_10_gm_avg_pace']
    missing_games['10gm_tm1_minus_nba_std_pace'] = missing_games['tm1_10_gm_std_pace'] - missing_games['nba_10_gm_std_pace']

    missing_games['10gm_tm2_minus_nba_avg_offrtg'] = missing_games['tm2_10_gm_avg_offrtg'] - missing_games['nba_10_gm_avg_offrtg']
    missing_games['10gm_tm2_minus_nba_std_offrtg'] = missing_games['tm2_10_gm_std_offrtg'] - missing_games['nba_10_gm_std_offrtg']
    missing_games['10gm_tm2_minus_nba_avg_defrtg'] = missing_games['tm2_10_gm_avg_defrtg'] - missing_games['nba_10_gm_avg_defrtg']
    missing_games['10gm_tm2_minus_nba_std_defrtg'] = missing_games['tm2_10_gm_std_defrtg'] - missing_games['nba_10_gm_std_defrtg']
    missing_games['10gm_tm2_minus_nba_avg_pace'] = missing_games['tm2_10_gm_avg_pace'] - missing_games['nba_10_gm_avg_pace']
    missing_games['10gm_tm2_minus_nba_std_pace'] = missing_games['tm2_10_gm_std_pace'] - missing_games['nba_10_gm_std_pace']

    missing_games['Tm1_Points_Estimate_80gm'] = ((missing_games['tm1_80_game_avg_pace'] + missing_games['tm2_80_game_avg_pace'])/2) * ((missing_games['tm1_80_game_avg_offrtg'] - (missing_games['tm1_80_game_avg_defrtg'] - missing_games['nba_80_gm_avg_defrtg'])))/100
    missing_games['Tm2_Points_Estimate_80gm'] = ((missing_games['tm1_80_game_avg_pace'] + missing_games['tm2_80_game_avg_pace'])/2) * ((missing_games['tm2_80_game_avg_offrtg'] - (missing_games['tm2_80_game_avg_defrtg'] - missing_games['nba_80_gm_avg_defrtg'])))/100
    missing_games['Estimate_Points_Difference_80gm'] = missing_games['Tm1_Points_Estimate_80gm'] - missing_games['Tm2_Points_Estimate_80gm']

    missing_games['Tm1_Points_Estimate_40gm'] = ((missing_games['tm1_40_gm_avg_pace'] + missing_games['tm2_40_gm_avg_pace'])/2) * ((missing_games['tm1_40_gm_avg_offrtg'] - (missing_games['tm1_40_gm_avg_defrtg'] - missing_games['nba_40_gm_avg_defrtg'])))/100
    missing_games['Tm2_Points_Estimate_40gm'] = ((missing_games['tm1_40_gm_avg_pace'] + missing_games['tm2_40_gm_avg_pace'])/2) * ((missing_games['tm2_40_gm_avg_offrtg'] - (missing_games['tm2_40_gm_avg_defrtg'] - missing_games['nba_40_gm_avg_defrtg'])))/100
    missing_games['Estimate_Points_Difference_40gm'] = missing_games['Tm1_Points_Estimate_40gm'] - missing_games['Tm2_Points_Estimate_40gm']

    missing_games['Tm1_Points_Estimate_20gm'] = ((missing_games['tm1_20_gm_avg_pace'] + missing_games['tm2_20_gm_avg_pace'])/2) * ((missing_games['tm1_20_gm_avg_offrtg'] - (missing_games['tm1_20_gm_avg_defrtg'] - missing_games['nba_20_gm_avg_defrtg'])))/100
    missing_games['Tm2_Points_Estimate_20gm'] = ((missing_games['tm1_20_gm_avg_pace'] + missing_games['tm2_20_gm_avg_pace'])/2) * ((missing_games['tm2_20_gm_avg_offrtg'] - (missing_games['tm2_20_gm_avg_defrtg'] - missing_games['nba_20_gm_avg_defrtg'])))/100
    missing_games['Estimate_Points_Difference_20gm'] = missing_games['Tm1_Points_Estimate_20gm'] - missing_games['Tm2_Points_Estimate_20gm']

    missing_games['Tm1_Points_Estimate_10gm'] = ((missing_games['tm1_10_gm_avg_pace'] + missing_games['tm2_10_gm_avg_pace'])/2) * ((missing_games['tm1_10_gm_avg_offrtg'] - (missing_games['tm1_10_gm_avg_defrtg'] - missing_games['nba_10_gm_avg_defrtg'])))/100
    missing_games['Tm2_Points_Estimate_10gm'] = ((missing_games['tm1_10_gm_avg_pace'] + missing_games['tm2_10_gm_avg_pace'])/2) * ((missing_games['tm2_10_gm_avg_offrtg'] - (missing_games['tm2_10_gm_avg_defrtg'] - missing_games['nba_10_gm_avg_defrtg'])))/100
    missing_games['Estimate_Points_Difference_10gm'] = missing_games['Tm1_Points_Estimate_10gm'] - missing_games['Tm2_Points_Estimate_10gm']

    # Weighted Average of the 4 estimates
    missing_games['Tm1_Points_Estimate_Weighted'] = missing_games['Tm1_Points_Estimate_80gm'] * 0.17 + missing_games['Tm1_Points_Estimate_40gm'] * 0.22 + missing_games['Tm1_Points_Estimate_20gm'] * 0.28 + missing_games['Tm1_Points_Estimate_10gm'] * 0.33
    missing_games['Tm2_Points_Estimate_Weighted'] = missing_games['Tm2_Points_Estimate_80gm'] * 0.17 + missing_games['Tm2_Points_Estimate_40gm'] * 0.22 + missing_games['Tm2_Points_Estimate_20gm'] * 0.28 + missing_games['Tm2_Points_Estimate_10gm'] * 0.33


    missing_games['Estimate_Points_Difference_Weighted'] = missing_games['Tm1_Points_Estimate_Weighted'] - missing_games['Tm2_Points_Estimate_Weighted']
    missing_games
    ### 2f update
    # load from csv
    bdb_df = pd.read_csv('data/team/aggregates/bigdataball_team_boxes.csv')
    bdb_df['date']= pd.to_datetime(bdb_df['DATE'])
    bdb_df['date'] = bdb_df['date'].dt.strftime('%Y-%m-%d')
    bdb_df.sort_values(by=['date'], ascending = False, inplace=True)
    bdb_df.head(10)
    bdb_df['opponent'] = bdb_df['Nba_com_team_2_abbrev']
    bdb_df.date = pd.to_datetime(bdb_df.date)
    # merge with missing games
    missing_games2 = pd.merge(missing_games, bdb_df, 
                                left_on= ['trad_team', 'trad_gamedate'], 
                                right_on= ['Nba_com_team_Abbrev', 'date'], 
                                how='left')

    ### Missing Columns
    # get columns in old_df_final that are not in missing_games2
    missing_games2_cols = missing_games2.columns
    old_df_final_cols = old_df_final.columns
    missing_cols = [col for col in old_df_final_cols if col not in missing_games2_cols]

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    missing_games2.to_csv('data/team/aggregates/daily_updates/'+str(today)+'.csv', index=False)
    
    
    ## Make an UPDATED DF

    # # drop min columns
    # to_drop  = ['Unnamed: 0.4',
    # 'Unnamed: 0.3',
    # 'Unnamed: 0.2',
    # 'Unnamed: 0.1',
    # 't1_running_trad_min',
    # 't1_running_adv_min',
    # 't1_running_four_min',
    # 't1_running_misc_min',
    # 't1_running_score_min',
    # 't2_running_trad_min',
    # 't2_running_adv_min',
    # 't2_running_four_min',
    # 't2_running_misc_min',
    # 't2_running_score_min',
    # 'running_t1-t2_trad_min',
    # 'running_t1-t2_adv_min',
    # 'running_t1-t2_four_min',
    # 'running_t1-t2_misc_min',
    # 'running_t1-t2_score_min',
    # 'league_running_trad_min',
    # 'league_running_adv_min',
    # 'league_running_four_min',
    # 'league_running_misc_min',
    # 'league_running_score_min',
    # 't1_league_delta_trad_min',
    # 't1_league_delta_adv_min',
    # 't1_league_delta_four_min',
    # 't1_league_delta_misc_min',
    # 't1_league_delta_score_min',
    # 't2_league_delta_trad_min',
    # 't2_league_delta_adv_min',
    # 't2_league_delta_four_min',
    # 't2_league_delta_misc_min',
    # 't2_league_delta_score_min',
    # 't1_delta_minus_t2_delta_trad_min',
    # 't1_delta_minus_t2_delta_adv_min',
    # 't1_delta_minus_t2_delta_four_min',
    # 't1_delta_minus_t2_delta_misc_min',
    # 't1_delta_minus_t2_delta_score_min',
    # 'win?',
    # 'DATASET',
    # 'MAIN REF',
    # 'CREW',
    # 'Opp_abbrev',
    # 'Nba_com_team_Abbrev.1',
    # 'date_y',
    # 'my_gameid']


    # # if any col in old_df_final is in to_drop, drop it
    # for col in old_df_final.columns:
    #     if col in to_drop:
    #         old_df_final.drop(col, axis=1, inplace=True)

    # find columns in old_df_final that are not in missing_games2
    missing_games2_cols = missing_games2.columns
    old_df_final_cols = old_df_final.columns
    missing_cols = [col for col in old_df_final_cols if col not in missing_games2_cols]

    old_df_final.rename(columns={'date_x' : 'date' }, inplace=True)
    missing_games2.rename(columns={'Matchup_GameDate_y' : 'Matchup_GameDate' }, inplace=True)

    # find columns in old_df_final that are not in missing_games2
    missing_games2_cols = missing_games2.columns
    old_df_final_cols = old_df_final.columns
    missing_cols = [col for col in old_df_final_cols if col not in missing_games2_cols]

    # Save as updated_all_things_(+ date)
    # append missing_games2 to old_df_final

    updated_df = old_df_final.append(missing_games2, ignore_index=True)
    # turn date to datetime
    updated_df['date'] = pd.to_datetime(updated_df['date'])

    updated_df.sort_values(by=['date'], ascending = False, inplace=True)

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    # save as csv
    updated_df.to_csv('data/team/aggregates/daily_updates/Updated_All_Things_' + str(today) +'.csv', index=False)

    print('Job Done!')