import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def csv_reader (file):
    return pd.read_csv(file, low_memory = False)
     
# First, we define the function that will iterate through every column of the dataset asking us if we want to keep it or not:
def column_droper(df):
    for column in df.columns:
        column_keeper = "--"
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
    
    for player in top10_year:
        for long_name in df["long_name"]:
            if re.match(regex_dict[player], long_name):
                info_dict["long_name"].append(long_name)
            else:
                pass
    
    for player in info_dict["long_name"]:
        info_dict['fifa_index'].append(df[(df['long_name'] == player)].index[0])

    for i in range(len(info_dict['fifa_index'])):
        info_dict["rating"].append(df[(df['long_name'] == info_dict['long_name'][i])]['overall'][info_dict['fifa_index'][i]])

    info_dict['short_name'] = [short_name for short_name in classification['Player']]
    
    for i in range(len(info_dict['fifa_index'])):
        info_dict['points'].append(classification[(classification['Player'] == info_dict['short_name'][i])]['Points'][i])

    merged_info = pd.DataFrame(info_dict)
    merged_info.sort_values(by=["fifa_index"])
    df = df.join(merged_info["points"])

    return df