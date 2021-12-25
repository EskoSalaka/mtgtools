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
import json
import os
import random
import re
import warnings
import uuid
import pathlib

from textwrap import dedent
from itertools import groupby
from persistent.list import PersistentList
from persistent import Persistent
from mtgtools.PCard import PCard
from BTrees.OOBTree import BTree


class PCardList(Persistent):
    """PCardList is a persistent card list object that mostly acts just like a normal Python list for PCard objects.
    These lists can be saved in the database just like any other persistent objects. It can optionally be initialized
    with another list of PCard objects and a name. Additionally, it will also have an attribute 'creation_date' and
    a unique uuid attribute 'id'. PCardLists are considered equal if they have the same 'id'.

    Except for the usual list methods like 'extend' and 'append', the PCardList is functional in style, meaning that
    calling any of the other filtering or querying methods return new PCardList objects leaving the original untouched.

    PCardList can also be used as a deck by adding cards to it's 'sideboard' attribute. Having cards in the 'sideboard'
    changes some functionalities of the methods like 'deck_str' in which now also the sideboard cards are added. Images
    are downloaded and proxies created for both the cards and the sideboard. However, Having  cards in the 'sideaboard'
    does not change the behaviour of the crucial internal methods like __len__, __getitem__ or __setitem__,
    so basically the cards in the 'sideboard' are a kind of an extra.

    args:
        cards (PCardList, PersistentList[PCard], list[PCard], tuple[PCard]): Initial cards of the card list.
        sideboard (PCardList, PersistentList[PCard], list[PCard], tuple[PCard]): Initial cards of the sideboard of the
            card list in case it is supposed to act like a deck.
        name (str): Name of the card list
    """

    def __init__(self, cards=None, sideboard=None, name=''):
        if isinstance(cards, PCardList):
            self._cards = PersistentList(cards.cards)
        elif isinstance(cards, (list, PersistentList, tuple)):
            self._cards = PersistentList(cards)
        elif not cards:
            self._cards = PersistentList()
        else:
            raise TypeError

        if isinstance(sideboard, PCardList):
            self._sideboard = PersistentList(cards.cards)
        elif isinstance(sideboard, (list, PersistentList, tuple)):
            self._sideboard = PersistentList(cards)
        elif not sideboard:
            self._sideboard = PersistentList()
        else:
            raise TypeError

        self.name = name
        self.creation_date = datetime.datetime.now()
        self.id = uuid.uuid4()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._cards.__getitem__(item)
        else:
            return PCardList(self.cards.__getitem__(item))

    def __setitem__(self, key, val):
        self._cards.__setitem__(key, val)

    def __iter__(self):
        return iter(self._cards)

    def __str__(self):
        return str(self._cards)

    def __repr__(self):
        return repr(self._cards)

    def __contains__(self, card):
        return self._cards.__contains__(card)

    def __eq__(self, other):
        if isinstance(other, PCardList):
            return self.id == other.id

    def __add__(self, other):
        if isinstance(other, PCardList):
            return PCardList(self.cards + other.cards)
        elif isinstance(other, (list, PersistentList, tuple)):
            return PCardList(self.cards + other)
        elif isinstance(other, PCard):
            new_cards = PersistentList(self.cards)
            new_cards.append(other)
            return PCardList(new_cards)
        else:
            raise TypeError

    def __radd__(self, other):
        if isinstance(other, PCardList):
            return PCardList(self.cards + other.cards)
        elif isinstance(other, (list, PersistentList, tuple)):
            return PCardList(self.cards + other)
        elif isinstance(other, PCard):
            new_cards = PersistentList(self.cards)
            new_cards.append(other)
            return PCardList(new_cards)
        else:
            raise TypeError

    def __iadd__(self, other):
        if isinstance(other, PCardList):
            return PCardList(self.cards + other.cards)
        elif isinstance(other, (list, PersistentList, tuple)):
            return PCardList(self.cards + other)
        elif isinstance(other, PCard):
            new_cards = PersistentList(self.cards)
            new_cards.append(other)
            return PCardList(new_cards)
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, PCardList):
            return PCardList([card for card in self.cards if card not in other.cards])
        elif isinstance(other, (list, PersistentList, tuple)):
            return PCardList([card for card in self.cards if card not in other])
        elif isinstance(other, PCard):
            return PCardList([card for card in self.cards if card is not other])
        else:
            raise TypeError

    def __mul__(self, num):
        plist = PCardList()

        for card in self.cards:
            for _ in range(num):
                plist.append(card)

        return plist

    def __rmul__(self, num):
        plist = PCardList()

        for card in self.cards:
            for _ in range(num):
                plist.append(card)

        return plist

    def __len__(self):
        return len(self.cards)

    def append(self, card):
        """Adds a card object to the end of the list in-place.

        Args:
            card (PCard): The card object to be appended
        """
        self._cards.append(card)

    def insert(self, index, card):
        """Inserts a card object to a given index in this list in-place

        Args:
            card (PCard): The card object to be inserted in the given index.
            index (int): The index to insert the given card object.
        """
        self._cards.insert(index, card)

    def index(self, card):
        """Returns the index where the given card object is located in the list.

        Args:
            card (PCard): The card object to be searched.
        """
        self._cards.index(card)

    def clear(self):
        """Clears te cards in this list."""
        self._cards.clear()

    def extend(self, cards):
        """Extends the list with a list of card objects in-place.

        Args:
            cards (PCardList, list, tuple, PersistentList): A PCardList, PersistentList, list or a tuple of
                card objects to extend this list with.
        """
        if isinstance(cards, PCardList):
            self._cards.extend(cards.cards)
        elif isinstance(cards, (list, PersistentList, tuple)):
            self._cards.extend(cards)

    def remove(self, card):
        """Removes a given card object from this list in-place.

        Args:
            card (PCard): A card object to remove from this list.
        """
        self._cards.remove(card)

    def pop(self, index):
        """Removes a card object from a given index from this list in-place.

        Args:
            index (int): An index to remove a card object from.
        """
        self._cards.pop(index)

    def count(self, card):
        """Returns the number of given card objects in this list. Cards are considered same if they have the same id.

        Args:
            card (PCard): A card object to count.

        Returns:
            int: The number of given card objects in this list
        """
        return self._cards.count(card)

    def sort(self, func):
        """Sorts the cards of this list with a given function in-place. The given function should return some
        attribute of a card object by which this list is sorted.

        Args:
            func: A function to sort this list with.
        """
        self._cards.sort(key=func)

    def filter(self, func):
        """Filters the cards of this list with a given function in-place. The new list contains all the cards
        for which the given function returns True.

        Args:
            func: A function to filter with.
        """
        self._cards.filter(key=func)

    def sorted(self, func):
        """Returns a new instance of this the list sorted with a given function. The given function should return some
        attribute of a card object by which this list is sorted.

        Args:
            func: A function to sort this list with.

        Returns:
            PCardList: A new instance of this list sorted.

        """
        return PCardList(sorted(self._cards, key=func))

    def filtered(self, func):
        """Returns a new instance of this the list filtered with a given function. The new list contains all the cards
        for which the given function returns True.

        Args:
            func: A function to filter with.

        Returns:
            PCardList: A new instance of this list filtered.

        """
        return PCardList(list(filter(func, self._cards)))

    def where(self, invert=False, search_all_faces=False, **kwargs):
        """Returns a new list of cards for which any of the given keyword arguments match partly or completely with the
        attributes of the cards in this list. The arguments should be any card attribute names such as 'power',
        'toughness' and 'name'. String attributes are case insensitive and it is enough that the argument is a
        substring. For list arguments the order does not matter and it is enough for one of the elements to match.

        Scryfall card objects contain the 'card_faces' attribute which holds data of the possible flipsides or backsides
        of certain cards like 'Akki Lavarunner // Tok-Tok, Volcano Born'. By default, if the card has different faces
        only the first face (the 'playing' face) is searched. If 'search_all_faces' is enabled
        all the faces are searched and any of their attributes must match partly like for normal attributes.

        The search can also be inverted by setting invert=True so that all the cards NOT matching will be returned.

        Note that searching for Null arguments is not supported.

        Args:
            search_all_faces (bool): (only for Scryfall cards) If True, searches all the cards faces of this lists'
                cards instead of the first one
            invert: If True, a list of cards NOT matching the arguments is returned
            **kwargs: Arguments to match with the attributes of this list's cards.

        Returns:
            bool: A new list of cards for which the given keyword arguments match partly or completely.
        """
        del_keys = []

        for (key, val) in kwargs.items():
            if val is None:
                msg = 'Ignoring an empty or null value for keyword {}. Null or empty values are not supported.'
                warnings.warn(msg.format(key))
                del_keys.append(key)
            elif len(self.cards) == 0:
                msg = 'Searching an empty list.'
                warnings.warn(msg)
            elif not hasattr(self.cards[0], key):
                msg = 'Ignoring an unrecognized keyword {}. Make sure you are using correct api type and spelling.'
                warnings.warn(msg.format(key))
                del_keys.append(key)
            elif key == 'card_faces':
                msg = 'Ignoring keyword "card_faces". Searching by this keyword is not supported'
                warnings.warn(msg)
                del_keys.append(key)

        for key in del_keys:
            del kwargs[key]

        if not invert:
            return PCardList([card for card in self if card.matches_any(search_all_faces, **kwargs)])
        else:
            return PCardList([card for card in self if not card.matches_any(search_all_faces, **kwargs)])

    def where_exactly(self, invert=False, search_all_faces=False, **kwargs):
        """Returns a new list of cards for which the given keyword arguments match completely with the attributes
        of the cards in this list. The arguments should be any card attribute names such as 'power',  'toughness' and
        'name'. String attributes are case insensitive and must match exactly. For list arguments the order does not
        matter and and each element must match exactly.

        Scryfall card objects contain the 'card_faces' attribute which holds data of the possible flipsides or backsides
        of certain cards like 'Akki Lavarunner // Tok-Tok, Volcano Born'. By default, if the card has different faces
        AND if he searched attribute has a null or an empty value, the first face(the 'playing' face) is matched
        instead. If 'search_all_faces' is enabled all the faces are matched and it is enough for one of them to match
        completely the way described above.

        The search can also be inverted by setting invert=True so that all the cards NOT matching will be returned.

        Note that searching for Null arguments is not supported.

        Args:
            search_all_faces (bool): (only for Scryfall cards) If True, searches all the cards faces of this lists'
                cards instead of the first one
            invert: If True, a list of cards NOT matching the arguments is returned
            **kwargs: Arguments to match with the attributes of this list's cards.

        Returns:
            bool: A new list of cards for which the given keyword arguments match completely.
        """
        del_keys = []

        for (key, val) in kwargs.items():
            if val is None:
                msg = 'Ignoring an empty or null value for keyword {}. Null or empty values are not supported.'
                warnings.warn(msg.format(key))
                del_keys.append(key)
            elif len(self.cards) == 0:
                msg = 'Searching an empty list.'
                warnings.warn(msg)
            elif not hasattr(self.cards[0], key):
                msg = 'Ignoring an unrecognized keyword {}. Make sure you are using correct api type and spelling.'
                warnings.warn(msg.format(key))
                del_keys.append(key)
            elif key == 'card_faces':
                msg = 'Ignoring keyword "card_faces". Searching with this keyword is not supported'
                warnings.warn(msg)
                del_keys.append(key)

        for key in del_keys:
            del kwargs[key]

        if not invert:
            return PCardList([card for card in self if card.matches_all(search_all_faces, **kwargs)])
        else:
            return PCardList([card for card in self if not card.matches_all(search_all_faces, **kwargs)])

    def has_all(self, cards):
        """Returns true if this list contains all the given cards.

        Args:
            cards (PCardlist, list, tuple, PersistentList): A list of card objects to check.

        Returns:
            bool: True if this list contains all the given card objects, False otherwise.
        """
        return all(card in self.cards for card in cards)

    def has_any(self, cards):
        """Returns true if this list contains any of the given cards.

        Args:
            cards (PCardlist, list, tuple, PersistentList): A list of card objects to check .

        Returns:
            bool: True if this list contains any of the given card objects, False otherwise.
        """
        return any(card in self.cards for card in cards)

    def random_sample(self, num, duplicates=False):
        """Returns a new list of cards with size 'num' which is a random sample from this list. If duplicates is enabled
        the sampling is done with with replacement.

        Args:
            num (int): The size of the random sample
            duplicates (bool): If True, duplicate values are allowed in the sample

        Returns:
            PCardList: A new list of cards randomly chosen from this list.
        """
        if duplicates:
            return PCardList([random.choice(self.cards) for _ in range(num)])
        else:
            try:
                return PCardList(random.sample(self.cards, num))
            except ValueError:
                return PCardList([random.choice(self.cards) for _ in range(num)])

    def random_card(self):
        """Returns a random card object from this list.

        Returns:
            PCard: A random card from this list.
        """
        return random.choice(self.cards)

    def random_pack(self, num_of_commons=11, num_of_uncommons=3, num_of_rares=1):
        """Returns a new list of cards representing a booster (or similar) pack drawn from this lists' cards. The
        number of commons, uncommons and rares (or mythics) the pack will contain can be adjusted and by default the
        pack will have 11, 3 and 1 respectively. On average 1/8 of the rares will be mythics if this card list
        contains any.

        Args:
            num_of_commons (int): The number of common cards to add in the pack.
            num_of_uncommons (int): The number of uncommon cards to add in the pack.
            num_of_rares(int): The number of rare or mythic cards to add in the pack.

        Returns:
            PCardList: A new list of cards corresponding a booster (or similar) pack
        """
        random_commons = self.where_exactly(rarity='common').random_sample(num_of_commons)
        random_uncommons = self.where_exactly(rarity='uncommon').random_sample(num_of_uncommons)
        random_rares = PCardList()

        if self.where_exactly(rarity='mythic rare'):
            for _ in range(num_of_rares):
                if random.randint(0, 7) == 0:
                    random_rares.extend(self.where_exactly(rarity='mythic rare').random_sample(1))
                else:
                    random_rares.extend(self.where_exactly(rarity='rare').random_sample(1))
        elif self.where_exactly(rarity='mythic'):
            for _ in range(num_of_rares):
                if random.randint(0, 7) == 0:
                    random_rares.extend(self.where(rarity='mythic').random_sample(1))
                else:
                    random_rares.extend(self.where(rarity='rare').random_sample(1))
        else:
            random_rares.extend(self.where(rarity='rare').random_sample(num_of_rares))

        return random_commons + random_uncommons + random_rares

    def normal_playable_cards(self):
        """Returns a new list of cards with all the special non-playable cards like emblems and tokens removed from
        this list. For magicthegathering.io api removes also cards which are backsides or flipsides of normal cards.

        Returns:
            PCardList: A new list of cards with all the special non-playable cards removed.
        """
        if self.api_type == 'scryfall':
            non_playable_layouts = ['vanguard', 'scheme', 'planar', 'emblem', 'token', 'double_faced_token']
            return self.filtered(lambda card: card.layout not in non_playable_layouts)
        else:
            non_playable_layouts = ['token', 'plane', 'scheme', 'phenomenon', 'vanguard', 'conspiracy']
            face_layouts = ['split', 'flip', 'double-faced', 'aftermath']

            return self.filtered(lambda card: card.layout not in face_layouts and self.name == self.names[0] or
                                 self.layout in non_playable_layouts)

    def unique_names(self):
        """Returns a new list of cards containing only singles of cards with unique names. In other words all the
        multiples of cards with the same names are removed leaving only single copies of cards in the new list.

        Returns:
            PCardList: A new list of cards containing only singles of cards with with unique names.
        """
        temp = set()
        return PCardList([card for card in self.cards if card.name not in temp and (temp.add(card.name) or True)])

    def unique_cards(self):
        """Returns a new list of cards containing only singles of each card object of this list. In other words all the
        multiples of the same card object are removed leaving only single copies of cards in the new list.

        Returns:
            PCardList: A new list of cards containing only singles cards.
        """
        return PCardList(list(set(self.cards)))

    def creatures(self):
        """Returns a new list which only contains the creatures of this list.

        Returns:
            PCardList: A new list of cards containing only the creature cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='creature')
        else:
            return self.where(type=['creature'])

    def artifacts(self):
        """Returns a new list which only contains the artifacts of this list.

        Returns:
            PCardList: A new list of cards containing only the artifact cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='artifact')
        else:
            return self.where(type=['artifact'])

    def instants(self):
        """Returns a new list which only contains the instants of this list.

        Returns:
            PCardList: A new list of cards containing only the instant cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='instant')
        else:
            return self.where(type=['instant'])

    def sorceries(self):
        """Returns a new list which only contains the sorceries of this list.

        Returns:
            PCardList: A new list of cards containing only the sorcery cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='sorcery')
        else:
            return self.where(type=['sorcery'])

    def planeswalkers(self):
        """Returns a new list which only contains the planeswalkers of this list.

        Returns:
            PCardList: A new list of cards containing only the planeswalker cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='planeswalker')
        else:
            return self.where(type=['planeswalker'])

    def enchantments(self):
        """Returns a new list which only contains the enchantments of this list.

        Returns:
            PCardList: A new list of cards containing only the enchantment cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='enchantment')
        else:
            return self.where(type=['enchantment'])

    def noncreatures(self):
        """Returns a new list which only contains the noncreatures of this list.

        Returns:
            PCardList: A new list of cards containing only the noncreature cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='creature', invert=True)
        else:
            return self.where(type=['creature'], invert=True)

    def lands(self):
        """Returns a new list which only contains the lands of this list.

        Returns:
            PCardList: A new list of cards containing only the land cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='land')
        else:
            return self.where(type='land')

    def basic_lands(self):
        """Returns a new list which only contains the basic lands of this list.

        Returns:
            PCardList: A new list of cards containing only the basic land cards.
        """
        if self.api_type == 'scryfall':
            return self.where(type_line='basic land')
        else:
            return self.where(type='basic land')

    def converted_mana_cost(self):
        """Returns the converted mana cost of the list.

        Returns:
            float: The converted mana cost of the list.

        """
        return sum(card.cmc for card in self.cards)

    def average_mana_cost(self):
        """Returns the average mana cost of the cards in this list.

        Returns:
            float: The average mana cost of the list.

        """
        if len(self.cards) == 0:
            return 0
        else:
            return sum(card.cmc for card in self.cards) / len(self.cards)

    def mana_symbol_counts(self):
        """Returns a dictionary containing the counts of all the manasymbols of the cards of this list.
        The dictionary is in the form:

        {'W': num, 'U': num, 'B': num, 'R': num, 'G': num}

        Returns:
            dict: a dictionary containing the counts of all the manasymbols this list.
        """
        count_dict = {'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}

        for card in self.cards:
            for mana in count_dict.keys():
                if card.mana_cost:
                    count_dict[mana] += card.mana_cost.count(mana)
                elif card.layout == 'transform' and card.card_faces[0].get('mana_cost'):
                    count_dict[mana] += card.card_faces[0].get('mana_cost').count(mana)

        return count_dict

    def grouped_by_converted_mana_cost(self):
        """Returns a dictionary containing the cards of this list grouped by their converted mana costs.
        The dictionary is in the form:

        {'0.0': cards with cmc 0, '1.0': cards with cmc 1, '2.0': cards with cmc 2, ...}

        The keys will only be in the dictionary if there are cards with the corresponding mana costs in this list.

        Returns:
            dict: A dictionary containing the cards grouped by their converted mana costs.
        """
        sorted_cards = self.sorted(lambda card: card.cmc)
        return dict((k, PCardList(list(v))) for k, v in groupby(sorted_cards, key=lambda card: card.cmc))

    def grouped_by_simple_type(self):
        """Returns a dictionary containing the cards of this list grouped by their types in a simple way.
        The dictionary is in the form:

        'creatures': creature cards,
        'lands': land cards,
        'noncreatures': noncreature cards

        Creatures that are both creatures and lands appear only in 'creatures'.

        Returns:
            dict: A dictionary containing the cards grouped by simple types.
        """
        creatures = self.creatures()
        lands = self.lands() - creatures
        noncreatures = self.noncreatures() - lands

        return {'creatures': creatures, 'lands': lands, 'noncreatures': noncreatures}

    def grouped_by_type(self):
        """Returns a dictionary containing the cards of this list grouped by their types.
        The dictionary is in the form:

        'creatures': creature cards
        'lands': land cards
        'instants': instant cards
        'sorceries': sorcery cards
        'enchantments': enchantment cards
        'artifacts': artifact cards
        'planeswalkers': planewalker cards


        Each card can only belong in one of these groups. Groupings are decided in the following priority:
        creatures > lands > enchantments > artifacts > the rest

        Returns:
            dict: A dictionary containing the cards grouped by simple types.
        """
        creatures = self.creatures()
        lands = self.lands() - creatures
        enchantments = self.enchantments() - creatures - lands
        artifacts = self.artifacts() - creatures - lands - enchantments
        instants = self.instants()
        sorceries = self.sorceries()
        planeswalkers = self.planeswalkers()

        return {'creatures': creatures, 'lands': lands, 'enchantments': enchantments, 'artifacts': artifacts,
                'instants': instants, 'sorceries': sorceries, 'planeswalkers': planeswalkers}

    def grouped_by_color_identity(self):
        """Returns a dictionary containing the cards of this list grouped by their color identities.
        The dictionary is in the form:

        {'': cards with no color identity, 'W': cards with white identity, 'RU': cards with blue and red identity, ...}
        The keys of the dictionary are always in alphabetical order, eg. 'GR' instead of 'RG'.

        Returns:
            dict: A dictionary containing cards grouped by their color identities.
        """
        sorted_cards = self.sorted(lambda card: card.color_identity)
        grouper = groupby(sorted_cards, key=lambda card: re.sub("[],'[ ]", "", str(sorted(card.color_identity))))

        return dict((k, PCardList(list(v))) for k, v in grouper)

    def grouped_by_color(self):
        """Returns a dictionary containing the cards of this list grouped by their colors.
        The dictionary is in the form:

        {'': colorless cards, 'W': white cards, 'RU': blue cards, ...}

        The keys of the dictionary are always in alphabetical order, eg. 'GR' instead of 'RG'.

        Returns:
            dict: A dictionary containing cards grouped by their colors.
        """
        def get_color(card):
            if card.colors:
                return re.sub("[],'[ ]", "", str(sorted(card.colors)))
            elif card.layout == 'transform' and card.card_faces[0].get('colors'):
                return re.sub("[],'[ ]", "", str(sorted(card.card_faces[0].get('colors'))))
            else:
                return ''

        grouper = groupby(self.sorted(get_color), key=get_color)

        return dict((k, PCardList(list(v))) for k, v in grouper)

    def grouped_by_id(self):
        """Returns a dictionary containing the cards of this list grouped by their unique id's.
        The dictionary is in the form:

        {'card_id': cards with that id, 'card_id': cards with that id, 'card_id': cards with that id, ...}

        Returns:
            dict: A dictionary containing cards grouped by their unique id's.
        """
        sorted_cards = self.sorted(lambda card: card.id)
        return dict((k, PCardList(list(v))) for k, v in groupby(sorted_cards, key=lambda card: card.id))

    def deck_str(self, group_by='type', add_set_codes=True):
        """Returns a string of the cards in this list in a readable deck form. Optionally the set code of the cards can
        be left out by setting 'add_set_codes' to False. If this card list has any cards in the sideboard, those will be
        added with the prefix 'SB:'.

        The string will be of the following format:
        --------------------------------------
        //This is a comment
        num Card Name [set_code] /n
        num Card Name [set_code] /n
        num Card Name [set_code] /n

        //Some other cards
        num Some Other Card Name [set_code] /n

        /Sideboard
        SB: num Some Sideboard Card Name [set_code] /n
        SB: num Some Sideboard Card Name [set_code] /n
        --------------------------------------

        eg.
        --------------------------------------
        //Creatures (8)
        1 Wild Mongrel [od]
        4 Aquamoeba [od]
        2 Werebear
        noose constrictor

        //Enchantments (1)
        rancor [ULG]

        //Sideboard (2)
        SB: 2 Werebear
        --------------------------------------

        The cards can be structured in multiple ways. The options are:

        'none': Just prints out every card without any comments and any grouping
        'color': Groups the cards by their colors. Eg. under 'Colorless', 'Multicolor', 'Red', 'Blue', ...
        'type': Groups the cards by their types. Eg. under 'Lands', 'Artifacts', 'Creatures', ...
        'cmc': Groups the cards by their converted casting costs. Eg. under '1', '2', '3', ...

        Args:
            group_by (str): How the cards are grouped in the string. Either 'none', 'color', 'type' or 'cmc'
            add_set_codes (bool): If enabled, also the set codes are added after the card names.
        Returns:
            str: A string of the cards of this list in a readable deck format.
        """
        deck = ''

        if group_by == 'type':
            for group_name, group_cards in self.grouped_by_type().items():
                if group_cards:
                    deck += '// {} ({})\n'.format(group_name.capitalize(), len(group_cards))

                    for cards in group_cards.grouped_by_id().values():
                        if add_set_codes:
                            deck += '{} {} [{}]\n'.format(len(cards), cards[0].name, cards[0].set)
                        else:
                            deck += '{} {}\n'.format(len(cards), cards[0].name)
                    deck += '\n'

        if group_by == 'cmc':
            for group_name, group_cards in self.grouped_by_converted_mana_cost().items():
                if group_cards:
                    deck += '// {} ({})\n'.format(str(int(group_name)), len(group_cards))

                    for cards in group_cards.grouped_by_id().values():
                        if add_set_codes:
                            deck += '{} {} [{}]\n'.format(len(cards), cards[0].name, cards[0].set)
                        else:
                            deck += '{} {}\n'.format(len(cards), cards[0].name)
                    deck += '\n'

        elif group_by == 'none':
            for cards in self.grouped_by_id().values():
                if add_set_codes:
                    deck += '{} {} [{}]\n'.format(len(cards), cards[0].name, cards[0].set)
                else:
                    deck += '{} {}\n'.format(len(cards), cards[0].name)
            deck += '\n'

        elif group_by == 'color':
            keymap = {'R': 'Red', 'G': 'Green', 'U': 'Blue', 'B': 'Black', 'W': 'White', '': 'Colorless'}
            r_groups = {'Multicolor': PCardList(), 'Colorless': PCardList(), 'Red': PCardList(),
                        'Blue': PCardList(), 'Black': PCardList(), 'White': PCardList(),  'Green': PCardList()}

            for key, val in self.grouped_by_color().items():
                if len(key) > 1:
                    r_groups['Multicolor'] += val
                else:
                    r_groups[keymap[key]] += val

            for group_name, group_cards in r_groups.items():
                if group_cards:
                    deck += '// {} ({})\n'.format(group_name.capitalize(), len(group_cards))

                    for cards in group_cards.grouped_by_id().values():
                        if add_set_codes:
                            deck += '{} {} [{}]\n'.format(len(cards), cards[0].name, cards[0].set)
                        else:
                            deck += '{} {}\n'.format(len(cards), cards[0].name)
                    deck += '\n'

        if self.sideboard:
            if group_by != 'none':
                deck += '// {} ({})\n'.format('Sideboard', len(self.sideboard))

            for cards in PCardList(self.sideboard).grouped_by_id().values():
                if add_set_codes:
                    deck += 'SB: {} {} [{}]\n'.format(len(cards), cards[0].name, cards[0].set)
                else:
                    deck += 'SB: {} {}\n'.format(len(cards), cards[0].name)
            deck += '\n'

        return deck

    def pprint(self):
        """Prints out the contents of this list in a nice readable way."""
        print(self.pretty_print_str())

    def pretty_print_str(self):
        """Returns a nice readable string of the contents of this list.

        Returns:
            str: a string of the contents of this list in a nice readable format.
        """

        if len(self) == 0:
            if self.name:
                return 'Empty card list "{}" created at {}\n'.format(self.name, str(self.creation_date))
            else:
                return 'Unnamed empty card list created at {}\n'.format(self.creation_date)

        pp_str = ''
        format_str = "{name:{w1}s}   {set:{w2}s}   {type:{w3}s}   {mana:{w4}s}   {rarity:{w5}s}\n"

        if self.name:
            pp_str += 'Card list "{}" created at {} with a total of {} cards\n'.format(self.name,
                                                                                       str(self.creation_date),
                                                                                       len(self))
        else:
            pp_str += 'Unnamed card list created at {} with a total of {} cards\n'.format(self.creation_date,
                                                                                          len(self))

        longest_name = max(len(card.name) for card in self.cards + self.sideboard) + 2
        longest_rarity = max(len(card.rarity) for card in self.cards + self.sideboard)
        longest_set = max(len(card.set) for card in self.cards + self.sideboard)

        longest_type_line = 0
        longest_mana_cost = 0

        for card in self.cards + self.sideboard:
            if self.api_type == 'scryfall':
                if card.type_line and len(card.type_line) > longest_type_line:
                    longest_type_line = len(card.type_line)

                if card.card_faces and card.card_faces[0].get('type_line'):
                    if len(card.card_faces[0].get('type_line')) > longest_type_line:
                        longest_type_line = len(card.card_faces[0].get('type_line'))

                if card.mana_cost and len(card.mana_cost) > longest_mana_cost:
                    longest_mana_cost = len(card.mana_cost)

                if card.card_faces and card.card_faces[0].get('mana_cost'):
                    if len(card.card_faces[0].get('mana_cost')) > longest_mana_cost:
                        longest_mana_cost = len(card.card_faces[0].get('mana_cost'))
            else:
                longest_type_line = max(len(card.type) for card in self.cards + self.sideboard)
                longest_mana_cost = max([len(card.mana_cost) for card in self.cards + self.sideboard
                                         if card.mana_cost], default=0)

        longest_type_line = 4 if longest_type_line < 4 else longest_type_line
        longest_mana_cost = 4 if longest_mana_cost < 4 else longest_mana_cost

        pp_str += '-' * (longest_name + longest_rarity + longest_type_line + longest_mana_cost + 17) + '\n'
        pp_str += format_str.format(name='Card', w1=longest_name,
                                    set='Set', w2=longest_set,
                                    type='Type', w3=longest_type_line,
                                    mana='Cost', w4=longest_mana_cost,
                                    rarity='Rarity', w5=longest_rarity)
        pp_str += '-' * (longest_name + longest_rarity + longest_type_line + longest_mana_cost + 17) + '\n'

        for cards in self.grouped_by_id().values():
            card = cards[0]
            num = len(cards)

            if self.api_type == 'scryfall':
                if card.card_faces and not card.type_line:
                    type_line = card.card_faces[0].get('type_line')
                else:
                    type_line = card.type_line

                if card.card_faces and not card.mana_cost:
                    mana_cost = card.card_faces[0].get('mana_cost')
                else:
                    mana_cost = card.mana_cost
            else:
                type_line = card.type
                mana_cost = card.mana_cost if card.mana_cost else ''

            pp_str += format_str.format(name=str(num) + ' ' + card.name, w1=longest_name,
                                        set=card.set, w2=longest_set,
                                        type=type_line.replace('—', '-'), w3=longest_type_line,
                                        mana=mana_cost, w4=longest_mana_cost,
                                        rarity=card.rarity, w5=longest_rarity)

        if self.sideboard:
            pp_str += '\nSideboard:\n'

            for cards in PCardList(self.sideboard).grouped_by_id().values():
                card = cards[0]
                num = len(cards)

                if self.api_type == 'scryfall':
                    if card.card_faces and not card.type_line:
                        type_line = card.card_faces[0].get('type_line')
                    else:
                        type_line = card.type_line

                    if card.card_faces and not card.mana_cost:
                        mana_cost = card.card_faces[0].get('mana_cost')
                    else:
                        mana_cost = card.mana_cost
                else:
                    type_line = card.type
                    mana_cost = card.mana_cost if card.mana_cost else ''

                pp_str += format_str.format(name=str(num) + ' ' + card.name, w1=longest_name,
                                            set=card.set, w2=4,
                                            type=type_line.replace('—', '-'), w3=longest_type_line,
                                            mana=mana_cost, w4=longest_mana_cost,
                                            rarity=card.rarity, w5=longest_rarity)

        return pp_str

    def download_images_from_scryfall(self, image_type='normal', dir_path=''):
        """Downloads all the of this list's cards from Scryfall to a given directory with path 'dir_path'. Scryfall
        hosts 6 types of image  files and by default 'normal' sized images are downloaded. More information at:
        https://scryfall.com/docs/api/images.

        If no path is specified the images are downloaded to the current working directory. If the given path is
        not found a new folder is created automatically. Paths should be specified in the format 
        'C:\\users\\Timmy\\...' and the image file names will be the card names, eq. 'Wild Mongrel.jpg'. Specifying 
        wrong kind of paths might lead to undefined behaviour or errors.

        Args:
            image_type (str): A type or size of image to download. Either 'png', 'border_crop', 'art_crop', 'small',
            'normal' or 'large'.
            dir_path (str): The path to the directory to download the images to.
        """
        if self.api_type != 'scryfall':
            raise TypeError('Images can only be only downloaded for card objects from Scryfall api.')

        for card in self.cards + self.sideboard:
            card.download_image_from_scryfall(image_type=image_type, dir_path=dir_path)

    def create_proxies(self, scaling_factor=1.0, margins=(130, 130), cut_space=True,
                       quality=75, dir_path='', image_format='jpeg', file_names='proxies'):
        """Creates A4-sized printable jpeg-proxy sheets of the cards in this list. Each page will have 9 card proxies.

        At normal dpi the A4 sheets have size 2480 × 3508 and by default the card proxy images will have size 745 × 1040
        which is the standard mtg card size on A4. The card image sizes can be scaled with the 'scaling_factor' in a
        simple manner: (745 * scaling_factor) × (1040 * scaling_factor). On some systems or printers it is sometimes
        good to use slightly smaller or larger (eg. scaling_factor=0.97) images for better results.

        If 'cut_space' is enabled the card proxy images on the sheet will have a 1 pixel space between them.

        The margins from the top-left corner of the sheets can be adjusted with 'margings' which is a 2-tuple
        (x-margin, y-margin). On some systems or printers it is sometimes good to use small margins. By default they
        are (130, 130) pixels.

        The 'quality' value is an integer between 1(worst) - 95(best). Values above 95 should be avoided. Using a large
        quality value will result in bigger image files and better quality which is often not needed.

        The image format of the sheets can be specified with 'image_format' which can be anything supported by PIL. 
        By default it is set to 'jpeg'.

        If no path is specified, the image is downloaded to the current working directory. If the given
        path is not found, a new folder is created automatically. Paths should be specified in the format
        'C:\\users\\Timmy\\some_folder\\' or 'C:/users/Timmy/some_folder/' The names for the proxy sheets 
        can be specified with 'file_names' which will name the sheets 'name1', 'name2', 'name3', etc.

        Note that the Pillow-image library is needed for creating printable proxies.

        Args:
            scaling_factor (float): A factor to scale the standard mtg card image size.
            margins (2-tuple[int]): Margins from the top-left corner of the sheets in the format (x-margin, y-margin).
            cut_space (bool): If enabled the card proxy images on the sheet will have a 1 pixel space between them.
            quality (int): Integer value between 1(worst) - 95(best). Values above 95 should be avoided.
            dir_path (str): Path to the directory to save the proxy sheet images to.
            image_format (str): An image format supported by PIL. Eg. 'jpeg' or 'png'.
            file_names (str): Names of the proxy sheet image files. Eg. 'name1', 'name2', 'name3', etc.
        """
        try:
            from PIL import Image
        except ImportError:
            print('The Pillow-image library is needed for creating printable proxies. Make sure you have it installed!')
            return
        
        path = pathlib.Path(dir_path)

        try:
            path.mkdir(exist_ok=True)
        except FileExistsError:
            print(
                'The given path {} already exists and it is not a folder.'.format(str(path)))

        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        page = Image.new('RGB', (2480, 3508), (255, 255, 255, 0))
        x, y = margins

        pages = 1
        for card in self.cards + self.sideboard:
            images = card.proxy_images(scaling_factor=scaling_factor)

            for image in images:
                image_width, image_height = image.size
                page.paste(image, (x, y))
                x = x + image_width + 1 if cut_space else x + image_width

                if x > 3 * image_width:
                    x = margins[0]
                    y = y + image_height + 1 if cut_space else y + image_height

                    if y > 3 * image_height:
                        y = margins[1]
                        page.save(fp=path / (file_names + str(pages) + '.' + image_format),
                                  format=image_format,
                                  quality=quality,
                                  dpi=(300, 300))
                        page = Image.new('RGB', (2480, 3508), 'white')
                        pages += 1

            page.save(fp=path / (file_names + str(pages) + '.' + image_format), 
                      format=image_format, 
                      quality=quality, 
                      dpi=(300, 300))

    def from_str(self, card_list_str, **kwargs):
        """Reads a given card list string and returns a new list of all the cards of this list found in the string.

        The string should be given in the following format:

        --------------------------------------
        //This is a comment
        num Card Name [set_code collector_number] /n
        num Card Name [set_code collector_number] /n
        num Card Name [set_code collector_number] /n

        //Some other cards
        num Some Other Card Name [set_code collector_number] /n

        /Sideboard
        SB: Some Sideboard Card Name [set_code collector_number] /n
        SB: Some Sideboard Card Name [set_code collector_number] /n
        --------------------------------------

        The number of cards 'num' and the set code '[set_code]' or '(set_code)' along with the collector number are
        optional. The collector number can only be specified after a valid set code. Card names and set codes
        are case-insensitive. Each card or cards must be on its own line and comments can only start in the beginning
        of lines. Cards found on lines starting with the prefix 'SB:' are added in the sideboard of the list.

        Lines from which no cards are found are ignored and if no card with the given set is found, a random card
        with the same name is returned.

        Additionally, you can include any card-specific keyword arguments such as lang='en' which will only return
        those matching cards.

        eg.
        --------------------------------------
        //Creatures (8)
        1 Wild Mongrel [od]
        4 Aquamoeba [od]
        2 Werebear
        noose constrictor

        //Enchantments (1)
        rancor [ULG]

        //Sideboard (2)
        SB: 2 Werebear
        --------------------------------------

        Args:
            card_list_str (str): A string representing a list of cards.
            **kwargs: Arguments to match with the attributes of every card in the list (see the documentation of where).

        Returns:
            PCardList: A new card list from the given card list string which belong in this card list.
        """

        card_list = PCardList()
        set_codes = {card.set for card in self.cards}

        for line in (_.strip() for _ in card_list_str.splitlines()):
            sb = False

            if line and line[0:2] != '//':
                if line[0:3] == 'SB:':
                    sb = True
                    line = line[3:]

                num = int(line.split()[0]) if line.split()[0].isdigit() else 1

                name = line.split(maxsplit=1)[1] if line.split()[0].isdigit() else line
                name = name.split('[')[0] if '[' in name and ']' in name else name
                name = name.strip()

                if "(" in line and ")" in line:
                    cl = line[line.find('(') + 1:line.find(')')].strip()
                    set_code = cl.split()[0] if len(cl.split()) > 0 else None
                    collector_number = cl.split()[1] if len(cl.split()) > 1 else None
                elif "[" in line and "]" in line:
                    cl = line[line.find('[') + 1:line.find(']')].strip()
                    set_code = cl.split()[0] if len(cl.split()) > 0 else None
                    collector_number = cl.split()[1] if len(cl.split()) > 1 else None
                else:
                    set_code = None

                if set_code and set_code not in set_codes:
                    msg = 'Could not find any matching {} API set code for the line --{}--'
                    warnings.warn(msg.format(self.api_type, line))
                    set_code = None

                try:
                    if set_code:
                        if collector_number:
                            card = self.where_exactly(name=name,
                                                      set=set_code,
                                                      search_all_faces=True,
                                                      collector_number=collector_number,
                                                      **kwargs)[0]
                        else:
                            card = self.where_exactly(name=name, set=set_code, search_all_faces=True, **kwargs)[0]
                    else:
                        card = self.where_exactly(name=name, search_all_faces=True, **kwargs).random_card()

                    if sb:
                        card_list.sideboard.extend([card for _ in range(num)])
                    else:
                        card_list.extend(num * (PCardList() + card))

                except IndexError:
                    msg = """
                    Could not find any cards matching the line --{}-- with given keyword arguments --{}--.
                    This could possibly be because of a typo, the card doesn't exist in the given set or 
                    because there are no cards matching the given keyword arguments or collector number if any were specified
                    """
                    warnings.warn(dedent(msg.format(line, list(kwargs.items()))))

        return card_list

    def from_file(self, file_path, **kwargs):
        """Reads a card list string from a given text file and returns a new list of all the cards of this list
        found in the file.

        The text file should be given in the following format:

        --------------------------------------
        //This is a comment
        num Card Name [set_code collector_number] /n
        num Card Name [set_code collector_number] /n
        num Card Name [set_code collector_number] /n

        //Some other cards
        num Some Other Card Name [set_code collector_number] /n

        /Sideboard
        SB: Some Sideboard Card Name [set_code collector_number] /n
        SB: Some Sideboard Card Name [set_code collector_number] /n
        --------------------------------------

        The number of cards 'num' and the set code '[set_code]' or '(set_code)' along with the collector number are
        optional. The collector number can only be specified after a valid set code. Card names and set codes
        are case-insensitive. Each card or cards must be on its own line and comments can only start in the beginning
        of lines. Cards found on lines starting with the prefix 'SB:' are added in the sideboard of the list.

        Lines from which no cards are found are ignored and if no card with the given set is found, a random card
        with the same name is returned.

        Additionally, you can include any card-specific keyword arguments such as lang='en' which will only return
        those matching cards.

        eg.
        --------------------------------------
        //Creatures (8)
        1 Wild Mongrel [od]
        4 Aquamoeba [od]
        2 Werebear
        noose constrictor

        //Enchantments (1)
        rancor [ULG]

        //Sideboard (2)
        SB: 2 Werebear
        --------------------------------------

        Args:
            file_path (str): A path to the file containing a list of cards to read.
            **kwargs: Arguments to match with the attributes of every card in the list (see the documentation of where).

        Returns:
            PCardList: A card list from the given string.
        """

        try:
            with open(file_path, 'r') as f:
                return self.from_str(f.read(), **kwargs)

        except (IOError, FileNotFoundError):
            print('Something went wrong with reading file {}'.format(file_path))
            print('Check that the file exists in the given path and that it is a simple text file.')

    def to_file(self, file_path, group_by='type', add_set_codes=True):
        """Writes the cards in this list in a readable deck form in a file. The cards cannot be written in an existing
        file. The file path must be given in the format of "C:/Users/jhonny/Desktop/my_text_file.txt" where
        "my_text_file.txt" is the name of the file to be created. The function results in an error if the file already
        exists or the path is invalid, eg. a path to a folder.

        Optionally the set code of the cards can be left out by setting 'add_set_codes' to False. If this card
        list has any cards in the sideboard, those will be added with the prefix 'SB:'.

        The string will be of the following format:
        --------------------------------------
        //This is a comment
        num Card Name [set_code] /n
        num Card Name [set_code] /n
        num Card Name [set_code] /n

        //Some other cards
        num Some Other Card Name [set_code] /n

        /Sideboard
        SB: num Some Sideboard Card Name [set_code] /n
        SB: num Some Sideboard Card Name [set_code] /n
        --------------------------------------

        eg.
        --------------------------------------
        //Creatures (8)
        1 Wild Mongrel [od]
        4 Aquamoeba [od]
        2 Werebear
        noose constrictor

        //Enchantments (1)
        rancor [ULG]

        //Sideboard (2)
        SB: 2 Werebear
        --------------------------------------

        The cards can be structured in multiple ways. The options are:

        'none': Just prints out every card without any comments and any grouping
        'color': Groups the cards by their colors. Eg. under 'Colorless', 'Multicolor', 'Red', 'Blue', ...
        'type': Groups the cards by their types. Eg. under 'Lands', 'Artifacts', 'Creatures', ...
        'cmc': Groups the cards by their converted casting costs. Eg. under '1', '2', '3', ...

        Args:
            group_by (str): How the cards are grouped in the text file. Either 'none', 'color', 'type' or 'cmc'
            add_set_codes (bool): If enabled, also the set codes are added after the card names.
            file_path (str): The path to create the file to.
        """
        try:
            with open(file_path, 'x') as f:
                f.write(self.deck_str(group_by=group_by, add_set_codes=add_set_codes))

        except (FileExistsError, IOError) as err:
            print('Something went wrong with writing to the file: {}'.format(str(err)))

    def create_id_index(self):
        """Creates and returns a fast persistent index of the unique cards of this list as a BTree which works
        quite like a normal Python dict. Cards are indexed by their unique 'id' values and each id maps to a single
        card object, so it does not matter if the list contains multiples of same cards.

        Returns:

        """
        sorted_cards = self.sorted(lambda card: card.id)
        return BTree(dict((k, list(v)[0]) for k, v in groupby(sorted_cards, key=lambda card: card.id)))

    @property
    def api_type(self):
        try:
            return self.cards[0].api_type
        except IndexError:
            return 'unspecified'

    @property
    def json(self):
        return json.dumps({'cards': [card.__dict__ for card in self.cards]}, sort_keys=True, indent=4)

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        if isinstance(cards, PCardList):
            self._cards = PersistentList(cards.cards)
        elif isinstance(cards, (list, PersistentList, tuple)):
            self._cards = PersistentList(cards)
        elif not cards:
            self._cards = PersistentList()
        else:
            raise TypeError

    @property
    def sideboard(self):
        return self._sideboard

    @sideboard.setter
    def sideboard(self, sideboard):
        if isinstance(sideboard, PCardList):
            self._sideboard = PersistentList(sideboard.cards)
        elif isinstance(sideboard, (list, PersistentList, tuple)):
            self._sideboard = PersistentList(sideboard)
        elif not sideboard:
            self._sideboard = PersistentList()
        else:
            raise TypeError
