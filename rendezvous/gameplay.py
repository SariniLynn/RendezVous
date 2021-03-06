import random

from rendezvous import GameSettings, SpecialSuit, SpecialValue, EffectType
from rendezvous import Alignment, TargetField
from rendezvous.deck import Deck, DeckDefinition
from rendezvous.dealer import ArtificialIntelligence

class Hand:

    """Holds cards for a player's hand.

    Attributes:
      cards -- the current hand of Cards
      deck  -- the player's deck from which to draw

    Methods:
      refill  -- bring the hand back up to its full count
      flush   -- empty the hand and refill it from the deck
      AI_play -- intelligently choose cards to play

    """

    def __init__(self, deck):
        self.deck = deck
        self.flush()

    # Treat as container (shortcut to .cards)
    
    def __len__(self):
        return GameSettings.CARDS_IN_HAND

    def __getitem__(self, key):
        return self.cards[key]

    def __iter__(self):
        return iter(self.cards)

    def index(self, card):
        return self.cards.index(card)

    def pop(self, index=-1):
        return self.cards.pop(index)

    def remove(self, card):
        self.cards.remove(card)

    def extend(self, cards):
        self.cards.extend(cards)

    def sort(self, *args, **kwargs):
        self.cards.sort(*args, **kwargs)

    # Additional methods
    
    def refill(self):
        """Fill up to maximum capacity from the deck."""
        while len(self.cards) < GameSettings.CARDS_IN_HAND:
            self.cards.append(self.deck.draw())

    def AI_easy(self, player_index, gameboard, score):
        """Select cards to play (by brute force)."""
        needed = gameboard[player_index].count(None)
        play = self.cards[:needed]
        while gameboard.validate(play):  # invalid specials found
            self.cards = self.cards[needed:]
            self.refill()
            play = self.cards[:needed]
        return play

    def AI_hard(self, player_index, gameboard, score):
        """Intelligently select cards to play."""
        while True:
            ai = ArtificialIntelligence(player_index, self, gameboard, score)
            try:
                return ai.get_best_play()
            except IndexError:  # no valid plays
                self.cant_play(player_index, score)

    def cant_play(self, player_index, score):
        """Take the points cut for not being able to play."""
        for i in range(len(score[player_index])):
            score[player_index][i] -= 10
        self.flush()

    def flush(self):
        """Empty hand and refill from deck."""
        self.cards = []
        self.refill()


class Gameboard:

    """Manages the cards in play.

    Attributes:
      board -- 2D list of Cards [player][index]
      wait  -- 2D list of booleans marking Cards held to the next round

    Methods:
      play_cards -- play one or more cards onto the Gameboard
      wait       -- mark a card to hold for the next round
      next_round -- clear all cards not marked to hold
      clear_wait -- reset the holds for the next round
      clear      -- clear all cards, ignoring holds
      is_full    -- return whether the player's side is full already

    """

    def __init__(self):
        self.clear_wait()
        self._clear_board()

    def __len__(self):
        return GameSettings.NUM_PLAYERS

    def __getitem__(self, key):
        return self.board[key]

    def __iter__(self):
        return iter(self.board[0] + self.board[1])

    def is_full(self, player):
        """Return boolean indicating whether player's side is full."""
        return None not in self.board[player]

    def play_cards(self, player, cards):
        """Place the player's card(s) onto the board where available."""
        indices = []
        for card in cards:
            try:
                first_available = self.board[player].index(None)
            except ValueError:
                break
            self.board[player][first_available] = card
            indices.append(first_available)
        return indices

    def wait(self, player_index, card_index):
        """Hold the given card through the next round."""
        self._wait[player_index][card_index] = True

    def clear_wait(self):
        """Clear all holds."""
        self._wait = [[False for i in range(GameSettings.CARDS_ON_BOARD)]
                      for i in range(GameSettings.NUM_PLAYERS)]

    def _clear_board(self):
        """Clear all cards from the board."""
        new_board = [[None for i in range(GameSettings.CARDS_ON_BOARD)]
                     for i in range(GameSettings.NUM_PLAYERS)]
        for (p, side) in enumerate(self._wait):
            for (c, hold) in enumerate(side):
                try:
                    self.board[p][c].reset()
                except: pass  # on first clear, or if None
                if hold:
                    new_board[p][c] = self.board[p][c]
        self.board = new_board

    def next_round(self):
        """Advance to the next round."""
        self._clear_board()

    def clear(self):
        """Reset the board for a new game."""
        self.clear_wait()
        self._clear_board()

    def validate(self, cards):
        """Confirm cards may be played together; return invalid indices list."""
        invalid = []
        for i, card in enumerate(cards):
            if card.suit == SpecialSuit.SPECIAL:
                if not card.requirement.verify(cards):
                    invalid.append(i)
        return invalid


