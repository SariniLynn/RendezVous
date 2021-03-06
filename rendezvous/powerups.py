import os
import copy

from rendezvous import PowerupType, FileReader


class Powerup:

    """A 'cheat code' that provides a special advantage."""

    def __init__(self, name, description, price, powerup_type, value=0):
        self.name = name
        self.description = description
        self.price = price
        self.type = powerup_type
        self.value = value

    def __eq__(self, other):
        return self.name == str(other)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(str(self))


"""Maintain a list of the available Powerups."""
class Powerups:

    available = [Powerup("Hand Tipper",
                         "Peek at the dealer's hand before playing.",
                         10, PowerupType.SHOW_DEALER_HAND),
                 Powerup("Psychic Pass",
                         "Peek at the dealer's selected cards!",
                         25, PowerupType.SHOW_DEALER_PLAY),
                 Powerup("Table Spin",
                         "You pick the dealer's cards, and he will pick yours.",
                         25, PowerupType.SWITCH_PLAY),
                 Powerup("Super Buff",
                         "Buff ALL of your cards in a round by 2.",
                         10, PowerupType.GLOBAL_BUFF, 2),
                 Powerup("Mega Buff",
                         "Buff ALL of your cards in a round by 4.",
                         25, PowerupType.GLOBAL_BUFF, 4),
                 Powerup("Ultra Buff",
                         "Buff ALL of your cards in a round by 6.",
                         100, PowerupType.GLOBAL_BUFF, 6),
                 Powerup("Super Debuff",
                         "Debuff ALL of the dealer's cards by 2.",
                         10, PowerupType.GLOBAL_DEBUFF, 2),
                 Powerup("Mega Debuff",
                         "Debuff ALL of the dealer's cards by 4.",
                         25, PowerupType.GLOBAL_DEBUFF, 4),
                 Powerup("Ultra Debuff",
                         "Debuff ALL of the dealer's cards by 6.",
                         100, PowerupType.GLOBAL_DEBUFF, 6),
                 Powerup("Redeal",
                         "Flush your hand and redraw it.",
                         75, PowerupType.FLUSH_HAND),
                 Powerup("Go Fish",
                         "Flush one card from your hand and draw again.",
                         10, PowerupType.FLUSH_CARD),
                 Powerup("Hold That Thought",
                         "Hold one card anywhere on the board.",
                         20, PowerupType.WAIT_CARD),
                 Powerup("Not This Time",
                         "Remove one held card from the board.",
                         10, PowerupType.UNWAIT_CARD),
                 Powerup("Time Machine",
                         "Go back in time and play a round again!",
                         50, PowerupType.REPLAY_TURN),
                 Powerup("Up Your Sleeve",
                         "Hide a card up your sleeve, and play it when you need it.",
                         0, PowerupType.PLAY_CARD)
                 ]

    def __init__(self, player_file=None):
        self.image_file = os.path.join("data", "Powerups.png")
        if player_file is None:
            self._purchased_file = os.path.join("player", "powerups.txt")
        else:
            self._purchased_file = player_file
        self._read_purchased()

    def __iter__(self):
        for powerup in self.available:
            yield copy.deepcopy(powerup)

    def __len__(self):
        return len(self.available)

    def __getitem__(self, key):
        return self.find(key)

    def index(self, powerup):
        return self.available.index(powerup)

    def find(self, name):
        """Return the powerup matching the name given."""
        name = str(name).upper()
        for powerup in self.available:
            if powerup.name.upper() == name:
                return copy.deepcopy(powerup)
        raise ValueError("No such powerup: %s" % name)

    def count(self, powerup):
        """Return the number of this powerup owned."""
        try:
            return self.purchased[powerup]
        except KeyError:
            return 0

    def cards(self):
        """Return list of available cards for PLAY_CARD powerup."""
        try:
            return self.purchased['cards_to_play']
        except KeyError:
            return []

    def get_powerup_texture(self, powerup):
        """Return (L, B, W, H) rectangle for the given Powerup."""
        index = self.available.index(powerup)
        return (128 * int(index / 8), 1024 - 128 * (index % 8 + 1), 128, 128)

    def _read_purchased(self):
        """Read the saved list of purchased powerups."""
        self.purchased = {}
        if not os.path.isfile(self._purchased_file):
            try: os.mkdir(os.path.dirname(self._purchased_file))
            except OSError: pass
            return
        for (tag, value) in FileReader(self._purchased_file):
            if tag == 'CARDS_TO_PLAY':
                self.purchased['cards_to_play'] = value.split(', ')
                continue
            powerup = self.find(tag)
            try:
                self.purchased[powerup] += int(value)
            except KeyError:
                self.purchased[powerup] = int(value)

    def _copy(self, powerup):
        """Return a copy of the powerup (or find by name), with value intact."""
        new_powerup = self.find(powerup)
        try:
            new_powerup.value = powerup.value
        except AttributeError: pass  # found by name
        return new_powerup

    def purchase(self, powerup, count=1):
        """Purchase another copy of the given powerup."""
        powerup = self._copy(powerup)
        try:
            self.purchased[powerup] += count
        except KeyError:
            self.purchased[powerup] = count
        if powerup.type == PowerupType.PLAY_CARD:
            try:
                self.purchased['cards_to_play'].extend([str(powerup.value)] * count)
            except KeyError:
                self.purchased['cards_to_play'] = [str(powerup.value)] * count
        self._write()

    def use(self, powerup):
        """Mark one copy of the given powerup used."""
        powerup = self._copy(powerup)
        self.purchased[powerup] -= 1
        if self.purchased[powerup] == 0:
            del self.purchased[powerup]
        if powerup.type == PowerupType.PLAY_CARD:
            self.purchased['cards_to_play'].remove(str(powerup.value))
            if not self.purchased['cards_to_play']:
                del self.purchased['cards_to_play']
        self._write()

    def _write(self):
        """Output the list of purchased powerups."""
        f = open(self._purchased_file, 'w')
        for powerup, count in self.purchased.items():
            if powerup != 'cards_to_play':
                f.write('[%s]%s\n' % (powerup.name, count))
        if 'cards_to_play' in self.purchased:
            f.write('[%s]%s\n' % ('cards_to_play',
                                  ', '.join(self.purchased['cards_to_play'])))
        f.close()
            
        
