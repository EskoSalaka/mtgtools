from contextlib import redirect_stdout
from io import StringIO

from tests.system_setup_test import MtgDBSystemSetupTest
import warnings
import unittest

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

    def test_has_all(self):
        self.assertTrue(self.testlist.has_all(self.creatures))
        self.assertTrue(self.testlist.has_any(self.creatures))
        self.assertTrue(self.testlist.has_all(self.planeswalkers))
        self.assertTrue(self.testlist.has_any(self.planeswalkers))
        self.assertTrue(self.testlist.has_all(self.other))
        self.assertTrue(self.testlist.has_any(self.other))
        self.assertTrue(self.testlist.has_all(self.non_creature_spells))
        self.assertTrue(self.testlist.has_any(self.non_creature_spells))
        self.assertTrue(self.testlist.has_all(self.non_basic_lands))
        self.assertTrue(self.testlist.has_any(self.non_basic_lands))
        self.assertTrue(self.testlist.has_all(self.basic_lands))
        self.assertTrue(self.testlist.has_any(self.basic_lands))

        self.assertTrue(self.testlist.has_all(self.creatures + self.creatures[0]))
        self.assertTrue(self.testlist.has_any(self.creatures + self.creatures[0]))
        self.assertTrue(self.testlist.has_all(self.planeswalkers + self.creatures[0]))
        self.assertTrue(self.testlist.has_any(self.planeswalkers + self.creatures[0]))
        self.assertTrue(self.testlist.has_all(self.other + self.creatures[0]))
        self.assertTrue(self.testlist.has_any(self.other + self.creatures[0]))
        self.assertTrue(self.testlist.has_all(self.non_creature_spells + self.creatures[0]))
        self.assertTrue(self.testlist.has_any(self.non_creature_spells + self.creatures[0]))
        self.assertTrue(self.testlist.has_all(self.non_basic_lands + self.creatures[0]))
        self.assertTrue(self.testlist.has_any(self.non_basic_lands + self.creatures[0]))
        self.assertTrue(self.testlist.has_all(self.basic_lands + self.creatures[0]))
        self.assertTrue(self.testlist.has_any(self.basic_lands + self.creatures[0]))

    def test_inclusion(self):
        self.assertFalse(self.cards.where_exactly(name="forest")[1] in self.basic_lands)
        self.assertFalse(self.cards.where_exactly(name="bayou")[1] in self.non_basic_lands)
        self.assertFalse(self.cards.where_exactly(name="island")[0] in self.non_basic_lands)

        self.assertTrue(self.cards.where_exactly(name="forest")[0] in self.basic_lands)
        self.assertTrue(self.cards.where_exactly(name="bayou")[0] in self.non_basic_lands)
        self.assertTrue(self.cards.where_exactly(name="Dryad Arbor")[0] in self.creatures)

    def test_len(self):
        self.assertEqual(len(self.testlist), 144)
        self.assertEqual(len(self.basic_lands), 15)
        self.assertEqual(len(self.non_basic_lands), 12)
        self.assertEqual(len(self.creatures), 48)
        self.assertEqual(len(self.non_creature_spells), 36)
        self.assertEqual(len(self.planeswalkers), 9)
        self.assertEqual(len(self.tokens), 12)
        self.assertEqual(len(self.other), 12)

        self.assertEqual(len(self.testlist.basic_lands()), 15)
        self.assertEqual(len(self.testlist.creatures()), 54)
        self.assertEqual(len(self.testlist.lands()), 30)
        self.assertEqual(len(self.testlist.noncreatures()), 90)
        self.assertEqual(len(self.testlist.unique_cards()), 48)
        self.assertEqual(len(self.testlist.unique_names()), 48)
        self.assertEqual(len(self.testlist.normal_playable_cards()), 120)

        self.assertEqual(len(self.testlist - self.testlist.lands()), 114)
        self.assertEqual(len(self.testlist - self.testlist.creatures()), 90)
        self.assertEqual(len(self.testlist + self.testlist.lands()), 174)
        self.assertEqual(len(self.testlist + self.testlist.creatures()), 198)

        self.assertEqual(len(self.testlist), self.testlist.len)

    def test_add_mul(self):
        # Basic add, mul and len tests of the fixtures
        self.assertEqual(len(self.tokens + self.other), 24)
        self.assertEqual(len(self.planeswalkers + self.other), 21)
        self.assertEqual(len(self.basic_lands + self.non_basic_lands), 27)

        self.assertEqual(len(self.testlist * 2), 288)
        self.assertEqual(len(2 * self.testlist), 288)
        self.assertEqual(len(5 * self.testlist[0:1]), 5)
        self.assertTrue(self.testlist[0] in 3 * self.testlist[0:1])

        list1 = PCardList(self.creatures[0:3])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1.append(self.creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2.append(self.creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

        list1 = PCardList([self.creatures[0], self.creatures[1], self.creatures[2]])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1.append(self.creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2.append(self.creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

        list1 = PCardList(self.creatures[0:3])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += self.creatures[7]

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2 += self.creatures[7]

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

        list1 = PCardList(self.creatures[0:3])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += list2

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 3)

        list2 += list1

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 9)

        list1 = self.creatures[0:3]
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += list2

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 3)

        list2 += list1

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 9)

        list1 = [self.creatures[0], self.creatures[1], self.creatures[2]]
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)
        self.assertEqual(len(list2 + list1), 6)
        self.assertEqual(len(list1 + list2), 6)
        self.assertEqual(len(list2 + list1[0]), 4)
        self.assertEqual(len(list1[0] + list2), 4)

        list2 += list1

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 6)

        list2 += list1[0]

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 7)

        list1 = PCardList() + self.creatures[0] + self.creatures[1] + self.creatures[2]
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1.append(self.creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2.append(self.creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

    def test_sub(self):
        self.assertEqual(len(self.testlist - self.testlist.lands()), 114)
        self.assertEqual(len(self.testlist - self.testlist.creatures()), 90)

        test_cardlist = PCardList()
        mongrels = 4 * self.cards.where_exactly(name="Wild Mongrel")[0:1]
        aquamoebas = 3 * self.cards.where_exactly(name="Aquamoeba")[0:1]
        forests = self.cards.where_exactly(name="Forest")[0:1]

        test_cardlist += mongrels
        test_cardlist += aquamoebas
        test_cardlist += forests

        self.assertEqual(len(test_cardlist), 8)

        no_mongrels = test_cardlist - mongrels
        self.assertEqual(len(no_mongrels), 4)
        self.assertTrue(mongrels[0] not in no_mongrels)

        less_aquamoebas = test_cardlist - aquamoebas[0]
        self.assertEqual(len(less_aquamoebas), 7)
        self.assertTrue(less_aquamoebas.count(aquamoebas[0]) == 2)

    def test_sub_removes_requested_occurrences_only(self):
        aquamoeba = self.creatures.where_exactly(name="Aquamoeba")[0]
        test_cardlist = PCardList([aquamoeba, self.creatures[1], aquamoeba, aquamoeba])

        self.assertEqual(list(test_cardlist - aquamoeba), [self.creatures[1], aquamoeba, aquamoeba])
        self.assertEqual(list(test_cardlist - [aquamoeba, aquamoeba]), [self.creatures[1], aquamoeba])
        self.assertEqual(list(test_cardlist - 5 * PCardList([aquamoeba])), [self.creatures[1]])

    def test_filter_and_sort(self):
        self.assertEqual(len(self.testlist), len(self.testlist.sorted(lambda card: card.name)))
        self.assertEqual(len(self.testlist), len(self.testlist.sorted(lambda card: card.cmc)))
        self.assertEqual(len(self.testlist), len(self.testlist.sorted(lambda card: card.type_line)))
        self.assertEqual(len(self.testlist), len(self.testlist.sorted(lambda card: card.color_identity)))

        self.assertEqual(
            self.creatures.where_exactly(name="Dryad Arbor")[0], self.creatures.sorted(lambda card: card.cmc)[0]
        )
        self.assertEqual(
            self.creatures.where_exactly(name="Homura, Human Ascendant // Homura's Essence")[0],
            self.creatures.sorted(lambda card: card.cmc)[-1],
        )

        self.assertEqual(
            len(self.creatures) + 6, len(self.testlist.filtered(lambda card: "Creature" in card.type_line))
        )
        self.assertTrue(self.testlist.filtered(lambda card: "Creature" in card.type_line).has_all(self.creatures))

    def test_index(self):
        mongrel = self.cards.where_exactly(name="Wild Mongrel")[0]
        aquamoeba = self.cards.where_exactly(name="Aquamoeba")[0]
        forest = self.cards.where_exactly(name="Forest")[0]
        torch = self.cards.where_exactly(name="Blazing Torch")[0]

        test_cards = 4 * PCardList([mongrel])  # Indexes 0, 1, 2, 3
        test_cards += 3 * PCardList([aquamoeba])  # Indexes 4, 5, 6
        test_cards += 2 * PCardList([forest])  # Indexes 7, 8
        test_cards += PCardList([torch])  # Index 9

        self.assertEqual(test_cards.index(mongrel), 0)
        self.assertEqual(test_cards.index(aquamoeba), 4)
        self.assertEqual(test_cards.index(forest), 7)
        self.assertEqual(test_cards.index(torch), 9)

        self.assertEqual(self.cards.index(self.cards[0]), 0)
        self.assertEqual(self.cards.index(self.cards[1]), 1)
        self.assertEqual(self.cards.index(self.cards[2]), 2)
        self.assertEqual(self.cards.index(self.cards[3]), 3)
        self.assertEqual(self.cards.index(self.cards[4]), 4)
        self.assertEqual(self.cards.index(self.cards[5]), 5)
        self.assertEqual(self.cards.index(self.cards[6]), 6)

    def test_groups(self):
        tgst = self.testlist.grouped_by_simple_type()
        tgstcards = tgst["creatures"] + tgst["noncreatures"] + tgst["lands"]

        self.assertEqual(len(tgstcards), len(self.testlist))
        self.assertTrue(tgstcards.has_all(self.testlist))
        self.assertTrue(tgst["creatures"].has_all(self.creatures))
        self.assertTrue(tgst["noncreatures"].has_all(self.non_creature_spells + self.planeswalkers + self.other))
        self.assertTrue(tgst["lands"].has_all(self.basic_lands + self.non_basic_lands))

        self.assertFalse(tgst["creatures"].has_any(self.non_creature_spells))
        self.assertFalse(tgst["creatures"].has_any(self.non_basic_lands))

        tgcmc = self.testlist.grouped_by_converted_mana_cost()
        tgcmccards = PCardList(list(card for sublist in tgcmc.values() for card in sublist))

        self.assertEqual(len(tgcmccards), len(self.testlist))
        self.assertTrue(tgcmccards.has_all(self.testlist))
        self.assertTrue(self.testlist.where_exactly(name="Ajani Steadfast Emblem")[0] in tgcmc[0])
        self.assertTrue(self.testlist.where_exactly(name="Ashnod")[0] in tgcmc[0])
        self.assertTrue(self.testlist.where_exactly(name="Clue")[0] in tgcmc[0])
        self.assertTrue(self.testlist.where_exactly(name="Blazing Torch")[0] in tgcmc[1])
        self.assertTrue(self.testlist.where_exactly(name="Wild Mongrel")[0] in tgcmc[2])
        self.assertTrue(self.testlist.where_exactly(name="Appeal // Authority")[0] in tgcmc[3])
        self.assertTrue(self.testlist.where_exactly(name="Ajani Vengeant")[0] in tgcmc[4])
        self.assertTrue(self.testlist.where_exactly(name="Trapjaw Tyrant")[0] in tgcmc[5])

        tgci = self.testlist.grouped_by_color_identity()
        tgciards = PCardList(list(card for sublist in tgci.values() for card in sublist))

        self.assertEqual(len(tgciards), len(self.testlist))
        self.assertTrue(tgciards.has_all(self.testlist))
        self.assertTrue(self.testlist.where_exactly(name="Ajani Steadfast Emblem")[0] in tgci[""])
        self.assertTrue(self.testlist.where_exactly(name="Ashnod")[0] in tgci[""])
        self.assertTrue(self.testlist.where_exactly(name="Clue")[0] in tgci[""])
        self.assertTrue(self.testlist.where_exactly(name="Blazing Torch")[0] in tgci[""])
        self.assertTrue(self.testlist.where_exactly(name="Wild Mongrel")[0] in tgci["G"])
        self.assertTrue(self.testlist.where_exactly(name="Appeal // Authority")[0] in tgci["GW"])
        self.assertTrue(self.testlist.where_exactly(name="Ajani Vengeant")[0] in tgci["RW"])
        self.assertTrue(self.testlist.where_exactly(name="Angel")[0] in tgci["W"])
        self.assertTrue(self.testlist.where_exactly(name="Dryad Arbor")[0] in tgci["G"])
        self.assertTrue(self.testlist.where_exactly(name="Forest")[0] in tgci["G"])
        self.assertTrue(self.cards.where_exactly(name="Izzet Signet")[0] in tgci["RU"])

        tgc = self.testlist.grouped_by_color()
        tgcards = PCardList(list(card for sublist in tgc.values() for card in sublist))
        self.assertEqual(len(tgcards), len(self.testlist))
        self.assertTrue(tgcards.has_all(self.testlist))
        self.assertTrue(self.testlist.where_exactly(name="Ajani Steadfast Emblem")[0] in tgc[""])
        self.assertTrue(self.testlist.where_exactly(name="Ashnod")[0] in tgc[""])
        self.assertTrue(self.testlist.where_exactly(name="Clue")[0] in tgc[""])
        self.assertTrue(self.testlist.where_exactly(name="Blazing Torch")[0] in tgc[""])
        self.assertTrue(self.testlist.where_exactly(name="Wild Mongrel")[0] in tgc["G"])
        self.assertTrue(self.testlist.where_exactly(name="Appeal // Authority")[0] in tgc["GW"])
        self.assertTrue(self.testlist.where_exactly(name="Ajani Vengeant")[0] in tgc["RW"])
        self.assertTrue(self.testlist.where_exactly(name="Angel")[0] in tgc["W"])
        self.assertTrue(self.testlist.where_exactly(name="Dryad Arbor")[0] in tgc["G"])
        self.assertTrue(self.testlist.where_exactly(name="Forest")[0] in tgc[""])
        self.assertTrue(self.testlist.where_exactly(name="Izzet Signet")[0] in tgc[""])

    @unittest.skip("Skipping test with heavy load.")
    def test_groups_global(self):
        self.cards.grouped_by_color()
        self.cards.grouped_by_color_identity()
        self.cards.grouped_by_converted_mana_cost()
        self.cards.grouped_by_simple_type()
        self.cards.mana_symbol_counts()

    def test_stats(self):
        self.assertEqual(self.creatures.converted_mana_cost(), 159)
        self.assertEqual(self.basic_lands.converted_mana_cost(), 0)
        self.assertEqual(self.non_basic_lands.converted_mana_cost(), 0)
        self.assertEqual(self.tokens.converted_mana_cost(), 0)
        self.assertEqual(self.other.converted_mana_cost(), 0)
        self.assertEqual(self.testlist.where_exactly(name="Izzet Signet")[0:1].converted_mana_cost(), 2)

        self.assertEqual(self.creatures.average_mana_cost(), 159 / 48)
        self.assertEqual(self.basic_lands.average_mana_cost(), 0)
        self.assertEqual(self.non_basic_lands.average_mana_cost(), 0)
        self.assertEqual(self.tokens.average_mana_cost(), 0)
        self.assertEqual(self.other.average_mana_cost(), 0)
        self.assertEqual(self.testlist.where_exactly(name="Izzet Signet")[0:2].average_mana_cost(), 2)

        self.assertEqual(self.creatures.mana_symbol_counts()["G"], 9)
        self.assertEqual(self.creatures.mana_symbol_counts()["W"], 12)
        self.assertEqual(self.non_creature_spells.mana_symbol_counts()["W"], 12)

        lands = self.non_basic_lands + self.basic_lands
        self.assertEqual(lands.mana_symbol_counts()["G"], 0)
        self.assertEqual(lands.mana_symbol_counts()["U"], 0)
        self.assertEqual(lands.mana_symbol_counts()["W"], 0)
        self.assertEqual(lands.mana_symbol_counts()["B"], 0)
        self.assertEqual(lands.mana_symbol_counts()["R"], 0)

        self.assertEqual(self.cards.where_exactly(name="Liliana of the Veil")[0:2].mana_symbol_counts()["B"], 4)
        self.assertEqual(self.cards.where_exactly(name="Liliana of the Veil")[0:2].mana_symbol_counts()["U"], 0)
        self.assertEqual(self.cards.where_exactly(name="Liliana of the Veil")[0:2].mana_symbol_counts()["W"], 0)
        self.assertEqual(self.cards.where_exactly(name="Liliana of the Veil")[0:2].mana_symbol_counts()["R"], 0)
        self.assertEqual(self.cards.where_exactly(name="Liliana of the Veil")[0:2].mana_symbol_counts()["G"], 0)

        self.assertEqual(self.creatures.where_exactly(name="Belligerent Hatchling")[0:2].mana_symbol_counts()["W"], 2)
        self.assertEqual(self.creatures.where_exactly(name="Belligerent Hatchling")[0:2].mana_symbol_counts()["R"], 2)
        self.assertEqual(
            self.creatures.where_exactly(name="Civilized Scholar // Homicidal Brute")[0:2].mana_symbol_counts()["U"], 2
        )
        self.assertEqual(self.non_creature_spells.where_exactly(name="Alive // Well")[0:2].mana_symbol_counts()["G"], 2)
        self.assertEqual(self.non_creature_spells.where_exactly(name="Alive // Well")[0:2].mana_symbol_counts()["W"], 2)

    def test_random(self):
        for _ in range(50):
            self.assertTrue(self.testlist.random_card() in self.testlist)

        for _ in range(50):
            self.assertTrue(self.testlist.has_all(self.testlist.random_sample(20, duplicates=True)))

        for _ in range(50):
            self.assertTrue(self.testlist.has_all(self.testlist.random_sample(20, duplicates=False)))

        for _ in range(50):
            self.assertTrue(self.testlist.has_all(self.testlist.random_pack()))

        init = self.testlist.random_pack()
        mythnum = 0
        rarenum = 0
        for _ in range(100):
            random_pack = self.testlist.random_pack()
            rares = [card for card in random_pack if card.rarity == "rare"]
            uncs = [card for card in random_pack if card.rarity == "uncommon"]
            coms = [card for card in random_pack if card.rarity == "common"]
            myths = [card for card in random_pack if "mythic" in card.rarity]

            mythnum += len(myths)
            rarenum += len(rares)

            self.assertEqual(len(rares + myths), 1)
            self.assertEqual(len(uncs), 3)
            self.assertEqual(len(coms), 11)
            self.assertFalse(init.has_all(random_pack))

        self.assertTrue(mythnum > 0)
        self.assertTrue(rarenum > 0)

    def test_where(self):
        self.assertEqual(len(self.testlist.where(type_line="creature")), 54)
        self.assertEqual(len(self.testlist.where(type_line="arti")), 12)
        self.assertEqual(len(self.testlist.where(type_line="enchant")), 24)
        self.assertEqual(len(self.testlist.where(colors="R")), 24)

        self.assertEqual(len(self.testlist.where(type_line="enchant").where(colors="R")), 3)
        self.assertEqual(len(self.testlist.where(type_line="enchant").where(colors=["R"])), 3)

        self.assertEqual(len(self.creatures.where_exactly(colors="R")), 9)
        self.assertEqual(len(self.creatures.where_exactly(colors=["R"])), 9)
        self.assertEqual(len(self.non_creature_spells.where_exactly(type_line="enchantment").where(colors=["G"])), 3)
        self.assertEqual(len(self.non_creature_spells.where_exactly(type_line="enchantment").where(colors="G")), 3)

        self.assertEqual(len(self.creatures.where(colors="G")), 12)
        self.assertEqual(len(self.creatures.where_exactly(colors="G")), 6)
        self.assertEqual(len(self.creatures.where(colors=["G", "B"])), 18)

        self.assertEqual(len(self.creatures.where_exactly(power="2", toughness="2")), 12)
        self.assertEqual(len(self.creatures.where_exactly(power="0")), 3)
        self.assertEqual(len(self.creatures.where_exactly(search_all_faces=True, power="5", toughness="1")), 3)
        self.assertEqual(len(self.creatures.where_exactly(power="0", toughness="1")), 3)
        self.assertEqual(
            len(self.creatures.where(search_all_faces=True, power="5").where(search_all_faces=True, toughness="1")), 3
        )

    def test_where_arg_warnings(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.testlist.where(colorrrrs="R")
            self.testlist.where(colors=None)
            self.testlist.where(colorrrrs=None)
            PCardList().where(colors=None)

            self.assertEqual(len(w), 4)

    def test_unique_cards(self):
        testcards = 4 * self.testlist.where_exactly(name="Wild Mongrel")[0:1]
        testcards += 3 * self.testlist.where_exactly(name="Aquamoeba")[0:1]
        testcards += 2 * self.testlist.where_exactly(name="Forest")[0:1]

        self.assertEqual(len(testcards), 9)

        unique = testcards.unique_cards()
        self.assertEqual(len(unique), 3)

        self.assertTrue(testcards.where_exactly(name="Wild Mongrel")[0] in unique)
        self.assertTrue(testcards.where_exactly(name="Aquamoeba")[0] in unique)
        self.assertTrue(testcards.where_exactly(name="Forest")[0] in unique)

    def test_pprint_runs(self):
        with redirect_stdout(StringIO()):
            self.testlist.unique_cards().pprint()

    def test_json(self):
        # Should have the attribute cards in the json output of the testlist
        self.assertIn('"cards": [', self.testlist.json)

        self.assertTrue(self.testlist.json.count("{") == self.testlist.json.count("}"))
        self.assertTrue(self.testlist.json.count("[") == self.testlist.json.count("]"))

        # Some spot tests for the JSON output of the testlist
        self.assertIn('"name": "Ajani Steadfast Emblem"', self.testlist.json)
        self.assertIn('"name": "Appeal // Authority"', self.testlist.json)
        self.assertIn('"name": "Belligerent Hatchling"', self.testlist.json)

    def test_jprint_runs(self):
        with redirect_stdout(StringIO()):
            self.testlist.unique_cards().jprint()

    def test_unique_names(self):
        testcards = 4 * self.testlist.where_exactly(name="Wild Mongrel")[0:1]
        testcards += 3 * self.testlist.where_exactly(name="Aquamoeba")[0:1]
        testcards += 2 * self.testlist.where_exactly(name="Forest")[0:1]

        self.assertEqual(len(testcards), 9)

        unique = testcards.unique_names()
        self.assertEqual(len(unique), 3)

        self.assertTrue(testcards.where_exactly(name="Wild Mongrel")[0] in unique)
        self.assertTrue(testcards.where_exactly(name="Aquamoeba")[0] in unique)
        self.assertTrue(testcards.where_exactly(name="Forest")[0] in unique)

    def test_count(self):
        testcards = 4 * self.testlist.where_exactly(name="Wild Mongrel")[0:1]
        testcards += 3 * self.testlist.where_exactly(name="Aquamoeba")[0:1]
        testcards += 2 * self.testlist.where_exactly(name="Forest")[0:1]

        self.assertEqual(len(testcards), 9)

        self.assertEqual(testcards.count(self.cards.where_exactly(name="Wild Mongrel")[0]), 4)
        self.assertEqual(testcards.count(self.cards.where_exactly(name="Aquamoeba")[0]), 3)
        self.assertEqual(testcards.count(self.cards.where_exactly(name="Forest")[0]), 2)

    def test_from_str_global(self):
        test_cards = self.cards.from_str("""
        3 Raging Ravine
        1 Wooded Foothills
        4 Verdant Catacombs
        1 Stomping Ground
        2 Overgrown Tomb
        1 Blood Crypt
        4 Blackcleave Cliffs
        2 Swamp
        1 Forest
        4 Bloodstained Mire

        2 Huntmaster of the Fells
        4 Dark Confidant
        2 Scavenging Ooze
        4 Tarmogoyf
        1 Fulminator Mage

        1 Chandra, Torch of Defiance
        4 Liliana of the Veil

        1 Kolaghan's Command
        4 Lightning Bolt
        3 Terminate
        3 Thoughtseize
        2 Abrupt Decay
        3 Inquisition of Kozilek

        1 Fatal Push

        1 Blooming Marsh
        1 Kalitas, Traitor of Ghet

        //Sideboard
        SB: 3 Fulminator Mage
        SB: 2 Collective Brutality
        SB: 1 Anger of the Gods
        SB: 1 Kolaghan's Command
        SB: 2 Ancient Grudge
        SB: 1 Maelstrom Pulse
        SB: 1 Liliana, the Last Hope
        SB: 2 Surgical Extraction
        SB: 1 Rakdos Charm
        SB: 1 Damnation""")

        self.assertEqual(test_cards.len, 60)
        self.assertEqual(len(test_cards.sideboard), 15)
        self.assertEqual(test_cards.where(name="Raging Ravine").len, 3)
        self.assertEqual(test_cards.where(name="Wooded Foothills").len, 1)
        self.assertEqual(test_cards.where(name="Verdant Catacombs").len, 4)

    def test_deck_str_group_by_type(self):
        test_cards = self.cards.from_str("""
        3 Raging Ravine
        1 Wooded Foothills
        4 Verdant Catacombs
        1 Stomping Ground
        2 Overgrown Tomb
        1 Blood Crypt
        4 Blackcleave Cliffs
        2 Swamp
        1 Forest
        4 Bloodstained Mire

        2 Huntmaster of the Fells
        4 Dark Confidant
        2 Scavenging Ooze
        4 Tarmogoyf
        1 Fulminator Mage

        1 Chandra, Torch of Defiance
        4 Liliana of the Veil

        1 Kolaghan's Command
        4 Lightning Bolt
        3 Terminate
        3 Thoughtseize
        2 Abrupt Decay
        3 Inquisition of Kozilek

        1 Fatal Push

        1 Blooming Marsh
        1 Kalitas, Traitor of Ghet

        //Sideboard
        SB: 3 Fulminator Mage
        SB: 2 Collective Brutality
        SB: 1 Anger of the Gods
        SB: 1 Kolaghan's Command
        SB: 2 Ancient Grudge
        SB: 1 Maelstrom Pulse
        SB: 1 Liliana, the Last Hope
        SB: 2 Surgical Extraction
        SB: 1 Rakdos Charm
        SB: 1 Damnation""")

        dstring = test_cards.deck_str(group_by="type")

        self.assertEqual(dstring.count("// Creatures (14)"), 1)
        self.assertEqual(dstring.count("// Planeswalkers (5)"), 1)
        self.assertEqual(dstring.count("// Sorceries (6)"), 1)
        self.assertEqual(dstring.count("// Instants (11)"), 1)
        self.assertEqual(dstring.count("// Lands (24)"), 1)
        self.assertEqual(dstring.count("// Sideboard (15)"), 1)

        self.assertEqual(dstring.count("SB:"), 10)

        self.assertEqual(dstring.count("3 Raging Ravine"), 1)
        self.assertEqual(dstring.count("1 Wooded Foothills"), 1)
        self.assertEqual(dstring.count("4 Verdant Catacombs"), 1)

        self.assertEqual(dstring.count("SB: 1 Liliana, the Last Hope"), 1)
        self.assertEqual(dstring.count("SB: 2 Ancient Grudge"), 1)

    def test_deck_str_group_by_color(self):
        test_cards = self.cards.from_str("""
        3 Raging Ravine
        1 Wooded Foothills
        4 Verdant Catacombs
        1 Stomping Ground
        2 Overgrown Tomb
        1 Blood Crypt
        4 Blackcleave Cliffs
        2 Swamp
        1 Forest
        4 Bloodstained Mire

        2 Huntmaster of the Fells
        4 Dark Confidant
        2 Scavenging Ooze
        4 Tarmogoyf
        1 Fulminator Mage

        1 Chandra, Torch of Defiance
        4 Liliana of the Veil

        1 Kolaghan's Command
        4 Lightning Bolt
        3 Terminate
        3 Thoughtseize
        2 Abrupt Decay
        3 Inquisition of Kozilek

        1 Fatal Push

        1 Blooming Marsh
        1 Kalitas, Traitor of Ghet

        //Sideboard
        SB: 3 Fulminator Mage
        SB: 2 Collective Brutality
        SB: 1 Anger of the Gods
        SB: 1 Kolaghan's Command
        SB: 2 Ancient Grudge
        SB: 1 Maelstrom Pulse
        SB: 1 Liliana, the Last Hope
        SB: 2 Surgical Extraction
        SB: 1 Rakdos Charm
        SB: 1 Damnation""")

        dstring = test_cards.deck_str(group_by="color")

        self.assertEqual(dstring.count("// Multicolor (9)"), 1)
        self.assertEqual(dstring.count("// Colorless (24)"), 1)
        self.assertEqual(dstring.count("// Red (5)"), 1)
        self.assertEqual(dstring.count("// Black (16)"), 1)
        self.assertEqual(dstring.count("// Green (6)"), 1)
        self.assertEqual(dstring.count("// Sideboard (15)"), 1)

        self.assertEqual(dstring.count("SB:"), 10)

        self.assertEqual(dstring.count("3 Raging Ravine"), 1)
        self.assertEqual(dstring.count("1 Wooded Foothills"), 1)
        self.assertEqual(dstring.count("4 Verdant Catacombs"), 1)

        self.assertEqual(dstring.count("SB: 1 Liliana, the Last Hope"), 1)
        self.assertEqual(dstring.count("SB: 2 Ancient Grudge"), 1)

    def test_deck_str_group_by_cmc(self):
        test_cards = self.cards.from_str("""
        3 Raging Ravine
        1 Wooded Foothills
        4 Verdant Catacombs
        1 Stomping Ground
        2 Overgrown Tomb
        1 Blood Crypt
        4 Blackcleave Cliffs
        2 Swamp
        1 Forest
        4 Bloodstained Mire

        2 Huntmaster of the Fells
        4 Dark Confidant
        2 Scavenging Ooze
        4 Tarmogoyf
        1 Fulminator Mage

        1 Chandra, Torch of Defiance
        4 Liliana of the Veil

        1 Kolaghan's Command
        4 Lightning Bolt
        3 Terminate
        3 Thoughtseize
        2 Abrupt Decay
        3 Inquisition of Kozilek

        1 Fatal Push

        1 Blooming Marsh
        1 Kalitas, Traitor of Ghet

        //Sideboard
        SB: 3 Fulminator Mage
        SB: 2 Collective Brutality
        SB: 1 Anger of the Gods
        SB: 1 Kolaghan's Command
        SB: 2 Ancient Grudge
        SB: 1 Maelstrom Pulse
        SB: 1 Liliana, the Last Hope
        SB: 2 Surgical Extraction
        SB: 1 Rakdos Charm
        SB: 1 Damnation""")

        dstring = test_cards.deck_str(group_by="cmc")
        print(dstring)

        self.assertEqual(dstring.count("// 0 (24)"), 1)
        self.assertEqual(dstring.count("// 1 (11)"), 1)
        self.assertEqual(dstring.count("// 2 (15)"), 1)
        self.assertEqual(dstring.count("// 3 (6)"), 1)
        self.assertEqual(dstring.count("// 4 (4)"), 1)

        self.assertEqual(dstring.count("3 Raging Ravine"), 1)
        self.assertEqual(dstring.count("1 Wooded Foothills"), 1)
        self.assertEqual(dstring.count("4 Verdant Catacombs"), 1)

        self.assertEqual(dstring.count("SB:"), 10)
        self.assertEqual(dstring.count("SB: 1 Liliana, the Last Hope"), 1)
        self.assertEqual(dstring.count("SB: 2 Ancient Grudge"), 1)

    @unittest.skip("Skipping test with heavy load.")
    def test_pprint_global(self):
        with redirect_stdout(StringIO()):
            self.cards.pprint()

    @unittest.skip("Skipping test to not bother Scryfall.")
    def test_download_images_overwrite_false(self):
        forests = self.cards.where_exactly(name="Forest")[0:5]
        forests.download_images_from_scryfall(dir_path=str(self.tmp_dir), overwrite=False)

        # The images Forest.jpg, Forest (1).jpg, etc. should be created in the temporary directory
        self.assertEqual(len(list(self.tmp_dir.glob("Forest*.jpeg"))), 5)

    @unittest.skip("Skipping test to not bother Scryfall.")
    def test_proxies(self):
        forests = self.cards.where_exactly(name="Forest")[0:5]
        forests.create_proxies(dir_path=str(self.tmp_dir), image_format="jpeg")

        # Should have 1 image in the folder
        self.assertEqual(len(list(self.tmp_dir.glob("*.jpeg"))), 1)


if __name__ == "__main__":
    unittest.main()
