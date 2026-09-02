import tempfile
import unittest
import shutil
from pathlib import Path

from mtgtools import MtgDB

SEED_DATABASE_PATH = Path(__file__).parent / "data" / "scryfall.fs"


class MtgDBSystemSetupTest(unittest.TestCase):
    """System test setup with a database seeded with Scryfall data. This class is intended to be used as a base
    class for system tests that require a database with Scryfall data.

    The system test require a database which is up to date with Scryfall data. The DB stays saved in the data folder
    of the tests folder, and should be updated manually when required. You can update/build the database by running the
    test `test_basic_update` in this class. It is skipped by default since it takes a while.
    """

    @classmethod
    def setUpClass(cls):
        print("Setting up system test database with Scryfall data...\n")
        cls._seed_database_path = SEED_DATABASE_PATH
        if not cls._seed_database_path.exists():
            cls._seed_database_path.parent.mkdir(parents=True, exist_ok=True)
            seed_db = MtgDB.MtgDB(str(cls._seed_database_path))
            try:
                seed_db.scryfall_bulk_update(verbose=False)
                seed_db.scryfall_bulk_update(bulk_type="rulings", verbose=False)
            finally:
                seed_db.close()

        cls.db = MtgDB.MtgDB(str(cls._seed_database_path))
        cls.cards = cls.db.root.scryfall_cards
        cls.sets = cls.db.root.scryfall_sets
        cls.rulings = cls.db.root.rulings

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_required_data_exists(self):
        self.assertTrue(self.cards is not None)
        self.assertTrue(self.sets is not None)
        self.assertTrue(self.rulings is not None)
        self.assertGreater(len(self.cards), 0)
        self.assertGreater(len(self.sets), 0)
        self.assertGreater(len(self.rulings), 0)

    @classmethod
    def tearDownClass(cls):
        print("\nClosing system test database...")
        cls.db.close()

    @unittest.skip("Skipping scryfall update test to avoid network calls during testing.")
    def test_basic_update(self):
        self.db.scryfall_bulk_update(verbose=False)
        self.db.scryfall_bulk_update(bulk_type="rulings", verbose=False)
