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

    def __init__(self, numDecks=1):
        self.numDecks = numDecks
        self.cards = []
        self.count = 0
        for deck in range(numDecks):
            for suit in range(4):
                for rank in range(1, 14):
                    card = Card(suit, rank)
                    self.cards.append(card)
        self.shuffle()

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def __len__(self):
        return len(self.cards)

    def add_card(self, card):
        """add a card to the deck"""
        self.cards.append(card)

    def pop_card(self, i=-1):
        """remove and return a card from the deck.
        By default, pop the last card."""
        card = self.cards.pop(i)
        self.count += self.count_card(card)
        
        if self.empty():
            self.reset()

        return card

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

    def count_card(self, card):
        card_value = card.get_value()

        if card_value >= 10 or card.rank is "Ace":
            return -1
        elif card_value < 10 and card_value > 6:
            return 0
        elif card_value <= 6:
            return 1

    def true_count(self):
        return self.count / self.remaining_decks()

    def remaining_decks(self):
        decks = int(round(len(self)/52))
        if decks is 0:
            return 1
        return decks

    def penetration(self):
        return (self.numDecks*52 - len(self.cards)) / (self.numDecks*52)

    def empty(self):
        return len(self.cards)==0
    
    def reset(self):
        
        self.cards.clear()
        self.count = 0
        
        for deck in range(self.numDecks):
            for suit in range(4):
                for rank in range(1, 14):
                    card = Card(suit, rank)
                    self.cards.append(card)
        self.shuffle()
        

class Hand(Deck):
    """represents a hand of playing cards"""

    def __init__(self, label=''):
        self.label = label
        self.cards = []

    def __str__(self):
        for card in self.cards:
            print(card)
        return "Value of hand: " + str(self.get_value())

    def __len__(self):
        return len(self.cards)

    """returns the value for the given Hand"""

    def get_value(self):
        hand_value = 0
        aces = self.get_num_aces()
        for card in self.cards:
            hand_value += card.value
        while (
            hand_value > 21) and aces:  # corner case to adjust value of hand given the number of aces and current value of the player's hand
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

    def bust(self):
        return self.get_value() > 21

    def blackjack(self):
        if len(self) == 2:
            if self.get_num_aces() == 1:
                for card in self.cards:
                    if card.get_value() == 10:
                        return True
        return False
    
    def clear(self):
        self.cards.clear()





