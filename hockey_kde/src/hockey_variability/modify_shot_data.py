#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 16:04:47 2023

@author: akshayghosh

URL for data: https://peter-tanner.com/moneypuck/downloads/shots_2022.zip
"""

import pandas as pd
import requests

input_filename = 'PATH/TO/SHOT_DATA/file.csv' # edit this to where you saved the moneypuck shot data
output_filename = 'PATH/TO/MODIFIED_SHOT_DATA/file.csv' # edit this to where you would like to save the modified dataframe

# open csv file as dataframe
df = pd.read_csv(input_filename)

# create the 'defenseTeamCode' column based on the conditions
df['defenseTeamCode'] = df.apply(lambda row: row['homeTeamCode'] if row['teamCode'] == row['awayTeamCode'] else row['awayTeamCode'], axis=1)

# create the 'real_game_id' column which matches the game ID from the NHL api, which is just (season)0(game_id)
df['real_game_id'] = df.apply(lambda row: f"{row['season']}0{row['game_id']}", axis=1)

df.to_csv(output_filename, index=False)