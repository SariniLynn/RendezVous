import unittest

from rendezvous import SpecialSuit, SpecialValue
from rendezvous.achievements import AchievementList
from rendezvous.deck import *


class TestCard(unittest.TestCase):

    """Test the Card class."""

    def setUp(self):
        """Initialize a simple card for testing."""
        self.c = Card("My Suit", 5)

    def test_attributes(self):
        """Test the __init__ function's attribute settings."""
        self.c = Card("My Suit", 5)
        self.assertEqual(self.c.name, "My Suit 5")
        self.assertEqual(self.c.description, "A normal My Suit card with value 5.")
        self.assertEqual(self.c.suit, "My Suit")
        self.assertEqual(self.c.value, 5)

    def test_string(self):
        """Test the string conversion."""
        self.assertEqual(str(self.c), "My Suit 5")

    def test_repr(self):
        """Test the Python-style string conversion."""
        self.assertEqual(repr(self.c), "Card('My Suit', 5)")

    def test_equality(self):
        """Verify that equality rests on both suit and value."""
        self.assertEqual(self.c, self.c)
        self.assertEqual(self.c, Card("My Suit", 5))
        self.assertNotEqual(self.c, Card("No Suit", 5))
        self.assertNotEqual(self.c, Card("My Suit", 1))

    def test_comparison(self):
        """Verify that < comparison rests on value only."""
        four = Card("My Suit", 4)
        six = Card("My Suit", 6)
        suit = Card("No Suit", 5)
        self.assertTrue(self.c < six)
        self.assertFalse(self.c > six)
        self.assertFalse(self.c < four)
        self.assertTrue(self.c > four)
        self.assertFalse(self.c < suit)
        self.assertFalse(self.c > suit)


