from bs4 import BeautifulSoup
import requests
import pandas as pd

url = 'https://www.pro-football-reference.com'
years = ["2015","2016", "2017","2018", "2019"]
maxp = 300
    
# request for grabbing teams
r = requests.get(url + '/teams/')
soup = BeautifulSoup(r.content, 'html.parser')
parsed_table = soup.find_all('table')[0]  

# first 2 rows are col headers
teams={}
for i,row in enumerate(parsed_table.find_all('tr')[2:]):
    if i >= maxp: 
        break
    #get all the tags with the abbreviations
    try:
        name = row.a.get_text()
        #get the abbreviations
        stub = row.a.get('href')
        teams[stub.split("/")[2]]=name
    except:
        #there are some old teams without hrefs, so we ignore them
        pass

year_df_list=[]
for year in years:
    #loop over all the teams    
    team_df_list=[]
    for team in teams.keys():
        #new request based on team abbreviation and year
        new_url=url+"/teams/"+str(team)+"/"+str(year)+"_injuries.htm"
        new_r = requests.get(new_url)
        new_soup = BeautifulSoup(new_r.content, 'html.parser')
        new_parsed_table = new_soup.find('table', attrs={"id": "team_injuries"})#[0]  

        player_df_list=[]
        for i,row in enumerate(new_parsed_table.find_all('tr')):
            date_list=[]
            opp_list=[]
            week_list=[]
            #first row contains week, date, opponent info which we can merge later with the players
            if i==0:
                games=row.find_all("th")
                for game in games[1:]:
                    opp=game.a.get_text()
                    w=game.get("data-stat").split("_")[1]
                    #only get the date part, its of the form mm/dd vsopp
                    date=str(game.get_text()[:5])

                    opp_list.append(opp)
                    week_list.append(w)
                    date_list.append(date)

                game_df=pd.DataFrame()
                game_df["Week"]=week_list
                game_df["Dates"]=date_list
                game_df["Opponent"]=opp_list

            #all the other rows of the data, used for getting player info
            else:
                if i >= maxp: 
                    break
                
                #get the player name
                player = row.find("th").get_text()
                #get the players abbreviated name (John Smith-->J.Smith)
                #Do this to match with another dataset we will be using
                p = player.split(" ")
                ps=p[0][0]+"."+p[1]

                #get all the html for weeks
                week_html = list(row.find_all("td"))
                
                #loop over the weeks, get the week, status (None, Questionable, IR, etc), and the injury description
                weeks=[]
                statuses=[]
                injuries=[]
                concussions=[]
                other_injuries=[]
                played=[]
                for w in week_html:
                    out=w.get("class")
                    if "dnp" in out:
                        played_week=False
                    else:
                        played_week=True
                    

                    week=w.get("data-stat").split("_")[1]
                    status=w.get("data-tip")
                    try:
                        status_split=status.split(":")
                        grade=status_split[0]
                        injury=status_split[1]
                        try:
                            #multiple listed injuries
                            injury_split=[x.strip().lower() for x in injury.split(",")]
                            #print("is: ", injury_split
                            #sometimes a player is listed for non injury reasons
                            #could consider undisclosed as a source for more injuries,
                            #but I think its not normally for that
                            if injury_split[0] in ["undisclosed", "notinjuryrelated"]:
                                other_injury=False
                            else:
                                other_injury=True
                            #check if one of the injuries is a concussion
                            if "concussion" in injury_split:
                                concussion=True
                            else:
                                concussion=False
                        except:
                            #only one injury
                            if injury=="Concussion":
                                concussion=True
                                other_injury=False
                            else:
                                concussion=False
                                other_injury=True
                        
                        
                    #if no injury then the above lines raise an exception, so return no status or injury
                    except:
                        grade=None
                        injury=None
                        concussion=False
                        other_injury=False

                    weeks.append(week)
                    statuses.append(grade)
                    injuries.append(injury)
                    concussions.append(concussion)
                    other_injuries.append(other_injury)
                    played.append(played_week)

                #make a df with all the player injury info for each team
                player_df=pd.DataFrame()
                player_df["Week"]=weeks
                player_df["Status"]=statuses
                player_df["Injury"]=injuries
                player_df["Player_full"]=player
                player_df["Player"]=ps
                player_df["Concussion"]=concussions
                player_df["Other_Injuries"]=other_injuries
                player_df["Played"]=played

                p_df=player_df.merge(game_df, on=["Week"])
                #add this to the list to be combined later
                player_df_list.append(p_df)

        #combine all the different players for a given team in a given year
        team_df=pd.concat(player_df_list)
        team_df["Team"]=teams[team]

        #add this df to a list to combine later
        team_df_list.append(team_df)

        print(team, year, " done")

    #combine all the teams in a given year
    Teams_df=pd.concat(team_df_list)
    Teams_df["Year"]=year

    year_df_list.append(Teams_df)
    print(year," done")

#combine all the years
Year_df = pd.concat(year_df_list)
print(Year_df["Year"].unique())
#send it to a csv
Year_df.to_csv(r"C:\Users\andyk\OneDrive\Documents\Statistical Applications\Project\Data\pfr_injuries.csv")