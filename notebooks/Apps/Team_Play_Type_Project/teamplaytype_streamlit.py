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
os.chdir('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\Apps\\Team_Play_Type_Project')

from bs4 import BeautifulSoup
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

home = 'C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\'


today = datetime.date.today()
today = today.strftime('%Y-%m-%d')



iso = home + 'data/team/Playtypes/isolation_offense' + today + '.csv'
if os.path.exists(iso):
    st.write('Data Appears to be up to date')
    pass
else:
    os.system('C:\\Users\\Travis\\OneDrive\\Data Science\\Personal_Projects\\Sports\\NBA_Prediction_V3_1\\notebooks_v3_1\\Apps\\Team_Play_Type_Project\\team_playtype_scrape.py')



st.sidebar.title('NBA Team Play Type Analysis')

#second = st.sidebar.checkbox('Add Second Team?')

    # load data where the data SHOULD be
isolation = pd.read_csv(home + 'data/team/Playtypes/isolation_offense' + today + '.csv')
postup = pd.read_csv(home + 'data/team/Playtypes/postup_offense' + today + '.csv')
prb = pd.read_csv(home + 'data/team/Playtypes/prb_offense' + today + '.csv')
pnr = pd.read_csv(home + 'data/team/Playtypes/pnr_offense' + today + '.csv')
spotup = pd.read_csv(home + 'data/team/Playtypes/spotup_offense' + today + '.csv')
handoff = pd.read_csv(home + 'data/team/Playtypes/handoff_offense' + today + '.csv')
cut = pd.read_csv(home + 'data/team/Playtypes/cut_offense' + today + '.csv')
offscreen = pd.read_csv(home + 'data/team/Playtypes/offscreen_offense' + today + '.csv')
transition = pd.read_csv(home + 'data/team/Playtypes/transition_offense' + today + '.csv')
putbacks = pd.read_csv(home + 'data/team/Playtypes/putbacks_offense' + today + '.csv')
misc = pd.read_csv(home + 'data/team/Playtypes/misc_offense' + today + '.csv')

# defensive data
isolation_def = pd.read_csv(home + 'data/team/Playtypes/isolation_defense' + today + '.csv')
postup_def = pd.read_csv(home + 'data/team/Playtypes/postup_defense' + today + '.csv')
prb_def = pd.read_csv(home + 'data/team/Playtypes/prb_defense' + today + '.csv')
pnr_def = pd.read_csv(home + 'data/team/Playtypes/pnr_defense' + today + '.csv')
spotup_def = pd.read_csv(home + 'data/team/Playtypes/spotup_defense' + today + '.csv')
handoff_def = pd.read_csv(home + 'data/team/Playtypes/handoff_defense' + today + '.csv')
cut_def = pd.read_csv(home + 'data/team/Playtypes/cut_defense' + today + '.csv')
offscreen_def = pd.read_csv(home + 'data/team/Playtypes/offscreen_defense' + today + '.csv')
transition_def = pd.read_csv(home + 'data/team/Playtypes/transition_defense' + today + '.csv')
putbacks_def = pd.read_csv(home + 'data/team/Playtypes/putbacks_defense' + today + '.csv')
misc_def = pd.read_csv(home + 'data/team/Playtypes/misc_defense' + today + '.csv')


# all offensive / defensive data
the_files = os.listdir(home + 'data/team/Playtypes')
off_files = [f for f in the_files if 'offense' in f]
off_files = [f for f in off_files if today in f]
def_files = [f for f in the_files if 'defense' in f]
def_files = [f for f in def_files if today in f]

playtype_list = ['isolation', 'postup', 'prb', 'pnr', 'spotup', 'handoff', 'cut', 'offscreen', 'transition', 'putbacks', 'misc']


teams = isolation['TEAM'].unique()
# drop nan
teams = teams[~pd.isnull(teams)]


pt = st.sidebar.selectbox('Choose Playtype to view NBA Team Scatter Plot', playtype_list)

