import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from tests.system_setup_test import MtgDBSystemSetupTest


class TestPRulingSystem(MtgDBSystemSetupTest):
    """System tests for PRuling objects from a full Scryfall database."""

    def setUp(self):
        super().setUp()

        # Basic tests for a ruling associated with a card that has rulings
        self.aquamoeba = self.cards.where_exactly(name="Aquamoeba", set="tor")[0]
        self.ruling = self.aquamoeba.rulings[0]

    def test_ruling_has_expected_scryfall_fields(self):
        self.assertEqual(self.ruling.object, "ruling")
        self.assertEqual(self.ruling.source, "wotc")
        self.assertEqual(self.ruling.published_at, "2021-03-19")
        self.assertIn("damage remains marked", self.ruling.comment)
        self.assertEqual(str(self.ruling), self.ruling.comment)
        self.assertEqual(repr(self.ruling), self.ruling.comment)

    def test_ruling_is_associated_with_card_printings(self):
        self.assertIsNotNone(self.ruling.cards)
        self.assertGreater(len(self.ruling.cards), 0)
        self.assertIn(self.aquamoeba, self.ruling.cards)
        self.assertTrue(all(card.oracle_id == self.ruling.oracle_id for card in self.ruling.cards))

    def test_ruling_is_associated_with_card_printings_general(self):
        for ruling in self.rulings[0:1000]:  # Test first 1000 rulings
            self.assertIsNotNone(ruling.cards)
            self.assertGreater(len(ruling.cards), 0)
            self.assertTrue(all(card.oracle_id == ruling.oracle_id for card in ruling.cards))

    def test_ruling_pprint_str(self):
        summary = self.ruling.pprint_str()
        expanded = self.ruling.pprint_str(expanded=True)

        self.assertIn("damage remains marked", summary)
        self.assertIn("Source: wotc", expanded)
        self.assertIn("Published at: 2021-03-19", expanded)
        self.assertIn("Associated cards: Aquamoeba", expanded)

    def test_ruling_pprint_and_jprint_run(self):
        with redirect_stdout(StringIO()):
            self.ruling.pprint()
            self.ruling.pprint(expanded=True)
            self.ruling.jprint()

    def test_ruling_json(self):
        ruling_json = self.ruling.json

        self.assertIn('"object": "ruling"', ruling_json)
        self.assertIn('"source": "wotc"', ruling_json)
        self.assertIn('"published_at": "2021-03-19"', ruling_json)
        self.assertNotIn('"_cards"', ruling_json)
        self.assertNotIn('"id"', ruling_json)
        json.loads(ruling_json)


if __name__ == "__main__":
    unittest.main()
