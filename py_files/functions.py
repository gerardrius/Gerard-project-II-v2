import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# FIFA RATINGS CLEANING FUNCTIONS
def csv_reader (file):
    """
    csv reader function
    """
    return pd.read_csv(file, low_memory = False)
     

def column_droper(df):
    """
    Function that asks for every column in a dataset whether we want to keep it or not
    Accepts the dataset to filter by columns as argument
    Returns the same dataset filtered
    """

    # Iteration for every column in the dataset
    for column in df.columns:
        column_keeper = "--"
        # Accepts input (Y/N) to keep or drop a column 
        while len(column_keeper) != 1 and column_keeper not in ["Y", "N"]:
            column_keeper = input(f"Do you want to keep column {column}? (Y/N)")
            if column_keeper == "Y":
                column_keeper = "--"
                break
            elif column_keeper == "N":
                df.drop([column], axis = 1, inplace = True)
                column_keeper = "--"
                break
            else:
                column_keeper = "--"
    
def year_filter (df, year):
    """
    Function that filters FIFA ratings' dataframe by FIFA version
    Receives the dataframe and a year input, which must be in two digits format (YY), e.g.
    17 for 2017.
    Returns the filtered version of the dataframe by year.
    """
    df = df[(df["fifa_version"] == year)]
    df.reset_index(drop = True, inplace = True)
    return df

def get_year_classification(url):
    """
    Function that provides a dataset with the classification of the Ballon d'Or.
    Accepts an url as argument, which must be the wikipedia page for a given year Ballon d'Or.
    Returns a dataset with the ranking, name club and points obtained by top 10 players.
    """
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    tags = soup.find_all("table", attrs = {"class":"wikitable"}) # <table class="wikitable">
    classification = pd.read_html(tags[0].prettify())[0][:10]
    return classification

def top_10_players (df):
    """
    Function that gives a list with the names of the top10 players
    From a given year classification dataframe
    """
    return [player for player in df["Player"]]

def all_players ():
    """
    Provides a list with short names of unique all players that have been in a year's top 10.
    """
    all_players_list = set(top_10_2017 + top_10_2018 + top_10_2019 + top_10_2021 + top_10_2022)
    return all_players_list

def regex_generator (players_list):
    """
    Function that creates a regular expression for each unique player in all top10's list
    Gets the list of unique players' names as argument
    Returns a dictionary where keys are players' names and values are regex that can match
    their name in FIFA ratings dataframe
    """
    regex_dict = {}
    
    for player in players_list:
        regex_dict[player] = (".*" + ".*".join(player.split(" ")) + ".*")

    return regex_dict


def long_name_creator (df, top10_year):
    """
    Function that iterates through FIFA ratings dataframes to get players' full names.
    Accepts a given year FIFA ratings and Ballon d'Or top10.
    Returns a long name list of players of that year top10.
    """
    long_name_list = []
    for player in top10_year:
        for long_name in df["long_name"]:
            if re.match(regex_dict[player], long_name):
                long_name_list.append(long_name)
            else:
                pass
    
    return list(set(long_name_list))

def players_filter (df, longnames_list):
    """
    Function that filters the original yearly dataframe applying name conditions on long_name column.
    It accepts two arguments.
        First, the dataframe to filter, e.g. fifa_ratings_2017.
        Second, the list of long_names obtained through the iteration of the regex dict and
        the list with the names of the year's Ballon d'Or classification.
    It returns the dataframe with the FIFA ratings of that particular year best players. 
    """
    c_plr_1 = (df["long_name"] == longnames_list[0]) # c_plr_1 stands for condition_player_1
    c_plr_2 = (df["long_name"] == longnames_list[1])
    c_plr_3 = (df["long_name"] == longnames_list[2])
    c_plr_4 = (df["long_name"] == longnames_list[3])
    c_plr_5 = (df["long_name"] == longnames_list[4])
    c_plr_6 = (df["long_name"] == longnames_list[5])
    c_plr_7 = (df["long_name"] == longnames_list[6])
    c_plr_8 = (df["long_name"] == longnames_list[7])
    c_plr_9 = (df["long_name"] == longnames_list[8])
    c_plr_10 = (df["long_name"] == longnames_list[9])
    
    dataframe = df[(c_plr_1)|(c_plr_2)|(c_plr_3)|(c_plr_4)|(c_plr_5)|(c_plr_6)|(c_plr_7)|(c_plr_8)|(c_plr_9)|(c_plr_10)]
    return dataframe

# To have the same index starting from 0 in every dataset (will be important in next steps)
def index_reset (df):
    df.reset_index(drop = True, inplace = True)
    return df

def single_position (df):
    """
    Function that removes non-common playing positions for each player.
    It accepts FIFA ratings of a given year.
    Returns it with players having only one position attribute, the most common, e.g.
    striker, left wing, etc.
    """
    for i in range(df.shape[0]):
        df["player_positions"][i] = df["player_positions"][i].split(",")[0]
    
    return df

