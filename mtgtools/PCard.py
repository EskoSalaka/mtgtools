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

import io
import json
import time
import urllib.request
import warnings
import pathlib
from urllib.error import URLError
from persistent import Persistent


class PCard(Persistent):
    """PCard is a simple persistent dataclass representing Magic: the Gathering cards with their characteristic
    attributes. It is constructed simply with a json response dictionary from either magicthegathering.io or Scryfall
    API.

    For easy querying of card objects from lists of cards, the PCard has two convenient methods to check for matching
    attributes.

    PCards have one of the following sets of attributes. In addition to these attributes, the cards have numerical
    versions of 'power', 'toughness' and 'loyalty' since these attributes are strings that might contain characters
    like '*' or 'X'. After stripping away these characters, the remaining numbers will be in the numerical version
    of the attribute. If nothing is left after stripping, the attribute will be 0.

    For magicthegathering.io api (more at https://docs.mtgio/#api_v1cards_list):

        name                    str
        layout                  str
        mana_cost               str
        cmc                     number
        colors                  list[str]
        color_identity          list[str]
        names                   list[str]
        type                    str
        supertypes              list[str]
        subtypes                list[str]
        types                   list[str]
        rarity                  str
        text                    str
        flavor                  str
        artist                  str
        number                  str
        power                   str
        toughness               str
        loyalty                 str
        multiverse_id           number
        variations              list[str]
        watermark               bool
        border                  str
        timeshifted             bool
        hand                    number
        life                    number
        release_date            str
        starter                 bool
        printings               list[str]
        original_text           str
        original_type           str
        source                  str
        image_url               str
        set                     str
        set_name                str
        id                      str
        legalities              list[dict]
        rulings                 list[dict]
        foreign_names           list[dict]

    For Scryfall (more at https://scryfall.com/docs/api/cards):

        id                      str
        name                    str
        layout                  str
        scryfall_uri            str
        cmc                     number
        type_line               str
        oracle_text             str
        mana_cost               str
        multiverse_ids          list[number]
        power                   str
        toughness               str
        loyalty                 str
        life_modifier           str
        hand_modifier           str
        colors                  list[str]
        color_indicator         list[str]
        color_identity          list[str]
        all_parts               list[dict]
        card_faces              list[dict]
        legalities              dict
        reserved                bool
        foil                    bool
        nonfoil                 bool
        oversized               bool
        edhrec_rank             number
        set                     str
        set_name                str
        collector_number        str
        highres_image           bool
        promo                   bool
        promo_types             list[string]
        printed_name            str
        printed_type_line       str
        printed_text            str
        reprint                 bool
        digital                 bool
        rarity                  str
        flavor_text             str
        artist                  str
        illustration_id         str
        frame                   str
        full_art                bool
        watermark               str
        border_color            str
        story_spotlight_number  number

        timeshifted             bool
        colorshifted            bool
        futureshifted           bool
        lang                    str

        set_search_uri          str
        scryfall_set_uri        str
        image_uris              list[dict]
        uri                     str
        story_spotlight_uri     str
        prices                  dict
        arena_id                str
        booster                 bool

        args:
            response_dict (str): A json response dictionary containing a set of attributes for the card object from.
                Tne response dict can be from either Scryfall of magicthegathering.io API.
    """
    def __init__(self, response_dict):
        if 'scryfall_uri' in response_dict:
            self.arena_id = response_dict.get('arena_id')
            self.id = response_dict.get('id')
            self.lang = response_dict.get('lang')
            self.mtgo_id = response_dict.get('mtgo_id')
            self.mtgo_foil_id = response_dict.get('mtgo_foil_id')
            self.multiverse_ids = response_dict.get('multiverse_ids')
            self.tcgplayer_id = response_dict.get('tcgplayer_id')
            self.tcgplayer_etched_id = response_dict.get('tcgplayer_etched_id')
            self.cardmarket_id = response_dict.get('cardmarket_id')
            self.oracle_id = response_dict.get('oracle_id')
            self.prints_search_uri = response_dict.get('prints_search_uri')
            self.rulings_uri = response_dict.get('rulings_uri')
            self.scryfall_uri = response_dict.get('scryfall_uri')
            self.uri = response_dict.get('uri')

            self.all_parts = response_dict.get('all_parts')
            self.card_faces = response_dict.get('card_faces')
            self.cmc = response_dict.get('cmc')
            self.color_identity = response_dict.get('color_identity')
            self.color_indicator = response_dict.get('color_indicator')
            self.colors = response_dict.get('colors')
            self.edhrec_rank = response_dict.get('edhrec_rank')
            self.hand_modifier = response_dict.get('hand_modifier')
            self.keywords = response_dict.get('keywords')
            self.layout = response_dict.get('layout')
            self.legalities = response_dict.get('legalities')
            self.life_modifier = response_dict.get('life_modifier')
            self.loyalty = response_dict.get('loyalty')
            self.mana_cost = response_dict.get('mana_cost')
            self.name = response_dict.get('name')
            self.oracle_text = response_dict.get('oracle_text')
            self.oversized = response_dict.get('oversized')
            self.power = response_dict.get('power')
            self.produced_mana = response_dict.get('produced_mana')
            self.reserved = response_dict.get('reserved')
            self.toughness = response_dict.get('toughness')
            self.type_line = response_dict.get('type_line')

            self.artist = response_dict.get('artist')
            self.booster = response_dict.get('booster')
            self.border_color = response_dict.get('border_color')
            self.card_back_id = response_dict.get('card_back_id')
            self.collector_number = response_dict.get('collector_number')
            self.content_warning = response_dict.get('content_warning')
            self.digital = response_dict.get('digital')
            self.finishes = response_dict.get('finishes')
            self.flavor_name = response_dict.get('flavor_name')
            self.flavor_text = response_dict.get('flavor_text')
            self.frame_effects = response_dict.get('frame_effects')
            self.frame = response_dict.get('frame')
            self.full_art = response_dict.get('full_art')
            self.games = response_dict.get('games')
            self.highres_image = response_dict.get('highres_image')
            self.illustration_id = response_dict.get('illustration_id')
            self.image_status = response_dict.get('image_status')
            self.image_uris = response_dict.get('image_uris')
            self.prices = response_dict.get('prices')
            self.printed_name = response_dict.get('printed_name')
            self.printed_text = response_dict.get('printed_text')
            self.printed_type_line = response_dict.get('printed_type_line')
            self.promo = response_dict.get('promo')
            self.promo_types = response_dict.get('promo_types')
            self.purchase_uris = response_dict.get('purchase_uris')
            self.rarity = response_dict.get('rarity')
            self.related_uris = response_dict.get('related_uris')
            self.released_at = response_dict.get('released_at')
            self.reprint = response_dict.get('reprint')
            self.scryfall_set_uri = response_dict.get('scryfall_set_uri')
            self.set_name = response_dict.get('set_name')
            self.set_search_uri = response_dict.get('set_search_uri')
            self.set_type = response_dict.get('set_type')
            self.set_uri = response_dict.get('set_uri')
            self.set = response_dict.get('set')
            self.set_id = response_dict.get('set_id')
            self.story_spotlight = response_dict.get('story_spotlight')
            self.textless = response_dict.get('textless')
            self.variation = response_dict.get('variation')
            self.variation_of = response_dict.get('variation_of')
            self.watermark = response_dict.get('watermark')

        else:
            self.name = response_dict.get('name')
            self.layout = response_dict.get('layout')
            self.mana_cost = response_dict.get('manaCost')
            self.cmc = response_dict.get('cmc')
            self.colors = response_dict.get('colors')
            self.color_identity = response_dict.get('colorIdentity')
            self.names = response_dict.get('names')
            self.type = response_dict.get('type')
            self.supertypes = response_dict.get('supertypes')
            self.subtypes = response_dict.get('subtypes')
            self.types = response_dict.get('types')
            self.rarity = response_dict.get('rarity')
            self.text = response_dict.get('text')
            self.flavor = response_dict.get('flavor')
            self.artist = response_dict.get('artist')
            self.number = response_dict.get('number')
            self.power = response_dict.get('power')
            self.toughness = response_dict.get('toughness')
            self.loyalty = response_dict.get('loyalty')
            self.multiverse_id = response_dict.get('multiverseid')
            self.variations = response_dict.get('variations')
            self.variation = response_dict.get('variation')
            self.watermark = response_dict.get('watermark')
            self.border = response_dict.get('border')
            self.timeshifted = response_dict.get('timeshifted')
            self.hand = response_dict.get('hand')
            self.life = response_dict.get('life')
            self.release_date = response_dict.get('releaseDate')
            self.starter = response_dict.get('starter')
            self.printings = response_dict.get('printings')
            self.original_text = response_dict.get('originalText')
            self.original_type = response_dict.get('originalType')
            self.source = response_dict.get('source')
            self.image_url = response_dict.get('imageUrl')
            self.set = response_dict.get('set')
            self.set_name = response_dict.get('setName')
            self.id = response_dict.get('id')
            self.legalities = response_dict.get('legalities')
            self.rulings = response_dict.get('rulings')
            self.foreign_names = response_dict.get('foreignNames')

        self.power_num = self.__mk_num(self.power)
        self.toughness_num = self.__mk_num(self.toughness)
        self.loyalty_num = self.__mk_num(self.loyalty)

        if getattr(self, 'card_faces', None):
            for card_face in self.card_faces:
                if 'power' in card_face:
                    card_face['power_num'] = self.__mk_num(
                        card_face.get('power'))

                if 'toughness' in card_face:
                    card_face['toughness_num'] = self.__mk_num(
                        card_face.get('toughness'))

                if 'loyalty' in card_face:
                    card_face['loyalty_num'] = self.__mk_num(
                        card_face.get('loyalty'))

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

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
        return '{} ({})'.format(self.name, self.set)

    def __repr__(self):
        return '{} ({})'.format(self.name, self.set)

    def __mk_num(self, s):
        if type(s) is float or type(s) is int:
            return float(s)

        if s is not None:
            s_num = s.translate(str.maketrans('', '', '+*∞?²X'))

            try:
                return float(s_num) if s_num else 0
            except:
                return None
        else:
            return None

    def __comp(self, attr, val):
        if isinstance(attr, list):
            if any(set(val).intersection(set(attr))):
                return True
        elif isinstance(attr, str):
            if val.lower() in attr.lower():
                return True
        elif isinstance(attr, bool):
            if val is attr:
                return True
        else:
            if val >= attr:
                return True

    def __comp_neg(self, attr, val):
        if isinstance(attr, list):
            if set(val) != set(attr):
                return True
        elif isinstance(attr, str):
            if val.lower() != attr.lower():
                return True
        elif isinstance(attr, bool):
            if val is not attr:
                return True
        else:
            if val != attr:
                return True

    def update(self, response_dict):
        for key, value in response_dict.items():
            setattr(self, key, value)

            if key == 'card_faces' and value is not None:
                for card_face in self.card_faces:
                    if 'power' in card_face:
                        card_face['power_num'] = self.__mk_num(
                            card_face.get('power'))

                    if 'toughness' in card_face:
                        card_face['toughness_num'] = self.__mk_num(
                            card_face.get('toughness'))

                    if 'loyalty' in card_face:
                        card_face['loyalty_num'] = self.__mk_num(
                            card_face.get('loyalty'))

    def matches_any(self, search_all_faces=False, **kwargs):
        """Returns True if any of the given keyword arguments match 'loosely' with this cards's attributes.
        The arguments should be any of the cards's attribute names such as 'power' and 'toughness' and 'name'.

        String attributes are case insensitive and it is enough that the argument is a substring of the attribute.

        For list attributes the order does not matter and it is enough for one of the elements to match exactly.

        For numerical attributes it is enough that the argument is larger or equal to the attribute.

        Scryfall card objects contain the 'card_faces' attribute which holds data of the possible flipsides or backsides
        of certain cards like 'Akki Lavarunner // Tok-Tok, Volcano Born'. By default, if the card has different faces
        AND if he searched attribute has a null or an empty value, the first face(the 'playing' face) is also
        matched. If 'search_all_faces' is enabled all the faces are matched and it is enough for one of them to partly
        match the way described above.

        Note that searching for Null arguments is not supported.

        Args:
            search_all_faces (bool): (only for Scryfall cards) If True, searches all the cards faces instead of the
                first one
            **kwargs: Arguments to match with the cards's attributes.

        Returns:
            bool: True if all of the given keyword arguments match completely and False otherwise.

        """
        for (key, val) in kwargs.items():
            attr = getattr(self, key, None)

            if attr is not None:
                if self.__comp(attr, val):
                    return True

            if getattr(self, 'card_faces', None):
                if search_all_faces:
                    for card_face in self.card_faces:
                        attr = card_face.get(key, None)

                        if attr is not None:
                            if self.__comp(attr, val):
                                return True
                else:
                    attr = self.card_faces[0].get(key, None)

                    if attr is not None:
                        if self.__comp(attr, val):
                            return True

        return False

    def matches_all(self, search_all_faces=False, **kwargs):
        """Returns True if all of the given keyword arguments match completely with this cards's attributes.
        The arguments should be any of the cards's attribute names such as 'power' and 'toughness' and 'name'.

        String attributes are case insensitive and must match completely.

        For list arguments the order does not matter and all of the elements must match exactly.

        Numerical arguments must match exactly

        Scryfall card objects contain the 'card_faces' attribute which holds data of the possible flipsides or backsides
        of certain cards like 'Akki Lavarunner // Tok-Tok, Volcano Born'. By default, if the card has different faces
        AND if he searched attribute has a null or an empty value, the first face(the 'playing' face) is matched
        instead. If 'search_all_faces' is enabled all the faces are matched and it is enough for one of them to match
        completely the way described above.

        Note that searching with Null arguments is not supported.

        Args:
            search_all_faces (bool): (only for Scryfall cards) If True, searches all the cards faces instead of the
                first one
            **kwargs (dict): Arguments to match with the cards's attributes.

        Returns:
            bool: True if all of the given keyword arguments match completely and False otherwise.

        """
        for (key, val) in kwargs.items():
            faces = getattr(self, 'card_faces', None)

            if not faces:
                attr = getattr(self, key, None)

                if attr is None or self.__comp_neg(attr, val):
                    return False
                else:
                    continue

            else:
                if search_all_faces:
                    attr = getattr(self, key, None)

                    if attr is not None and not self.__comp_neg(attr, val):
                        continue

                    found = False
                    for card_face in faces:
                        attr = card_face.get(key, None)

                        if attr is not None and not self.__comp_neg(attr, val):
                            found = True

                    if found:
                        continue
                    else:
                        return False
                else:
                    attr = getattr(self, key, None)

                    if attr is not None and not self.__comp_neg(attr, val):
                        continue

                    attr = self.card_faces[0].get(key, None)

                    if attr is None or self.__comp_neg(attr, val):
                        return False
                    else:
                        continue

        return True

    def download_image_from_scryfall(self,
                                     image_type='normal',
                                     dir_path='',
                                     replace_forwardlashes=' '):
        """Downloads the image for this card from Scryfall to a given directory with path 'dir_path'. Scryfall hosts
        6 types of image files and by default 'normal' sized images are downloaded. More information at:
        https://scryfall.com/docs/api/images.

        If no path is specified the image is downloaded to the current working directory. If the given path is not
        found a new folder is created automatically. Paths should be specified in the format
        'C:\\users\\Timmy\\some_folder\\' and the image file name will be the card name, eq. 'Wild Mongrel.jpg'.
        Specifying wrong kind of paths might lead to undefined behaviour or related errors.

        Some single-faced cards like 'Fire // Ice' will have two forward slashes in their names. These are not allowed
        as filenames and will be replaced by given argument 'replace_forwardlashes' which is a single space by default.

        Args:
            image_type (str): A type or size of image to download. Either 'png', 'border_crop', 'art_crop', 'small',
            'normal' or 'large'.
            dir_path (str): The path to the directory to download the image to.
            replace_forwardlashes (str): A string to replace forward slashes in certain card names.
        """
        if self.api_type != 'scryfall':
            print(
                'Images can only be only downloaded for card objects from Scryfall api.'
            )
            return

        path = pathlib.Path(dir_path)

        try:
            path.mkdir(exist_ok=True)
        except FileExistsError:
            print('The given path {} already exists and it is not a folder.'.
                  format(str(path)))

        try:
            if self.image_uris and self.image_uris.get(image_type):
                name = self.name.replace(' // ', replace_forwardlashes)

                if image_type == 'png':
                    urllib.request.urlretrieve(self.image_uris.get(image_type),
                                               path / (name + '.png'))
                    time.sleep(0.1)
                else:
                    urllib.request.urlretrieve(self.image_uris.get(image_type),
                                               path / (name + '.jpg'))
                    time.sleep(0.1)

            elif getattr(self, 'card_faces'):
                for face in self.card_faces:
                    if face.get('image_uris') and face.get('image_uris').get(
                            image_type):
                        urllib.request.urlretrieve(
                            face.get('image_uris').get(image_type),
                            path / (face.get('name') + '.jpg'))
                        time.sleep(0.1)
            else:
                warnings.warn(
                    'No image of the format --{}-- found for the card --{}--'.
                    format(image_type, str(self)))

        except URLError as err:
            print(
                'Something went wrong with downloading an image for {} from Scryfall: '
                .format(str(self)))
            print(str(err))

    def proxy_images(self, scaling_factor=1.0, image_type='normal'):
        """Returns a tuple of proxy images of the card as PIL Image objects. In most cases the card will have one single
        image and some cards (double-sided) will have two. By default the images will have size 745 × 1040 which is
        the standard mtg card size on A4 with normal dpi.

        The size of the images can be scaled with the 'scaling_factor' in a simple manner:
        (745 * scaling_factor) × (1040 * scaling_factor). On some systems or printers it is sometimes good to use
        slightly smaller or larger (eg. scaling_factor=0.97) images for better results.

        What size or type of images to return can be specified with 'image_type' .Scryfall hosts 6 types of image files
        and by default 'normal' sized images are downloaded. Using 'png' or 'large' might yield better quality images.
        More information at: https://scryfall.com/docs/api/images.

        Note that the Pillow-image library is needed for creating printable proxies.

        Args:
            scaling_factor (float): Scales the default mtg card size with the factor.
            image_type (str): A type or size of image to use from Scryfall. Either 'png', 'border_crop', 'art_crop',
                'small', 'normal' or 'large'.

        Returns:
            tuple[PIL Image]: A suitable proxy images of the card as a PIL Image objects.
        """
        if self.api_type != 'scryfall':
            print(
                'Images can only be only downloaded for card objects from Scryfall api.'
            )
            return

        try:
            from PIL import Image
        except ImportError:
            print(
                'The Pillow-image library is needed for creating printable proxies. Make sure you have it installed!'
            )
            return

        try:
            if self.image_uris and self.image_uris.get(image_type):
                image = Image.open(
                    io.BytesIO(
                        urllib.request.urlopen(
                            self.image_uris.get(image_type)).read()))
                time.sleep(0.1)
                image = image.resize(
                    (int(745 * scaling_factor), int(1040 * scaling_factor)),
                    Image.ANTIALIAS)
                return (image, )

            elif getattr(self, 'card_faces'):
                images = ()
                for face in self.card_faces:
                    if face.get('image_uris') and face.get('image_uris').get(
                            image_type):
                        image_uri = face.get('image_uris').get(image_type)
                        image = Image.open(
                            io.BytesIO(
                                urllib.request.urlopen(image_uri).read()))
                        time.sleep(0.1)
                        image = image.resize((int(
                            745 * scaling_factor), int(1040 * scaling_factor)),
                                             Image.ANTIALIAS)
                        images = images + (image, )

                return images
            else:
                warnings.warn('No image found for the card --{}--'.format(
                    str(self)))
                return

        except URLError as err:
            print(
                'Something went wrong with downloading an image for {} from Scryfall: '
                .format(str(self)))
            print(str(err))

    @property
    def api_type(self):
        if hasattr(self, 'scryfall_uri'):
            return 'scryfall'
        else:
            return 'mtgio'

    @property
    def json(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True,
                          indent=4)
