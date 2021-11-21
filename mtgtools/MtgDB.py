########################################################################################################################
# Copyright © 2018 Esko-Kalervo Salaka.
# All rights reserved.
#
#
# Zope Public License (ZPL) Version 2.1
#
# A copyright notice accompanies this license document that identifies the
# copyright holders.
#
# This license has been certified as open source. It has also been designated as
# GPL compatible by the Free Software Foundation (FSF).
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions in source code must retain the accompanying copyright
# notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the accompanying copyright
# notice, this list of conditions, and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Names of the copyright holders must not be used to endorse or promote
# products derived from this software without prior written permission from the
# copyright holders.
#
# 4. The right to distribute this software or to use it for any purpose does not
# give you the right to use Servicemarks (sm) or Trademarks (tm) of the
# copyright
# holders. Use of them is covered by separate agreement with the copyright
# holders.
#
# 5. If any files are modified, you must cause the modified files to carry
# prominent notices stating that you changed the files and the date of any
# change.
#
# Disclaimer
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESSED
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# This software uses ZODB, a native object database for Python, which is a
# copyright © by Zope Foundation and Contributors.
#
# This software uses Scryfall's rest-like API which is a copyright © by Scryfall LLC.
#
# This software uses rest-like API of magicthegathering.io which is a copyright © by Andrew Backes.
#
# This software uses the Python Imaging Library (PIL) which is a copyright © 1997-2011 by Secret Labs AB and
# copyright © 1995-2011 by Fredrik Lundh
#
# All the graphical and literal information and data related to Magic: The Gathering which can be handled with this
# software, such as card information and card images, is copyright of Wizards of the Coast LLC, a
# Hasbro inc. subsidiary.
#
# This software is in no way endorsed or promoted by Scryfall, Zope Foundation, magicthegathering.io or
# Wizards of the Coast.
########################################################################################################################
import datetime
import sys
import time

import ZODB
import ZODB.FileStorage
import transaction
from warnings import warn

from mtgtools.PSetList import PSetList
from mtgtools.PCardList import PCardList
from .util.api_requests import process_scryfall_cards, process_scryfall_sets, get_tot_mtgio_cards, process_mtgio_sets, \
    process_mtgio_cards, get_scryfall_card_bulks, download_scryfall_bulk_data, process_cards_bulk


