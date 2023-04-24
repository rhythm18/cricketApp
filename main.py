import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

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
