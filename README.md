# README

## How Daryl's code works

He uses ReCom (a Markov Chain proposal function) to generate 100,000 plans

First he generates a "starting_plan.json". This plan assigns each Census Tract
to a district subject to population balance constraints. Each Census Tract's
district is given in nodes, under the "New_Seed" key.

`data["nodes'][0]['New_Seed']`

## Understanding flips_X.json

Each `flips_X.json` contains 10,000 different plans. More accurately, they are
a collection of dictionaries of the nodes that changed assignment at each step,
so you just have to update a single dictionary with the new assignments. 

It starts with "starting_plan.json", which assigns each Census Tract to a
district.

If you have {"21": 13}, this means that Census Tract 21 has been assigned to
District 13.

[TODO] Issue with Census Tracts not matching between Stephanopoulos's data and
Daryl's data. For instance, 13083040101, Census Tract 401.01 (and 401.02) in
Dade County, but Stephanopoulos only has 1308040100, Census Tract 401 in Dade
County. The tracts are combined.