class TestSpecialEffects(unittest.TestCase):

    """Test those Effects that are applied to a card."""

    def setUp(self):
        """Create a card for testing."""
        self.card = Card("My Suit", 5)
        self.card.description = "Test."

    def test_buff(self):
        """Test a simple buff."""
        self.card.apply(Effect(EffectType.BUFF, 2))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 7)
        self.assertEqual(self.card.description, "Test.  Buffed to 7.")

    def test_debuff(self):
        """Test a simple debuff."""
        self.card.apply(Effect(EffectType.BUFF, -2))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 3)
        self.assertEqual(self.card.description, "Test.  Debuffed to 3.")

    def test_multiply(self):
        """Test a value multiplication."""
        self.card.apply(Effect(EffectType.MULTIPLY, 1.5))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 8)
        self.assertEqual(self.card.description, "Test.  Increased to 150% (8).")

    def test_double(self):
        """Test a value double."""
        self.card.apply(Effect(EffectType.MULTIPLY, 2))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 10)
        self.assertEqual(self.card.description, "Test.  Doubled.")

    def test_triple(self):
        """Test a value double."""
        self.card.apply(Effect(EffectType.MULTIPLY, 3))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 15)
        self.assertEqual(self.card.description, "Test.  Tripled.")

    def test_divide(self):
        """Test a value division."""
        self.card.apply(Effect(EffectType.MULTIPLY, 0.35))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 1)
        self.assertEqual(self.card.description, "Test.  Reduced to 35% (1).")

    def test_halve(self):
        """Test a value halve."""
        self.card.apply(Effect(EffectType.MULTIPLY, 0.5))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 2)
        self.assertEqual(self.card.description, "Test.  Halved.")

    def test_buff_lose(self):
        """Verify that WIN/LOSE is not affected by buffs."""
        self.card.value = SpecialValue.LOSE
        self.card.apply(Effect(EffectType.BUFF, 2))
        self.assertEqual(self.card.value, SpecialValue.LOSE)

    def test_win(self):
        """Test a WIN."""
        self.card.apply(Effect(EffectType.BUFF, SpecialValue.WIN))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, SpecialValue.WIN)
        self.assertEqual(self.card.description, "Test.  Winning!")

    def test_lose(self):
        """Test a LOSE."""
        self.card.apply(Effect(EffectType.BUFF, SpecialValue.LOSE))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, SpecialValue.LOSE)
        self.assertEqual(self.card.description, "Test.  Losing!")

    def test_kiss(self):
        """Test a KISS."""
        self.card.apply(Effect(EffectType.KISS))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, SpecialValue.KISS)
        self.assertEqual(self.card.description, "Test.  Kissed!")

    def test_reverse(self):
        """Test a REVERSE."""
        self.card.apply(Effect(EffectType.REVERSE))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 6)
        self.assertEqual(self.card.description, "Test.  Reversed to 6.")
        self.card.value = 10
        self.card.apply(Effect(EffectType.REVERSE))
        self.assertEqual(self.card.value, 1)
        self.assertEqual(self.card.description, "Test.  Reversed to 6.  Reversed to 1.")

    def test_reverse_win_lose(self):
        """Test a REVERSE on a WIN/LOSE."""
        self.card.value = SpecialValue.WIN
        self.card.apply(Effect(EffectType.REVERSE))
        self.assertEqual(self.card.value, SpecialValue.LOSE)
        self.assertEqual(self.card.description, "Test.  Reversed.")
        self.card.apply(Effect(EffectType.REVERSE))
        self.assertEqual(self.card.value, SpecialValue.WIN)
        self.assertEqual(self.card.description, "Test.  Reversed.  Reversed.")

    def test_replace(self):
        """Test a REPLACE."""
        self.card.apply(Effect(EffectType.REPLACE, "New Suit"))
        self.assertEqual(self.card.suit, "New Suit")
        self.assertEqual(self.card.value, 5)
        self.assertEqual(self.card.description, "Test.  Replaced suit with New Suit.")

    def test_replace_value(self):
        """Test a REPLACE value."""
        self.card.apply(Effect(EffectType.REPLACE, 8))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 8)
        self.assertEqual(self.card.description, "Test.  Replaced value with 8.")

    def test_replace_both(self):
        """Test a REPLACE both suit and value."""
        self.card.apply(Effect(EffectType.REPLACE, Card("New Suit", 8)))
        self.assertEqual(self.card.suit, "New Suit")
        self.assertEqual(self.card.value, 8)
        self.assertEqual(self.card.description, "Test.  Replaced by New Suit 8.")

    def test_switch(self):
        """Test a SWITCH (post-value-replacement)."""
        self.card.apply(Effect(EffectType.SWITCH, 10))
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 10)
        self.assertEqual(self.card.description, "Test.  Switched to 10.")
        
    def test_clone(self):
        """Test a CLONE."""
        self.card.apply(Effect(EffectType.CLONE, Card("New Suit", 10)))
        self.assertEqual(self.card.suit, "New Suit")
        self.assertEqual(self.card.value, 10)
        self.assertEqual(self.card.description, "Test.  Cloned to New Suit 10.")

    def test_kissed_immunity(self):
        """Verify that KISSED cards do not change."""
        self.card.value = SpecialValue.KISS
        self.card.apply(Effect(EffectType.BUFF, 2))
        self.card.apply(Effect(EffectType.BUFF, -2))
        self.card.apply(Effect(EffectType.BUFF, SpecialValue.WIN))
        self.card.apply(Effect(EffectType.BUFF, SpecialValue.LOSE))
        self.card.apply(Effect(EffectType.REVERSE))
        self.card.apply(Effect(EffectType.REPLACE, "New Suit"))
        self.card.apply(Effect(EffectType.SWITCH, 10))
        self.card.apply(Effect(EffectType.CLONE, Card("New Suit", 10)))
        self.assertEqual(self.card.description, "Test.")

    def test_reset(self):
        """Verify the reset() method to undo SpecialCard Effects."""
        self.card.apply(Effect(EffectType.BUFF, 2))
        self.card.apply(Effect(EffectType.BUFF, -2))
        self.card.apply(Effect(EffectType.BUFF, SpecialValue.WIN))
        self.card.apply(Effect(EffectType.BUFF, SpecialValue.LOSE))
        self.card.apply(Effect(EffectType.REVERSE))
        self.card.apply(Effect(EffectType.REPLACE, "New Suit"))
        self.card.apply(Effect(EffectType.SWITCH, 10))
        self.card.apply(Effect(EffectType.CLONE, Card("New Suit", 10)))
        self.card.apply(Effect(EffectType.KISS))
        self.card.reset()
        self.assertEqual(self.card.suit, "My Suit")
        self.assertEqual(self.card.value, 5)
        self.assertEqual(self.card.name, "My Suit 5")
        self.assertEqual(self.card.description, "A normal My Suit card with value 5.")
        

