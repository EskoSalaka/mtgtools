import unittest
import warnings

from mtgtools import MtgDB

from mtgtools.PCardList import PCardList
from mtgtools.PSetList import PSetList

tool = MtgDB.MtgDB("testdb.fs")
tool.scryfall_update()
cards = tool.root.scryfall_cards
sets = tool.root.scryfall_sets

basic_lands = 3 * cards.where_exactly(name='forest')[0:1] + \
              3 * cards.where_exactly(name='mountain')[0:1] + \
              3 * cards.where_exactly(name='island')[0:1] + \
              3 * cards.where_exactly(name='swamp')[0:1] + \
              3 * cards.where_exactly(name='plains')[0:1]

non_basic_lands = 3 * cards.where_exactly(name='bayou')[0:1] + \
                  3 * cards.where_exactly(name='Cascading Cataracts')[0:1] + \
                  3 * cards.where_exactly(name='Evolving Wilds')[0:1] + \
                  3 * cards.where_exactly(name='Mutavault')[0:1]

creatures = 3 * cards.where_exactly(name='wild mongrel')[0:1] + \
            3 * cards.where_exactly(name='Ogre Taskmaster')[0:1] + \
            3 * cards.where_exactly(name='Aquamoeba')[0:1] + \
            3 * cards.where_exactly(name='Midnight Banshee')[0:1] + \
            3 * cards.where_exactly(name='Trapjaw Tyrant')[0:1] + \
            3 * cards.where_exactly(name='Merfolk Mistbinder')[0:1] + \
            3 * cards.where_exactly(name='Storm Fleet Sprinter')[0:1] + \
            3 * cards.where_exactly(name='Jungle Creeper')[0:1] + \
            3 * cards.where_exactly(name='Belligerent Hatchling')[0:1] + \
            3 * cards.where_exactly(name='Crackleburr')[0:1] + \
            3 * cards.where_exactly(name='Akki Lavarunner // Tok-Tok, Volcano Born')[0:1] + \
            3 * cards.where_exactly(name="Homura, Human Ascendant // Homura's Essence")[0:1] + \
            3 * cards.where_exactly(name='Accursed Witch // Infectious Curse')[0:1] + \
            3 * cards.where_exactly(name='Civilized Scholar // Homicidal Brute')[0:1] +\
            3 * cards.where_exactly(name='Dryad Arbor')[0:1] + \
            3 * cards.where_exactly(name='Aegis of the Gods')[0:1]

non_creature_spells = 3 * cards.where_exactly(name='Back from the Brink')[0:1] + \
                      3 * cards.where_exactly(name='Blazing Torch')[0:1] + \
                      3 * cards.where_exactly(name='Fall of the Thran')[0:1] + \
                      3 * cards.where_exactly(name='Bonds of Faith')[0:1] + \
                      3 * cards.where_exactly(name='Brimstone Volley')[0:1] + \
                      3 * cards.where_exactly(name='Bump in the Night')[0:1] + \
                      3 * cards.where_exactly(name='Cellar Door')[0:1] + \
                      3 * cards.where_exactly(name='Curse of the Bloody Tome')[0:1] + \
                      3 * cards.where_exactly(name="Full Moon's Rise")[0:1] + \
                      3 * cards.where_exactly(name='Alive // Well')[0:1] + \
                      3 * cards.where_exactly(name='Appeal // Authority')[0:1] + \
                      3 * cards.where_exactly(name='Izzet Signet')[0:1]

planeswalkers = 3 * cards.where_exactly(name='Liliana of the Veil')[0:1] + \
                3 * cards.where_exactly(name='Garruk Relentless // Garruk, the Veil-Cursed')[0:1] + \
                3 * cards.where_exactly(name='Ajani Vengeant')[0:1]

tokens = 3 * cards.where_exactly(name='Angel')[0:1] + \
         3 * cards.where_exactly(name='Clue')[0:1] + \
         3 * cards.where_exactly(name='Energy Reserve')[0:1] + \
         3 * cards.where_exactly(name='Angel // Demon')[0:1]

