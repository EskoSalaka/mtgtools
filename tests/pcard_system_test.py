import json

from tests.system_setup_test import MtgDBSystemSetupTest
import unittest
from contextlib import redirect_stdout
from io import StringIO

from mtgtools.PCardList import PCardList

# A set of test card fixtures which represent a decently diverse set of cards.
# Not completely exhaustive, but enough to test most cases
CARD_GROUPS = {
    "basic_lands": ("forest", "mountain", "island", "swamp", "plains"),
    "non_basic_lands": ("bayou", "Cascading Cataracts", "Evolving Wilds", "Mutavault"),
    "creatures": (
        "wild mongrel",
        "Ogre Taskmaster",
        "Aquamoeba",
        "Midnight Banshee",
        "Trapjaw Tyrant",
        "Merfolk Mistbinder",
        "Storm Fleet Sprinter",
        "Jungle Creeper",
        "Belligerent Hatchling",
        "Crackleburr",
        "Akki Lavarunner // Tok-Tok, Volcano Born",
        "Homura, Human Ascendant // Homura's Essence",
        "Accursed Witch // Infectious Curse",
        "Civilized Scholar // Homicidal Brute",
        "Dryad Arbor",
        "Aegis of the Gods",
    ),
    "non_creature_spells": (
        "Back from the Brink",
        "Blazing Torch",
        "Fall of the Thran",
        "Bonds of Faith",
        "Brimstone Volley",
        "Bump in the Night",
        "Cellar Door",
        "Curse of the Bloody Tome",
        "Full Moon's Rise",
        "Alive // Well",
        "Appeal // Authority",
        "Izzet Signet",
    ),
    "planeswalkers": ("Liliana of the Veil", "Garruk Relentless // Garruk, the Veil-Cursed", "Ajani Vengeant"),
    "tokens": ("Angel", "Clue", "Energy Reserve", "Angel // Demon"),
    "other": ("Ajani Steadfast Emblem", "Ashnod", "Agyrem", "All in Good Time"),
}


def card_copies(cards, names, copies=3):
    result = PCardList()
    for name in names:
        result += copies * cards.where_exactly(name=name)[0:1]
    return result


class TestPCardListSystem(MtgDBSystemSetupTest):
    """System tests for the PCardList with a full database."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        for group, names in CARD_GROUPS.items():
            setattr(cls, group, card_copies(cls.cards, names))
        cls.testlist = (
            cls.other
            + cls.tokens
            + cls.creatures
            + cls.non_basic_lands
            + cls.non_creature_spells
            + cls.basic_lands
            + cls.planeswalkers
        )

    def test_pprint_should_run(self):
        with redirect_stdout(StringIO()):
            for card in self.testlist.unique_cards():
                card.pprint()
                card.pprint(expanded=True)

    def test_rulings_exist(self):
        aquamoeba = self.testlist.where_exactly(name="Aquamoeba")[0]  # Has rulings
        self.assertTrue(len(aquamoeba.rulings) > 0)

    def test_rulings_not_exist(self):
        mongrels = self.testlist.where_exactly(name="Wild Mongrel")[0]  # Has no rulings
        self.assertIsNone(mongrels.rulings)

    def test_rprint_runs_on_card_with_rulings(self):
        aquamoeba = self.testlist.where_exactly(name="Aquamoeba")[0]

        with redirect_stdout(StringIO()):
            aquamoeba.rprint()

    def test_rprint_runs_on_card_with_no_rulings(self):
        mongrels = self.testlist.where_exactly(name="Wild Mongrel")[0]

        with redirect_stdout(StringIO()):
            mongrels.rprint()

    def test_json(self):
        # Spot check the json output of a card
        aquamoeba = self.testlist.where_exactly(name="Aquamoeba")[0]
        self.assertIn('"name": "Aquamoeba"', aquamoeba.json)
        self.assertIn('"mana_cost": "{1}{U}"', aquamoeba.json)
        self.assertIn('"rarity": "common"', aquamoeba.json)

        # It should loads as a valid JSON object
        json.loads(aquamoeba.json)

    def test_jprint_runs(self):
        with redirect_stdout(StringIO()):
            for card in self.testlist.unique_cards():
                card.jprint()

    def test_matches_any(self):
        aquamoeba = self.testlist.where_exactly(name="Aquamoeba")[0]

        self.assertTrue(aquamoeba.matches_any(name="aqua"))
        self.assertTrue(aquamoeba.matches_any(colors=["U"]))
        self.assertTrue(aquamoeba.matches_any(cmc=2))
        self.assertTrue(aquamoeba.matches_any(type_line="elemental"))
        self.assertTrue(aquamoeba.matches_any(oracle_text="switch this creature's power"))
        self.assertTrue(aquamoeba.matches_any(reserved=False))
        self.assertFalse(aquamoeba.matches_any(name="forest", colors=["G"], cmc=1))
        self.assertFalse(aquamoeba.matches_any(reserved=True))

    def test_matches_any_searches_all_faces_when_enabled(self):
        scholar = self.testlist.where_exactly(name="Civilized Scholar // Homicidal Brute")[0]

        self.assertFalse(scholar.matches_any(oracle_text="didn't attack this turn"))
        self.assertTrue(scholar.matches_any(search_all_faces=True, oracle_text="didn't attack this turn"))
        self.assertFalse(scholar.matches_any(colors=["R"]))
        self.assertTrue(scholar.matches_any(search_all_faces=True, colors=["R"]))

    def test_matches_all(self):
        aquamoeba = self.testlist.where_exactly(name="Aquamoeba")[0]

        self.assertTrue(aquamoeba.matches_all(name="AQUAMOEBA", colors=["U"], cmc=2))
        self.assertTrue(
            aquamoeba.matches_all(
                type_line="Creature — Elemental Beast",
                power="1",
                toughness="3",
                rarity="common",
                set="tor",
                booster=True,
            )
        )
        self.assertFalse(aquamoeba.matches_all(name="aqua"))
        self.assertFalse(aquamoeba.matches_all(name="Aquamoeba", colors=["G"]))
        self.assertFalse(aquamoeba.matches_all(power="2"))
        self.assertFalse(aquamoeba.matches_all(booster=False))

    def test_matches_all_searches_all_faces_when_enabled(self):
        scholar = self.testlist.where_exactly(name="Civilized Scholar // Homicidal Brute")[0]

        homicide_oracle_text = (
            "At the beginning of your end step, if this creature didn't attack this turn, tap this creature, "
            "then transform it."
        )
        self.assertFalse(scholar.matches_all(oracle_text=homicide_oracle_text))
        self.assertTrue(scholar.matches_all(search_all_faces=True, oracle_text=homicide_oracle_text))
        self.assertFalse(scholar.matches_all(colors=["R"]))
        self.assertTrue(scholar.matches_all(search_all_faces=True, colors=["R"]))


if __name__ == "__main__":
    unittest.main()