class Scoreboard:

    """Tracks the score for the game.

    Attributes:
      suits  -- the names of the current deck's suits
      scores -- the current scores by [player][suit]

    Methods:
      score -- update based on the cards in play
      zero  -- reset all scores to zero
      total -- returns the total score for a specific player

    """

    def __init__(self, deck):
        self.suits = deck.suits
        self.zero()

    def __len__(self):
        return GameSettings.NUM_PLAYERS

    def __getitem__(self, key):
        return self.scores[key]

    def __iter__(self):
        return iter(zip(*self.scores))

    def zero(self):
        """Zero the score for all players and suits."""
        self.scores = [[0 for suit in self.suits]
                       for p in range(GameSettings.NUM_PLAYERS)]

    def total(self, player):
        """Return player's total score."""
        return sum(self.scores[player])

    def wins(self, player):
        """Return the suits this player has won."""
        return [suit for i, suit in enumerate(self.suits)
                if self[player][i] > self[player-1][i]]

    def winner(self, suit):
        """Return the winner(s) of the given suit."""
        if suit in self.suits:
            suit = self.suits.index(suit)
        suit_scores = list(zip(*self.scores))[suit]
        high_score = max(suit_scores)
        return [i for i, score in enumerate(suit_scores) if score == high_score]

    def by_suit(self, suit):
        """Return a tuple of the scores in the given suit."""
        if suit in self.suits:
            suit = self.suits.index(suit)
        return list(zip(*self.scores))[suit]

    def best_suit(self, player):
        """Return the suit where the player has the biggest lead."""
        deltas = list(map(lambda x: x[player] - x[player-1], zip(*self.scores)))
        best_lead = max(deltas)
        return self.suits[deltas.index(best_lead)]

    def score(self, board):
        """Score the board, adjusting each player's totals."""
        for i in range(GameSettings.CARDS_ON_BOARD):
            for p in range(GameSettings.NUM_PLAYERS):
                self._score_match(p, board[p][i], p-1, board[p-1][i])
                # wraps around when -1 is last player

    def _score_match(self, player, player_card, enemy, enemy_card):

        """Adjust player's score (only) based on the card matchup.

        Return 1 for a win, -1 for a loss, 0 for a draw.

        """

        if SpecialValue.SPECIAL in (player_card.value, enemy_card.value):
            return 0
        
        elif (player_card.value in (SpecialValue.KISS, SpecialValue.WIN) or
                enemy_card.value in (SpecialValue.KISS, SpecialValue.LOSE)):
            self._win(player, player_card.suit)
            self._win(player, enemy_card.suit)
            return 1

        elif (player_card.value == SpecialValue.LOSE or
                enemy_card.value == SpecialValue.WIN):
            self._lose(player, player_card.suit)
            return -1
            
        elif player_card.value > enemy_card.value:
            self._win(player, player_card.suit)
            self._win(player, enemy_card.suit)
            return 1

        elif player_card.value < enemy_card.value:
            self._lose(player, player_card.suit)
            return -1

        return 0

    def _win(self, player, suit, value=10):
        """Record a win for player in suit for value points (default: 10)."""
        if suit != SpecialSuit.SPECIAL:
            self.scores[player][self.suits.index(suit)] += value

    def _lose(self, player, suit):
        """Record a loss for player in suit of 10 points."""
        self._win(player, suit, -10)



