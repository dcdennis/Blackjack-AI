import json
from ast import literal_eval


def writeQ(filename, Q):
    
    strQ = {}
    for entry in Q:
        strQ[str(entry)] = Q[entry]
    
    
    with open(filename, "w+") as writer:
        writer.write(json.dumps(strQ))
    writer.close()

def readQ(filename):
    with open(filename) as f:
        data = f.read().replace("\n", " ")
    f.close()
    
    strQ = json.loads(data)
    Q = {}
    
    for entry in strQ:
        
        Q[literal_eval(entry[1:-1])] = strQ[entry]
    
    return Q


