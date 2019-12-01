# Script First Worked on: 2019-12-1
# By: Charles S Turvey (With huge thanks to BitBait)

import json
import requests

# The request template (all one string lines are one string, just formatted in unusual python {source 0})
template = (
            # The website
            "https://app.bto.org/webs-reporting/"
            
            # The first year of the desired WeBS report edition (2005 up to 2017, we're using 17/18 so 2017)
            # (Years later than 2017 default to 2017 (writing this in Dec 2019), earlier than 2005 fail)
            "SpecLocReport?reported_year=2017"
            
            # The first table row index to collect...
            "&start_at={:d}"
            
            # ... and the number of rows to get starting from this, inclusive
            # (Appears to cap out at 120, i.e. 4 pages of data at the standard 30 per page)
            "&go_on_for=100"
            
            # Whether or not to include supplementary data (presumably can be y or n)
            "&inc_supps=y"
            
            # For location selection, the ID corresponding to the location selected
            # e.g. "LOC648397" for the "Severn Estuary" location page
            # Must be "" for species selection
            "&loc_id="
            
            # For location selection, where the location is (argument omitted in species searches):
            # "GB" for Great Britain
            # "NI" for Northern Ireland
            # (Others may exist, but doesn't seem to mind omission anyway)
            # "&reg_label=GB"
            
            # For species selection, the ID  corresponding to the species selected
            # e.g. "46" for the "Mute Swan" page
            # Must be "" for location selection
            "&species_code={:d}"
            
            # For location pages, the group of birds to filter by:
            # "" for all (must be set to this for species pages)
            # "WIL" for Wildfowl (Like Ducks, Geese, Swans...)
            # "WAD" for Waders (As in shoreline wading birds)
            # "GUL" for Gulls
            # "TER" for Terns
            # "OTH" for Others (Like Kingfishers, Coot, Moorhen, Heron, Cormorant...)
            "&birdy="
            
            # For location pages, whether to sort by taxon (y or n, but must be n for species pages)
            "&taxonsort=n"
            
            # For species pages, the region to filter by:
            # (the "-" in -1, -2, -3 or -4 may also be replaced with 0 indexed values to get specific regions)
            # "0" for all (must be set to this for location pages)
            # "-1" for English counties
            # "-2" for Welsh counties
            # "-3" for Scottish counties
            # "-4" for Northern Irish Counties
            # "-5" for the Isle of Man
            # "-6" for the Channel Islands
            # "-7" for Offshore counties
            "&area=0"
            
            # For species pages, the type of habitat to filter by:
            # "0" for all (must be set to this for location pages)
            # "1" for natural inland still water
            # "2" for reservoir
            # "3" for gravel pit
            # "4" for river or marsh
            # "5" for open coast
            # "6" for estuarine
            # "7" for goose or swan 'fields'
            # "8" for unknown
            "&habicat=0"

            # Looks like a "cachebusting" parameter; ensures that each request distinct to avoid being served old data?
            # This one appears to be made up of the time since the epoch to 3 D.P. at the first open of the page
            # to which one is added each time a new request is made {discovered thanks to source 3}
            "&_={:d}"
            )

"""
0 https://stackoverflow.com/a/17630918
1 https://benbernardblog.com/web-scraping-and-crawling-are-perfectly-legal-right/
2 https://bto.org/robots.txt
3 https://stackoverflow.com/a/3687765
"""