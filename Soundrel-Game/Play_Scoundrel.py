from Scoundrel_Deck import create_scoundrel_deck, Suit, Card
from Scoundrel_Exceptions import ResolveRoomError, InRoomError, NotInRoomError, CanNotSkipRoomError, GameOverError
import random as rand
import json

STARTING_LIFE = 20
BASE_DURABILITY = 15 # Weapon durability refers to the largest monster slain with a weapon.
                     # Base durability is 15 implying that any monster can still be slain with this weapon.
BASE_NUM_MONSTERS = 26

class Scoundrel:
    """
    This object is a game of Scoundrel. Its attributes represent the game state and the methods enter_room,
    skip_room, resolve_room, and end_game are used to take game actions
    """

    def __init__(self, verbose:bool=False, life:int=STARTING_LIFE, num_monsters:int=BASE_NUM_MONSTERS,
                 game_over:bool=False, weapon:Card=None, weapon_durability:int=0, can_skip:bool=True,
                 turn_resolved:bool=True, deck:list[Card]=None, discard_pile:list[Card]=None, room:list[Card]=None):
        
        self.verbose = verbose
        # If set to true then the methods enter_room, skip_room, resolve_room, and end_game describe the game state yielded
        # after they are called. False by default. Useful for debugging.

        self.life = life # player's remaining life points
        self.num_monsters = num_monsters # number of monsters remaining in dungeon
        self.game_over = game_over # true if the game has ended
        self.weapon = weapon # equipped weapon
        self.weapon_durability = weapon_durability # value of last minster slain with weapon. 15 if no weapon equipped or weapon
                                                   # has not been used yet
        self.can_skip = can_skip # True if you can skip this room. False if you skipped the previous room.
        self.can_heal_this_turn = True # True at the beginning of each turn. Used during resolution to denote whether you have
                                       # previously healed
        self.turn_resolved = turn_resolved # True if the next game action must be enter_room. False if the next game action
                                           # must be either resolve_room or skip_room.

        if deck == None:
            self.deck = create_scoundrel_deck()
        else:
            self.deck = deck
        # the list of Card objects in the deck
        
        if discard_pile == None:
            self.discard_pile = list()
        else:
            self.discard_pile = discard_pile
        # the list of Card objects in the discard pile

        if room == None:
            self.room = list()
        else:
            self.room = room
        # the list of Card objects in the current room

    def end_game(self):
        """
        Called by _change_life and _resolve_monster to end the game if the player's life total drops below 0 or if the last
        monster is slain. Can be called if the player would like to give up.
        """
        if self.num_monsters == 0:
            totla_val_of_health_potions_remaining = 0

            for card in self.room:
                if card:
                    if card.suit == Suit.Heart:
                        totla_val_of_health_potions_remaining += card.value
            for card in self.deck:
                if card.suit == Suit.Heart:
                    totla_val_of_health_potions_remaining += card.value
            
            self.score = self.life + totla_val_of_health_potions_remaining
        else:
            total_val_of_monsters_remaining = 0

            for card in self.room:
                if card:
                    if card.suit == Suit.Club or card.suit == Suit.Spade:
                        total_val_of_monsters_remaining += card.value
            for card in self.deck:
                if card.suit == Suit.Club or card.suit == Suit.Spade:
                    total_val_of_monsters_remaining += card.value
            
            self.score = self.life - total_val_of_monsters_remaining
        
        self.game_over = True

        if self.verbose:
            print(f"Game Over. {"You Win!!!" if self.num_monsters == 0 else "You Lose..."} Final score: {self.score}")
    
    def _change_life(self, delta:int):
        """
        Called by _resolve_monster and _resolve_health_potion to change the players life. Used instead of assignment operators to
        facilitate the game's maximum life value (the starting life), and to end the game if the player's life total drops below 0.
        """
        new_life = min(STARTING_LIFE, self.life + delta)
        self.life = new_life
        if new_life <= 0:
            self.end_game()

    def enter_room(self):
        """
        Call only if turn_resolved is True and game_over is False. Fills the room with our cards or the rest of the deck,
        whichever is fewer.
        """
        if self.game_over:
            raise GameOverError(f"Game Over. {"You Win!!!" if self.num_monsters == 0 else "You Lose..."} Final score: {self.score}")
        if not self.turn_resolved:
            raise InRoomError("The current room must be reolved first")
        while len(self.room) < 4 and len(self.deck) > 0:
            self.room.append(self.deck.pop(0))

        self.turn_resolved = False

        if self.verbose:
            pass
    
    def skip_room(self) -> None:
        """
        Call only if turn_resolved is False. Called to skip the current room by shuffling the cards in the room to the bottom of
        the deck. Set can_skip to False.
        """
        if self.turn_resolved:
            raise NotInRoomError("Turn already resolved, enter a new room first")
        if not self.can_skip:
            raise CanNotSkipRoomError("Can not skip 2 rooms in a row.")
        else:
            rand.shuffle(self.room)
            self.deck.extend(self.room)
            self.room = []
            self.can_skip = False
            self.turn_resolved = True

        if self.verbose:
            pass

    def resolve_room(self, card_order:list[int], slay_by_hand:tuple[bool]=(False, False, False)) -> None:
        """
        Call only if turn_resolved is False. Face 3 cards in the room (fewer if the last room contains 1 or 2 cards). Set
        can_skip to True.

            card_order:iterable[int]
                The 0th item is the index of the card in the room you want to face first. The 1st item is the index of the card in
                the room you want to face second, and the 2nd item is the index of the card you want to face third.

            slay_by_hand:iterable[bool]
                (False, False, False) by default. If the player choses to face a monster and can slay it with their weapon they
                may still choose to slay it by hand (i.e. the player has the 10 of Diamonds as their weapon with durability 15 and
                the room contains the Ace of Spades, King of Spades, 2 of Spades, and 2 of Clubs. The player may slay the Ace and
                king with their weapon but then slay a 2 by hand to maintian their weapon's durability).

                This argument is used to denote such decisions. If the ith index of slay_by_hand is true and the ith index of
                card_order is a monster card that couldbe slain with the currently equipped weapon, then that monster will be
                slain by hand instead.
        """
        if self.turn_resolved:
            raise NotInRoomError("Turn already resolved, enter a new room first")
        
        Scoundrel._validate_args_for_resolve_room(card_order, slay_by_hand, len(self.room))
        
        self.can_heal_this_turn = True
        
        len_of_iterables = 3
        room_size = len(self.room)
        if room_size < 4:
            len_of_iterables = room_size
        
        for resoltion_placing in range(len_of_iterables):
            card_room_placing = card_order[resoltion_placing]
            card = self.room[card_room_placing]
            self._resolve_card(card, slay_by_hand[resoltion_placing])
            
            self.room[card_order[resoltion_placing]] = None

            if self.num_monsters == 0:
                self.end_game(card)
                break

        if not self.game_over:
            new_room = list()
            for card in self.room:
                if card is not None:
                    new_room.append(card)
            
            if len(new_room) == 1:
                self.room = new_room.copy()
                self.turn_resolved = True
                self.can_skip = True
            else:
                raise Exception("room not cleared properly")

            

        if self.verbose:
            pass

    def _resolve_card(self, card:Card, slay_by_hand:int) -> None:
        """
        This method is called by resolve room for each card the player chooses to resolve.
        This method checks the suit of the card then calls the method used to resolve cards of that suit.
        """
        card_suit = card.suit

        match card_suit:
            case Suit.Club:
                self._resolve_monster(card, slay_by_hand)
            case Suit.Diamond:
                self._resolve_weapon(card)
            case Suit.Heart:
                self._resolve_health_potion(card)
            case Suit.Spade:
                self._resolve_monster(card, slay_by_hand)
    
    def _resolve_monster(self, card:Card, slay_by_hand:bool) -> None:
        """
        This method is called by the _resolve_card method when the card it is resolving has the suit Club or Spade.
        If no weapon is equipped, the weapon's durability is less than or equal tothe card's value, or slay_by_hand is
        True then the player's life is decreased by this card's value. Otherwise the player's life is decreased by this
        card's value minus their weapon's value, their weapon's durability is set to this card's value. This card is then 
        moved to the discard pile.
        """
        monster_val = card.value
        weapon_dur = self.weapon_durability
        if self.weapon:
            weapon_val = self.weapon.value
            weapon_equipped = True
        else:
            weapon_val = 0
            weapon_equipped = False

        if slay_by_hand or not Scoundrel._can_slay_with_weapon(weapon_equipped, weapon_dur, monster_val):
            # the monster is to be slain by hand, by choice or by necessity
            life_loss = monster_val
        else:
            self.weapon_durability = monster_val
            life_loss = max(monster_val - weapon_val, 0)
        
        self._change_life(-life_loss)
        self.num_monsters -= 1
        self.discard_pile.append(card)

        if self.verbose:
            pass

    def _resolve_weapon(self, card:Card) -> None:
        """
        This method is called by the _resolve_card method when the card it is resolving has the suit Diamond.
        The player equips this card to their weapon slot, and discards their previous weapon (if one was equipped.)
        """
        if self.weapon:
            self.discard_pile.append(self.weapon)
        self.weapon = card
        self.weapon_durability = BASE_DURABILITY

        if self.verbose:
            pass

    def _resolve_health_potion(self, card:Card) -> None:
        """
        This method is called by the _resolve_card method when the card it is resolving has the suit Heart.
        The player to heals an amount of life equal to the value of the card if it is their first health potion
        this turn. This card is then moved to the discard pile.
        """
        heal_val = card.value

        if self.can_heal_this_turn:
            self._change_life(heal_val)

        self.discard_pile.append(card)
        self.can_heal_this_turn = False

        if self.verbose:
            pass

    @staticmethod
    def _can_slay_with_weapon(Weapon_equipped:bool, weapon_duarability:int, monster_val:int) -> bool:
        """
        This static method is used to deterimine if the player can slay the monster they are facing with their weapon.

            weapon_equipped:bool
                True if the player is equipped with a weapon. Otherwise False.

            weapon_durability:int
                the durability of the palyer's currently equipped weapon.

            monster_val:int
                the value of the monster the player is facing.

            returns:bool
                True if the player can slay the monster they're facing with their weapon. Otherwise False.
        """

        if Weapon_equipped:
            return weapon_duarability > monster_val
        
        return False
    
    @staticmethod
    def _validate_args_for_resolve_room(card_order, slay_by_hand, room_size:int) -> None:
        """
        This static method is called by the resolve_room method to validate its arguments
        """
        
        if not hasattr(card_order, '__iter__'):
            raise TypeError("card_order must be an iterable.")
        if not hasattr(slay_by_hand, '__iter__'):
            raise TypeError("slay_by_hand must be an iterable.")
        
        len_of_iterables = 3
        if room_size < 4:
            len_of_iterables = room_size
        
        if len(card_order) < len_of_iterables:
            raise ResolveRoomError(f"card_order must contain at least {len_of_iterables} items")
        if len(card_order) < len_of_iterables:
            raise ResolveRoomError(f"card_order must contain at least {len_of_iterables} items")
        
        room_indicies_to_resolve = set()
        for i in range(len_of_iterables):
            if card_order[i] not in range(0,4):
                raise ResolveRoomError("each item in card_order must be an integer from 0 to 3 (inclusive)")
            room_indicies_to_resolve.add(card_order[i])
        if len(room_indicies_to_resolve) != len_of_iterables:
            raise ResolveRoomError("the items in card_order must be unique")
        
        for i in range(len_of_iterables):
            if not isinstance(slay_by_hand[i], bool):
                raise TypeError("the items in slay_by_hand must all be bool values")
        
