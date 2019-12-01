# Script First Worked on: 2019-12-1
# By: Charles S Turvey (With huge thanks to BitBait)

import requests

template = "https://app.bto.org/webs-reporting/" \
           "SpecLocReport?reported_year=2017" \
           "&start_at=0" \
           "&go_on_for=30" \
           "&inc_supps=y" \
           "&loc_id=LOC648397" \
           "&reg_label=GB" \
           "&species_code=" \
           "&birdy=" \
           "&taxonsort=y" \
           "&area=0" \
           "&habicat=0" \
           # "&_=1575160388994"  # TODO: Find out what this is for (in fact, find out what all of these do)
