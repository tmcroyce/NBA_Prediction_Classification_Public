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
headers

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
df

today = datetime.datetime.today().strftime('%Y-%m-%d')

df.to_csv('data/team/aggregates/daily_updates/draftkings' + str(today) + '.csv', index=False)

# close driver
driver.close()