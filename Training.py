import Deck
import numpy as np
import random
import sys
import fileIO


'''Basic Functions'''

# hand_to_state(): returns a tuple of the hand's value and number of aces
def hand_to_state(hand):
    value = hand.get_value()
    aces = hand.get_num_aces()
    return (value, aces)


# validMoves(): returns a list of valid moves (hit or stand)
def validMoves():
    return ["Hit", "Stand"]


# makeMove(): applies move to hand
def makeMove(hand, move, deck):
    if move == 'Hit':
        hand.add_card(deck.pop_card())
    else:
        return


# end_of_hand(): returns true if move marks end of play
def end_of_hand(hand, move):
    if hand.bust():
        return True
    if move is "Stand":
        return True
    return False


# playDealer(): makes play decisions for dealer (stand on values of 17 or more) 
def play_dealer(dealer, deck):
    value = dealer.get_value()
    while value < 17:
        card = deck.pop_card()
        dealer.add(card)
        value += card.get_value()


# winner(): returns true if p1 beats p2
def winner(p1, p2):
    if p1.blackjack():
        return True
    if p2.bust():
        return True
    return p1.get_value() > p2.get_value()


# readBasicMatrix(): reads in decision matrix for basic player
def readBasicMatrix(filename):
    decisions = {}
    dealer = []
    player = []
    index = 0
    with open(filename) as f:
        dealer = f.readline().split()
        player = [(int(entry.split(",")[0][1:]), int(entry.split(",")[1][:1])) for entry in f.readline().split()]
        for line in f:
            vals = line.split()
            for i in range(len(dealer)):
                decisions[(player[index], dealer[i])] = vals[i]
            index += 1
    f.close()
    return decisions


# readCardCountingmatrix(): reads in card counting matrix with card counts and BC/PA/IC values
def readCardCountingMatrix(filename):
    # Format: strategy: [list of card counts, list of BC/PE/IC values]
    cc = {}
    with open(filename) as f:
        for line in f:
            vals = line.split()
            cc[vals[0]] = [vals[1:11], vals[11:]] 
    return cc


# state_dealer_tuple(): returns a tuple of state and dealer's card
def state_dealer_tuple(state, dealer):
    dealerCard = str(dealer.cards[0].rank)
    if dealerCard is 'Ace':
        dealerCard = 'A'
    elif dealerCard is 'Jack' or dealerCard is 'Queen' or dealerCard is 'King':
        dealerCard = '10'
    return (state, dealerCard)



'''Epsilon Greedy Functions'''

# random_epsilonGreedy(): epsilon greedy function for random player
def random_epsilonGreedy(Q, epsilon, state, dealer, deck):
    valid = validMoves()
    if np.random.uniform() < epsilon:
        return valid[random.randint(0, len(valid)-1)]
    else:
        Qs = np.array([Q.get((state, move), 0) for move in valid])
        return valid[np.argmax(Qs)]


# basic_epsilonGreedy(): epsilon greedy function for basic player
def basic_epsilonGreedy(Q, epsilon, state, dealer, deck):
    valid = validMoves()
    decisions = readBasicMatrix("basic_matrix.txt")
    lookupTuple = state_dealer_tuple(state, dealer)
    if np.random.uniform() < epsilon:
        if lookupTuple in decisions:
            return decisions[lookupTuple]
        else:
            return valid[random.randint(0, len(valid)-1)]
    else:
        Qs = np.array([Q.get((state, move), 0) for move in valid])
        return valid[np.argmax(Qs)]
    
    return


# counter_epsilonGreedy(): epsilon greedy function for card counter
def counter_epsilonGreedy(Q, epsilon, state, dealer, deck):
    valid = validMoves()
    basic_decisions = readBasicMatrix("basic_matrix.txt")
    counter_decisions = readBasicMatrix("counter_matrix.txt")
    lookupTuple = state_dealer_tuple(state, dealer)
    if np.random.uniform() < epsilon:
        if lookupTuple in counter_decisions:
            decision = counter_decisions[lookupTuple]
            if decision == "Hit" or decision == "Stand":
                return decision
            else:
                print(lookupTuple)
                print("|" + str(decision) + "|")
                print(deck.true_count())
                if deck.true_count() >= int(decision):
                    if basic_decisions[lookupTuple] is "Stand":
                        return "Hit"
                    else:
                        return "Stand"
        elif lookupTuple in basic_decisions:
            return basic_decisions[lookupTuple]
        else:
            return valid[random.randint(0, len(valid)-1)]
    else:
        Qs = np.array([Q.get((state, move), 0) for move in valid])
        return valid[np.argmax(Qs)]
    
    return
            
 
 
'''Training Functions'''
            
