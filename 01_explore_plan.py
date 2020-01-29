import json


with open("Tract_Ensembles/13/starting_plan.json") as f:
    data = json.load(f)
    print(len(data["nodes"]))
    print(data["nodes"][0:1])

    for idx,node in enumerate(data["nodes"]):
        #print(idx, node["New_Seed"])
        if (node["New_Seed"] == 13):
            print(node["id"], 0)
        else:
            #print(node["New_Seed"])
            pass