if pt == 'isolation':
    df = isolation
    df_def = isolation_def
elif pt == 'postup':
    df = postup
    df_def = postup_def
elif pt == 'prb':
    df = prb
    df_def = prb_def
elif pt == 'pnr':
    df = pnr
    df_def = pnr_def
elif pt == 'spotup':
    df = spotup
    df_def = spotup_def
elif pt == 'handoff':
    df = handoff
    df_def = handoff_def
elif pt == 'cut':
    df = cut
    df_def = cut_def
elif pt == 'offscreen':
    df = offscreen
    df_def = offscreen_def
elif pt == 'transition':
    df = transition
    df_def = transition_def
elif pt == 'putbacks':
    df = putbacks
    df_def = putbacks_def
elif pt == 'misc':
    df = misc
    df_def = misc_def

st.subheader('NBA Team Offensive Playtype Scatter Plot')
st.write('Select the playtype you would like to view from the sidebar. It automatically defaults to isolation.')

# plotly scatter plot of team playtype PPP

fig = px.scatter(df, x = 'FREQ%', y = 'PPP', color = 'PPP', 
                    hover_name = 'TEAM', text= 'TEAM', title = pt + ' PPP')
fig.update_layout(
    xaxis_title = 'Frequency of Playtype',
    yaxis_title = 'Points Per Play',
    font = dict(
        family = 'Courier New, monospace',
        size = 14,
        color = '#7f7f7f'
    )
)
fig.update_traces(textposition='top center')

st.plotly_chart(fig)

selected_team = st.sidebar.selectbox('Choose Team to Analyze', teams)
st.subheader('Selected Team: ' + selected_team + ' Offense')

#if second == True:
   # team2 = st.sidebar.selectbox('Select Second Team', options = teams)



data = home + 'data/team/Playtypes/offensive_playtypes/' + today + '.csv'
df1 = pd.read_csv(data)
team_offensive_playtype = df1[df1['TEAM'] == selected_team]
# move the 'playtype' column to the front
cols = team_offensive_playtype.columns.tolist()
cols.remove('play_type')
new_cols = ['play_type'] + cols
team_offensive_playtype = team_offensive_playtype[new_cols]
team_offensive_playtype = team_offensive_playtype.sort_values(by = 'FREQ%', ascending = False).reset_index(drop = True)

# drop the misc playtype
team_offensive_playtype = team_offensive_playtype[team_offensive_playtype['play_type'] != 'misc']


# plot the selected team's playtype PPP vs FREQ%
fig = px.scatter(team_offensive_playtype, x = 'play_type', y = 'PPP', color = 'FREQ%', size = 'FREQ%',
                    hover_name = 'play_type', title = selected_team + ' Playtype PPP')
fig.update_layout(
    xaxis_title = 'Playtype',
    yaxis_title = 'Points Per Play',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)

see_df2 = st.checkbox('Show Offensive Data')
if see_df2:
    st.dataframe(team_offensive_playtype)


#################     DEFENSIVE DATA      #################################

st.subheader('Selected Team: ' + selected_team + ' Defense')
data = home + 'data/team/Playtypes/defensive_playtypes/' + today + '.csv'
df2 = pd.read_csv(data)
team_defensive_playtype = df2[df2['TEAM'] == selected_team]
# move the 'playtype' column to the front
cols = team_defensive_playtype.columns.tolist()
cols.remove('play_type')
new_cols = ['play_type'] + cols
team_defensive_playtype = team_defensive_playtype[new_cols]
team_defensive_playtype = team_defensive_playtype.sort_values(by = 'FREQ%', ascending = False).reset_index(drop = True)
# DROP THE MISC PLAYTYPE
team_defensive_playtype = team_defensive_playtype[team_defensive_playtype['play_type'] != 'misc']

