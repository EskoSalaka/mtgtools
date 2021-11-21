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
import json

from persistent import Persistent
from mtgtools.PCardList import PCardList


class PSet(PCardList, Persistent):
    """Pset is a simple Persistent dataclass representing Magic: The Gathering sets with their characteristic
    attributes. It is constructed simply with a json response dictionary from either magicthegathering.io or Scryfall
    API. Additionally, PSet inherits from PCardList so a list of PCard instances can initially be supplied.

    For easy querying of card objects from lists of cards, the PSet has two convenient methods to check for matching
    attributes.

    PSets have one of the following sets of attributes:

    For magicthegathering.io api (more at https://docs.magicthegathering.io/#api_v1sets_list):

        code:                  str
        name:                  str
        type:                  str
        border:                str
        mkm_id:                int
        mkm_name:              str
        release_date:          str
        gatherer_code:         str
        booster:               list[str]
        old_code:              str
        block:                 str
        online_only:           bool
        magic_cards_info_code: str

    for Scryfall (more at https://scryfall.com/docs/api/sets):

        code:                  str
        mtgo_code:             str
        name:                  str
        uri:                   str
        scryfall_uri:          str
        search_uri:            str
        released_at:           str
        set_type:              str
        card_count:            int
        digital:               bool
        foil_only:             bool
        block_code:            str
        block:                 str
        icon_svg_uri:          str
    """

    def __init__(self, response_dict, cards=None):
        super().__init__(cards=cards)

        if 'scryfall_uri' in response_dict:
            self.id = response_dict.get('id')
            self.code = response_dict.get('code')
            self.mtgo_code = response_dict.get('mtgo_code')
            self.tcgplayer_id = response_dict.get('tcgplayer_id')
            self.name = response_dict.get('name')
            self.uri = response_dict.get('uri')
            self.scryfall_uri = response_dict.get('scryfall_uri')
            self.search_uri = response_dict.get('search_uri')
            self.set_type = response_dict.get('set_type')
            self.printed_size = response_dict.get('printed_size')
            self.released_at = response_dict.get('released_at')
            self.block_code = response_dict.get('block_code')
            self.block = response_dict.get('block')
            self.parent_set_code = response_dict.get('parent_set_code')
            self.card_count = response_dict.get('card_count')
            self.digital = response_dict.get('digital')
            self.foil_only = response_dict.get('foil_only')
            self.nonfoil_only = response_dict.get('nonfoil_only')
            self.icon_svg_uri = response_dict.get('icon_svg_uri')

        else:
            self.code = response_dict.get('code')
            self.name = response_dict.get('name')
            self.type = response_dict.get('type')
            self.border = response_dict.get('border')
            self.mkm_id = response_dict.get('mkm_id')
            self.mkm_name = response_dict.get('mkm_name')
            self.release_date = response_dict.get('releaseDate')
            self.gatherer_code = response_dict.get('gathererCode')
            self.magic_cards_info_code = response_dict.get('magicCardsInfoCode')
            self.booster = response_dict.get('booster')
            self.old_code = response_dict.get('oldCode')
            self.block = response_dict.get('block')
            self.online_only = response_dict.get('onlineOnly')

    def __hash__(self):
        return hash(self.name + self.code)

    def __eq__(self, other):
        return self.code == other.code

    def __ne__(self, other):
        return not self == other

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        elif self.__lt__(other):
            return -1
        else:
            return 1

    def __str__(self):
        return self.name + '(' + self.code + ')'

    def __repr__(self):
        return self.name + '(' + self.code + ')'

    def update(self, response_dict):
        for key, value in response_dict.items():
            setattr(self, key, value)

    def matches_any(self, **kwargs):
        """Returns True if any of the given keyword arguments match partly or completely with this set's
        attributes. The arguments should be any of the set's attribute names such as 'card_count' and 'code' and 'name'.
        String attributes are case insensitive and it is enough that the argument is a substring. For list arguments
        the order does not matter and it is enough for one of the elements to match.

        Args:
            **kwargs: Arguments to match with the set's attributes.

        Returns:
            bool: True if any of the given keyword arguments match partly and False otherwise.

        Examples:
        """
        for (key, val) in kwargs.items():
            attr = getattr(self, key, None)

            if attr:
                if isinstance(attr, list):
                    if any(set(val).intersection(set(attr))):
                        return True
                elif isinstance(attr, str):
                    if val.lower() in attr.lower():
                        return True
                else:
                    if val == attr:
                        return True

        return False

    def matches_all(self, **kwargs):
        """Returns True if all of the given keyword arguments match completely with this set's attributes.
        The arguments should be any of the set's attribute names such as 'card_count' and 'code' and 'name'.
        String attributes are case insensitive and must match completely. For list arguments the order does not matter
        and all of the elements must match.

        Args:
            **kwargs: Arguments to match with the set's attributes.

        Returns:
            bool: True if all of the given keyword arguments match completely and False otherwise.
        """
        for (key, val) in kwargs.items():
            attr = getattr(self, key, None)

            if attr:
                if isinstance(attr, list):
                    if set(val) != set(attr):
                        return False
                elif isinstance(attr, str):
                    if val.lower() != attr.lower():
                        return False
                else:
                    if val != attr:
                        return False

                continue

        return True

    def download_images_from_scryfall(self, image_type='normal', dir_path=''):
        """Downloads all the of this set's images from Scryfall to a directory with given path 'dir_path. Scryfall hosts
        6 types of image files and by default 'normal' sized images are downloaded. More information at:
        https://scryfall.com/docs/api/images.

        If no path is given a new folder named with the set's code is created in the current working folder and images
        downloaded there. If a path is given, a new folder named with the set's code is created in the given path.
        Paths should be specified in the format 'C:\\users\\Timmy\\...' and the names of the image files name
        will be the card names, eq. 'Wild Mongrel.jpg'. Specifying wrong kind of paths might lead to
        undefined behaviour or errors.

        Args:
            image_type: A type or size of images to download. Either 'png', 'border_crop', 'art_crop', 'small', 'normal'
                or 'large'.
            dir_path: The path to download the images to.
        """

        if not dir_path:
            super().download_images_from_scryfall(image_type=image_type, dir_path=self.code + '\\')
        else:
            super().download_images_from_scryfall(image_type=image_type, dir_path=dir_path + self.code + '\\')

    @property
    def json(self):
        json_dict = dict(self.__dict__)
        json_dict['cards'] = [card.__dict__ for card in self.cards]

        return json.dumps(json_dict, sort_keys=True, indent=4)
