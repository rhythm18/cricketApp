import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import numpy as np


def extract_batting_data(series_id, match_id):
    URL = 'https://www.espncricinfo.com/series/'+ str(series_id) + '/scorecard/' + str(match_id)
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')

    table_body=bs.find_all('tbody')
    batsmen_df = pd.DataFrame(columns=["Name","Desc","Runs", "Balls", "4s", "6s", "SR", "Team"])
    for i, table in enumerate(table_body[0:4:2]):
        rows = table.find_all('tr')
        for row in rows[::2]:
            cols=row.find_all('td')
            if len(cols) < 2:
                continue
            cols=[x.text.strip() for x in cols]
            if cols[0] == 'Extras':
                continue
            if len(cols) > 7:
                batsmen_df = batsmen_df.append(pd.Series(
                [re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), cols[1], 
                cols[2], cols[3], cols[5], cols[6], cols[7], i+1], 
                index=batsmen_df.columns ), ignore_index=True)
            else:
                batsmen_df = batsmen_df.append(pd.Series(
                [re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), cols[1], 
                0, 0, 0, 0, 0, i+1], index = batsmen_df.columns), ignore_index=True)
                
    for i in range(2):
        tfoot_tags = bs.find_all("tfoot")
        if len(tfoot_tags) > i:
            dnb_row = tfoot_tags[i].find_all("div")
            for c in dnb_row:
                dnb_cols = c.find_all('span')
                dnb = [x.text.strip().split("(c)")[0] for x in dnb_cols]
                dnb = filter(lambda item: item, [re.sub(r"\W+", ' ', x).strip() for x in dnb])
                for dnb_batsman in dnb:
                    batsmen_df = batsmen_df.append(pd.Series([dnb_batsman, "DNB", 0, 0, 0, 0, 0, i+1], index = batsmen_df.columns), ignore_index =True)

    return batsmen_df

def extract_bowling_data(series_id, match_id):

    URL = 'https://www.espncricinfo.com/series/'+ str(series_id) + '/scorecard/' + str(match_id)
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')

    table_body=bs.find_all('tbody')
    bowler_df = pd.DataFrame(columns=['Name', 'Overs', 'Maidens', 'Runs', 'Wickets',
                                      'Econ', 'Dots', '4s', '6s', 'Wd', 'Nb','Team'])
    for i, table in enumerate(table_body[1:4:2]):
        rows = table.find_all('tr')
        for row in rows:
            cols=row.find_all('td')
            if len(cols) > 10:
                bowler_df = bowler_df.append(pd.Series([cols[0].text.strip(), cols[1].text.strip(), 
                                                        cols[2].text.strip(), cols[3].text.strip(), 
                                                        cols[4].text.strip(), cols[5].text.strip(), 
                                                        cols[6].text.strip(), cols[7].text.strip(), 
                                                        cols[8].text.strip(), cols[9].text.strip(), 
                                                        cols[10].text.strip(), (i==0)+1], 
                                                       index=bowler_df.columns ), ignore_index=True)
    return bowler_df

def calculate_batting_points(batsmen_df):

    int_cols = ["Runs", "Balls", "4s", "6s", "Team"]
    for col in int_cols:
        batsmen_df[col] = batsmen_df[col].astype(int)
        
    batsmen_df["base_points"] = batsmen_df["Runs"]
    batsmen_df["pace_points"] = batsmen_df["Runs"] - batsmen_df["Balls"]
    batsmen_df["milestone_points"] = (np.floor(batsmen_df["Runs"]/25)).replace(
                                      {1.0:5, 2.0:15, 3.0:30, 4.0:50, 5.0:50, 6.0:50, 7.0:50, 8.0:50})
    batsmen_df["impact_points"] = batsmen_df["4s"] + 2 * batsmen_df["6s"] + \
                                  (batsmen_df["Runs"] == 0) * (batsmen_df["Desc"] != "not out") * \
                                  (batsmen_df["Desc"] != "DNB") * (batsmen_df["Desc"] != "absent hurt") * (-5) 
    batsmen_df["batting_points"] = batsmen_df["base_points"] + batsmen_df["pace_points"] + \
                                    batsmen_df["milestone_points"] + batsmen_df["impact_points"]    
    
    return batsmen_df
    
    
def calculate_bowling_points(bowler_df):
 
    int_cols = ["Wickets","Runs", "Dots", "Maidens", "Team"]
    for col in int_cols:
        bowler_df[col] = bowler_df[col].astype(int) 
    bowler_df["Balls"] = bowler_df["Overs"].apply(lambda x: x.split(".")).\
                        apply(lambda x: int(x[0])*6 + int(x[1]) if len(x)>1 else int(x[0])*6)

    bowler_df["base_points"] = 20*bowler_df["Wickets"]
    bowler_df["pace_points"] = 1.5*bowler_df["Balls"] - bowler_df["Runs"]
    bowler_df["pace_points"] = bowler_df["pace_points"] + (bowler_df.loc[:,"pace_points"]>0) * bowler_df["pace_points"]
    bowler_df["milestone_points"] = bowler_df["Wickets"].replace({1:0, 2:5, 3:15, 4:30, 5:50, 6:50, 7:50, 8:50})
    bowler_df["impact_points"] = bowler_df["Dots"] + bowler_df["Maidens"]*25
    bowler_df["bowling_points"] = bowler_df["base_points"] + bowler_df["pace_points"] + \
                                    bowler_df["milestone_points"] + bowler_df["impact_points"]
                                    
    return bowler_df