# trainQ(): trains player for nRepetitions using the provided epsion greedy function
def trainQ(nRepetitions, epsilonDecayRate, learningRate, epsilonGreedyF):
    Q = {}
    rho = learningRate
    epsilon = 1.0
    deck = Deck.Deck()
    hand = Deck.Hand()
    dealer = Deck.Hand()
    
    win = 0
    loss = 0
    bust = 0
    draw = 0

    for n in range(nRepetitions):
        epsilon *= epsilonDecayRate
        step = 0
        done = False
        
        hand.add(deck.pop_card())
        hand.add(deck.pop_card())
        deck.pop_card()
        dealer.add(deck.pop_card())

        while not done:
            step += 1
            state = hand_to_state(hand)
            move = epsilonGreedyF(Q, epsilon, state, dealer, deck)
            #print("Move is " + move)
            makeMove(hand, move, deck)
            newState = hand_to_state(hand)
            

            if state not in Q:
                Q[(state, move)] = 0

            if end_of_hand(hand, move):  # player stands or busts
                play_dealer(dealer, deck)
                if hand.bust():
                    penalty = 0.5 * (hand.get_value()-21)
                    Q[(state, move)] += rho * (-penalty - Q[(state, move)])
                    bust += 1
                elif winner(hand, dealer):
                    Q[(state, move)] += rho * (1 + Q[(state, move)])
                    win += 1
                elif winner(dealer, hand):
                    '''We may reduce the -1 to put a smaller penalty on losing since
                       you can make a good decision and still lose (i.e. Stand at 19)
                    '''
                    penalty = 0.03 * (dealer.get_value() - hand.get_value())
                    Q[(state, move)] += rho * (Q[(state, move)] - penalty)
                    loss += 1
                else:
                    draw += 1
                    
                done = True
                hand.clear()
                dealer.clear()

            if step > 1:
                Q[(oldState, oldMove)] += rho * (Q[(state, move)] - Q[(oldState, oldMove)])

            oldState, oldMove = state, move
            state = newState
    
    return Q, (win, loss, bust, draw)


# moveFromQ(): makes move based on Q table
def moveFromQ(Q, state):
    valid = validMoves()
    qVal = -1*sys.float_info.max
    move = ""
    for v in valid:
        curr = (state, v)
        if Q.get(curr, 0) > qVal:
            qVal = Q.get(curr, 0)
            move = v 
    return move



'''Betting Functions'''

# randomBet(): makes a bet for random player
def randomBet(tableMin, won, bet):
    return random.randint(1, 6) * tableMin


# basicBet(): makes a bet for basic player
def basicBet(tableMin, won, bet):
    if won:
        return min(bet + (5 * (random.randint(1, 5))), 7*tableMin)
    else:
        return max(bet - (5 * (random.randint(1, 5))), tableMin)


# counterBet(): makes a bet for card counting player (defaults to basic, else calls appropriate method)
def counterBet(tableMin, count, deck, bet, won, counterType):    
    if counterType is "obvious":
        return obviousBet(tableMin, count)
    elif counterType is "penetration":
        return penetrationBet(tableMin, count, deck, bet, won)
    elif counterType is "camo":
        return camouflageBet(tableMin, count, deck, bet, won)
    elif counterType is "allin":
        return allInBet(tableMin, count, deck, bet, won)
    else:
        return basicCounterBet(tableMin, count)


# basicCounterBet(): makes a bet for card counting player (basic)
def basicCounterBet(tableMin, count):
    if count < 0:
        return tableMin + 5*random.randint(0, 3)
    elif count == 0:
        return tableMin + 10*random.randint(0, 3)
    else:
        return tableMin + round(count)*5*random.randint(0, 3)
 
 
# obviousBet(): makes a bet for card counting player (obvious)
def obviousBet(tableMin, count):
    if count < 1:
        return tableMin
    elif count >= 1 and count < 5:
        return tableMin*(2**(count-1))
    else:
        return tableMin*12


# penetrationBet(): makes a bet for card counting player (pentration)
def penetrationBet(tableMin, count, deck, bet, won):
    if deck.penetration() < 0.6:
        return basicBet(tableMin, won, bet)
    else:
        return basicCounterBet(tableMin, count)


# camouflageBet(): makes a bet for card counting player (camouflage)
def camouflageBet(tableMin, count, deck, bet, won):
    initialBet = penetrationBet(tableMin, count, deck, bet, won)
    if won is False:
        if initialBet == tableMin:
            return tableMin
        else:
            bestBet = min(bet + round(((initialBet-bet)/2) / 5)*5, round(((initialBet-tableMin)/2) / 5)*5)
            return max(bestBet, tableMin)
    elif won is None:
        return bet
    else:
        return initialBet


# allInBet(): 
def allInBet(tableMin, count, deck, bet, won):
    if deck.penetration() < 0.75:
        return basicBet(tableMin, won, bet)
    else:
        if count > 7:
            return 50000
        else:
            return basicBet(tableMin, won, bet)


