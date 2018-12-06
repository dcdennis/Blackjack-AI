#! /usr/bin/python3.6
import sys

numGames = 0
wins = 0
losses = 0
busts = 0
draws = 0

with open(sys.argv[1]) as f:
    for line in f:
        vals = line.split()
        wins += int(vals[0])
        losses += int(vals[1])
        busts += int(vals[2])
        draws += int(vals[3])
        numGames += 1
        
print("Averages W/L/B/D: " + "{0:.2f}".format(wins/numGames) + "/" + "{0:.2f}".format(losses/numGames) + "/" + "{0:.2f}".format(busts/numGames) + "/" + "{0:.2f}".format(draws/numGames))
        
