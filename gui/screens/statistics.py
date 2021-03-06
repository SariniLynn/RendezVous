from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.actionbar import ActionBar


class BaseStatsDisplay(BoxLayout):

    title = StringProperty()
    basestats = ObjectProperty(allownone=True)


class StatisticsDisplay(BoxLayout):

    deck = ObjectProperty()
    statistics = ObjectProperty(allownone=True)

    def best_suit(self, *binds):
        """Return the suit with the most wins for the current deck."""
        if self.deck is None or self.statistics is None: return ""
        best = ("", 0)
        for suit in self.deck.suits:
            if suit not in self.statistics.suits:
                continue
            if self.statistics.suits[suit].wins > best[1]:
                best = (suit, self.statistics.suits[suit].wins)
        return best[0]

    def worst_suit(self, *binds):
        """Return the suit with the most losses for the current deck."""
        if self.deck is None or self.statistics is None: return ""
        best = ("", 0)
        for suit in self.deck.suits:
            if suit not in self.statistics.suits:
                continue
            if self.statistics.suits[suit].losses > best[1]:
                best = (suit, self.statistics.suits[suit].losses)
        return best[0]


class StatisticsScreen(Screen):
    
    """Displays the player's latest statistics."""

    statistics = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(ActionBar(size_hint=(1, .125)))
        self.main = StatisticsDisplay(statistics=self.statistics,
                                      deck=App.get_running_app().loaded_deck)
        layout.add_widget(self.main)
        self.add_widget(layout)