class RendezVousGame:

    """A single game of RendezVous.

    Attributes:
      players     -- the Hands participating in the game
      board       -- the Gameboard accepting play
      score       -- the Scoreboard keeping track

    Methods:
      new_game       -- begin a new game
      score_round    -- apply specials and score the current round of play
      next_round     -- advance to the next round of play
      validate       -- confirm that the play is acceptable

    """

    def __init__(self, deck=DeckDefinition(), achievements=None):
        """Create the elements of the game."""
        self.deck = deck
        self.achievements = achievements
        self.players = [Hand(Deck(self.deck, achievements=achievements))
                        for i in range(GameSettings.NUM_PLAYERS)]
        self.board = Gameboard()
        self.score = Scoreboard(self.deck)

    def load_deck(self, deck):
        """Switch to a new deck."""
        self.deck = deck
        self.score.suits = deck.suits
        for hand in self.players:
            hand.deck = Deck(deck, achievements=self.achievements)
            hand.flush()
        
    def new_game(self):
        """Begin a new game."""
        for hand in self.players:
            hand.deck.shuffle()
            hand.flush()
        self.board.clear()
        self.score.zero()
        self.round = 1

    def score_round(self):
        """Score the current round, applying all specials."""
        self.board.clear_wait()
        self._apply_specials()
        self.score.score(self.board)

    def next_round(self):
        """Clear the board; refill the hands; return True if game over."""
        for hand in self.players:
            hand.refill()
        self.board.next_round()
        self.round += 1
        return self.round > GameSettings.NUM_ROUNDS

    def validate(self, player):
        """Return list of invalid board indices (if any)."""
        return self.board.validate(self.board[player])
    
    def _apply_specials(self):
        """Apply all special cards in play, left-to-right, top-to-bottom."""
        for i in range(GameSettings.CARDS_ON_BOARD):
            for p in range(GameSettings.NUM_PLAYERS):
                if self.board[p][i].suit == SpecialSuit.SPECIAL:
                    self._apply(p, i)

    def _apply(self, player_index, board_index):
        """Apply the special card at the given location across the board."""
        special = self.board[player_index][board_index]
        special.applied_to = [0 for p in range(GameSettings.NUM_PLAYERS)]

        # Flush applies to the hand, not to individual cards      
        if special.effect.effect == EffectType.FLUSH:
            self.players[player_index].flush()
            return

        # Some cards need to pre-determine a value
        if special.effect.effect == EffectType.CLONE:
            special.effect.value = special.requirement.filter(
                        Alignment.FRIENDLY, self.board[player_index])[0]

        # Switches have to be careful not to undo themselves
        if special.effect.effect == EffectType.SWITCH:
            for c in range(GameSettings.CARDS_ON_BOARD):
                for p in range(GameSettings.NUM_PLAYERS):
                    if special.application.match(p == player_index,
                                                 self.board[p][c],
                                                 self.board[p-1][c]):
                        special.applied_to[p] += 1
                        self._apply_to_card(special.effect, p, c)
                        # check the newly switched card
                        if special.application.match(p != player_index,
                                                     self.board[p][c],
                                                     self.board[p-1][c]):
                            special.applied_to[p-1] += 1
                            self._apply_to_card(special.effect, p, c)
                        break  # skip any other checks in this match
            return

        # Apply to some or all of the cards in play
        for p in range(GameSettings.NUM_PLAYERS):
            for c in range(GameSettings.CARDS_ON_BOARD):
                if special.application.match(p == player_index,
                                             self.board[p][c],
                                             self.board[p-1][c]):
                    special.applied_to[p] += 1
                    self._apply_to_card(special.effect, p, c)

    def _apply_to_card(self, effect, player, index):

        # Most effects are handled by the card itself
        if effect.effect in (EffectType.BUFF, EffectType.KISS,
                             EffectType.REVERSE, EffectType.REPLACE,
                             EffectType.CLONE, EffectType.MULTIPLY):
            self.board[player][index].apply(effect)

        # Switch values with the opposing card on the board
        elif effect.effect == EffectType.SWITCH:
            hold_value = self.board[player][index].value
            effect.value = self.board[player-1][index].value
            if (hold_value == SpecialValue.SPECIAL or
                effect.value == SpecialValue.SPECIAL):
                return
            self.board[player][index].apply(effect)
            effect.value = hold_value
            self.board[player-1][index].apply(effect)

        # Mark the card held for the next round
        elif effect.effect == EffectType.WAIT:
            self.board.wait(player, index)

        # Randomize a new suit, value, or card
        elif effect.effect == EffectType.RANDOMIZE:
            if effect.value == TargetField.SUIT:
                self.board[player][index].suit = random.choice(self.score.suits)
            elif effect.value == TargetField.VALUE:
                self.board[player][index].value = random.randint(1, 10)
            else:  #effect.value == TargetField.ALL:
                if random.randint(1, 6) == 0:
                    self.board[player][index] = self.deck.get_special()
                    return
                self.board[player][index].suit = random.choice(self.score.suits)
                self.board[player][index].value = random.randint(1, 10)
            
        else:
            raise InvalidSpecialEffectError()
    

