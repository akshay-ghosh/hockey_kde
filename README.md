Created on Sat Jun  3 15:18:11 2023

@author: akshayghosh

Version: 0.0.1

############################################################################

Example to preview the 2023 Cup finals:
![panthers_vs_knights_regseason_kde](https://github.com/akshay-ghosh/hockey_kde/assets/42668323/3e202eb0-f79d-45a9-963c-d04311762708)

Clone to folder where you would like to do your analysis:
```
git clone https://github.com/akshay-ghosh/hockey_kde.git .
```

DOWNLOAD SHOT DATA (type this in the terminal):
```
$ curl https://peter-tanner.com/moneypuck/downloads/shots_2022.zip -o shots_2022
```

Run the file ```modify_shot_data.py```, and properly set the input and output filenames.

Edit line 70 of ```hockey_variability.py``` to where you saved the modified csv shot data.

Example of how to do a KDE analysis of an NHL team's shot locations from the 2022-23 NHL season:

First create your analysis file in the ```hockey_variability``` folder.

Then import the 'hockey_variability' module:
```
import hockey_variability as hv
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

To create the Panthers vs Knights plot:
```
hv.calc_shot_kde(specific_game = False,OFF_team = 'FLA',date_string = None, DEF_team = 'VGK',playoffs = False)
```

NOTE:
'playoffs' must be set to either 'True' or 'False'. You CANNOT combine regular season and playoff data.
