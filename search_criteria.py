## Demo file!
### Syntax is [search terms, distro list, grinder selection, context required, distro number]
### Grinder List:
### 1 = Main grinder
### 2 = Forced notification grinder

### Context required 0 = no, 1 = yes
### Distro number to track to see if notifications have already been sent to this distro

from distro_lists import *

search_queries = [
['your business AND (location one OR location two) -filter:retweets', distro_list_1, 1, 0, 1],
['(kill OR shoot OR murder) (your executive OR other executive OR other executive) -filter:retweets', distro_list_3, 1, 0, 3],
['geocode:38.948123,-77.427195,1km', distro_list_1, 2, 0, 1],
['(doxx OR dox OR doxing OR doxxing) AND (your organization OR your orgs nickname) -filter:retweets', distro_list_6, 2, 0, 6],
['your org leak -filter:retweets', distro_list_1, 2, 0, 1]