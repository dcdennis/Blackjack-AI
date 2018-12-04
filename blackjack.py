"""

This module contains code from
Think Python: an Introduction to Software Design
Allen B. Downey
  
Modified Card, Deck, Hand to fit the requirements of our Blackjack AI:
    - Devin Dennis
    - Tanner Nickels
    - Diego Batres
"""

import random

class Card(object):
    """represents a standard playing card."""

    suit_names = ["Clubs", "Diamonds", "Hearts", "Spades"]
    rank_names = [None, "Ace", "2", "3", "4", "5", "6", "7", 
              "8", "9", "10", "Jack", "Queen", "King"]
   

    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        self.value = self.get_value()

    def __str__(self):
        return '%s of %s has a value of %s.' % (Card.rank_names[self.rank],
                             Card.suit_names[self.suit], self.value)

    def __cmp__(self, other):
        t1 = self.suit, self.rank
        t2 = other.suit, other.rank
        return cmp(t1, t2)

    def __lt__(self, other):
        if self.suit < other.suit:
            return True
        elif self.suit > other.suit:
            return False
        else:
            return self.rank < other.rank

    def get_value(self):
        rank = Card.rank_names[self.rank]
        if self.is_ace():
            return 11
        elif rank in ["Jack", "Queen", "King"]:
            return 10
        else:
            return int(rank)
        
    def is_ace(self):
        return Card.rank_names[self.rank] == "Ace"
        

class Deck(object):
    """represents a deck of cards"""
    
    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1, 14):
                card = Card(suit, rank)
                self.cards.append(card)

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def add_card(self, card):
        """add a card to the deck"""
        self.cards.append(card)

    def pop_card(self, i=-1):
        """remove and return a card from the deck.
        By default, pop the last card."""
        return self.cards.pop(i)
    
    def shuffle(self):
        """shuffle the cards in this deck"""
        random.shuffle(self.cards)

    def sort(self):
        """sort the cards in ascending order"""
        self.cards.sort()

    def move_cards(self, hand, num):
        """move the given number of cards from the deck into the Hand"""
        for i in range(num):
            hand.add_card(self.pop_card())


class Hand(Deck):
    """represents a hand of playing cards"""
    
    def __init__(self, label=''):
        self.label = label
        self.cards = []
    
    """returns the value for the given Hand"""
    def get_value(self):
        hand_value = 0
        aces = self.get_num_aces()
        for card in self.cards:
            hand_value += card.value
        while (hand_value > 21) and aces: # corner case to adjust value of hand given the number of aces and current value of the player's hand
            hand_value -= 10
            aces -= 1
        return hand_value
            
    """ helper method for get_value()"""
    def get_num_aces(self):
        num_aces = 0
        for card in self.cards:
            if card.is_ace():
                num_aces += 1
        return num_aces

    """adds card to hand"""
    def add(self, card):
        self.cards.append(card)
        return self.cards
    


class Dealer(Hand): # will be the instance for the House to play and facade for play hand mechanics
    """represents a dealer and general play functionality"""
    def __init__(self, name, deck):
        Hand.__init__(self)
        self.name = name
        self.deck = deck
        self.isBust = False

    def show_hand(self): # print the players hand
        print("%s Hand: " % self.name)
        for card in self.cards:
            print("\t%s" % card)
        print('\tTotal value of hand is %s' % self.get_value()) # print hand value

    def hit(self): # adds card from deck to the dealer/player hand
        card = self.deck.pop_card()
        self.add(card)
        return card #self.hand

    def stand(self):
        print("%s stands with %s" % (self.name, self.get_value()))
        #return None # what should we do here??

    def check_for_bust(self): # returns flag to check if player is busted
        if self.get_value() > 21:
            self.isBust = True
            print("%s busts with %s!" % (self.name, self.get_value()))
        else:
            self.isBust = False
            self.stand()
        return self.isBust


class Player(Dealer): # Dealer already has general play functionality so the player will play through that classes functions
    """represents a blackjack player"""
    def __init__(self, person, deck, ): # will need to construct a new player every game
        self.bet = person.bet # used to check validity of certain moves within play_hand
        self.balance = person.get_available_balance() # used to check validity of certain moves within play_hand
        self.person = person
        self.isBust = False
        Dealer.__init__(self, person.name, deck)
        
    def doubledown(self): # takes care of the person's financial bookkeeping
        self.person.available_balance -= self.bet
        self.bet += self.bet
        print("%s doubled down.. balance is now $%s" % (self.person.name, self.person.available_balance))
        
    def addEarnings(self, earnings):
        self.person.add_to_balance(earnings)
    
    def get_available_balance(self):
        return self.person.available_balance
    
    
class Person(object): # provides data persistence throughout a blackjack session, atleast thats the idea
    def __init__(self, name, cash):
        self.name = name
        self.available_balance = cash
        self.isAI = True 
        self.bet = -1000
        
    def get_available_balance(self): # persistent access to buba jenkins available_balance
        return self.available_balance
    
    def add_to_balance(self, cash): # if game was won, add earning to balance here
        self.available_balance += cash
        
    #TODO: update betting functionality?
    def place_bet(self): # removes money being bet in a game from balance
        if (self.available_balance <= 10):
            # Bet all money if balance < 10
            self.bet = self.available_balance
        else:
            # Bet a random number between 10 and 100, or 10 and balance if < 100
            self.bet = random.randint(10, min(100, self.available_balance))
        self.available_balance -= self.bet
        return self.bet
    
    def play_session_of_blackjack(self): # currently continues to play games until you go broke
        games_played = 0
        while True:
            games_played += 1
            winnings_or_lack_thereof = blackjack(self) # currently only plays a game against the house
            #self.add_to_balance(winnings_or_lack_thereof) # will add 0 for L, earnings for W, move adding to displayer 
            if self.available_balance <= 0:
                print("Out of money :(")
                print("%s Played %d games!" % (self.name, games_played))
                break
        
  