class MtgDB:
    """MTGDatabaseTool is a simple to use ZODB object database tool to handle downloading and storing
    Magic: the Gathering card and set data from Scryfall and/or magicthegathering.io API's. Querying the databases is
    simple and straightforward with no SQL needed. It is also possible to easily store your own card lists and other
    data.

    The tool is initiated with a path to an existing ZODB storage. If no storage is found, a new empty one is
    automatically created. After initialization the storage, database, connection and root of the connection can be
    accessed with self.storage, self.database, self.connection and self.root.
    More on how to use ZODB: http://www.zodb.org/en/latest/.

    The database contains two kinds of 'indexes' for each API, a list of cards (PCardList) containing all the cards
    and sets (PSetList) which each also contain their own respective cards. For scryfall, the cards can be accessed with
    self.root.scryfall_cards and the sets can be accessed with self.root.scryfall_sets. For magicthegathering.io
    self.root.mtgio_cards and self.root.mtgio_sets.

    The persistent card lists (PCardList objects) and persistent set lists (PSetList objects) have their own handy ways
    for querying for certain objects. The PCardLists further contain persistent card objects (PCard) and PsetLists
    contain persistent set objects (PSet) which can be easily stored in the database under your own indexes in the
    root of the database.

    For example any persistent card list can be stored with:

        my_list = ... (some PCardList instance)
        self.root.my_list = my_list
        transaction.commit()

    Also lists of persistent list instances can be saved with using the PersistentList objects from ZODB which mostly
    work like normal Python lists:

        from Persistent.list import PersistentList
        self.root.my_lists = PersistentList([my_list1, my_list2, my_list3, ...])
        transaction.commit()

    For information on how to query lists, check PCardList and PSetList documentation.

    Args:
        storage_path (str): A path to a ZODB storage to open. If no storage is found, a new one is created.
    """

    def __init__(self, storage_path):
        self.storage = ZODB.FileStorage.FileStorage(storage_path)
        self.database = ZODB.DB(self.storage)
        self.connection = self.database.open()
        self.root = self.connection.root

        try:
            self.root.scryfall_cards
        except (AttributeError, KeyError):
            self.root.scryfall_cards = PCardList()

        try:
            self.root.scryfall_sets
        except (AttributeError, KeyError):
            self.root.scryfall_sets = PSetList()

        try:
            self.root.mtgio_cards
        except (AttributeError, KeyError):
            self.root.mtgio_cards = PCardList()

        try:
            self.root.mtgio_sets
        except (AttributeError, KeyError):
            self.root.mtgio_sets = PSetList()

    def scryfall_update(self, verbose=True, workers=8):
        """Completely updates the database from scryfall downloading new sets and cards and also
        updating the current objects if there are any changes.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())

        current_sets = self.root.scryfall_sets
        current_cards = self.root.scryfall_cards
        old_set_count = len(current_sets)

        if verbose:
            print('Attempting to update all the data...')
            print('querying Scryfall API...')

        # Update sets and check for obsolete sets
        obsolete_sets = process_scryfall_sets(current_sets)

        tot_new_cards = sum([pset.card_count for pset in current_sets]) + \
                        sum([pset.card_count for pset in obsolete_sets]) - \
                        len(current_cards)
        tot_new_sets = len(current_sets) + len(obsolete_sets) - old_set_count

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards and updating old.')
            print('-----------------------------------------------------------------------------------------------')

        # Update cards
        process_scryfall_cards(current_sets, current_cards, verbose=verbose, workers=workers)

        # Transfer cards from obsolete sets to new ones
        for obsolete_set in obsolete_sets:
            cards = obsolete_set.cards
            if cards:
                pset = current_sets.where_exactly(code=cards[0].set)
                if len(pset):
                    pset[0].extend(cards)

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe Scryfall database is now up to date! \nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def scryfall_bulk_update(self, bulk_type="default_cards", verbose=True):
        """Completely updates the database from scryfall downloading new sets and cards and also
        updating the current objects if there are any changes. The sets are downloaded from the
        API as usual but the cards are downloaded from bulk data provided by scryfall.
        
        The bulk data currently contains 4 different kinds of datasets of cards: 'oracle_cards', 'unique_artwork',
        'default_cards' or 'all_cards'.

        Args:
            bulk_type (str): Which type of bulk data downloaded, either 'oracle_cards', 'unique_artwork',
                'default_cards' or 'all_cards'
            verbose (bool): If enabled, prints out progression messages during the updating process.
        """
        start = round(time.time())

        current_sets = self.root.scryfall_sets
        current_cards = self.root.scryfall_cards
        old_set_count = len(current_sets)

        if verbose:
            print('Attempting to update all the data from bulk...')
            print('querying Scryfall API for sets...')

        # Update sets and check for obsolete sets
        obsolete_sets = process_scryfall_sets(current_sets)

        if verbose:
            print('querying Scryfall API for bulk data...')

        scryfall_card_bulks = get_scryfall_card_bulks()['data']
        bulk_type_data = next((bulk for bulk in scryfall_card_bulks if bulk['type'] == bulk_type), None)

        if verbose:
            print('-----------------------------------------------------------------------------------------------')
            print('Selected bulk type: "%s":  %s' % (bulk_type, bulk_type_data['description']))
            print('Updated at: %s ' % bulk_type_data['updated_at'])
            print('Size: %s MB' % round(int(bulk_type_data['compressed_size']) / 1024**2))
            print('-----------------------------------------------------------------------------------------------')
            print("Downloading bulk data...")

        bulk_card_data = download_scryfall_bulk_data(bulk_type_data['download_uri'])
        tot_new_cards = len(bulk_card_data) - len(current_cards)
        tot_new_sets = len(current_sets) + len(obsolete_sets) - old_set_count

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Processing bulk data and updating cards.')
            print('-----------------------------------------------------------------------------------------------')

        if tot_new_cards < 0:
            print('Looks like the selected bulk data type contains less cards than what are currently in your')
            print('database, you probably want to select unique_artwork, default_cards or all_cards to update from.')

        process_cards_bulk(current_sets, current_cards, bulk_card_data, verbose)

        # Transfer cards from obsolete sets to new ones
        for obsolete_set in obsolete_sets:
            cards = obsolete_set.cards
            if cards:
                pset = current_sets.where_exactly(code=cards[0].set)
                if len(pset):
                    pset[0].extend(cards)

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe Scryfall database is now up to date! \nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def mtgio_update(self, verbose=True, workers=8):
        """Completely updates the database from magicthegathering.io downloading new sets and cards and also
        updating the current objects if there are any changes.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())
        current_cards = self.root.mtgio_cards
        current_sets = self.root.mtgio_sets
        old_set_count = len(current_sets)
        old_card_count = len(current_cards)

        if verbose:
            print('Attempting to update the current database objects and fetch new data.')
            print('querying magicthegathering.io API...')

        # Update sets
        obsolete_sets = process_mtgio_sets(current_sets)

        tot_new_cards = get_tot_mtgio_cards() - old_card_count
        tot_new_sets = len(current_sets) + len(obsolete_sets) - old_set_count

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards and updating old.')
            print('-----------------------------------------------------------------------------------------------')

        # Update cards
        process_mtgio_cards(current_sets, current_cards, verbose=verbose, workers=workers)

        # Transfer cards from obsolete sets to new ones
        for obsolete_set in obsolete_sets:
            cards = obsolete_set.cards
            if cards:
                pset = current_sets.where_exactly(code=cards[0].set)
                if len(pset):
                    pset[0].extend(cards)

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe magicthegathering.io database is now up to date!\nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def update_new_from_scryfall(self, verbose=True, workers=8):
        """deprecated"""
        warn('This method is currently deprecated. The method "scryfall_update" is automatically called instead"')
        self.scryfall_update(verbose=verbose, workers=workers)

    def full_update_from_scryfall(self, verbose=True, workers=8):
        """deprecated"""
        warn('This method is currently deprecated. The method "scryfall_update" is automatically called instead"')
        self.scryfall_update(verbose=verbose, workers=workers)

    def update_new_from_mtgio(self, verbose=True, workers=8):
        """deprecated"""
        warn('This method is currently deprecated. The method "mtgio_update" is automatically called instead"')
        self.mtgio_update(verbose=verbose, workers=workers)

    def full_update_from_mtgio(self, verbose=True, workers=8):
        """deprecated"""
        warn('This method is currently deprecated. The method "mtgio_update" is automatically called instead"')
        self.mtgio_update(verbose=verbose, workers=workers)

    def format_and_pack(self):
        """Formats the database. After this operation, the old objects are still available in 'mydata.fs.old'
        storage.
        """
        answer = input('Attempting to format the whole database. Continue (y/n)?')

        if answer == 'y' or answer == 'yes':
            self.root.scryfall_sets = PSetList()
            self.root.scryfall_cards = PCardList()
            self.root.mtgio_sets = PSetList()
            self.root.mtgio_cards = PCardList()
            transaction.commit()
            self.database.pack()

    def close(self):
        """Closes the database properly. Using this is recommended after you are done using the database."""
        self.connection.close()
        self.database.close()
        self.storage.close()

    def commit(self):
        """Commits any changes to the database."""
        transaction.commit()

    def abort(self):
        """Aborts any changes made to the database."""
        transaction.abort()

    def pack(self):
        """Packs the database."""
        self.database.pack()

    def verify_scryfall_integrity(self):
        """
        Asserts a certain set of integrity conditions related to the Scryfall card&set database. These conditions are:
          - The sum of cards is the same as the separate sums of cards in each set
          - No set has duplicate cards
          - The cards database has no duplicate cards
          - Each card is in the set it belongs to
          - Each card belongs in a set
          - The set database has no duplicate sets
          - The number of cards in each set matches the set's 'card_count' attribute

        The database should be fine if no assertation or other errors are raised.
        """
        cards = self.root.scryfall_cards
        sets = self.root.scryfall_sets

        # The sum of cards is the same as the separate sums of cards in each set
        assert len(cards) == sum([len(pset.cards) for pset in sets])

        # The cards database has no duplicate cards
        ids = [card.id for card in cards]
        assert len(ids) == len(set(ids))

        # The sets database has no duplicate sets
        ids = [pset.id for pset in sets]
        assert len(ids) == len(set(ids))

        for pset in sets:
            # The number of cards in each set matches the set's 'card_count' attribute
            assert len(pset.cards) == pset.card_count

            # Each card of the set is in the set it belongs to
            for card in pset.cards:
                assert card.set == pset.code

            # No set has duplicate cards
            ids = [card.id for card in pset.cards]
            assert len(ids) == len(set(ids))

        # Each card belongs in a set
        for card in cards:
            assert card in sets.where_exactly(code=card.set)[0].cards

        print("If no errors were encountered then your database should be fine!")
