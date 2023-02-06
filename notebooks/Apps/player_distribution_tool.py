import requests
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import datetime
import os
import sys
import nba_api
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.stats.static import teams 
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.endpoints import CommonPlayerInfo
# turn off warnings
import warnings
warnings.filterwarnings('ignore')
import streamlit as st

# set up the page
st.title('NBA Player Distribution Tool')
st.write('This tool allows you to visualize the distribution of a player\'s points, rebounds, and assists over the course of a season or their career.')
st.write('To get started, select a player from the sidebar.')
st.write('Then, select a timeframe from the sidebar.')
st.write('')

home = 'C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1'
# Get current nba rosters 
current_rosters = pd.read_csv(home + '/data/team/Current_Rosters/0_All_rosters.csv')

teams = current_rosters.team.unique()
teams = sorted(teams)

# SELECT OTHER PLAYER
player_dict = players.get_players()
# get only players currently playing
player_dict = [player for player in player_dict if player['is_active'] == True]


# make checkbox for choose by team
st.sidebar.write('Choose by Team?')
choose_by_team = st.sidebar.checkbox('Yes/No')
if choose_by_team:
    st.sidebar.write('Select a team')
    selected_team = st.sidebar.selectbox('Team', teams)
    st.sidebar.write('Select a player')
    team_players = current_rosters[current_rosters['team'] == selected_team]['Player'].unique()
    selected_player = st.sidebar.selectbox('Player', team_players)
    # show roster
    st.sidebar.write('Roster')
    st.sidebar.write(team_players)

    
else:
    # make sidebar for player selection
    st.sidebar.write('Select a player')
    selected_player = st.sidebar.selectbox('Player', [player['full_name'] for player in player_dict])

# make sidebar for date selection

st.sidebar.write('Select a date range')
date_options = ['2018-10-01', '2019-10-01', '2020-10-01', '2021-10-01', '2022-10-01']

date_start = st.sidebar.selectbox('Start Date', date_options)

# get current players
player = [player for player in player_dict if player['full_name'] == selected_player][0]
player_id = player['id']
gamelog_player_all = playergamelog.PlayerGameLog(player_id=player_id, season = SeasonAll.all)

df_player_games_all = gamelog_player_all.get_data_frames()
df_player_games_all = df_player_games_all[0]
df_player_games_all['GAME_DATE'] = pd.to_datetime(df_player_games_all['GAME_DATE'])
df_player_games_all= df_player_games_all[df_player_games_all['GAME_DATE'] > date_start]
df_player_games_all['SEASON_ID'] = df_player_games_all['SEASON_ID'].astype(str)
df_player_games_all['SEASON_ID'] = df_player_games_all['SEASON_ID'].str[1:]
# drop Game_ID, GAME_DATE, PLAYER_ID
df_player_games_all = df_player_games_all.drop(['Game_ID', 'Player_ID', 'VIDEO_AVAILABLE'], axis=1)


# make three columns
col1, col2, col3 = st.columns(3)

# violin plot points
with col1:
    st.write('Points by Season')
    fig, ax = plt.subplots()
    sns.violinplot(y='PTS', x = 'SEASON_ID', data=df_player_games_all)
    st.pyplot(fig)

# violin plot rebounds
with col2:
    st.write('Rebounds by Season')
    fig, ax = plt.subplots()
    sns.violinplot(y='REB', x = 'SEASON_ID', data=df_player_games_all)
    st.pyplot(fig)

# violin plot assists
with col3:
    st.write('Assists by Season')
    fig, ax = plt.subplots()
    sns.violinplot(y='AST', x = 'SEASON_ID', data=df_player_games_all)
    st.pyplot(fig)

st.set_option('deprecation.showPyplotGlobalUse', False)


# make three columns
col1, col2, col3 = st.columns(3)
with col1:
    st.write('Points vs Minutes')
    sns.jointplot(x=df_player_games_all['MIN'], y=df_player_games_all['PTS'],kind="reg")
    st.pyplot()

