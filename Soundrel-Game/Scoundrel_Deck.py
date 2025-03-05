from enum import Enum
import random as rand

class Suit(Enum):
    Club = 1
    Diamond = 2
    Heart = 3
    Spade = 4

class Card:
    """
    Card objects. Takes a suit and value from 2 to 14 inclusive where 11 is Jack, 12 is Queen, 13 is King, and 14 is Ace
    as arguments.

    suit:Suit
        The card's suit, an object from the Suit enum.

    value:int
        An integer denoting the cards value. Must be a value from 2 to 14.
    """
    def __init__(self, suit:Suit, value:int):
        Card.validate(suit, value)
        self.suit = suit
        self.value = value

    def __string__(self):
        match self.suit:
            case Suit.Club:
                suit_str = " of Clubs"
            case Suit.Diamond:
                suit_str = " of Diamonds"
            case Suit.Heart:
                suit_str = " of Hearts"
            case Suit.Spade:
                suit_str = " of Spades"
            case _:
                raise Exception("Unknown Suit")
        return str(self.value) + suit_str

    @staticmethod
    def validate(suit, value):
        if not isinstance(suit, Suit):
            raise Exception("The suit provided must be a member of the class Suit")
        if value not in range(2, 15):
            raise Exception("The value provided must be an integer between 2 and 14 (inclusive)")
        
def create_scoundrel_deck():
    """
    Creates a deck of cards that can be used to play Scoundrel (See the rules to see how this differes
    from a regular deck of cards). Returns a shuffled list of Card objects.
    """

    deck = list()

    for suit in [Suit.Diamond, Suit.Heart]:
        for val in range(2, 11):
            card = Card(suit, val)
            deck.append(card)

    for suit in [Suit.Club, Suit.Spade]:
        for val in range(2, 15):
            card = Card(suit, val)
            deck.append(card)

    rand.shuffle(deck)
    return deck
