#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 23 23:08:05 2023

@author: akshayghosh

BIG PICTURE IDEAS:
    - speed up KDE calculation... C++ or fortran??
    - add another feature to kde that is the shot probaility
    
SMALL PICTURE IDEAS:
    - add column to shooting dataframe: opponentTeamCode
        - use columns teamCode, homeTeamCode, awayTeamCode to determine opponentTeamCode
        - will now have data for shots against for each team, plot these as blue on the heat map
        
    - NEED TO FIX SCORE IN TITLE OF GAMES THAT ENDED IN SHOOTOUT, currently does not include winning goal
        
FUNCTION IDEA:
    - input offensive team and date of game
        - from this get the game ID and defensive team
        - calculate the KDE (can weigh by another column such as xGoal)
        - plot to the rink with the offensive and defensive team logos
        - example title of plot: KDE weighed by 'xGoal': OTT vs BOS, OCT 7 2022
        
inputs for function calc_shot_kde():
    - specific game -> true or false
    - offensive team
    - date of specific game
    - defensive team if not specific game (eg all OTT vs BOS games for the season)
    - playoffs or regular season or both
    - vector of columns to calc KDE weight, eg weight = 0.5*xGoal + 0.5*rebound
"""

# IMPORTS

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests # to get game info such as game ID
from datetime import datetime

# KDE stuff
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import LeaveOneOut

# plot the rink
from hockey_rink import NHLRink, RinkImage

# from NHLTeam import NHLTeam # this does not work yet, learn about the classes

######################################################################################################################################

# FUNCTIONS

def calc_shot_kde(specific_game = True,OFF_team = None,date_string = None, DEF_team = None,playoffs = False):
    
    plot_size = 10.5 # <----- ********USE THIS TO ADJUST SIZE OF PLOTS!!!!!!!!!!********
    font_size_axes = 25 # <----- *****USE THIS TO ADJUST SIZE OF AXIS FONT!!!!!!!!!!****
    font_size_titles = 17 # <----- ***USE THIS TO ADJUST SIZE OF TITLE FONT!!!!!!!!!!***
    axis_font_size = 20
    plot_res = 500
    
    '''
    LOAD SHOT DATA
    '''
    
    # fn = '/Users/akshayghosh/hockey/shots_2022.csv'
    fn = '/Users/akshayghosh/hockey/shots_2022_modified.csv'
    df = pd.read_csv(fn)
    
    
    '''
    SELECT SUBSET OF DATAFRAME
    '''

    # include xGoal column to use as weight for KDE
    result_df = df[['teamCode', 'defenseTeamCode', 'xCordAdjusted', 'yCordAdjusted','xGoal','real_game_id','goal','isPlayoffGame']]
    
    '''
    THIS IS THE OFFENSIVE KDE
    '''
    
    select_OFF,select_DEF,OFF_logo,DEF_logo,formatted_date = select_subset_kde(result_df,specific_game=specific_game, OFF_team=OFF_team, 
                                                                date_string=date_string, DEF_team=DEF_team, playoffs=playoffs)
    goals_OFF = select_OFF['goal'].sum()
    goals_DEF = select_DEF['goal'].sum()
    
    
    x = select_OFF[['xCordAdjusted']];#print(f'{len(x)} goals')
    y = select_OFF[['yCordAdjusted']]
    weight_off = select_OFF[['xGoal']]
    
    f1_mesh_off, f2_mesh_off, kde2d_amplitude_off = calc_kde2d_amplitude(x,y, print_bandwidth = False, kde_weight = weight_off)
    
    '''
    THIS IS THE DEFENSIVE KDE
    '''
    
    x_d = -1*select_DEF[['xCordAdjusted']]
    y_d = -1*select_DEF[['yCordAdjusted']]
    weight_def = select_DEF[['xGoal']];#print(f'{len(x_d)} events')
    f1_mesh_def, f2_mesh_def, kde2d_amplitude_def = calc_kde2d_amplitude(x_d,y_d, print_bandwidth = False, kde_weight = weight_def)
    
    print(f'{len(x)} off events')
    print(f'{len(x_d)} def events')
    
#     # plot of dist of kde amps
#     plt.figure()
#     plt.hist(kde2d_amplitude,bins = 50)
#     plt.show()

    # rink = generate_rink(home = 'OTT',away = 'NHL')
    rink = generate_rink_from_logo(home = OFF_logo,away = DEF_logo)
    
    # PLOT KDE
    plt.figure(figsize=(14,12))
    if specific_game == False:
        plt.title(f'Kernel Density Estimation: {OFF_team} vs {DEF_team} shot locations 2022-23 weighted by xGoal')
    if specific_game == True:
        plt.title(f'KDE: {OFF_team} ({goals_OFF}) vs {DEF_team} ({goals_DEF}): {formatted_date}\n Shot locations weighted by xGoal')
    
    # plot with rink
    v_percentiles = [5,97]
    '''
    boston bruins 5 and 97 percentile kde = (1.3018098847033908e-06, 0.0005018844215575045), can use these for consistent vmin and vmax
    '''
    vmin_,vmax_ = np.percentile(kde2d_amplitude_off, q = (v_percentiles[0],v_percentiles[1]))
    # print(f'boston bruins 5 and 97 percentile kde = {vmin_},{vmax_}')
    # vmin_ = 1.3018098847033908e-06
    # vmax_ = 0.0005018844215575045
    
    levels_ = 20
    # rink.scatter(x, y, s=0.0001, facecolor='white') # do not need to plot the shot locations, just the kde
    # plt.pcolormesh(f1_mesh_off, f2_mesh_off, kde2d_amplitude_off, cmap = 'Reds',vmin = vmin_,vmax = vmax_)
    rink.contourf(f1_mesh_off, f2_mesh_off, kde2d_amplitude_off, 
                  nbins = 100, cmap = 'Reds',levels = levels_,vmin = vmin_,vmax = vmax_,extend = 'both')
    rink.contourf(f1_mesh_def, f2_mesh_def, kde2d_amplitude_def, 
                  nbins = 100, cmap = 'Blues',levels = levels_,vmin = vmin_,vmax = vmax_,extend = 'both')
    if specific_game == True:
        scatter_size = 400
        rink.scatter(x, y,c=select_OFF['goal'].map({0: 'black', 1: 'green'}),s=scatter_size*weight_off)
        rink.scatter(x_d, y_d,c=select_DEF['goal'].map({0: 'black', 1: 'green'}),s=scatter_size*weight_def)
    
    
    plt.tight_layout()
    plt.show()
    
    return()


######################################################################################################################################


def kde2D(x, y, bandwidth, xbins=100j, ybins=100j,kde_weight = None, **kwargs): 
    """Build 2D kernel density estimate (KDE)."""

    # create grid of sample locations (default: 100x100)
    xx, yy = np.mgrid[x.min():x.max():xbins, 
                      y.min():y.max():ybins]

    xy_sample = np.vstack([yy.ravel(), xx.ravel()]).T
    xy_train  = np.vstack([y, x]).T

    kde_skl = KernelDensity(bandwidth=bandwidth, **kwargs)
    kde_skl.fit(xy_train,sample_weight = kde_weight)

    # score_samples() returns the log-likelihood of the samples
    z = np.exp(kde_skl.score_samples(xy_sample))
    return xx, yy, np.reshape(z, xx.shape)


######################################################################################################################################

def generate_rink_from_logo(home,away):
    '''
    create rink to plot
    '''
    
    rink = NHLRink(
        home_logo={
            "feature_class": RinkImage,
            "image_path": home,
            "x": 7, "length": get_logo_size(home)[0], "width": get_logo_size(home)[1], # "x": 7, "length": 50/4, "width": 42/4, <- FOR SENS LOGO
            "zorder": 15, "alpha": 0.5,
        },
        away_logo={
            "feature_class": RinkImage,
            "image_path": away,
            "x": -7, "length": get_logo_size(away)[0], "width": get_logo_size(away)[1],
            "zorder": 15, "alpha": 0.5,
        }
    )
    
    return(rink)

def get_logo_size(team):
    '''
    this is because the sens logo appears warped, test to see if needed for any other logos
    so far, BOS, TOR, NHL all work
    '''
    if team == 'OTT':
        length = 50/4
        width = 42/4
    else:
        length = 42/4
        width = 42/4
    
    return(length,width)


######################################################################################################################################

def calc_kde2d_amplitude(x,y, print_bandwidth = False,kde_weight = None):
    '''
    input two variables x and y, to be the features
    x and y are converted to np arrays of the right shape
    return the kde amplitude
    '''
    
    # set up data vectors
    f1 = np.array(x,dtype = 'float32').reshape(len(x),)#np.abs(x)
    f2 = np.array(y,dtype = 'float32').reshape(len(x),)
    
    f = np.transpose(np.vstack((f1,f2)))
    
    # calc best bandwidth
    bandwidths = np.linspace(0.1, 5, 100)
    grid = GridSearchCV(KernelDensity(kernel='gaussian'),
                        {'bandwidth': bandwidths}) # default is cv = 5, ie 5 fold cross validation
    
    grid.fit(X = f,y = None);
    
    best_bandwidth_dict = grid.best_params_
    best_bandwidth = best_bandwidth_dict.get('bandwidth')
    
    
    best_bandwidth *= 1
    
    if print_bandwidth:
        print('using offensive bandwidth {}'.format(best_bandwidth))
    
    # calc kde
    f1_mesh, f2_mesh, kde2d_amplitude = kde2D(f1, f2, bandwidth = best_bandwidth, kde_weight = None)
    
    return(f1_mesh, f2_mesh, kde2d_amplitude)

######################################################################################################################################

def get_game_id(date,team):
    '''
    date = YYYY-MM-DD
    
    EXAMPLE:
        # Input the date and team
        date = datetime(2022, 10, 7) # for October 7th, 2022
        team = "San Jose Sharks"

        # Get the game ID
        game_id = get_game_id(date, team)

        if game_id:
            print(f"The game ID for {team} on {date.strftime('%Y-%m-%d')} is: {game_id}")
        else:
            print(f"No game found for {team} on {date.strftime('%Y-%m-%d')}.")
            
        OUTPUT: The game ID for San Jose Sharks on 2022-10-07 is: 2022020001
        
    NOTE: the game ID in the money puck dataframe for this game would be 20001, need to add 20220 to start
    '''
    # date = datetime(date)
    
    # Format the date string in the required format (YYYY-MM-DD)
    formatted_date = date.strftime('%Y-%m-%d')

    # Construct the API URL
    url = f"https://statsapi.web.nhl.com/api/v1/schedule?date={formatted_date}"

    try:
        # Send a GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the response JSON
            data = response.json()

            # Extract the game ID if available
            if 'dates' in data and len(data['dates']) > 0 and 'games' in data['dates'][0]:
                games = data['dates'][0]['games']
                for game in games:
                    # Check if the team is playing in the game
                    if team in (game['teams']['away']['team']['name'], game['teams']['home']['team']['name']):
                        game_id = game['gamePk']
                        return game_id

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None

######################################################################################################################################

def get_team_info(abbreviation):
    team_info = {
        'ANA': {'name': 'Anaheim Ducks', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/7/72/Anaheim_Ducks.svg/2560px-Anaheim_Ducks.svg.png'},
        'ARI': {'name': 'Arizona Coyotes', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Arizona_Coyotes_logo_%282021%29.svg/1863px-Arizona_Coyotes_logo_%282021%29.svg.png'},
        'BOS': {'name': 'Boston Bruins', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/12/Boston_Bruins.svg/2048px-Boston_Bruins.svg.png'},
        'BUF': {'name': 'Buffalo Sabres', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Buffalo_Sabres_Logo.svg/2048px-Buffalo_Sabres_Logo.svg.png'},
        'CGY': {'name': 'Calgary Flames', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/61/Calgary_Flames_logo.svg/2395px-Calgary_Flames_logo.svg.png'},
        'CAR': {'name': 'Carolina Hurricanes', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/32/Carolina_Hurricanes.svg/2560px-Carolina_Hurricanes.svg.png'},
        'CHI': {'name': 'Chicago Blackhawks', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/2/29/Chicago_Blackhawks_logo.svg/2349px-Chicago_Blackhawks_logo.svg.png'},
        'COL': {'name': 'Colorado Avalanche', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/45/Colorado_Avalanche_logo.svg/2514px-Colorado_Avalanche_logo.svg.png'},
        'CBJ': {'name': 'Columbus Blue Jackets', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Columbus_Blue_Jackets_logo.svg/2366px-Columbus_Blue_Jackets_logo.svg.png'},
        'DAL': {'name': 'Dallas Stars', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Dallas_Stars_logo_%282013%29.svg/2493px-Dallas_Stars_logo_%282013%29.svg.png'},
        'DET': {'name': 'Detroit Red Wings', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e0/Detroit_Red_Wings_logo.svg/2560px-Detroit_Red_Wings_logo.svg.png'},
        'EDM': {'name': 'Edmonton Oilers', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/4d/Logo_Edmonton_Oilers.svg/2048px-Logo_Edmonton_Oilers.svg.png'},
        'FLA': {'name': 'Florida Panthers', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/43/Florida_Panthers_2016_logo.svg/1831px-Florida_Panthers_2016_logo.svg.png'},
        'LAK': {'name': 'Los Angeles Kings', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/63/Los_Angeles_Kings_logo.svg/1719px-Los_Angeles_Kings_logo.svg.png'},
        'MIN': {'name': 'Minnesota Wild', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Minnesota_Wild.svg/2560px-Minnesota_Wild.svg.png'},
        'MTL': {'name': 'Montreal Canadiens', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Montreal_Canadiens.svg/2560px-Montreal_Canadiens.svg.png'},
        'NSH': {'name': 'Nashville Predators', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9c/Nashville_Predators_Logo_%282011%29.svg/2560px-Nashville_Predators_Logo_%282011%29.svg.png'},
        'NJD': {'name': 'New Jersey Devils', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/New_Jersey_Devils_logo.svg/2002px-New_Jersey_Devils_logo.svg.png'},
        'NYI': {'name': 'New York Islanders', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/42/Logo_New_York_Islanders.svg/2124px-Logo_New_York_Islanders.svg.png'},
        'NYR': {'name': 'New York Rangers', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/New_York_Rangers.svg/2123px-New_York_Rangers.svg.png'},
        'OTT': {'name': 'Ottawa Senators', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b2/Ottawa_Senators_2020-2021_logo.svg/2560px-Ottawa_Senators_2020-2021_logo.svg.png'},
        'PHI': {'name': 'Philadelphia Flyers', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/dc/Philadelphia_Flyers.svg/2560px-Philadelphia_Flyers.svg.png'},
        'PIT': {'name': 'Pittsburgh Penguins', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c0/Pittsburgh_Penguins_logo_%282016%29.svg/2164px-Pittsburgh_Penguins_logo_%282016%29.svg.png'},
        'SEA': {'name': 'Seattle Kraken', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/4/48/Seattle_Kraken_official_logo.svg/1631px-Seattle_Kraken_official_logo.svg.png'},
        'SJS': {'name': 'San Jose Sharks', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/37/SanJoseSharksLogo.svg/2447px-SanJoseSharksLogo.svg.png'},
        'STL': {'name': 'St. Louis Blues', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/ed/St._Louis_Blues_logo.svg/2560px-St._Louis_Blues_logo.svg.png'},
        'TBL': {'name': 'Tampa Bay Lightning', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/2/2f/Tampa_Bay_Lightning_Logo_2011.svg/2199px-Tampa_Bay_Lightning_Logo_2011.svg.png'},
        'TOR': {'name': 'Toronto Maple Leafs', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b6/Toronto_Maple_Leafs_2016_logo.svg/1835px-Toronto_Maple_Leafs_2016_logo.svg.png'},
        'VAN': {'name': 'Vancouver Canucks', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/Vancouver_Canucks_logo.svg/2124px-Vancouver_Canucks_logo.svg.png'},
        'VGK': {'name': 'Vegas Golden Knights', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/a/ac/Vegas_Golden_Knights_logo.svg/1513px-Vegas_Golden_Knights_logo.svg.png'},
        'WSH': {'name': 'Washington Capitals', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/2/2d/Washington_Capitals.svg'},
        'WPG': {'name': 'Winnipeg Jets', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/93/Winnipeg_Jets_Logo_2011.svg/2048px-Winnipeg_Jets_Logo_2011.svg.png'},
        'NHL': {'name': 'National Hockey League', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/05_NHL_Shield.svg/1782px-05_NHL_Shield.svg.png'}
    }
    
    team = team_info.get(abbreviation)
    if team:
        return team['name'], team['logo']
    else:
        return 'Unknown', 'Unknown'


######################################################################################################################################

def select_subset_kde(result_df,specific_game=True, OFF_team=None, date_string=None, DEF_team=None, playoffs=False):
    
    # fn = '/Users/akshayghosh/hockey/shots_2022_modified.csv'
    # df = pd.read_csv(fn)
    # result_df = df[['teamCode', 'defenseTeamCode', 'xCordAdjusted', 'yCordAdjusted','xGoal','real_game_id','goal','isPlayoffGame']]

    '''
    FILTER BY PLAYOFFS
    '''
    result_df = result_df[result_df['isPlayoffGame'] == int(playoffs)]


    '''
    specific game, filter by:
        'teamCode', 'real_game_id'
    '''
    if specific_game:
        '''
        get game ID using date_string
        '''
        # date_string = '2022-10-18'  # Example date string
        date_format = '%Y-%m-%d'  # Example date format

        date_obj = datetime.strptime(date_string, date_format)
        # date = datetime(2022,10,18) # date = (YYYY,MM,DD)
        date = date_obj
        team = get_team_info(OFF_team)[0]
        formatted_date = date.strftime('%Y-%m-%d')
        GAME_ID = get_game_id(date,team) # Get the game ID
        team,OFF_logo = get_team_info(OFF_team)
    
        
        select_OFF = result_df[(result_df['teamCode'] == OFF_team) & (result_df['real_game_id'] == GAME_ID)] # specific game
        goals_OFF = select_OFF['goal'].sum()
        # print('off goals =',goals_OFF)
        DEF_team = select_OFF['defenseTeamCode'].values[0]  # Get the value of defenseTeamCode
        DEF_logo = get_team_info(DEF_team)[1]
        
        # get select_OFF
        select_OFF = result_df[(result_df['teamCode'] == OFF_team) & (result_df['real_game_id'] == GAME_ID)] # specific game
        goals_OFF = select_OFF['goal'].sum()
        DEF_team = select_OFF['defenseTeamCode'].values[0]  # Get the value of defenseTeamCode
        DEF_logo = get_team_info(DEF_team)[1]
        
        # get select_DEF
        select_DEF = result_df[(result_df['defenseTeamCode'] == OFF_team) & (result_df['real_game_id'] == GAME_ID)] # specific game


    if specific_game == False:
        '''
        either team vs another team, or team vs NHL
        '''
        if playoffs == True:
            formatted_date = 'Playoffs'
        if playoffs == False:
            formatted_date = 'Regular Season'
            
        if DEF_team == None: # team vs NHL
            select_OFF = result_df[result_df['teamCode'] == OFF_team] # all games
            OFF_logo = get_team_info(OFF_team)[1]
            DEF_team = 'NHL'
            DEF_logo = get_team_info('NHL')[1]
            select_DEF = result_df[result_df['defenseTeamCode'] == OFF_team] # all games
        else: # team vs team
            OFF_logo = get_team_info(OFF_team)[1]
            DEF_logo = get_team_info(DEF_team)[1]
            select_OFF = result_df[(result_df['teamCode'] == OFF_team) & (result_df['defenseTeamCode'] == DEF_team)]
            select_DEF = result_df[(result_df['teamCode'] == DEF_team) & (result_df['defenseTeamCode'] == OFF_team)]


    return(select_OFF,select_DEF,OFF_logo,DEF_logo,formatted_date)


######################################################################################################################################