with col2:
    st.write('Rebounds vs Minutes')
    sns.jointplot(x='MIN', y='REB', data=df_player_games_all, kind= 'reg', truncate = False, color = 'm', height = 7)
    st.pyplot()

with col3:
    st.write('Assists vs Minutes')
    sns.jointplot(x='MIN', y='AST', data=df_player_games_all, kind= 'reg', truncate = False, color = (45/255, 50/255, 196/255, 0.6), height = 7)
    st.pyplot()


# make three columns
col1, col2, col3 = st.columns(3)
with col1:
    # make histogram of points
    st.write('Points')
    fig, ax = plt.subplots()
    sns.histplot(df_player_games_all['PTS'], kde = True)
    st.pyplot(fig)

with col2:
    # make histogram of rebounds
    st.write('Rebounds')
    fig, ax = plt.subplots()
    sns.histplot(df_player_games_all['REB'], kde = True, color = 'm')
    st.pyplot(fig)

with col3:
    # make histogram of assists
    st.write('Assists')
    fig, ax = plt.subplots()
    sns.histplot(df_player_games_all['AST'], kde = True, color = (45/255, 50/255, 196/255, 0.6))
    st.pyplot(fig)
    

import matplotlib.dates as mdates

st.subheader('Last 20 Games')
last_20 = df_player_games_all.head(20)
st.write(last_20)

# Season averages
st.write('Averages for 2022 Season')
sea_avg_1 = df_player_games_all.mean()
# transpose
sea_avg = sea_avg_1.to_frame().T
cols_to_keep = ['PTS', 'REB', 'AST', 'MIN', 'FG3M', 'FG3_PCT', 'FGA', 'FG_PCT', 'FTA', 'FT_PCT', 'STL', 'BLK', 'TOV', 'PF', 'PLUS_MINUS']
sea_avg = sea_avg[cols_to_keep]
sea_avg['data_type'] = '2022 Season Averages'

last_20_avg = last_20.mean()
last_20_avg = last_20_avg.to_frame().T
last_20_avg = last_20_avg[cols_to_keep]
last_20_avg['data_type'] = 'Last 20 Games Averages'
# add to sea_avg
sea_avg = sea_avg.append(last_20_avg)

# new row, difference between last 20 games and season average
diff2 = pd.DataFrame()
for col in cols_to_keep:
    diff2[col] = last_20_avg[col] / sea_avg_1[col] -1
diff2['data_type'] = 'Difference'
# drop last row

sea_avg = sea_avg.append(diff2)
#drop if PTS is 0.00
sea_avg = sea_avg[sea_avg['PTS'] != 0.00]

# Last 6 games
last_6 = df_player_games_all.head(6)
last_6_avg = last_6.mean()
last_6_avg = last_6_avg.to_frame().T
last_6_avg = last_6_avg[cols_to_keep]
last_6_avg['data_type'] = 'Last 6 Games Averages'
# add to sea_avg
sea_avg = sea_avg.append(last_6_avg)

st.dataframe(sea_avg.style.format(subset = cols_to_keep, formatter='{:.2f}'))

col1, col2, col3 = st.columns(3)
with col1:
    st.write('Points')
    fig, ax = plt.subplots()
    sns.histplot(last_20['PTS'], kde = True)
    st.pyplot(fig)

with col2:
    st.write('Rebounds')
    fig, ax = plt.subplots()
    sns.histplot(last_20['REB'], kde = True, color = 'm')
    st.pyplot(fig)

with col3:
    st.write('Assists')
    fig, ax = plt.subplots()
    sns.histplot(last_20['AST'], kde = True, color = (45/255, 50/255, 196/255, 0.6))
    st.pyplot(fig)

last_20['date'] = last_20['GAME_DATE'].dt.strftime('%m/%d')
last_20.sort_values(by='GAME_DATE', inplace=True)