''' Testing Functions '''

# writeGameData(): write game data to file
def writeGameData(counterType, won, bet, count, state, dealer, penetration):
    with open("game_data.txt", "a+") as f:
        f.write(str(counterType) + "\t" str(won) + "\t" + str(bet) + "\t" + str(count) + "\t" + str(state) + "\t" + str(dealer) + "\t" + str(penetration) + "\n")
    f.close()


# playGames(): plays numGames games using the provided Q table and betting function
def playGames(Q, numGames, betF, counterType=None):
    tableMin = 10
    bet = tableMin
    playerBalance = 100000
    won_last_game = False
    deck = Deck.Deck()
    deck.shuffle()
    player = Deck.Hand()
    dealer = Deck.Hand()
    
    win = 0
    loss = 0
    bust = 0
    draw = 0
    
    for n in range(numGames):
        
        if counterType is not None:
            bet = betF(tableMin, deck.true_count(), deck, bet, won_last_game, counterType)
        else:
            bet = betF(tableMin, won_last_game, bet)
   
        playerBalance -= bet
        count_at_bet = deck.true_count()
        done = False
        print("-------------------------------")
        print("Game number " + str(n+1))
        print("Running count is " + str(deck.count))
        print("Table count is " + str(count_at_bet))
        print("Player bets $" + str(bet))
        player.add(deck.pop_card())     #deal to player
        player.add(deck.pop_card())     #deal to player
        dealer.add(deck.pop_card())     #give dealer card
        print("Player hand: ")
        print(player, end="\n\n")
        print("Dealer hand: ")
        print(dealer, end="\n\n")
        
        while not done:
            move = moveFromQ(Q, hand_to_state(player))
            makeMove(player, move, deck)
            print("Player decides to " + move)
            print("Player hand: ")
            print(player, end="\n\n")
            if end_of_hand(player, move):  # player stands or busts
                play_dealer(dealer, deck)
                if player.bust():
                    print("Player Busted!")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    won_last_game = False
                    bust += 1
                elif winner(player, dealer):
                    if player.blackjack():
                        print("BLACKJACK!")
                        playerBalance += bet*2.5
                    else:
                        print("Player Won!")
                        playerBalance += bet*2
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    won_last_game = True
                    win += 1
                elif winner(dealer, player):
                    print("Dealer won...")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    won_last_game = False
                    loss += 1
                else:
                    print("Draw!")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    playerBalance += bet
                    won_last_game = None
                    draw += 1
                    
                done = True
                writeGameData(won_last_game, bet, count_at_bet, hand_to_state(player), hand_to_state(dealer), deck.penetration())
                player.clear()
                dealer.clear()
                print()
                   
        if(counterType is "allin"):
            if bet > 500:
                print("Big Spender!!! Balance:", playerBalance)
                break;
            
                  
    return playerBalance, (win, loss, bust, draw)


# runMultiple(): test using specified player type and number of iterations
def runMultiple(playerType, iterations, betF, counterType=None):
    for n in range(iterations):
        Q = fileIO.readQ(playerType + "Q.json")
        balance, results = playGames(Q, 100, betF, counterType)
        if counterType is not None:
            playerType += "_" + counterType
        with open(playerType + '_results.txt', 'a+') as writer:
            writer.write(str(results[0]) + " " + str(results[1]) + " " + str(results[2]) + " " + str(results[3]) + " " + str(balance) + '\n')
        writer.close()

def fullRun(playerType, numGames, betF, counterType=None):
    Q = fileIO.readQ(playerType + "Q.json")
    balance, results = playGames(Q, numGames, betF, counterType)
    if counterType is not None:
        playerType += "_" + counterType
    with open(playerType + '_results.txt', 'a+') as writer:
        writer.write(str(results[0]) + " " + str(results[1]) + " " + str(results[2]) + " " + str(results[3]) + " " + str(balance) + '\n')
    writer.close()


# Main method: train player for 5000 iterations
if __name__ == "__main__":
    '''
    print("Training")
    Q, results = trainQ(5000, 0.99, 0.99, random_epsilonGreedy)
    fileIO.writeQ("randomQ.json", Q)
    
    for item in Q:
        print(str(item) + ": " + str(Q[item]))
 
    print(results)
    '''
    numIterations = int(sys.argv[3])
    counterType = sys.argv[2]
    if counterType == "None":
        counterType = None
    
    if counterType is None:
        if sys.argv[1] is "random":
            runMultiple(sys.argv[1], numIterations, randomBet)
        else:
            runMultiple(sys.argv[1], numIterations, basicBet)
    else:
        runMultiple(sys.argv[1], numIterations, counterBet, counterType)
    
    #runMultiple('counter', 20, 'penetration')
    

