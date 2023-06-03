"""
Created on Sat Jun  3 15:18:11 2023

@author: akshayghosh

Version: 0.0.1
"""

Clone to folder where you would like to do your analysis:
```
git clone https://github.com/akshay-ghosh/hockey_kde.git .
```

Example of how to do a KDE analysis of an NHL team's shot locations from the 2022-23 NHL season:

First import the 'hockey_variability' module:
```
from hockey_kde import hockey_variability as hv
```

This will return the KDE plot of all of Ottawa's shots for the season:
```
hv.calc_shot_kde(specific_game = False,OFF_team = 'OTT',date_string = False, DEF_team = None,playoffs = False)
```

This will return the KDE plot of the OTT vs TBL game from March 23rd, 2023:
```
hv.calc_shot_kde(specific_game = True,OFF_team = 'OTT',date_string = '2023-03-23', DEF_team = None,playoffs = False)
```

This will return the KDE plot of every OTT vs TOR game for the 2022-23 regular season:
```
hv.calc_shot_kde(specific_game = False,OFF_team = 'OTT',date_string = None, DEF_team = 'TOR',playoffs = False)
```

NOTE:
'playoffs' must be set to either 'True' or 'False'. You CANNOT combine regular season and playoff data.