class TestSpecialCard(unittest.TestCase):

    """Test the SpecialCard class."""

    def setUp(self):
        """Create a simple SpecialCard for testing."""
        self.req = Requirement()
        self.app = Application()
        self.eff = Effect()
        self.sc = SpecialCard("Name", "Desc", self.req, self.app, self.eff)

    def test_init(self):
        """Verify the attributes created on __init__."""
        self.assertEqual(self.sc.name, "Name")
        self.assertEqual(self.sc.description, "Desc\nRequires: Nothing\nApplies to: ALL cards\nEffect: No effect")
        self.assertEqual(self.sc.suit, SpecialSuit.SPECIAL)
        self.assertEqual(self.sc.value, SpecialValue.SPECIAL)
        self.assertIs(self.sc.requirement, self.req)
        self.assertIs(self.sc.application, self.app)
        self.assertIs(self.sc.effect, self.eff)

    def test_apply(self):
        """Verify that special cards do not change."""
        self.sc.apply(Effect(EffectType.BUFF, 2))
        self.sc.apply(Effect(EffectType.BUFF, -2))
        self.sc.apply(Effect(EffectType.BUFF, SpecialValue.WIN))
        self.sc.apply(Effect(EffectType.BUFF, SpecialValue.LOSE))
        self.sc.apply(Effect(EffectType.MULTIPLY, 2))
        self.sc.apply(Effect(EffectType.REVERSE))
        self.sc.apply(Effect(EffectType.REPLACE, "New Suit"))
        self.sc.apply(Effect(EffectType.REPLACE, 15))
        self.sc.apply(Effect(EffectType.SWITCH, 10))
        self.sc.apply(Effect(EffectType.CLONE, Card("New Suit", 10)))
        self.assertEqual(self.sc.description, "Desc\nRequires: Nothing\nApplies to: ALL cards\nEffect: No effect")
        self.assertEqual(self.sc.suit, SpecialSuit.SPECIAL)
        self.assertEqual(self.sc.value, SpecialValue.SPECIAL)
    

class TestDeck(unittest.TestCase):

    """Test the Deck class."""

    def setUp(self):
        """Initialize a simple deck for testing."""
        self.d = Deck(DeckDefinition(), False)
        self.d._cards = [Card("Suit", 2), Card("Suit", 4), Card("Suit", 11)]

    def test_draw(self):
        """Test that cards are drawn properly."""
        self.assertEqual(self.d.draw(False), Card("Suit", 2))
        self.assertEqual(self.d.draw(False), Card("Suit", 4))
        self.assertEqual(self.d.draw(False), Card("Suit", 11))
        self.assertRaises(StopIteration, self.d.draw, False)

    def test_shuffle(self):
        """Test that the cards are shuffled correctly."""
        self.d = Deck(DeckDefinition(), False)
        self.unshuffled = Deck(DeckDefinition(), False)
        self.assertEqual(self.d._cards, self.unshuffled._cards)
        self.d.shuffle()
        self.assertNotEqual(self.d._cards, self.unshuffled._cards)

    def test_initial_shuffle(self):
        """Test that the cards begin shuffled by default."""
        self.d = Deck(DeckDefinition())
        self.assertNotEqual(self.d._cards[:10], [Card("Boyfriend", i+1) for i in range(10)])
        
    def test_auto_shuffle(self):
        """Verify that the draw command auto-shuffles by default."""
        self.assertEqual(self.d.draw(), Card("Suit", 2))
        self.assertEqual(self.d.draw(), Card("Suit", 4))
        self.assertEqual(self.d.draw(), Card("Suit", 11))
        self.assertIn(self.d.draw().suit, ["Boyfriend", "Girlfriend", "Spy", "Counterspy", "Time", SpecialSuit.SPECIAL])


