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
import math
import sys
import json
import time
import urllib

import asyncio
import concurrent.futures
from urllib.error import URLError
from urllib.request import Request, urlopen

import ZODB
import ZODB.FileStorage
import transaction

from mtgtools.PCardList import PCardList
from mtgtools.PSetList import PSetList
from mtgtools.PCard import PCard
from mtgtools.PSet import PSet


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

    def _get_response_json_with_headers(self, url, headers):
        try:
            with urlopen(urllib.request.Request(url, headers=headers), timeout=30) as conn:
                return json.loads(conn.read().decode('utf-8'))
        except URLError as err:
            print('Something went wrong with requesting url {}: '.format(url) + str(err))

    def _get_response_json(self, url):
        try:
            with urlopen(url, timeout=30) as conn:
                return json.loads(conn.read().decode('utf-8'))
        except URLError as err:
            print('Something went wrong with requesting url {}: '.format(url) + str(err))

    def _process_card_page_response(self, card_page_uri, list_identifier):
        return [PCard(card_response) for card_response in self._get_response_json(card_page_uri)[list_identifier]]

    def _process_card_page_response_with_headers(self, card_page_uri, list_identifier, headers):
        return [PCard(card_response) for card_response in
                self._get_response_json_with_headers(card_page_uri, headers)[list_identifier]]

    def update_new_from_mtgio(self, verbose=True, workers=8):
        """Downloads only the new set data along with the sets' cards from magicthegathering.io and leaves everything
        else intact. This is a a bit faster than a full update.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())
        current_cards = self.root.mtgio_cards
        current_sets = self.root.mtgio_sets
        current_set_codes = [pset.code for pset in current_sets]

        new_sets = PSetList()
        new_cards = PCardList()

        if verbose:
            print('Attempting to only fetch new data.')
            print('querying magicthegathering.io API...')

        url = 'https://api.magicthegathering.io/v1/sets/'
        headers = {'User-Agent': 'Mozilla/5.0'}

        set_response_dicts = self._get_response_json_with_headers(url, headers)['sets']
        for set_response_dict in set_response_dicts:
            if set_response_dict.get('code') not in current_set_codes:
                new_sets.append(PSet(set_response_dict))

        if len(new_sets) == 0:
            if verbose:
                print("No new sets found. Exiting")
            return

        tot_new_cards = 0
        cards_uri = 'https://api.magicthegathering.io/v1/cards?set={}'.format(new_sets[0].code)
        for pset in new_sets[1:]:
            cards_uri += '|' + pset.code

        try:
            req = Request(cards_uri, headers=headers)
            with urlopen(req, timeout=30) as conn:
                tot_new_cards = int(conn.info().get('Total-Count'))
        except URLError as err:
            print('Something went wrong with requesting url {}: '.format(url) + str(err))
            return

        pages = int(math.ceil(tot_new_cards / 100))
        cards_uri += '&page={}'
        card_page_uris = [cards_uri.format(page) for page in range(1, pages + 1)]

        tot_requests = len(card_page_uris)
        tot_new_sets = len(new_sets)

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards.')
            print('-----------------------------------------------------------------------------------------------')

        async def process_cards():
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                p_loop = asyncio.get_event_loop()

                calls = []
                for uri in card_page_uris:
                    if verbose:
                        sys.stdout.write('\rSending requests: [{} / {}]'.format(len(calls), tot_requests))
                    calls.append(p_loop.run_in_executor(executor,
                                                        self._process_card_page_response_with_headers,
                                                        uri,
                                                        'cards',
                                                        headers))
                    await asyncio.sleep(0.2)

                for future in asyncio.as_completed(calls):
                    cards = await future
                    new_cards.extend(cards)

                    for card in cards:
                        new_sets.where_exactly(code=card.set)[0].append(card)

                    if verbose:
                        gather_update_str = '\rGathering responses and processing cards: [{} / {}]'
                        sys.stdout.write(gather_update_str.format(len(new_cards), tot_new_cards))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_cards())
        loop.close()

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        current_sets.extend(new_sets)
        current_cards.extend(new_cards)
        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe magicthegathering.io database is now up to date!\nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def full_update_from_mtgio(self, verbose=True, workers=8):
        """Completely updates the database from magicthegathering.io downloading new sets and cards and also
        updating the current objects if there are any changes.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())
        current_cards = self.root.mtgio_cards
        current_sets = self.root.mtgio_sets
        current_card_index = current_cards.create_id_index()
        current_set_codes = [pset.code for pset in current_sets]

        if verbose:
            print('Attempting to update the current database objects and fetch new data.')
            print('querying magicthegathering.io API...')

        url = 'https://api.magicthegathering.io/v1/sets/'
        headers = {'User-Agent': 'Mozilla/5.0'}

        set_response_dicts = self._get_response_json_with_headers(url, headers)['sets']
        tot_new_sets = 0
        for set_response_dict in set_response_dicts:
            if set_response_dict['code'] in current_set_codes:
                current_sets.where_exactly(code=set_response_dict['code'])[0].update(set_response_dict)
            else:
                current_sets.append(PSet(set_response_dict))
                tot_new_sets += 1

        tot_cards = 0
        try:
            req = Request('https://api.magicthegathering.io/v1/cards', headers=headers)
            with urlopen(req, timeout=30) as conn:
                tot_cards = int(conn.info().get('Total-Count'))
        except URLError as err:
            print('Something went wrong with requesting url {}: '.format(url) + str(err))
            return

        pages = int(math.ceil(tot_cards / 100))
        base_uri = 'https://api.magicthegathering.io/v1/cards?page={}'
        card_page_uris = [base_uri.format(page) for page in range(1, pages + 1)]

        tot_new_cards = tot_cards - len(current_cards)
        tot_requests = len(card_page_uris)

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards and updating old.')
            print('-----------------------------------------------------------------------------------------------')

        async def process_cards():
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                p_loop = asyncio.get_event_loop()

                calls = []
                for uri in card_page_uris:
                    if verbose:
                        sys.stdout.write('\rSending requests: [{} / {}]'.format(len(calls), tot_requests))
                    calls.append(p_loop.run_in_executor(executor,
                                                        self._process_card_page_response_with_headers,
                                                        uri,
                                                        'cards',
                                                        headers))
                    await asyncio.sleep(0.2)

                processed = 0
                for future in asyncio.as_completed(calls):
                    cards = await future
                    processed += len(cards)

                    for card in cards:
                        if card.id not in current_card_index:
                            current_sets.where_exactly(code=card.set)[0].append(card)
                            current_cards.append(card)
                        else:
                            current_card_index[card.id].update(card.__dict__)

                    if verbose:
                        gather_update_str = '\rGathering responses and processing cards: [{} / {}]'
                        sys.stdout.write(gather_update_str.format(processed, tot_cards))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_cards())
        loop.close()

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe magicthegathering.io database is now up to date!\nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def update_new_from_scryfall(self, verbose=True, workers=8):
        """Downloads only the new set data along with the sets' cards from Scryfall and leaves everything
        else intact. This is a a bit faster than a full update.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())
        current_sets = self.root.scryfall_sets
        current_cards = self.root.scryfall_cards
        current_set_codes = [pset.code for pset in current_sets]

        new_sets = PSetList()
        new_cards = PCardList()

        if verbose:
            print('Attempting to only fetch new data.')
            print('querying Scryfall API...')

        set_response_dicts = self._get_response_json('https://api.scryfall.com/sets')['data']

        for set_response_dict in set_response_dicts:
            if set_response_dict.get('code') not in current_set_codes:
                new_sets.append(PSet(set_response_dict))

        card_page_uris = []
        base_uri = 'https://api.scryfall.com/cards/search?include_extras=true&order=set&page={}&q=e%3A{' \
                   '}&unique=prints '

        for pset in new_sets:
            card_page_uris.extend([base_uri.format(page, pset.code) for page in
                                   range(1, int(math.ceil(pset.card_count / 175)) + 1)])

        tot_new_sets = len(new_sets)
        tot_new_cards = sum([pset.card_count for pset in new_sets])
        tot_requests = len(card_page_uris)

        if len(new_sets) == 0:
            if verbose:
                print("No new sets found. Exiting")
            return

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards.')
            print('-----------------------------------------------------------------------------------------------')

        async def process_scryfall_cards():
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                p_loop = asyncio.get_event_loop()

                calls = []
                for uri in card_page_uris:
                    if verbose:
                        sys.stdout.write('\rSending requests: [{} / {}]'.format(len(calls), tot_requests))
                    calls.append(p_loop.run_in_executor(executor, self._process_card_page_response, uri, 'data'))
                    await asyncio.sleep(0.11)

                for future in asyncio.as_completed(calls):
                    cards = await future
                    new_cards.extend(cards)
                    new_sets.where_exactly(code=cards[0].set)[0].extend(cards)

                    if verbose:
                        gather_update_str = '\rGathering responses and processing cards: [{} / {}]'
                        sys.stdout.write(gather_update_str.format(len(new_cards), tot_new_cards))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_scryfall_cards())
        loop.close()

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        current_sets.extend(new_sets)
        current_cards.extend(new_cards)
        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe Scryfall database is now up to date!\nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

    def full_update_from_scryfall(self, verbose=True, workers=8):
        """Completely updates the database from magicthegathering.io downloading new sets and cards and also
        updating the current objects if there are any changes.

        Args:
            verbose (bool): If enabled, prints out progression messages during the updating process.
            workers (int): Maximum numbers fo threads for the updating.
        """
        start = round(time.time())

        current_sets = self.root.scryfall_sets
        current_cards = self.root.scryfall_cards
        current_card_index = current_cards.create_id_index()
        current_set_codes = [pset.code for pset in current_sets]

        print('Attempting to update the current database objects and fetch new data.')
        print('querying Scryfall API...')

        set_response_dicts = self._get_response_json('https://api.scryfall.com/sets')['data']
        tot_new_sets = 0
        for set_response_dict in set_response_dicts:
            if set_response_dict['code'] in current_set_codes:
                current_sets.where_exactly(code=set_response_dict['code'])[0].update(set_response_dict)
            else:
                current_sets.append(PSet(set_response_dict))
                tot_new_sets += 1

        card_page_uris = []
        base_uri = 'https://api.scryfall.com/cards/search?include_extras=true&order=set&page={}&q=e%3A{' \
                   '}&unique=prints '

        for pset in current_sets:
            card_page_uris.extend([base_uri.format(page, pset.code) for page in
                                   range(1, int(math.ceil(pset.card_count / 175)) + 1)])

        tot_new_cards = sum([pset.card_count for pset in current_sets]) - len(current_cards)
        tot_cards = tot_new_cards + len(current_cards)
        tot_requests = len(card_page_uris)

        if verbose:
            print('Found a total of {} new sets and {} new cards'.format(tot_new_sets, tot_new_cards))
            print('Fetching new cards and updating old.')
            print('-----------------------------------------------------------------------------------------------')

        async def process_scryfall_cards():
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                p_loop = asyncio.get_event_loop()

                calls = []
                for uri in card_page_uris:
                    if verbose:
                        sys.stdout.write('\rSending requests: [{} / {}]'.format(len(calls), tot_requests))
                    calls.append(p_loop.run_in_executor(executor, self._process_card_page_response, uri, 'data'))
                    await asyncio.sleep(0.11)

                processed = 0
                for future in asyncio.as_completed(calls):
                    cards = await future
                    pset = current_sets.where_exactly(code=cards[0].set)[0]
                    processed += len(cards)

                    for card in cards:
                        if card.id not in current_card_index:
                            pset.append(card)
                            current_cards.append(card)
                        else:
                            current_card_index[card.id].update(card.__dict__)

                    if verbose:
                        gather_update_str = '\rGathering responses and processing cards: [{} / {}]'
                        sys.stdout.write(gather_update_str.format(processed, tot_cards))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_scryfall_cards())
        loop.close()

        if verbose:
            sys.stdout.write('\rSaving and committing...')

        transaction.commit()
        self.database.pack()

        if verbose:
            update_str = '\rThe Scryfall database is now up to date!\nElapsed time: {}'
            sys.stdout.write(update_str.format(datetime.timedelta(seconds=round(time.time()) - start)))

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


