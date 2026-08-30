import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from tests.system_setup_test import MtgDBSystemSetupTest


class TestPSetSystem(MtgDBSystemSetupTest):
    """System tests for PSet objects from the seeded Scryfall database."""

    def setUp(self):
        super().setUp()

        # Basic tests for a set containing known persisted cards.
        self.torment = self.sets.where_exactly(code="tor")[0]

    def test_set_has_expected_scryfall_fields(self):
        self.assertEqual(self.torment.code, "tor")
        self.assertEqual(self.torment.name, "Torment")
        self.assertEqual(self.torment.set_type, "expansion")
        self.assertEqual(self.torment.card_count, 143)
        self.assertEqual(self.torment.released_at, "2002-02-04")
        self.assertFalse(self.torment.digital)
        self.assertEqual(str(self.torment), "Torment(tor)")
        self.assertEqual(repr(self.torment), "Torment(tor)")

    def test_set_contains_expected_cards(self):
        aquamoeba = self.cards.where_exactly(name="Aquamoeba", set="tor")[0]

        self.assertGreater(len(self.torment), 0)
        self.assertIn(aquamoeba, self.torment)
        self.assertTrue(all(card.set == self.torment.code for card in self.torment))

    def test_set_matches_any(self):
        self.assertTrue(self.torment.matches_any(name="tor"))
        self.assertTrue(self.torment.matches_any(code="TOR"))
        self.assertTrue(self.torment.matches_any(set_type="pans"))
        self.assertTrue(self.torment.matches_any(card_count=143))
        self.assertFalse(self.torment.matches_any(name="innistrad", code="isd", card_count=264))

    def test_set_matches_all(self):
        self.assertTrue(
            self.torment.matches_all(
                name="TORMENT",
                code="tor",
                set_type="expansion",
                card_count=143,
                released_at="2002-02-04",
            )
        )
        self.assertFalse(self.torment.matches_all(name="tor"))
        self.assertFalse(self.torment.matches_all(name="Torment", code="isd"))
        self.assertFalse(self.torment.matches_all(card_count=264))

    def test_set_pprint_and_jprint_run(self):
        with redirect_stdout(StringIO()):
            self.torment.pprint()
            self.torment.jprint()

    def test_set_json(self):
        set_json = self.torment.json

        self.assertIn('"code": "tor"', set_json)
        self.assertIn('"name": "Torment"', set_json)
        self.assertIn('"set_type": "expansion"', set_json)
        self.assertIn('"cards": [', set_json)
        json.loads(set_json)


if __name__ == "__main__":
    unittest.main()
