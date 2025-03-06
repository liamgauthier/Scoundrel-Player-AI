from Scoundrel_Deck import create_scoundrel_deck, Suit, Card
import random as rand

STARTING_LIFE = 20
BASE_DURABILITY = 15 # Weapon durability refers to the largest monster slain with a weapon.
                     # Base durability is 15 implying that any monster can still be slain with this weapon.
BASE_SCORE = -134 # The current score at the beginning of the game. Equal to 20 + sum of all health potion values
                  # - sum of all monster values
BASE_NUM_MONSTERS = 26

class Scoundrel:

    def __init__(self):
        self.life = STARTING_LIFE
        self.deck = create_scoundrel_deck()
        self.weapon = None
        self.weapon_durability = 0
        self.discard_pile = []
        self.can_skip = True
        self.can_heal_this_turn = True
        self.turn_resolved = True
        self.room = []
        self.score = BASE_SCORE
        self.num_monsters = BASE_NUM_MONSTERS
        self.game_over = False

    def lose(self):
        self.game_over = True

    def win(self):
        self.game_over = True
    
    def change_life(self, delta:int):
        new_life = min(STARTING_LIFE, self.life + delta)
        self.life = new_life
        if new_life <= 0:
            self.lose()

    def enter_room(self):
        if self.game_over:
            raise Exception("Game Over")
        if not self.turn_resolved:
            raise Exception("The current room must be reolved first")
        while len(self.room) < 4 or len(self.deck) > 0:
            self.room.append(self.deck.pop(0))

        self.turn_resolved = False

        return self.room
    
    def skip_room(self):
        if self.turn_resolved:
            raise Exception("Turn already resolved, enter a new room first")
        if not self.can_skip:
            raise Exception("Can not skip 2 rooms in a row.")
        else:
            rand.shuffle(self.room)
            self.deck.extend(self.room)
            self.room = []
            self.can_skip = False
            self.turn_resolved = True

    def resolve_room(self, card_order, slay_by_hand=(False, False, False)):
        if self.turn_resolved:
            raise Exception("Turn already resolved, enter a new room first")
        
        Scoundrel.verify_card_order(card_order, slay_by_hand, len(self.room))
        
        self.can_heal_this_turn = True
        
        for resoltion_placing in range(4):
            card_room_placing = card_order[resoltion_placing]
            card = self.room[card_room_placing]
            self.resolve_card(card, slay_by_hand[resoltion_placing])
            
            self.room[resoltion_placing] = None

        new_room = list()
        for card in self.room:
            if card is not None:
                new_room.append(card)
        
        if len(new_room) == 0 or self.num_monsters == 0:
            self.win()
        elif len(new_room) == 1:
            self.room = new_room.copy()
        else:
            raise Exception("room not cleared properly")

        self.turn_resolved = True
        self.can_skip = True

    def resolve_card(self, card:Card, slay_by_hand:int):
        
        card_suit = card.suit

        match card_suit:
            case Suit.Club:
                self.resolve_monster(card, slay_by_hand)
            case Suit.Diamond:
                self.resolve_weapon(card)
            case Suit.Heart:
                self.resolve_health_potion(card)
            case Suit.Spade:
                self.resolve_monster(card, slay_by_hand)
    
    def resolve_monster(self, card:Card, slay_by_hand:bool):
        monster_val = card.value
        weapon_dur = self.weapon_durability

        if slay_by_hand or monster_val >= weapon_dur:
            life_loss = monster_val
        else:
            weapon_dur = monster_val
            life_loss = max(monster_val - self.weapon.value, 0)
        self.change_life(-life_loss)
        self.num_monsters -= 1
        self.score += monster_val - life_loss
        self.discard_pile.append(card)

    def resolve_weapon(self, card:Card):
        if self.weapon:
            self.discard_pile.append(self.weapon)
        self.weapon = card
        self.weapon_durability = BASE_DURABILITY

    def resolve_health_potion(self, card:Card):
        heal_val = card.value

        if not self.can_heal_this_turn:
            self.score -= heal_val
        elif (life_to_gain := STARTING_LIFE - self.life) < heal_val:
            loss_to_score = heal_val - life_to_gain
            self.score -= loss_to_score
        
        if self.can_heal_this_turn:
            self.change_life(heal_val)

        self.discard_pile.append(card)
        self.can_heal_this_turn = False

    @staticmethod
    def verify_card_order(card_order, slay_by_hand, room_size:int):
        
        if hasattr(card_order, '__iter__'):
            raise Exception("card_order must be an iterable.")
        if hasattr(slay_by_hand, '__iter__'):
            raise Exception("slay_by_hand must be an iterable.")
        
        len_of_iterables = 3
        if room_size < 4:
            len_of_iterables = room_size
        
        if len(card_order) < len_of_iterables:
            raise Exception("card_order must contain at least 3 items")
        if len(card_order) < len_of_iterables:
            raise Exception("card_order must contain at least 3 items")
        
        room_indicies_to_resolve = set()
        for i in range(len_of_iterables):
            if card_order[i] not in range(0,4):
                raise Exception("each item in card_order must be an integer from 0 to 3 (inclusive)")
            room_indicies_to_resolve.add(card_order[i])
        if len(room_indicies_to_resolve) != len_of_iterables:
            raise Exception("the items in card_order must be unique")
        
        for i in range(len_of_iterables):
            if not isinstance(slay_by_hand[i], bool):
                raise Exception("the items in slay_by_hand must all be bool values")
        