# plot barchart of teams defensive playtype PPP
fig = px.scatter(team_defensive_playtype, x = 'play_type', y = 'PPP', color = 'FREQ%', size = 'FREQ%',
                    hover_name = 'play_type', title = selected_team + ' Defensive Playtype PPP')
fig.update_layout(
    xaxis_title = 'Points Per Play',
    yaxis_title = '',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)

see_df = st.checkbox('Show Defensive Data')
if see_df:
    st.dataframe(team_defensive_playtype)


#################   DATA COMPARISON   #################################

# get average PPP for each playtype on offense
avg_ppp = df1.groupby('play_type')['PPP'].mean().reset_index()
avg_ppp = avg_ppp.sort_values(by = 'PPP', ascending = False).reset_index(drop = True)
#st.dataframe(avg_ppp)

avg_cut = avg_ppp[avg_ppp['play_type'] == 'cut']['PPP'].values[0]
avg_handoff = avg_ppp[avg_ppp['play_type'] == 'handoff']['PPP'].values[0]
avg_isolation = avg_ppp[avg_ppp['play_type'] == 'isolation']['PPP'].values[0]
avg_offscreen = avg_ppp[avg_ppp['play_type'] == 'offscreen']['PPP'].values[0]
avg_postup = avg_ppp[avg_ppp['play_type'] == 'postup']['PPP'].values[0]
avg_prb = avg_ppp[avg_ppp['play_type'] == 'prb']['PPP'].values[0]
avg_pnr = avg_ppp[avg_ppp['play_type'] == 'pnr']['PPP'].values[0]
avg_putbacks = avg_ppp[avg_ppp['play_type'] == 'putbacks']['PPP'].values[0]
avg_spotup = avg_ppp[avg_ppp['play_type'] == 'spotup']['PPP'].values[0]
avg_transition = avg_ppp[avg_ppp['play_type'] == 'transition']['PPP'].values[0]

# now defense
avg_ppp_def = df2.groupby('play_type')['PPP'].mean().reset_index()
avg_ppp_def = avg_ppp_def.sort_values(by = 'PPP', ascending = False).reset_index(drop = True)
#st.dataframe(avg_ppp_def)

avg_cut_def = avg_ppp_def[avg_ppp_def['play_type'] == 'cut']['PPP'].values[0]
avg_handoff_def = avg_ppp_def[avg_ppp_def['play_type'] == 'handoff']['PPP'].values[0]
avg_isolation_def = avg_ppp_def[avg_ppp_def['play_type'] == 'isolation']['PPP'].values[0]
avg_offscreen_def = avg_ppp_def[avg_ppp_def['play_type'] == 'offscreen']['PPP'].values[0]
avg_postup_def = avg_ppp_def[avg_ppp_def['play_type'] == 'postup']['PPP'].values[0]
avg_prb_def = avg_ppp_def[avg_ppp_def['play_type'] == 'prb']['PPP'].values[0]
avg_pnr_def = avg_ppp_def[avg_ppp_def['play_type'] == 'pnr']['PPP'].values[0]
avg_putbacks_def = avg_ppp_def[avg_ppp_def['play_type'] == 'putbacks']['PPP'].values[0]
avg_spotup_def = avg_ppp_def[avg_ppp_def['play_type'] == 'spotup']['PPP'].values[0]
avg_transition_def = avg_ppp_def[avg_ppp_def['play_type'] == 'transition']['PPP'].values[0]


# plot team defensive PPP vs average PPP as a shadow bar
fig = go.Figure()
fig.add_trace(go.Bar(x = team_defensive_playtype['play_type'], y = team_defensive_playtype['PPP'],
                    name = 'Team PPP', marker_color = 'rgb(180, 83, 109)'))
fig.add_trace(go.Bar(x = team_defensive_playtype['play_type'], y = [avg_cut_def, avg_handoff_def, avg_isolation_def, avg_offscreen_def, avg_postup_def, avg_prb_def, avg_pnr_def, avg_putbacks_def, avg_spotup_def, avg_transition_def],
                    name = 'Avg PPP', marker_color = 'rgb(169, 169, 169)'))
