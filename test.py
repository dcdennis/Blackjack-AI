#! /usr/bin/python3.6

import json

thing = {}

for n in range(60):
    label = "LABEL" + str(n)
    thing[label] = n
    

    
    
    
with open("dict.json", "w+") as writer:
    writer.write(json.dumps(thing))
writer.close()

with open("dict.json") as f:
    data = f.read().replace("\n", " ")
f.close()

newDict = json.loads(data)
print(newDict)