class Casino(object):
    def __init__(self):
        self.scum_bags = 12
       
       
def find_defining_class(obj, meth_name): # useful when you cant tell where the mehtod is propagated down to
    """find and return the class object that will provide 
    the definition of meth_name (as a string) if it is
    invoked on obj.
    """
    for ty in type(obj).mro():
        if meth_name in ty.__dict__:
            return ty
    return None


def play_hand(player, deck): # essentially plays the game for a player, by making moves based on the hand delt
    
    player.show_hand()
    
    if player.name == "Dealer": # Dealer Hand
        while player.get_value() < 17:
            card = player.hit()
            print("%s Hitting!" % player.name)
            print("Received %s" % card)
        player.check_for_bust()
    else: # Player Hand
        if player.balance >= (player.bet * 2):
            # player can either Hit, Stand, or Doubledown 
            move = random.choice(["Hit", "Stand", "Doubledown"]) # subsitiude make_move here later?
        else:
            move = random.choice(["Hit", "Stand"]) # subsitiude make_move here later?
            
        while move is "Hit":
            card = player.hit()
            print("%s Hitting!" % player.name)
            print("Received %s" % card)
            isBust = player.check_for_bust()
            if isBust:
                break
            else:
                # TODO: extract logic to method
                if player.balance >= (player.bet * 2):
                    # player can either Hit, Stand, or Doubledown 
                    move = random.choice(["Hit", "Stand", "Doubledown"]) # subsitiude make_move here later?
                else:
                    move = random.choice(["Hit", "Stand"]) # subsitiude make_move here later?
                
        if move is "Stand":
            player.stand()
            
        if move is "Doubledown":
            player.doubledown() # takes care of the person's financial bookkeeping
            card = player.hit()
            print("%s Hitting!" % player.name)
            print("Received %s" % card)
            player.check_for_bust()
            
            
def results_displayer(player, dealer): 
    # displays the outcomes after player and dealer have both played their hands
    """When a player receives a blackjack, he wins a bonus. Normally, all bets are paid off at even money when playing blackjack, but when you get a blackjack, you receive a three-to-two payoff. If you've bet $10, you'll get paid $15, for example."""
    print("OUTCOME: ")
    if player.isBust:
        print("%s: lose       Balance = %d" % (player.name,player.get_available_balance()))
    elif len(player.cards) == 2 and player.get_value() == 21:
        player.addEarnings(player.bet * 3)
        print("%s: blackjack       Balance = %d" % (player.name,player.get_available_balance()))
    elif dealer.isBust or player.get_value() > dealer.get_value():
        player.addEarnings(player.bet * 2)
        print("%s: win       Balance = %d" % (player.name,player.get_available_balance()))
    elif player.get_value() == dealer.get_value():
         print("%s: draw       Balance = %d" % (player.name,player.get_available_balance()))
    else:
        print("%s: lose       Balance = %d" % (player.name, player.get_available_balance()))


def blackjack(person): # currently only supports one person to play against the house at a time
    """provides functionality for playing a game of blackjack, returns 0 for L or earnings for W """
    min_bet, max_bet = 10, 100
    deck = Deck()
    deck.shuffle()
    
    # Initialize Player and Dealer
    bet = person.place_bet() # updates players available balance after placting bet
    print("%s bets %d" % (person.name, bet))
    player = Player(person, deck) 
    dealer = Dealer("Dealer", deck) # House
    
    # Deal Cards
    deal_cards([dealer, player], deck)
    
    # Play Hand
    for p in [player, dealer]:
        play_hand(p, deck)
        
    # Display Results
    results_displayer(player, dealer)
    
    print("\nCurrent Balance is %s.\n" % person.get_available_balance())


def deal_cards(players, deck): # helper function for a game of blackjack, every player receives two cards from the deck
    for _ in range(2):
        for player in players:
            player.add(deck.pop_card())
    
    
    
#PSA: a deck will pop cards regardless of its size, need to add error handling at some point
# TODO: add error handling so that you dont bet more than you have
if __name__ == '__main__':
    deck = Deck()
    deck.shuffle()
    hand = Hand()
    
    print("\nTESTING FIND_DEFINING_CLASS FOR METHODS: ")
    print("Shuffle is invoked within: %s" % find_defining_class(hand, 'shuffle'))

    print("\nTESTING CARD, HAND, DECK: ")
    deck.move_cards(hand, 2)
    hand.sort()
    print(hand) # print cards in hnad
    print('Total value of hand is %s' % hand.get_value()) # print hand value
    
    print("\nTESTING DEALER, PERSON, PLAYER, BLACKJACK: ")
    charlie_kelly = Person(name="Green Man", cash=1000)
    charlie_kelly.play_session_of_blackjack()
    

    
