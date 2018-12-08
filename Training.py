import Deck
import numpy as np
import random
import sys

def hand_to_state(hand):
    value = hand.get_value()
    aces = hand.get_num_aces()
    return (value, aces)

def validMoves():
    return ["Hit", "Stand"]

def makeMove(hand, move, deck):
    if move == 'Hit':
        hand.add_card(deck.pop_card())
    else:
        return

def end_of_hand(hand, move):
    if hand.bust():
        return True
    if move is "Stand":
        return True

    return False

def play_dealer(dealer, deck):
    value = dealer.get_value()
    while value < 17:
        card = deck.pop_card()
        dealer.add(card)
        value += card.get_value()
            
def winner(p1, p2):
    if p1.blackjack():
        return True
    if p2.bust():
        return True
    return p1.get_value() > p2.get_value()

def random_epsilonGreedy(Q, epsilon, state, dealer):
    valid = validMoves()
    if np.random.uniform() < epsilon:
        return valid[random.randint(0, len(valid)-1)]
    else:
        Qs = np.array([Q.get((state, move), 0) for move in valid])
        return valid[np.argmax(Qs)]

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

def readCardCountingMatrix(filename):
    # Format: strategy: [list of card counts, list of BC/PE/IC values]
    cc = {}
    with open(filename) as f:
        for line in f:
            vals = line.split()
            cc[vals[0]] = [vals[1:11], vals[11:]] 

def state_dealer_tuple(state, dealer):
    dealerCard = dealer.cards[0].rank
    if dealerCard is 'Ace':
        dealerCard = 'A'
    elif dealerCard is 'Jack' or dealerCard is 'Queen' or dealerCard is 'King':
        dealerCard = '10'
    
    return (state, dealerCard)

def basic_epsilonGreedy(Q, epsilon, state, dealer):
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
            move = epsilonGreedyF(Q, epsilon, state, dealer)
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

def randomBet(tableMin, won, count):
    return random.randint(1, 5) * tableMin

def moveFromQ(Q, state):
    valid = validMoves()
    qVal = -1*sys.float_info.max
    move = ""
    for v in valid:
        curr = (state, v)
        if Q.get(curr, 0) > qVal:
            qVal = Q[curr]
            move = v
    
    return move

def playGames(Q, numGames, betF):
    
    tableMin = 10
    playerBalance = 100000
    won_last_game = False
    deck = Deck.Deck()
    player = Deck.Hand()
    dealer = Deck.Hand()
    
    win = 0
    loss = 0
    bust = 0
    draw = 0
    
    for n in range(numGames):
        
        bet = betF(tableMin, won_last_game, deck.true_count())
        playerBalance -= bet
        done = False
        player.add(deck.pop_card())     #deal to player
        deck.pop_card()                 #burn a card
        player.add(deck.pop_card())     #deal to player
        dealer.add(deck.pop_card())     #give dealer card
        print("Game number " + str(n+1))
        while not done:
            print("Player hand: ")
            print(player)
            move = moveFromQ(Q, hand_to_state(player))
            makeMove(player, move, deck)
            print("Player decides to " + move)
            
            if end_of_hand(player, move):  # player stands or busts
                play_dealer(dealer, deck)
                if player.bust():
                    print("Player Busted!")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    bust += 1
                elif winner(player, dealer):
                    print("Player Won!")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    playerBalance += bet*2
                    win += 1
                elif winner(dealer, player):
                    print("Dealer won...")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    loss += 1
                else:
                    print("Draw!")
                    print("Player: " + str(player.get_value()))
                    print("Dealer: " + str(dealer.get_value()))
                    playerBalance += bet
                    draw += 1
                    
                done = True
                player.clear()
                dealer.clear()
                print()
    return playerBalance, (win, loss, bust, draw)
            
'''
for n in range(100):
    Q, results = trainQ(1000, 0.8, 0.9, basic_epsilonGreedy)
    print("Training results basic W/L/B/D: " + str(results))
    randQ, randRes = trainQ(1000, 0.8, 0.9, random_epsilonGreedy)
    print("Training results random W/L/B/D: " + str(randRes))


    with open('random_results.txt', 'a+') as writer:
        writer.write(str(randRes[0]) + " " + str(randRes[1]) + " " + str(randRes[2]) + " " + str(randRes[3]) + '\n')
    writer.close()
    with open('basic_results.txt', 'a+') as writer:
        writer.write(str(results[0]) + " " + str(results[1]) + " " + str(results[2]) + " " + str(results[3]) + '\n')
    writer.close()
'''

# Main method: train player for 5000 iterations
if __name__ == "__main__":
    print("Training...")
    Q, results = trainQ(5000, 0.9, 0.9, basic_epsilonGreedy)
    print(Q)
    print("Playing games")
    balance, results = playGames(Q, 50, randomBet)
    print("Blackjack results basic W/L/B/D: " + str(results))
    print("Player balance: " + str(balance))

