#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 16:33:34 2022

@author: abiodun
"""

# %% Install dependencies on Google Colab (remove the # sign in front of the syntaxes to install the dependencies to your environment)
#!pip install selenium
#!apt-get update
#!apt install chromium-chromedriver

# %% import needed libraries
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
from time import sleep

import warnings
warnings.filterwarnings('ignore')

# %% Set the url link
url = "https://www.flashscore.com/football/england/premier-league/results/"

# %% Configure web driver for the scrape job

options = Options()
options.add_argument('--headless') # Prevents the engine from launching an instance of the specified browser. Instead, it runs in a silent mod
options.add_argument('--no-sandbox') # Disables sandbox, and allows the driver execute functions without constraints.
options.add_argument('--disable-dev-shm-usage') # Prevents the driver engine from crashing
driver = webdriver.Chrome('chromedriver', options=options)

# %% Initiate connection to the url
html = driver.get(url)
# html = html.text
sleep(5)

# %% Initiate beautiful soup
soup = bs(driver.page_source, 'lxml') # lxml is a Python library which allows for easy handling of XML and HTML files, and can also be used for web scraping.

# %% Find the class that holds soccer information
divs = soup.find('div', {'class': 'sportName soccer'}) # Specify the parent class

# %%  Fetch goal details


def parse_goal(bsTag, ownGoal):
    goalTime = bsTag.find(
        'div', {'class': 'smv__timeBox'}).text.replace("'", '')
    scorer = bsTag.find('a', {'class': 'smv__playerName'}).text
    if ownGoal:
        assist = 'NA'
        isOwnGoal = True
    else:
        try:
            assist = bsTag.find_all('div')[-1].find('a').text
        except:
            try:
                assist = bsTag.find('div', {'class': "smv__subIncident"}).text.replace(
                    '(', '').replace(')', '')
            except:
                assist = 'Not assisted'
        isOwnGoal = False
    return [goalTime, scorer, assist, isOwnGoal]

# %%
def get_match_date(bsTag, date):
    match_date = bsTag.find(
        'div', {'class': 'duelParticipant__startTime'}
    ).text
    date = match_date.split(' ')[0]
    time = match_date.split(' ')
    return [match_date]

# %% Fetch card details


def parse_card(bsTag, card_type):
    cardTime = bsTag.find(
        'div', {'class': 'smv__timeBox'}).text.replace("'", '')
    player = bsTag.find('a', {'class': 'smv__playerName'}).text
    if card_type == 'red':
        isRed = True
    else:
        isRed = False
    why = bsTag.find_all('div')[-1].text.replace('(', '').replace(')', '')
    return [cardTime, isRed, why]

# %% Fetch substitution data


def parse_substitution(bsTag):
    subTime = bsTag.find(
        'div', {'class': 'smv__timeBox'}).text.replace("'", '')
    try:
        player = bsTag.find('a', {'class': 'smv__playerName'}).text
    except:
        player = 'error'
    try:
        outPlayer = bsTag.find(
            'a', {'class': 'smv__subDown smv__playerName'}).text
    except:
        # bsTag.find('div',{'class':'smv__incidentSubOut '}).find('a').text
        outPlayer = 'error'

    return [subTime, player, outPlayer]


# %%
all_div = divs.find_all(recursive=False)

# %%
match = []

# %%

# %%
rounds = []

# %%
for i in all_div[1:]:
    if len(rounds) > 7:
        break

    if i.text.startswith('Round'):
        rounds.append(i.text)
    else:
        match.append(i)

# %% Define a function to fetch match data


def get_stats(all_stat):
    first_sec = []
    home_event = []
    away_event = []

    for i in all_stat:

        if 'section__title' in i.get('class'):
            score = i.text.split('Half')[1]
            first_sec.append(score)

        elif 'smv__empty' in i.get('class'):
            continue
        else:
            if 'smv__homeParticipant' in i.get('class'):
                event_type = i.find('svg').get('class')
                if event_type[0] == 'soccer':
                    if len(event_type) > 1:
                        itsOwnGoal = True
                    else:
                        itsOwnGoal = False
                    ans = parse_goal(i, itsOwnGoal)
#                   print(ans)
                    home_event.append(ans)
                elif event_type[0] == 'card-ico':
                    try:
                        if 'yellow' in event_type[1]:
                            ans = parse_card(i, 'yellow')
                        else:
                            ans = parse_card(i, 'red')
                    except:
                        ans = parse_card(i, 'red')
#                       print(ans)
                    home_event.append(ans)
                else:
                    ans = parse_substitution(i)
#                   print(ans)
                    home_event.append(ans)
            else:
                event_type = i.find('svg').get('class')
                if event_type[0] == 'soccer':
                    if len(event_type) > 1:
                        itsOwnGoal = True
                    else:
                        itsOwnGoal = False
                    ans = parse_goal(i, itsOwnGoal)
#                   print(ans)
                    away_event.append(ans)
                elif event_type[0] == 'card-ico':
                    try:
                        if 'yellow' in event_type[1]:
                            ans = parse_card(i, 'yellow')
                        else:
                            ans = parse_card(i, 'red')
#                           print(ans)
                    except:
                        ans = parse_card(i, 'red')
#                       print(ans)
                    away_event.append(ans)
                else:
                    ans = parse_substitution(i)
#                   print(ans)
                    away_event.append(ans)
    return first_sec, home_event, away_event


# %% Create an empty list to store the match statistics.
stat_column = []

# %% Define a column for fetch match statistics.


def get_stats_match():
    global stat_column
    soup2 = bs(driver.page_source, 'lxml')
    x = soup2.find_all('div', {'class': 'stat__category'})
    match_stat = []
    y = [i.find_all(recursive=True) for i in x]
    for l in y:
        temp = [i.text for i in l]
        match_stat.append([temp[0], temp[2]])
        if temp[1] not in stat_column:
            stat_column.append(temp[1])
        # print(match_stat)
    return match_stat


# %% Create an empty list to store the scraped data
all_data = []

# %% Scrape the respective match data and append them to the empty list (all_data).
for k in match:
    try:
        home = k.find('div', {
                      "class": "event__participant event__participant--home fontExtraBold"}).text
        away = k.find(
            'div', {"class": "event__participant event__participant--away"}).text
    except:
        try:
            home = k.find(
                'div', {"class": "event__participant event__participant--home"}).text
            away = k.find('div', {
                          "class": "event__participant event__participant--away fontExtraBold"}).text
        except:
            home = k.find(
                'div', {"class": "event__participant event__participant--home"}).text
            away = k.find(
                'div', {"class": "event__participant event__participant--away"}).text
    match_id = k.get('id').rsplit('_')[-1]
    driver.get(
        f'https://www.flashscore.com/match/{match_id}/#/match-summary/match-summary')
    sleep(5)
    stats_soup = bs(driver.page_source, 'lxml')

    stat = stats_soup.find('div', {'class': "smv__verticalSections section"})
#     stats_soup.find_all('div',{'class':'participant__participantName participant__overflow '})
    all_stat = stat.find_all(recursive=False)
    first_sec, home_event, away_event = get_stats(all_stat)
    test_url = f'https://www.flashscore.com/match/{match_id}/#/match-summary' + \
        '/match-statistics/0'
    driver.get(test_url)
    sleep(3)
    # stats goes here
#     ext = '/match-statistics/0'
    all_stat = get_stats_match()
    all_data.append([home, away, first_sec, home_event, away_event, all_stat])
#    print(match_id)

# %%

# %% Convert the scraped data into a dataframe
df = pd.DataFrame(data=all_data, columns=[
                  'Home Team', 'Away Team', 'HT/FT', 'Home Events', 'Away Events', 'Game Stats'])

# %%
df['First Half Score'] = df['HT/FT'].apply(lambda x: x[0])
df['Second Half Score'] = df['HT/FT'].apply(lambda x: x[1])

# %% Drop the Half Time/Full Time Score column.
df.drop('HT/FT', axis=1, inplace=True)

# %%
for i, j in enumerate(stat_column[:-2]):
    print(j)
    df[f'{j} Home'] = df['Game Stats'].apply(lambda x: x[i][0])
    df[f'{j} Away'] = df['Game Stats'].apply(lambda x: x[i][1])
df.drop('Game Stats', axis=1, inplace=True)

# %% Create separate dataframes for both home and away events.
df_home = df[['Home Team', 'Away Team',
              'First Half Score',	'Second Half Score', 'Home Events']]
df_away = df[['Home Team', 'Away Team',
              'First Half Score',	'Second Half Score', 'Away Events']]

# %% Unpivot the separated dataframes.
df_home_melted = pd.melt(df_home, id_vars=[
                         'Home Team', 'Away Team', 'First Half Score',	'Second Half Score', ],
                         var_name='Event', value_name='Value')
df_away_melted = pd.melt(df_away, id_vars=[
                         'Home Team', 'Away Team', 'First Half Score',	'Second Half Score', ],
                         var_name='Event', value_name='Value')

# %% Remove the brackets from the column contents, and remove trailing commas from the texts.
df_home_melted = df_home_melted['Value'].apply(lambda x: pd.Series(
    str(x).split("]")).str.replace(r'[][]+', '', regex=True).str.lstrip(','))
df_away_melted = df_away_melted['Value'].apply(lambda x: pd.Series(
    str(x).split("]")).str.replace(r'[][]+', '', regex=True).str.lstrip(','))

# %% Rename columns
df_home_melted = df_home_melted.rename({0: 'Home Event_1', 1: 'Home Event_2', 2: 'Home Event_3', 3: 'Home Event_4', 4: 'Home Event_5',
                                        5: 'Home Event_6', 6: 'Home Event_7', 7: 'Home Event_8', 8: 'Home Event_9', 9: 'Home Event_10',
                                        10: 'Home Event_11', 11: 'Home Event_12', 12: 'Home Event_13', 13: 'Home Event_14'}, axis=1)
df_away_melted = df_away_melted.rename({0: 'Away Event_1', 1: 'Away Event_2', 2: 'Away Event_3', 3: 'Away Event_4', 4: 'Away Event_5',
                                        5: 'Away Event_6', 6: 'Away Event_7', 7: 'Away Event_8', 8: 'Away Event_9', 9: 'Away Event_10',
                                        10: 'Away Event_11', 11: 'Away Event_12', 12: 'Away Event_13', 13: 'Away Event_14'}, axis=1)

# %% Drop the original event columns.
df_home = df_home.drop('Home Events', axis=1).reset_index().merge(
    df_home_melted.reset_index()).set_index('index')
df_away = df_away.drop('Away Events', axis=1).reset_index().merge(
    df_away_melted.reset_index()).set_index('index')

# %% Merge the separated events (home and away) into a single dataframe.
match_data = df_home.merge(df_away.drop(
    ['First Half Score', 'Second Half Score'], axis=1), on=['Home Team', 'Away Team'])

# The number of columns (events) slightly varies in each match.
# Hence, we try to increase the number of events to 15 (bearing in mind that some will contain empty values).
# This will ensure that our code does not break down when there are less events we have earlier specified.
try:
    for i in range(15):
        if f'Home Event_{i}' in match_data:
            match_data[f'Home Event_{i}'] = match_data[f'Home Event_{i}']
        else:
            match_data[f'Home Event_{i}'] = pd.Series(
                [np.nan for x in range(len(match_data.index))]
            )
    for i in range(15):
        if f'Away Event_{i}' in match_data:
            match_data[f'Away Event_{i}'] = match_data[f'Away Event_{i}']
        else:
            match_data[f'Away Event_{i}'] = pd.Series(
                [np.nan for x in range(len(match_data.index))]
            )
except:
    pass
match_data['Match'] = match_data['Home Team'] + \
    " " + "VS" + " " + match_data['Away Team']
match_data = match_data[['Match', 'Home Team', 'Away Team', 'First Half Score', 'Second Half Score', 'Home Event_1',
                         'Away Event_1', 'Home Event_2', 'Away Event_2', 'Home Event_3', 'Away Event_3', 'Home Event_4',
                         'Away Event_4', 'Home Event_5', 'Away Event_5', 'Home Event_6', 'Away Event_6', 'Home Event_7',
                         'Away Event_7', 'Home Event_8', 'Away Event_8', 'Home Event_9', 'Away Event_9', 'Home Event_10',
                         'Away Event_10', 'Home Event_11', 'Away Event_11', 'Home Event_11', 'Away Event_12', 'Home Event_13',
                         'Away Event_13', 'Home Event_14',  'Away Event_14']]

# %% Merge the derived match data with the original dataframe.
match_data = df.drop(['Home Events', 'Away Events'], axis=1).merge(match_data.drop(
    ['First Half Score', 'Second Half Score'], axis=1), on=['Home Team', 'Away Team'])

# %% Unpivot match_data by converting the events header into a single column, and another column that hold the information.
# This reduces the number of columns and increases the number of rows.
match_data_melted = pd.melt(match_data, id_vars=['Match', 'Home Team', 'Away Team', 'First Half Score', 'Second Half Score',
                                                 'Ball Possession Home', 'Ball Possession Away', 'Goal Attempts Home',
                                                 'Goal Attempts Away', 'Shots on Goal Home', 'Shots on Goal Away',
                                                 'Shots off Goal Home', 'Shots off Goal Away', 'Blocked Shots Home',
                                                 'Blocked Shots Away', 'Free Kicks Home', 'Free Kicks Away',
                                                 'Corner Kicks Home', 'Corner Kicks Away', 'Offsides Home',
                                                 'Offsides Away', 'Throw-in Home', 'Throw-in Away',
                                                 'Goalkeeper Saves Home', 'Goalkeeper Saves Away', 'Fouls Home',
                                                 'Fouls Away', 'Yellow Cards Home', 'Yellow Cards Away',
                                                 'Total Passes Home', 'Total Passes Away', 'Completed Passes Home',
                                                 'Completed Passes Away', 'Tackles Home', 'Tackles Away', 'Attacks Home',
                                                 'Attacks Away', ], var_name='Event', value_name='Details')

# %% Split the 'Details' columns to extract the information contained in it
match_data_melted[['Minute', 'Event/Player', 'Type/Assist', 'Goal Status']
                  ] = match_data_melted['Details'].apply(lambda x: pd.Series(str(x).split(",")))
match_data_melted = match_data_melted.drop('Details', axis=1)
match_data_melted = match_data_melted.replace("'", '', regex=True)

# %% Extract goals from the data.
goals = match_data_melted.dropna(subset=['Goal Status'])
goals = goals.rename(
    {'Event/Player': 'Scorer', 'Type/Assist': 'Assist'}, axis=1)

# %% Convert the dataframes into csv files.
match_data_melted.to_csv('FlashScore_Matches.csv', index=False, header=True)
goals.to_csv('FlashScore_goals.csv', index=False, header=True)

# %%