fig.update_layout(
    title = selected_team + ' Defensive PPP vs League Avg',
    xaxis_title = 'Playtype',
    yaxis_title = 'Points Per Play',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)


# plot team PPP as a bar and average PPP as a shadow bar
fig = go.Figure()
fig.add_trace(go.Bar(x = team_offensive_playtype['play_type'], y = team_offensive_playtype['PPP'],
                    name = 'Team PPP', marker_color = 'rgb(180, 83, 109)'))
fig.add_trace(go.Bar(x = team_offensive_playtype['play_type'], y = [avg_cut, avg_handoff, avg_isolation, avg_offscreen, avg_postup, avg_prb, avg_pnr, avg_putbacks, avg_spotup, avg_transition],
                    name = 'Average PPP', marker_color = 'rgb(169, 169, 169)'))
fig.update_layout(
    title= selected_team + ' Offensive PPP vs League Avg',
    xaxis_title = 'Play Type',
    yaxis_title = 'Points Per Play',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)

# calculate net difference between team PPP and average PPP
top= team_offensive_playtype[team_offensive_playtype['play_type'] != 'misc']
# add league average PPP to dataframe
top['avg_ppp'] = [avg_cut, avg_handoff, avg_isolation, avg_offscreen, avg_postup, avg_prb, avg_pnr, avg_putbacks, avg_spotup, avg_transition]
# calculate net difference
top['net_ppp_diff'] = top['PPP'] - top['avg_ppp']
# sort by net difference
top = top.sort_values(by = 'net_ppp_diff', ascending = False).reset_index(drop = True)

# add average FREQ% from league
avg_freq = df1.groupby('play_type')['FREQ%'].mean().reset_index()
avg_freq = avg_freq.sort_values(by = 'FREQ%', ascending = False).reset_index(drop = True)
# add average FREQ% to dataframe
top['avg_freq'] = [avg_freq[avg_freq['play_type'] == 'cut']['FREQ%'].values[0],
                     avg_freq[avg_freq['play_type'] == 'handoff']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'isolation']['FREQ%'].values[0], 
                        avg_freq[avg_freq['play_type'] == 'offscreen']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'postup']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'prb']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'pnr']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'putbacks']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'spotup']['FREQ%'].values[0],
                        avg_freq[avg_freq['play_type'] == 'transition']['FREQ%'].values[0]]
# calculate net difference
top['net_freq_diff'] = top['FREQ%'] - top['avg_freq']
# sort by net difference
top = top.sort_values(by = 'net_freq_diff', ascending = False).reset_index(drop = True)


# plot team PPP as a bar and average PPP as a shadow bar
st.subheader('Points Per Play Differential vs. League Average (OFF)')
fig = go.Figure()
fig.add_trace(go.Bar(x = top['play_type'], y = top['net_ppp_diff'],
                    name = 'Net PPP Difference', marker_color = top['net_ppp_diff']))
fig.update_layout(
    xaxis_title = 'Play Type',
    yaxis_title = 'Points Per Play',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)


# FREQUENCY DIFFERENTIAL
st.subheader('Frequency Differential vs. League Average (OFF)')
fig = go.Figure()
fig.add_trace(go.Bar(x = top['play_type'], y = top['net_freq_diff'],
                    name = 'Net Frequency Difference', marker_color = top['net_freq_diff']))
fig.update_layout(
    xaxis_title = 'Play Type',
    yaxis_title = 'Frequency',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)

# calculate net difference between team defensive PPP and average defensive PPP
top_def= team_defensive_playtype[team_defensive_playtype['play_type'] != 'misc']
# add league average PPP to dataframe
top_def['avg_ppp'] = [avg_cut_def, avg_handoff_def, avg_isolation_def, avg_offscreen_def, avg_postup_def, avg_prb_def, avg_pnr_def, avg_putbacks_def, avg_spotup_def, avg_transition_def]
# calculate net difference
top_def['net_ppp_diff'] = top_def['PPP'] - top_def['avg_ppp']
# sort by net difference
top_def = top_def.sort_values(by = 'net_ppp_diff', ascending = False).reset_index(drop = True)

