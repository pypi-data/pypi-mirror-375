Package to retrieve Hyrox race data programmatically

At the moment, only 3 endpoints -- examples below



```commandline
s6races_info = list_races(season=6)  #  list available races of season 6
all_races_info = list_races()  #  without passing in a season parameter - see all available races in the data warehouse
s6races_subset = get_season(season=6, locations=['london', 'hamburg'])  # get a subset of races from a specified season
london_season6 = get_race(season=6, location="london")   #  get a specific race
hamburg_season6 = get_race(season=6, location="hamburg", division="open", gender="m")  #  get a specific race, with extra-filtering applied
```