other = 3 * cards.where_exactly(name='Ajani Steadfast Emblem')[0:1] + \
        3 * cards.where_exactly(name='Ashnod')[0:1] + \
        3 * cards.where_exactly(name='Agyrem')[0:1] + \
        3 * cards.where_exactly(name='All in Good Time')[0:1]

testlist = other + tokens + creatures + non_basic_lands + \
                non_creature_spells + basic_lands + planeswalkers


class TestPCardsListMethodsScryfall(unittest.TestCase):
    def test_integrity(self):
        tool.verify_scryfall_integrity()

    def test_basic_update(self):
        clean_db = MtgDB.MtgDB("clean_db.fs")
        clean_db.scryfall_update()
        clean_db.verify_scryfall_integrity()
        clean_db.close()


    def test_update_changed_sets(self):
        clean_db = MtgDB.MtgDB("clean_db.fs")
        c_set = clean_db.root.scryfall_sets[0]
        c_cards = PCardList(c_set._cards)
        c1_l = len(clean_db.root.scryfall_cards)
        s1_l = len(clean_db.root.scryfall_sets)

        c_set_code = c_set.code
        c_set_name = c_set.name

        c_set.code= 'xxxyyyy'
        c_set.name = 'xxxyyyy'

        self.assertTrue(c_set_code not in [pset.code for pset in clean_db.root.scryfall_sets])
        self.assertTrue(c_set_name not in [pset.name for pset in clean_db.root.scryfall_sets])
        self.assertTrue('xxxyyyy' in [pset.code for pset in clean_db.root.scryfall_sets])
        self.assertTrue('xxxyyyy' in [pset.name for pset in clean_db.root.scryfall_sets])

        clean_db.commit()
        clean_db.scryfall_update()

        self.assertTrue('xxxyyyy' not in [pset.code for pset in clean_db.root.scryfall_sets])
        self.assertTrue('xxxyyyy' not in [pset.name for pset in clean_db.root.scryfall_sets])
        self.assertTrue(c_set_code in [pset.code for pset in clean_db.root.scryfall_sets])
        self.assertTrue(c_set_name in [pset.name for pset in clean_db.root.scryfall_sets])
        self.assertEqual(c1_l, len(clean_db.root.scryfall_cards))
        self.assertEqual(s1_l, len(clean_db.root.scryfall_sets))
        self.assertTrue(clean_db.root.scryfall_sets.where_exactly(code=c_set_code)[0].has_all(c_cards))
        self.assertEqual(len(clean_db.root.scryfall_sets.where_exactly(code=c_set_code)[0]), len(c_cards))

        self.assertEqual(len(clean_db.root.scryfall_cards),
                         sum([len(pset.cards) for pset in clean_db.root.scryfall_sets]))

        for pset in clean_db.root.scryfall_sets:
            self.assertEqual(len(pset.cards), pset.card_count)

            for card in pset.cards:
                self.assertEqual(card.set, pset.code)

        clean_db.verify_scryfall_integrity()

        clean_db.close()

    def test_update_changed_cards(self):
        clean_db = MtgDB.MtgDB("clean_db.fs")
        c1_l = len(clean_db.root.scryfall_cards)
        s1_l = len(clean_db.root.scryfall_sets)
        c1 = clean_db.root.scryfall_cards[10000]
        old_name = c1.name
        old_code = c1.set
        c1.name = "xxxyyyy"
        c1.set = "xxxyyyy"

        clean_db.commit()

        clean_db.scryfall_update()
        self.assertEqual(c1_l, len(clean_db.root.scryfall_cards))
        self.assertEqual(s1_l, len(clean_db.root.scryfall_sets))
        self.assertNotEqual(c1.name, "xxxyyyy")
        self.assertNotEqual(c1.set, "xxxyyyy")
        self.assertEqual(c1.name, old_name)
        self.assertEqual(c1.set, old_code)

        self.assertEqual(len(clean_db.root.scryfall_cards),
                         sum([len(pset.cards) for pset in clean_db.root.scryfall_sets]))

        for pset in clean_db.root.scryfall_sets:
            self.assertEqual(len(pset.cards), pset.card_count)

            for card in pset.cards:
                self.assertEqual(card.set, pset.code)

        clean_db.verify_scryfall_integrity()
        clean_db.close()

    def test_basic(self):
        self.assertEqual(len(tokens + other), 24)
        self.assertEqual(len(planeswalkers + other), 21)
        self.assertEqual(len(basic_lands + non_basic_lands), 27)

        self.assertEqual(len(testlist), 144)
        self.assertEqual(len(basic_lands), 15)
        self.assertEqual(len(non_basic_lands), 12)
        self.assertEqual(len(creatures), 48)
        self.assertEqual(len(non_creature_spells), 36)
        self.assertEqual(len(planeswalkers), 9)
        self.assertEqual(len(tokens), 12)
        self.assertEqual(len(other), 12)

        self.assertEqual(len(testlist.basic_lands()), 15)
        self.assertEqual(len(testlist.creatures()), 54)
        self.assertEqual(len(testlist.lands()), 30)
        self.assertEqual(len(testlist.noncreatures()), 90)
        self.assertEqual(len(testlist.unique_cards()), 48)
        self.assertEqual(len(testlist.unique_names()), 48)
        self.assertEqual(len(testlist.normal_playable_cards()), 120)

        self.assertEqual(len(testlist - testlist.lands()), 114)
        self.assertEqual(len(testlist - testlist.creatures()), 90)
        self.assertEqual(len(testlist + testlist.lands()), 174)
        self.assertEqual(len(testlist + testlist.creatures()), 198)
        self.assertEqual(len(testlist * 2), 288)
        self.assertEqual(len(2 * testlist), 288)
        self.assertEqual(len(5 * testlist[0:1]), 5)
        self.assertTrue(testlist[0] in 3 * testlist[0:1])

        self.assertTrue(testlist.has_all(creatures))
        self.assertTrue(testlist.has_any(creatures))
        self.assertTrue(testlist.has_all(planeswalkers))
        self.assertTrue(testlist.has_any(planeswalkers))
        self.assertTrue(testlist.has_all(other))
        self.assertTrue(testlist.has_any(other))
        self.assertTrue(testlist.has_all(non_creature_spells))
        self.assertTrue(testlist.has_any(non_creature_spells))
        self.assertTrue(testlist.has_all(non_basic_lands))
        self.assertTrue(testlist.has_any(non_basic_lands))
        self.assertTrue(testlist.has_all(basic_lands))
        self.assertTrue(testlist.has_any(basic_lands))

        self.assertTrue(testlist.has_all(creatures + creatures[0]))
        self.assertTrue(testlist.has_any(creatures + creatures[0]))
        self.assertTrue(testlist.has_all(planeswalkers + creatures[0]))
        self.assertTrue(testlist.has_any(planeswalkers + creatures[0]))
        self.assertTrue(testlist.has_all(other + creatures[0]))
        self.assertTrue(testlist.has_any(other + creatures[0]))
        self.assertTrue(testlist.has_all(non_creature_spells + creatures[0]))
        self.assertTrue(testlist.has_any(non_creature_spells + creatures[0]))
        self.assertTrue(testlist.has_all(non_basic_lands + creatures[0]))
        self.assertTrue(testlist.has_any(non_basic_lands + creatures[0]))
        self.assertTrue(testlist.has_all(basic_lands + creatures[0]))
        self.assertTrue(testlist.has_any(basic_lands + creatures[0]))

        self.assertFalse(cards.where_exactly(name='forest')[1] in basic_lands)
        self.assertFalse(cards.where_exactly(name='bayou')[1] in non_basic_lands)
        self.assertFalse(cards.where_exactly(name='island')[0] in non_basic_lands)

        self.assertTrue(cards.where_exactly(name='forest')[0] in basic_lands)
        self.assertTrue(cards.where_exactly(name='bayou')[0] in non_basic_lands)
        self.assertTrue(cards.where_exactly(name='Dryad Arbor')[0] in creatures)

        list1 = PCardList(creatures[0:3])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1.append(creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2.append(creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

        list1 = PCardList([creatures[0], creatures[1], creatures[2]])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1.append(creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2.append(creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

        list1 = PCardList(creatures[0:3])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += creatures[7]

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2 += creatures[7]

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

        list1 = PCardList(creatures[0:3])
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += list2

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 3)

        list2 += list1

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 9)

        list1 = creatures[0:3]
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += list2

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 3)

        list2 += list1

        self.assertEqual(len(list1), 6)
        self.assertEqual(len(list2), 9)

        list1 = [creatures[0], creatures[1], creatures[2]]
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

        list1 = PCardList() + creatures[0] + creatures[1] + creatures[2]
        list2 = PCardList(list1)

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1.append(creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list2.append(creatures[7])

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 4)

    def test_filter_and_sort(self):
        self.assertEqual(len(testlist), len(testlist.sorted(lambda card: card.name)))
        self.assertEqual(len(testlist), len(testlist.sorted(lambda card: card.cmc)))
        self.assertEqual(len(testlist), len(testlist.sorted(lambda card: card.type_line)))
        self.assertEqual(len(testlist), len(testlist.sorted(lambda card: card.color_identity)))

        self.assertEqual(creatures.where_exactly(name='Dryad Arbor')[0], creatures.sorted(lambda card: card.cmc)[0])
        self.assertEqual(creatures.where_exactly(name="Homura, Human Ascendant // Homura's Essence")[0],
                         creatures.sorted(lambda card: card.cmc)[-1])

        self.assertEqual(len(creatures) + 6, len(testlist.filtered(lambda card: 'Creature' in card.type_line)))
        self.assertTrue(testlist.filtered(lambda card: 'Creature' in card.type_line).has_all(creatures))

    def test_groups(self):
        tgst = testlist.grouped_by_simple_type()
        tgstcards = tgst['creatures'] + tgst['noncreatures'] + tgst['lands']

        self.assertEqual(len(tgstcards), len(testlist))
        self.assertTrue(tgstcards.has_all(testlist))
        self.assertTrue(tgst['creatures'].has_all(creatures))
        self.assertTrue(tgst['noncreatures'].has_all(non_creature_spells + planeswalkers + other))
        self.assertTrue(tgst['lands'].has_all(basic_lands + non_basic_lands))

        self.assertFalse(tgst['creatures'].has_any(non_creature_spells))
        self.assertFalse(tgst['creatures'].has_any(non_basic_lands))

        tgcmc = testlist.grouped_by_converted_mana_cost()
        tgcmccards = PCardList(list(card for sublist in tgcmc.values() for card in sublist))

        self.assertEqual(len(tgcmccards), len(testlist))
        self.assertTrue(tgcmccards.has_all(testlist))
        self.assertTrue(testlist.where_exactly(name="Ajani Steadfast Emblem")[0] in tgcmc[0])
        self.assertTrue(testlist.where_exactly(name="Ashnod")[0] in tgcmc[0])
        self.assertTrue(testlist.where_exactly(name="Clue")[0] in tgcmc[0])
        self.assertTrue(testlist.where_exactly(name="Blazing Torch")[0] in tgcmc[1])
        self.assertTrue(testlist.where_exactly(name="Wild Mongrel")[0] in tgcmc[2])
        self.assertTrue(testlist.where_exactly(name="Appeal // Authority")[0] in tgcmc[3])
        self.assertTrue(testlist.where_exactly(name="Ajani Vengeant")[0] in tgcmc[4])
        self.assertTrue(testlist.where_exactly(name="Trapjaw Tyrant")[0] in tgcmc[5])

        tgci = testlist.grouped_by_color_identity()
        tgciards = PCardList(list(card for sublist in tgci.values() for card in sublist))

        self.assertEqual(len(tgciards), len(testlist))
        self.assertTrue(tgciards.has_all(testlist))
        self.assertTrue(testlist.where_exactly(name="Ajani Steadfast Emblem")[0] in tgci[''])
        self.assertTrue(testlist.where_exactly(name="Ashnod")[0] in tgci[''])
        self.assertTrue(testlist.where_exactly(name="Clue")[0] in tgci[''])
        self.assertTrue(testlist.where_exactly(name="Blazing Torch")[0] in tgci[''])
        self.assertTrue(testlist.where_exactly(name="Wild Mongrel")[0] in tgci['G'])
        self.assertTrue(testlist.where_exactly(name="Appeal // Authority")[0] in tgci['GW'])
        self.assertTrue(testlist.where_exactly(name="Ajani Vengeant")[0] in tgci['RW'])
        self.assertTrue(testlist.where_exactly(name="Angel")[0] in tgci['W'])
        self.assertTrue(testlist.where_exactly(name="Dryad Arbor")[0] in tgci['G'])
        self.assertTrue(testlist.where_exactly(name="Forest")[0] in tgci['G'])
        self.assertTrue(cards.where_exactly(name="Izzet Signet")[0] in tgci['RU'])

        tgc = testlist.grouped_by_color()
        tgcards = PCardList(list(card for sublist in tgc.values() for card in sublist))
        self.assertEqual(len(tgcards), len(testlist))
        self.assertTrue(tgcards.has_all(testlist))
        self.assertTrue(testlist.where_exactly(name="Ajani Steadfast Emblem")[0] in tgc[''])
        self.assertTrue(testlist.where_exactly(name="Ashnod")[0] in tgc[''])
        self.assertTrue(testlist.where_exactly(name="Clue")[0] in tgc[''])
        self.assertTrue(testlist.where_exactly(name="Blazing Torch")[0] in tgc[''])
        self.assertTrue(testlist.where_exactly(name="Wild Mongrel")[0] in tgc['G'])
        self.assertTrue(testlist.where_exactly(name="Appeal // Authority")[0] in tgc['GW'])
        self.assertTrue(testlist.where_exactly(name="Ajani Vengeant")[0] in tgc['RW'])
        self.assertTrue(testlist.where_exactly(name="Angel")[0] in tgc['W'])
        self.assertTrue(testlist.where_exactly(name="Dryad Arbor")[0] in tgc['G'])
        self.assertTrue(testlist.where_exactly(name="Forest")[0] in tgc[''])
        self.assertTrue(testlist.where_exactly(name="Izzet Signet")[0] in tgc[''])

        cards.grouped_by_color()
        cards.grouped_by_color_identity()
        cards.grouped_by_converted_mana_cost()
        cards.grouped_by_simple_type()
        cards.mana_symbol_counts()

    def test_stats(self):
        self.assertEqual(creatures.converted_mana_cost(), 159)
        self.assertEqual(basic_lands.converted_mana_cost(), 0)
        self.assertEqual(non_basic_lands.converted_mana_cost(), 0)
        self.assertEqual(tokens.converted_mana_cost(), 0)
        self.assertEqual(other.converted_mana_cost(), 0)
        self.assertEqual(testlist.where_exactly(name="Izzet Signet")[0:1].converted_mana_cost(), 2)

        self.assertEqual(creatures.average_mana_cost(), 159 / 48)
        self.assertEqual(basic_lands.average_mana_cost(), 0)
        self.assertEqual(non_basic_lands.average_mana_cost(), 0)
        self.assertEqual(tokens.average_mana_cost(), 0)
        self.assertEqual(other.average_mana_cost(), 0)
        self.assertEqual(testlist.where_exactly(name="Izzet Signet")[0:2].average_mana_cost(), 2)

        self.assertEqual(creatures.mana_symbol_counts()['G'], 9)
        self.assertEqual(creatures.mana_symbol_counts()['W'], 12)
        self.assertEqual(non_creature_spells.mana_symbol_counts()['W'], 12)

        lands = non_basic_lands + basic_lands
        self.assertEqual(lands.mana_symbol_counts()['G'], 0)
        self.assertEqual(lands.mana_symbol_counts()['U'], 0)
        self.assertEqual(lands.mana_symbol_counts()['W'], 0)
        self.assertEqual(lands.mana_symbol_counts()['B'], 0)
        self.assertEqual(lands.mana_symbol_counts()['R'], 0)

        self.assertEqual(cards.where_exactly(name='Liliana of the Veil')[0:2].mana_symbol_counts()['B'], 4)
        self.assertEqual(cards.where_exactly(name='Liliana of the Veil')[0:2].mana_symbol_counts()['U'], 0)
        self.assertEqual(cards.where_exactly(name='Liliana of the Veil')[0:2].mana_symbol_counts()['W'], 0)
        self.assertEqual(cards.where_exactly(name='Liliana of the Veil')[0:2].mana_symbol_counts()['R'], 0)
        self.assertEqual(cards.where_exactly(name='Liliana of the Veil')[0:2].mana_symbol_counts()['G'], 0)

        self.assertEqual(creatures.where_exactly(name='Belligerent Hatchling')[0:2].mana_symbol_counts()['W'], 2)
        self.assertEqual(creatures.where_exactly(name='Belligerent Hatchling')[0:2].mana_symbol_counts()['R'], 2)
        self.assertEqual(creatures.where_exactly(name='Civilized Scholar // Homicidal Brute')[0:2].mana_symbol_counts()['U'], 2)
        self.assertEqual(non_creature_spells.where_exactly(name='Alive // Well')[0:2].mana_symbol_counts()['G'], 2)
        self.assertEqual(non_creature_spells.where_exactly(name='Alive // Well')[0:2].mana_symbol_counts()['W'], 2)

    def test_random(self):
        for _ in range(50):
            self.assertTrue(testlist.random_card() in testlist)

        for _ in range(50):
            self.assertTrue(testlist.has_all(testlist.random_sample(20, duplicates=True)))

        for _ in range(50):
            self.assertTrue(testlist.has_all(testlist.random_sample(20, duplicates=False)))

        for _ in range(50):
            self.assertTrue(testlist.has_all(testlist.random_pack()))

        init = testlist.random_pack()
        mythnum = 0
        rarenum = 0
        for _ in range(100):
            random_pack = testlist.random_pack()
            rares = [card for card in random_pack if card.rarity == 'rare']
            uncs = [card for card in random_pack if card.rarity == 'uncommon']
            coms = [card for card in random_pack if card.rarity == 'common']
            myths = [card for card in random_pack if 'mythic' in card.rarity]

            mythnum += len(myths)
            rarenum += len(rares)

            self.assertEqual(len(rares + myths), 1)
            self.assertEqual(len(uncs), 3)
            self.assertEqual(len(coms), 11)
            self.assertFalse(init.has_all(random_pack))

        self.assertTrue(mythnum > 0)
        self.assertTrue(rarenum > 0)

    def test_search(self):
        self.assertEqual(len(testlist.where(type_line='creature')), 54)
        self.assertEqual(len(testlist.where(type_line='arti')), 12)
        self.assertEqual(len(testlist.where(type_line='enchant')), 24)
        self.assertEqual(len(testlist.where(colors='R')), 24)

        self.assertEqual(len(testlist.where(type_line='enchant').where(colors='R')), 3)
        self.assertEqual(len(testlist.where(type_line='enchant').where(colors=['R'])), 3)

        self.assertEqual(len(creatures.where_exactly(colors='R')), 9)
        self.assertEqual(len(creatures.where_exactly(colors=['R'])), 9)
        self.assertEqual(len(non_creature_spells.where_exactly(type_line='enchantment').where(colors=['G'])), 3)
        self.assertEqual(len(non_creature_spells.where_exactly(type_line='enchantment').where(colors='G')), 3)

        self.assertEqual(len(creatures.where(colors='G')), 12)
        self.assertEqual(len(creatures.where_exactly(colors='G')), 6)
        self.assertEqual(len(creatures.where(colors=['G', 'B'])), 18)

        self.assertEqual(len(creatures.where_exactly(power='2', toughness='2')), 12)
        self.assertEqual(len(creatures.where_exactly(power='0')), 3)
        self.assertEqual(len(creatures.where_exactly(search_all_faces=True, power='5', toughness='1')), 3)
        self.assertEqual(len(creatures.where_exactly(power='0', toughness='1')), 3)
        self.assertEqual(len(creatures.
                             where(search_all_faces=True, power='5').
                             where(search_all_faces=True, toughness='1')), 3)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            testlist.where(colorrrrs='R')
            testlist.where(colors=None)
            testlist.where(colorrrrs=None)
            PCardList().where(colors=None)

            self.assertEqual(len(w), 4)

    def test_sets(self):
        self.assertEqual(len(sets.where(code='aer')), 3)
        self.assertEqual(len(sets.where_exactly(code='aer')), 1)
        self.assertEqual(len(sets.where(block='kaladesh')), 7)
        self.assertEqual(len(sets.where(block='kaladesh').where(set_type='expansion')), 2)

        self.assertTrue(len(sets.where(set_type='expansion')) > 0)
        self.assertTrue(len(sets.where(set_type='core')) > 0)
        self.assertTrue(len(sets.where(set_type='masters')) > 0)
        self.assertTrue(len(sets.where(set_type='masterpiece')) > 0)
        self.assertTrue(len(sets.where(set_type='from_the_vault')) > 0)
        self.assertTrue(len(sets.where(set_type='spellbook')) > 0)
        self.assertTrue(len(sets.where(set_type='premium_deck')) > 0)
        self.assertTrue(len(sets.where(set_type='duel_deck')) > 0)
        self.assertTrue(len(sets.where(set_type='draft_innovation')) > 0)
        self.assertTrue(len(sets.where(set_type='commander')) > 0)
        self.assertTrue(len(sets.where(set_type='planechase')) > 0)
        self.assertTrue(len(sets.where(set_type='archenemy')) > 0)
        self.assertTrue(len(sets.where(set_type='vanguard')) > 0)
        self.assertTrue(len(sets.where(set_type='funny')) > 0)
        self.assertTrue(len(sets.where(set_type='starter')) > 0)
        self.assertTrue(len(sets.where(set_type='box')) > 0)
        self.assertTrue(len(sets.where(set_type='promo')) > 0)
        self.assertTrue(len(sets.where(set_type='token')) > 0)
        self.assertTrue(len(sets.where(set_type='memorabilia')) > 0)
        self.assertTrue(len(sets.where(name='pro')) > 0)
        self.assertTrue(len(sets.where_exactly(name='pro')) == 0)

        list1 = PSetList() + sets[3] + sets[20] + sets[50]
        list2 = PSetList(list1)
        self.assertTrue(isinstance(list1, PSetList))

        self.assertEqual(len(list1), 3)
        self.assertEqual(len(list2), 3)

        list1 += sets[22]

        self.assertEqual(len(list1), 4)
        self.assertEqual(len(list2), 3)

        list1 += list2

        self.assertEqual(len(list1), 7)
        self.assertEqual(len(list2), 3)

        list2 += list1

        self.assertEqual(len(list1), 7)
        self.assertEqual(len(list2), 10)

        list1 += list1

        self.assertEqual(len(list1), 14)
        self.assertEqual(len(list2), 10)

        sets.pprint()
        sets.json

        list1 = PSetList() + sets[20] + sets[21]
        print(list1.json)
        print(list1.json)

    def test_pretty_print_and_str(self):
        cards.pprint()
        print(cards.deck_str())
        print(cards.json)

    def test_download_images(self):
        testlist.download_images_from_scryfall(dir_path='test_images')

    def test_proxies(self):
        testlist.create_proxies(dir_path='test_images')


if __name__ == '__main__':
    unittest.main()