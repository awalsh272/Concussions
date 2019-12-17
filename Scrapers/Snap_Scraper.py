from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

url="https://www.fantasypros.com/nfl/reports/snap-counts/"


years=["2017", "2018"]

both_sides_dfs=[]

#loop over offense and defense tabs
for side in ["","defense.php"]:
    year_dfs=[]
    #get 2017 and 2018
    for year in years:
        r = requests.get(url + side + "?year="+year)
        soup = BeautifulSoup(r.content, 'html.parser')
        #table=soup.find("table")
        #print(headers)

        table_body = soup.find("tbody")

        #print(parsed_table)
        players=[]
        positions=[]
        teams=[]
        snaps=[]
        
        #loop over rows of the table
        for i,row in enumerate(table_body.find_all('tr')):
            #get the different columns
            cols=row.find_all("td")
            #all the values in each column
            vals=[col.get_text() for col in cols]
            #get different values based on the order in the columns they are
            player=vals[0].strip()
            position=vals[1]
            team=vals[2]
            snap=vals[3:-2]
            total=vals[-2]
            avg=vals[-1]

            #add found values to lists
            players.append(player)
            positions.append(position)
            teams.append(team)
            snaps.append(snap)

        year_df=pd.DataFrame()
        #week numbers for each player
        weeks=list(range(1,18))*len(players)
        #np.repeat extends each value in a list a certain number of times
        #for each week the player name etc is replicated for all weeks
        year_df["Player"]=np.repeat(players,17)
        year_df["Position"]=np.repeat(positions,17)
        year_df["Team"]=np.repeat(teams,17)
        #print(np.repeat(players, 17).shape)
        
        year_df["Week"]=weeks
        #flatten list of snaps
        flat_snaps = [item for sublist in snaps for item in sublist]
        year_df["Snaps"]=flat_snaps
        year_df["Year"]=int(year)

        year_dfs.append(year_df)
    #combine years
    side_df=pd.concat(year_dfs)
    both_sides_dfs.append(side_df)

#combine offense and defense
both_sides=pd.concat(both_sides_dfs)

#write to csv
both_sides.to_csv(r"C:\Users\andyk\OneDrive\Documents\Statistical Applications\Project\Data\snap_count.csv", )


    




