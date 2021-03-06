import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser  # Python 2.x


class GameSettings(object):  # 2.x requires explicit new-style classes

    """Stores customizable settings for the game.

    All settings defined here are automatically populated into a new .ini
    configuration file on demand.  All updates are automatically synchronized,
    from file to GameSettings object and from object to saved file.

    """

    class Setting(object):  # 2.x requires explicit new-style classes

        """Data descriptor to disguise config values as class attributes."""

        def __init__(self, defaultvalue, minvalue=1, maxvalue=10, typ=int,
                     doc=None):
            if typ is bool: # store as integers
                typ = int
                minvalue = 0
                maxvalue = 1
            self.value = typ(defaultvalue)
            self.min = minvalue
            self.max = maxvalue
            self._typecast = typ
            if doc is not None:
                self.__doc__ = doc

        def __get__(self, instance, type_):
            instance.update()
            return self.value

        def __set__(self, instance, value):
            if self._typecast in (float, int):
                if float(value) < self.min:
                    value = self.min
                if float(value) > self.max:
                    value = self.max
            if self.value == self._typecast(value):
                return
            self.value = self._typecast(value)
            instance.write()        

    NUM_PLAYERS = Setting(2,
            doc="The number of players in the game (including AI)")
    CARDS_ON_BOARD = Setting(4,
            doc="The number of cards each players plays per turn")
    CARDS_IN_HAND = Setting(10, maxvalue=20,
            doc="The number of cards held in a player's Hand")
    NUM_ROUNDS = Setting(20, maxvalue=100,
            doc="The number of rounds in a single game")
    SPEED = Setting(1.0, typ=float, minvalue=0.001,
            doc="Speed multiplier for special effects; lower == faster")
    AI_DIFFICULTY = Setting(2, minvalue=1, maxvalue=3,
            doc="Intelligence of your opponent")
    CURRENT_DECK = Setting("Standard", typ=str,
            doc="The base filename for the deck of cards to play with")
    FULLSCREEN = Setting(False, typ=bool,
            doc="Abstract setting to be implemented by the GUI")
    SHOW_PRIVATE = Setting(False, typ=bool,
            doc="Include decks marked private in the catalog?")
    BACKGROUND = Setting("001RendezVous.png", typ=str,
            doc="Selected background image base filename")

    def __init__(self, filename="rendezvous.ini"):
        self.config = configparser.SafeConfigParser()
        self.filename = filename
        self.section = "DEFAULT"
        self.mtime = 0
        self.update()
        self.write()

    def write(self):
        """Update the saved .ini file."""
        updated = False
        for name in dir(self.__class__):
            if name[:2] == "__": continue
            elif callable(getattr(self, name)): continue
            value = str(getattr(self, name))
            if ((not self.config.has_option(self.section, name)) or
                self.config.get(self.section, name) != value):
                    self.config.set(self.section, name, value)
                    updated = True
        if updated:
            fp = open(self.filename, 'w')
            try:
                self.config.write(fp)
            finally:
                fp.close()

    def update(self):
        """Read the .ini file and update settings if it has changed."""
        try:
            if self.mtime == os.path.getmtime(self.filename):
                return
        except OSError:  # FileNotFoundError in v3.3
            return
        self.config.read(self.filename)
        for (name, value) in self.config.items(self.section):
            setattr(self, name.upper(), value)
        self.mtime = os.path.getmtime(self.filename)


