from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

url="https://www.footballoutsiders.com/stats/nfl/snap-counts?team=ALL&week=%s&position=ALL&year=%s&op=Submit&form_build_id=form-E-iLYebXQhn92QjRjHrJje10kk0rok8-P9qqKktwfAY&form_id=fo_stats_snap_counts_form"

years=["2017", "2018"]

year_dfs=[]
#get 2017 and 2018
for year in years:
    week_dfs=[]
    #drop down for week, so loop over the weeks and get a different url for each
    for week in range(1, 18):
        r = requests.get(url %(week, year))
        soup = BeautifulSoup(r.content, 'html.parser')
        
        table_body = soup.find_all("tbody")[1]

        players=[]
        positions=[]
        teams=[]
        snaps=[]
        off_snaps=[]
        def_snaps=[]
        st_snaps=[]
        
        #loop over rows of the table
        for i,row in enumerate(table_body.find_all('tr')):
            #get the different columns
            cols=row.find_all("td")
          
            #all the values in each column
            vals=[col.get_text() for col in cols]

            #get different values based on the order in the columns they are

            #some weird numbering and team things connected to the names
            player=vals[0].split("-")[1].strip()
            team=vals[1]
            position=vals[2]
            start=vals[3]
            snap=vals[4]
            off_snap=vals[5]
            def_snap=vals[7]
            st_snap=vals[9]

            #add found values to lists
            players.append(player)
            positions.append(position)
            teams.append(team)
            snaps.append(snap)
            off_snaps.append(off_snap)
            def_snaps.append(def_snap)
            st_snaps.append(st_snap)

            
        #turn the lists into dataframe columns
        week_df=pd.DataFrame()
        
        week_df["Player"]=players
        week_df["Position"]=positions
        week_df["Team"]=teams
        week_df["Week"]=week
        week_df["Snaps"]=snaps
        week_df["Off_Snaps"]=off_snaps
        week_df["Def_Snaps"]=def_snaps
        week_df["ST_Snaps"]=st_snaps

        #add to list to concat
        week_dfs.append(week_df)
        print("Done with year: %s, week: %s" %(year, week))

    #combine all weeks for a given year
    year_df=pd.concat(week_dfs)
    
    year_df["Year"]=int(year)
    year_dfs.append(year_df)
    print("Done with year: %s" %(year))

#combine the years
all_df=pd.concat(year_dfs)
#write to csv
all_df.to_csv(r"C:\Users\andyk\OneDrive\Documents\Statistical Applications\Project\Data\snap_count_V2.csv")


    