class TestDeckDefinition(unittest.TestCase):

    """Test the definition of a custom playing deck."""

    def setUp(self):
        """Create the standard deck."""
        self.dd = DeckDefinition()

    def test_invalid(self):
        """Test an invalid deck request."""
        self.assertRaises(MissingDeckError, DeckDefinition, "Not A Deck")

    def test_attributes(self):
        """Verify the simple storage."""
        self.assertEqual(self.dd.base_filename, "Standard")
        self.assertEqual(self.dd.name, "Lovers & Spies Deck")
        self.assertEqual(self.dd.desc, "A standard deck featuring Lovers & Spies.")
        self.assertEqual(self.dd.suits, ["Boyfriend", "Girlfriend", "Spy",
                                         "Counterspy", "Time"])
        self.assertEqual(self.dd.values, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(len(self.dd.specials), 17)

    def test_generator(self):
        """Verify the generator yields the full sorted deck."""
        expected = []
        for suit in ['Boyfriend', 'Girlfriend', 'Spy', 'Counterspy', 'Time']:
            for value in range(1, 11):
                expected.append(Card(suit, value))
        self.assertEqual(list(self.dd.cards())[:50], expected)
        self.assertEqual(len(list(self.dd.cards())), 67)

    def test_blocked(self):
        """Verify the generator skips blocked cards."""
        self.dd.blocked_cards = [str(Card('Boyfriend', i+1)) for i in range(4)]
        self.assertEqual(list(self.dd.cards())[0], Card('Boyfriend', 5))
        self.assertEqual(len(list(self.dd.cards())), 63)
        
    def test_unlocks(self):
        """Verify the generator removes locked SpecialCards."""
        a = AchievementList()
        self.assertTrue(len(list(self.dd.cards(a))) < 67)

    def test_parse_requirement(self):
        """Verify requirement parsing from the text file."""
        self.assertEqual(str(self.dd._parse_requirement("min 3")),
                         "At least 3 cards")
        self.assertEqual(str(self.dd._parse_requirement("3")),
                         "Exactly 3 cards")
        self.assertEqual(str(self.dd._parse_requirement("max 3")),
                         "No more than 3 cards")
        self.assertEqual(str(self.dd._parse_requirement("")),
                         "Nothing")
        self.assertEqual(str(self.dd._parse_requirement("any")),
                         "Nothing")
        self.assertEqual(str(self.dd._parse_requirement("none")),
                         "Nothing")
        self.assertEqual(str(self.dd._parse_requirement("na")),
                         "Nothing")
        self.assertEqual(str(self.dd._parse_requirement("n/a")),
                         "Nothing")
        self.assertEqual(str(self.dd._parse_requirement("min 1 <= 5")),
                         "At least 1 card with a value of 5 or less")

    def test_parse_application(self):
        """Verify application parsing from the text file."""
        self.assertEqual(str(self.dd._parse_application("friendly boyfriend")),
                         "Friendly Boyfriend cards")
        self.assertEqual(str(self.dd._parse_application("enemy < 5")),
                         "Enemy cards with a value of 4 or less")
        self.assertEqual(str(self.dd._parse_application("girlfriend >= 6")),
                         "Girlfriend cards with a value of 6 or greater")
        self.assertEqual(str(self.dd._parse_application("= 6")),
                         "cards with a value of 6")
        self.assertEqual(str(self.dd._parse_application("all boyfriend vs > 9")),
                         "Boyfriend cards placed VS cards with a value of 10 or greater")
        self.assertEqual(str(self.dd._parse_application("hand")),
                         "The player's hand")
        self.assertEqual(str(self.dd._parse_application("any")),
                         "ALL cards")
        self.assertEqual(str(self.dd._parse_application("all")),
                         "ALL cards")
        self.assertEqual(str(self.dd._parse_application("friendly all")),
                         "Friendly cards")
        self.assertEqual(str(self.dd._parse_application("friendly boyfriend or girlfriend vs Time")),
                         "Friendly Boyfriend or Girlfriend cards placed VS Time cards")
        self.assertEqual(str(self.dd._parse_application("friendly boyfriend, girlfriend, or SPY >= 5")),
                         "Friendly Boyfriend, Girlfriend, or Spy cards with a value of 5 or greater")
        self.dd.suits = ["Multi Word Suit"]
        self.assertEqual(str(self.dd._parse_application("friendly multi word suit")),
                         "Friendly Multi Word Suit cards")

    def test_parse_effect(self):
        """Verify effect parsing from the text file."""
        self.assertEqual(str(self.dd._parse_effect("buff 3")),
                         "Buff value by 3")
        self.assertEqual(str(self.dd._parse_effect("debuff 3")),
                         "Debuff value by 3")
        self.assertEqual(str(self.dd._parse_effect("double")),
                         "Double value")
        self.assertEqual(str(self.dd._parse_effect("triple")),
                         "Triple value")
        self.assertEqual(str(self.dd._parse_effect("halve")),
                         "Halve value")
        self.assertEqual(str(self.dd._parse_effect("multiply 1.5")),
                         "Increase value by 150%")
        self.assertEqual(str(self.dd._parse_effect("multiply .25")),
                         "Reduce value to 25%")
        self.assertEqual(str(self.dd._parse_effect("divide 3")),
                         "Reduce value to 33%")
        self.assertEqual(str(self.dd._parse_effect("wait")),
                         "Wait through the next turn")
        self.assertEqual(str(self.dd._parse_effect("lose")),
                         "Automatically LOSE")
        self.assertEqual(str(self.dd._parse_effect("win")),
                         "Automatically WIN")
        self.assertEqual(str(self.dd._parse_effect("switch")),
                         "Switch values with opponent")
        self.assertEqual(str(self.dd._parse_effect("reverse")),
                         "Reverse value (e.g. 1 becomes 10)")
        self.assertEqual(str(self.dd._parse_effect("replace Girlfriend")),
                         "Replace suit with Girlfriend")
        self.assertEqual(str(self.dd._parse_effect("replace 1")),
                         "Replace value with 1")
        self.assertEqual(str(self.dd._parse_effect("replace Girlfriend 1")),
                         "Replace card with Girlfriend 1")
        self.assertEqual(str(self.dd._parse_effect("kiss")),
                         "KISS (both sides WIN)")
        self.assertEqual(str(self.dd._parse_effect("clone")),
                         "All matching cards become clones of the first requirement found")
        self.assertEqual(str(self.dd._parse_effect("flush")),
                         "Flush all cards from the player's hand and redraws")
        self.assertEqual(str(self.dd._parse_effect("randomize")),
                         "Randomize each card")
        self.assertEqual(str(self.dd._parse_effect("randomize all")),
                         "Randomize each card")
        self.assertEqual(str(self.dd._parse_effect("randomize suit")),
                         "Randomize the suit of each card")
        self.assertEqual(str(self.dd._parse_effect("randomize value")),
                         "Randomize the value of each card")

    def test_get_special(self):
        card = self.dd.specials[0]
        result = self.dd.get_special(card.name)
        self.assertEqual(card, result)
        self.assertIsNot(card, result)

    def test_get_special_random(self):
        result = self.dd.get_special()
        self.assertIn(result, self.dd.specials)

    def test_get_card(self):
        self.assertEqual(self.dd.get_card('Boyfriend 10'),
                         Card('Boyfriend', 10))
        self.assertIs(self.dd.get_card('No Suit 1'), None)
        self.assertEqual(self.dd.get_card(self.dd.specials[0].name),
                         self.dd.specials[0])

    def test_get_cards(self):
        self.assertEqual(self.dd.get_cards(['Boyfriend 10', 'Knight 10']),
                         [Card('Boyfriend', 10)])

    def test_get_card_texture(self):
        self.assertEqual(self.dd.get_card_texture(Card("Boyfriend", 1)),
                         (0, 2048 - 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(Card("Time", 10)),
                         (4 * 130, 2048 - 1820, 130, 182))
        self.assertEqual(self.dd.get_card_texture(self.dd.specials[0]),
                         (5 * 130, 2048 - 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(self.dd.specials[10]),
                         (5 * 130, 2048 - 11 * 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(self.dd.specials[11]),
                         (6 * 130, 2048 - 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(Card("Boyfriend",
                                                       SpecialValue.KISS)),
                         (7 * 130, 2048 - 2 * 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(Card("Boyfriend",
                                                       SpecialValue.WIN)),
                         (7 * 130, 2048 - 3 * 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(Card("Boyfriend",
                                                       SpecialValue.LOSE)),
                         (8 * 130, 2048 - 2 * 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(Card("Boyfriend", 11)),
                         (7 * 130, 2048 - 4 * 182, 130, 182))
        self.assertEqual(self.dd.get_card_texture(Card("Boyfriend", 0)),
                         (8 * 130, 2048 - 3 * 182, 130, 182))

    def test_get_back_texture(self):
        self.assertEqual(self.dd.get_back_texture(),
                         (7 * 130, 2048 - 182, 130, 182))

    def test_get_suit_texture(self):
        self.assertEqual(self.dd.get_suit_texture(self.dd.suits[0]),
                         (0, 0, 130, 130))
        self.assertEqual(self.dd.get_suit_texture(4),
                         (4 * 130, 0, 130, 130))

    def test_get_dealer_texture(self):
        self.assertEqual(self.dd.get_dealer_texture("Boyfriend", 1),
                         (13 * 130, 2048 - 3 * 182, 260, 364))
        self.assertEqual(self.dd.get_dealer_texture(4, 0),
                         (9 * 130, 2048 - 11 * 182, 260, 364))
        self.assertEqual(self.dd.get_dealer_texture("Spy", -1),
                         (11 * 130, 2048 - 7 * 182, 260, 364))


class TestDeckCatalogEntry(unittest.TestCase):

    def setUp(self):
        self.deck = DeckCatalogEntry("Name", "Desc", "Directory", "Base")

    def test_init(self):
        self.assertEqual(self.deck.name, "Name")
        self.assertEqual(self.deck.description, "Desc")
        self.assertEqual(self.deck.base_filename, "Base")
        self.assertEqual(self.deck.definition,
                         os.path.join("Directory", "Base.txt"))
        self.assertEqual(self.deck.image_file,
                         os.path.join("Directory", "Base.png"))
        self.assertEqual(self.deck.icon,
                         os.path.join("Directory", "BaseIcon.png"))
        self.assertEqual(self.deck.hand,
                         os.path.join("Directory", "BaseHand.png"))

    def test_string(self):
        self.assertEqual(str(self.deck), "Name")

    def test_equal(self):
        self.assertEqual(self.deck, "Name")


class TestDeckCatalog(unittest.TestCase):

    def setUp(self):
        self.catalog = DeckCatalog("test_deck_catalog.txt")

    def tearDown(self):
        os.remove("test_deck_catalog.txt")

    def test_init(self):
        self.assertTrue(len(self.catalog.decks) > 0)
        self.assertEqual(self.catalog._purchased, [])

    def test_container(self):
        self.assertEqual(len(self.catalog), len(self.catalog.decks))
        standard = self.catalog["Standard"]
        self.assertIsInstance(standard, DeckCatalogEntry)
        self.assertEqual(self.catalog["Lovers & Spies Deck"], standard)
        self.assertEqual(self.catalog[standard], standard)

    def test_purchase(self):
        self.assertIs(self.catalog.purchased("Standard"), None)
        standard = self.catalog.purchase("Standard")
        self.assertIsInstance(standard, DeckCatalogEntry)
        self.assertEqual(self.catalog._purchased, ["Lovers & Spies Deck"])

    def test_permanent_purchase(self):
        self.assertEqual(self.catalog._purchased, [])
        self.catalog.purchase("Standard")
        self.catalog = DeckCatalog("test_deck_catalog.txt")
        self.assertEqual(self.catalog._purchased, ["Lovers & Spies Deck"])
        
        
if __name__ == "__main__":
    unittest.main()
