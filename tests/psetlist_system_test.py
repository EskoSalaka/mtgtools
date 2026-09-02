from contextlib import redirect_stdout
from io import StringIO
import unittest

from mtgtools.PSetList import PSetList
from tests.system_setup_test import MtgDBSystemSetupTest


class TestPSetListSystem(MtgDBSystemSetupTest):
    """System tests for PSet objects for a full Scryfall database."""

    def test_add(self):
        test_sets = PSetList()
        self.assertEqual(len(test_sets), 0)

        torment = self.sets.where_exactly(code="tor")[0]
        innistrad = self.sets.where_exactly(code="isd")[0]

        test_sets += torment
        self.assertEqual(len(test_sets), 1)

        test_sets += innistrad
        self.assertEqual(len(test_sets), 2)

        test_sets = self.sets[0:2] + self.sets[2:4]
        self.assertEqual(len(test_sets), 4)

    def test_basic_search(self):
        self.assertEqual(len(self.sets.where(code="aer")), 3)
        self.assertEqual(len(self.sets.where_exactly(code="aer")), 1)
        self.assertEqual(len(self.sets.where(block="kaladesh")), 7)
        self.assertEqual(len(self.sets.where(block="kaladesh").where(set_type="expansion")), 2)

        self.assertTrue(len(self.sets.where(set_type="expansion")) > 0)
        self.assertTrue(len(self.sets.where(set_type="core")) > 0)
        self.assertTrue(len(self.sets.where(set_type="masters")) > 0)
        self.assertTrue(len(self.sets.where(set_type="masterpiece")) > 0)
        self.assertTrue(len(self.sets.where(set_type="from_the_vault")) > 0)
        self.assertTrue(len(self.sets.where(set_type="spellbook")) > 0)
        self.assertTrue(len(self.sets.where(set_type="premium_deck")) > 0)
        self.assertTrue(len(self.sets.where(set_type="duel_deck")) > 0)
        self.assertTrue(len(self.sets.where(set_type="draft_innovation")) > 0)
        self.assertTrue(len(self.sets.where(set_type="commander")) > 0)
        self.assertTrue(len(self.sets.where(set_type="planechase")) > 0)
        self.assertTrue(len(self.sets.where(set_type="archenemy")) > 0)
        self.assertTrue(len(self.sets.where(set_type="vanguard")) > 0)
        self.assertTrue(len(self.sets.where(set_type="funny")) > 0)
        self.assertTrue(len(self.sets.where(set_type="starter")) > 0)
        self.assertTrue(len(self.sets.where(set_type="box")) > 0)
        self.assertTrue(len(self.sets.where(set_type="promo")) > 0)
        self.assertTrue(len(self.sets.where(set_type="token")) > 0)
        self.assertTrue(len(self.sets.where(set_type="memorabilia")) > 0)
        self.assertTrue(len(self.sets.where(name="pro")) > 0)
        self.assertTrue(len(self.sets.where_exactly(name="pro")) == 0)

    def test_inclusion(self):
        torment = self.sets.where_exactly(code="tor")[0]
        innistrad = self.sets.where_exactly(code="isd")[0]

        test_sets = PSetList()
        test_sets += torment
        test_sets += innistrad

        self.assertIn(torment, test_sets)
        self.assertIn(innistrad, test_sets)

        self.assertTrue(torment in test_sets)
        self.assertTrue(innistrad in test_sets)

        self.assertNotIn(self.sets[5], test_sets)
        self.assertFalse(self.sets[5] in test_sets)

    def test_index(self):
        torment = self.sets.where_exactly(code="tor")[0]
        innistrad = self.sets.where_exactly(code="isd")[0]

        test_sets = PSetList()
        test_sets += torment
        test_sets += innistrad

        self.assertEqual(test_sets[0], torment)
        self.assertEqual(test_sets[1], innistrad)

        self.assertEqual(test_sets.index(torment), 0)
        self.assertEqual(test_sets.index(innistrad), 1)

        self.assertEqual(self.sets.index(self.sets[0]), 0)
        self.assertEqual(self.sets.index(self.sets[1]), 1)
        self.assertEqual(self.sets.index(self.sets[2]), 2)
        self.assertEqual(self.sets.index(self.sets[3]), 3)
        self.assertEqual(self.sets.index(self.sets[4]), 4)
        self.assertEqual(self.sets.index(self.sets[5]), 5)
        self.assertEqual(self.sets.index(self.sets[6]), 6)

    def test_pprint_global_runs(self):
        with redirect_stdout(StringIO()):
            self.sets.pprint()

    def test_json(self):
        torment = self.sets.where_exactly(code="tor")[0]
        torment_json = torment.json

        self.assertIsInstance(torment_json, str)
        self.assertIn('"code": "tor"', torment_json)
        self.assertIn('"name": "Torment"', torment_json)
        self.assertIn('"set_type": "expansion"', torment_json)
        self.assertIn('"card_count": 143', torment_json)
        self.assertIn('"released_at": "2002-02-04"', torment_json)
        self.assertIn('"digital": false', torment_json)

        self.assertIn('"cards": [', torment_json)  # Should include the cards in the set

    def test_jprint_runs(self):
        with redirect_stdout(StringIO()):
            self.sets.jprint()

    def test_len(self):
        self.assertEqual(len(self.sets[0:10]), 10)
        self.assertEqual(self.sets[0:10].len, 10)


if __name__ == "__main__":
    unittest.main()