st.subheader('MPG and Points last 20 games')
# plot minutes per game and points per game in the same plot, with both colors opaque
fig, ax = plt.subplots()
ax.bar(last_20['date'], last_20['MIN'], color = 'b', alpha = 0.5)
ax.bar(last_20['date'], last_20['PTS'], color = 'r', alpha = 0.5)
ax.set_xlabel('Date')
ax.set_ylabel('Minutes/Points')
# set x ticks at 45 degree angle
plt.xticks(rotation=45)
# set x ticks smaller
plt.xticks(fontsize=8)
ax.set_title('Minutes and Points last 20 games')
ax.legend(['Minutes', 'Points'])
st.pyplot(fig)



st.subheader('All Stats last 20 games')
# Add horizontal boxplot with observations
fig, ax = plt.subplots(figsize = (10, 10))
stats_to_plot = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'MIN', 'FGA', 'FTA', 'OREB', 'DREB', 'PLUS_MINUS']
sns.boxplot(data=last_20[stats_to_plot], orient="h", color = "lightgrey")
sns.stripplot(data=last_20[stats_to_plot], orient="h", color="black", alpha=0.3)
st.pyplot(fig)

st.subheader('VS Opponent...')
# make a dropdown for the opponent
all_matchups = df_player_games_all['MATCHUP'].unique()
all_matchups = pd.DataFrame(all_matchups, columns=['Matchup'])
all_matchups['Opponent'] = all_matchups['Matchup'].str[-3:0]
df_player_games_all['Opponent'] = df_player_games_all['MATCHUP'].str[-3:]

opponent_options = df_player_games_all['Opponent'].unique()
# sort alphabetically
opponent_options = sorted(opponent_options)

opponent = st.selectbox('Choose an opponent', opponent_options)

opponent_df = df_player_games_all[df_player_games_all['MATCHUP'].str.contains(opponent)]


st.dataframe(opponent_df)

# Chart points, rebounds, assists, and minutes
col1, col2, col3 = st.columns(3)
with col1:
    st.write('Points')
    fig, ax = plt.subplots()
    sns.histplot(opponent_df['PTS'], kde = True)
    st.pyplot(fig)

with col2:
    st.write('Rebounds')
    fig, ax = plt.subplots()
    sns.histplot(opponent_df['REB'], kde = True, color = 'm')
    st.pyplot(fig)

with col3:
    st.write('Assists')
    fig, ax = plt.subplots()
    sns.histplot(opponent_df['AST'], kde = True, color = (45/255, 50/255, 196/255, 0.6))
    st.pyplot(fig)

# import plotly
import plotly.express as px

# make plotly chart of points, rebounds, assists, and minutes by date
fig = px.line(opponent_df, x='GAME_DATE', y=['PTS', 'REB', 'AST', 'MIN'])
fig.update_layout(title = 'Points, Rebounds, Assists, and Minutes by Date')
st.plotly_chart(fig)


# HOME vs AWAY
st.subheader('HOME vs AWAY')

df_player_games_all['home_away'] = np.where(df_player_games_all['MATCHUP'].str.contains('vs'), 'Home', 'Away')

# with plotly, make a distribution chart of points by home/away
import plotly.figure_factory as ff
home_pts = df_player_games_all[df_player_games_all['home_away'] == 'Home']['PTS']
away_pts = df_player_games_all[df_player_games_all['home_away'] == 'Away']['PTS']
hist_data = [home_pts, away_pts]
group_labels = ['Home', 'Away']
fig = ff.create_distplot(hist_data, group_labels, bin_size=2, show_rug=False)
st.plotly_chart(fig)

# show distributions of points, rebounds, assists, and minutes by home/away with violin plot with plotly
fig = px.violin(df_player_games_all, y="PTS", x="home_away", box=True, points="all", hover_data=df_player_games_all.columns)
# add color to layout
fig.update_layout(title = 'Points by Home/Away')
# make two colors


st.plotly_chart(fig)