# add average FREQ% from league
avg_freq_def = df1.groupby('play_type')['FREQ%'].mean().reset_index()
avg_freq_def = avg_freq_def.sort_values(by = 'FREQ%', ascending = False).reset_index(drop = True)
# add average FREQ% to dataframe
top_def['avg_freq'] = [avg_freq_def[avg_freq_def['play_type'] == 'cut']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'handoff']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'isolation']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'offscreen']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'postup']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'prb']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'pnr']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'putbacks']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'spotup']['FREQ%'].values[0],
                        avg_freq_def[avg_freq_def['play_type'] == 'transition']['FREQ%'].values[0]]
# calculate net difference
top_def['net_freq_diff'] = top_def['FREQ%'] - top_def['avg_freq']
# sort by net difference
top_def = top_def.sort_values(by = 'net_freq_diff', ascending = False).reset_index(drop = True)

# plot team PPP as a bar and average PPP as a shadow bar
st.subheader('Points Per Play Differential vs. League Average (DEF)')
fig = go.Figure()
fig.add_trace(go.Bar(x = top_def['play_type'], y = top_def['net_ppp_diff'],
                    name = 'Net PPP Difference', marker_color = top_def['net_ppp_diff']))
fig.update_layout(
    xaxis_title = 'Play Type',
    yaxis_title = 'Points Per Play',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)

# FREQUENCY DIFFERENTIAL
st.subheader('Frequency Differential vs. League Average (DEF)')
fig = go.Figure()
fig.add_trace(go.Bar(x = top_def['play_type'], y = top_def['net_freq_diff'],
                    name = 'Net Frequency Difference', marker_color = top_def['net_freq_diff']))
fig.update_layout(
    xaxis_title = 'Play Type',
    yaxis_title = 'Frequency',
    font = dict(
        family = 'Courier New, monospace',
        size = 18,
        color = '#7f7f7f'
    )
)
st.plotly_chart(fig)



# TEAM 2 - OFFENSE
#st.subheader('Team 2 - Offense')

#df_t2 = pd.read_csv(data)
#team2_offensive_playtype = df_t2[df_t2['TEAM'] == team2]
# move the 'playtype' column to the front
#cols2 = team2_offensive_playtype.columns.tolist()
#cols2.remove('play_type')
#new_cols2 = ['play_type'] + cols2
#team2_offensive_playtype = team2_offensive_playtype[new_cols2]
#team2_offensive_playtype = team2_offensive_playtype.sort_values(by = 'FREQ%', ascending = False).reset_index(drop = True)


# Violin plot of all teams playtype PPP
#st.subheader('Team 2 - Points Per Play')

#st.subheader('All Teams')

# add league average PPP and FREQ% to df1
#df1['avg_ppp'] = df1.groupby('play_type')['PPP'].transform('mean')
#df1['avg_freq'] = df1.groupby('play_type')['FREQ%'].transform('mean')

#play_selection = st.select_slider('Select a Play Type', options = ['cut', 'handoff', 'isolation', 'offscreen', 'postup', 'prb', 'pnr', 'putbacks', 'spotup', 'transition'])

# plot PPP for all teams
#fig = px.bar(df1[df1['play_type'] == play_selection], y = 'TEAM', x = 'PPP', orientation= 'h',
#                                                        hover_data = df1.columns)

#fig.update_layout(
#    xaxis_title = 'Team',
#    yaxis_title = 'Points Per Play',
#    font = dict(
#        family = 'Courier New, monospace',
#        size = 12,
#        color = '#7f7f7f'
#    )
#)
#st.plotly_chart(fig)