def points_column_append (df, top10_year, classification):
    """
    This amazing function has a very important objective: append the points 
    received by each player in a Ballon d'Or ceremony to the eventual yearly FIFA
    ratings dataframe. This is really important because points are the result to which
    we will want to run regressions and stuff!

    It receives the yearly FIFA ratings dataframe, the top 10 players of that year, and the 
    scrapped classification.
    
    It returns the FIFA ratings dataframe with brand new points column!!! (Struggled a lot here)
    """
    info_dict = {"long_name": [], "fifa_index": [], "rating": [], "points": [], "short_name": []}
    
    # Iteration of each player in a given year top10. If the regex expression match a long name in df, it appends that long name in the dictionary long_name key.
    for player in top10_year:
        for long_name in df["long_name"]:
            if re.match(regex_dict[player], long_name):
                info_dict["long_name"].append(long_name)
            else:
                pass
    
    # For every long name in the dictionary_key -> appends the index of that name in the FIFA rating dataset.
    # It will be essential to match a player and its Ballon d'Or points.
    for player in info_dict["long_name"]:
        info_dict['fifa_index'].append(df[(df['long_name'] == player)].index[0])

    # For every FIFA rating index, appends the rating to the correspondent dictionary key 
    for i in range(len(info_dict['fifa_index'])):
        info_dict["rating"].append(df[(df['long_name'] == info_dict['long_name'][i])]['overall'][info_dict['fifa_index'][i]])

    # Gets short name from Ballon d'Or classification dataframe
    info_dict['short_name'] = [short_name for short_name in classification['Player']]
    
    # Appends Ballon d'Or points to the correspondent player in the dictionary.
    for i in range(len(info_dict['fifa_index'])):
        info_dict['points'].append(classification[(classification['Player'] == info_dict['short_name'][i])]['Points'][i])

    # From the dictionary, we create a new dataframe with the info to merge at FIFA ratings dataframe
    merged_info = pd.DataFrame(info_dict)
    # Sorts this dictionary by fifa_index -> now Points will match the accurate player in FIFA ratings
    merged_info.sort_values(by=["fifa_index"])
    # Dataframe gets points column appended!
    df = df.join(merged_info["points"])

    return df

def general_position (df):
    """
    Takes the dataframe as argument and appends a new column with a generic position according
    to 'players_positions'.
    """
    # We define an empty list and three generic lists including all positions in the datasets.
    general_position = []
    attacker = ['LW', 'RW', 'ST', 'CF']
    midfielder = ['CM', 'CAM', 'CDM']
    defender = ['CB']
    goalkeeper = ['GK']

    # We iterate through every 'player_position' and append the generic one to the list.
    for position in df['player_positions']:
        if position in attacker:
            general_position.append('ATT')
        elif position in midfielder:
            general_position.append('MID')
        elif position in defender:
            general_position.append('DEF')
        elif position in goalkeeper:
            general_position.append('GK')

    # We append the new column to the dataframe.
    df.insert(5, 'general_position', general_position)
    return df

def goalkeeper_df (df):
    """
    Function that filters by GK condition
    Accepts the dataframe as argument and 
    Returns the new dataframe of GK's while removes the GK from the original df.
    """
    fifa_gk = df[(df['player_positions'] == "GK")]
    fifa_gk.reset_index(drop = True, inplace = True)

    GK_condition = df[(df['player_positions'] == "GK")].index
    df = df.drop(GK_condition)

    return fifa_gk

# Squared deviations sum function with respect to 2020's mean values per variable.
def squared_error (df):
    """
    We'll use this function to take a FIFA ratings dataset as reference to make our 2020 Ballon d'Or prediction.
    This function takes a dataframe as argument and
    Returns the sum of the squared deviations of its variables' means with respect to 2020's
    """
    list1 = list(fifa_20.describe().loc['mean'])
    list2 = list(df.describe().loc['mean'])
    
    sum_of_square_differences = [(list1[i] - list2[i])**2 for i in range(len(list1))]

    return sum([x for x in sum_of_square_differences if str(x) != 'nan'])

# VISUALIZATION FUNCTIONS
def drop_gk_attributes (player_df):
    """
    This function drops all elements belonging to goalkeeping attribute columns, since they can affect the correlation of other 
    meaningful player attributes.
    """
    player_df.drop(['goalkeeping_diving', 'goalkeeping_handling', 'goalkeeping_kicking', 'goalkeeping_positioning', 'goalkeeping_reflexes', 'goalkeeping_speed'], axis = 1, inplace = True)

    return player_df


def regression_runner ():
    """
    This function provides a dataframe with the results of the prediction of 2020's Ballon d'Or results
    Does not take any argument and
    Returns the mentioned dataframe
    """
    # Takes the explanatory variables' beta from the visualizations file as well as the fifa20 dataframe (could be modified to accept arguments and perform other regressions)
    df = fifa_20_reg
    alpha = res.params['const']
    beta_overall = res.params['overall']
    beta_wage = res.params['wage_eur']
    beta_age = res.params['age']
    beta_weight = res.params['weight_kg']
    results_list = []
        
    # Iterates through a subset made out of the explanatory variables and appends the results to the returned dataframe, which is sorted by expected points.
    for i in range(fifa_20_reg.shape[0]):
        results_list.append(alpha + fifa_20_reg.loc[fifa_20_reg['level_0'] == i]['overall'][i]*beta_overall + fifa_20_reg.loc[fifa_20_reg['level_0'] == i]['wage_eur'][i]*beta_wage + fifa_20_reg.loc[fifa_20_reg['level_0'] == i]['age'][i]*beta_age +fifa_20_reg.loc[fifa_20_reg['level_0'] == i]['weight_kg'][i]*beta_weight)
    
    fifa_20.insert(0, "Expected points", results_list)
    fifa_20.sort_values(by=['Expected points'], ascending=False, inplace=True)
    
    return fifa_20[['Expected points', 'long_name']].head(10)

# Plot functions to be included to make the plot proces more agile.