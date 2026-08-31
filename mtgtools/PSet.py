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

        if "scryfall_uri" in response_dict:
            self.id = response_dict.get("id")
            self.code = response_dict.get("code")
            self.mtgo_code = response_dict.get("mtgo_code")
            self.tcgplayer_id = response_dict.get("tcgplayer_id")
            self.name = response_dict.get("name")
            self.uri = response_dict.get("uri")
            self.scryfall_uri = response_dict.get("scryfall_uri")
            self.search_uri = response_dict.get("search_uri")
            self.set_type = response_dict.get("set_type")
            self.printed_size = response_dict.get("printed_size")
            self.released_at = response_dict.get("released_at")
            self.block_code = response_dict.get("block_code")
            self.block = response_dict.get("block")
            self.parent_set_code = response_dict.get("parent_set_code")
            self.card_count = response_dict.get("card_count")
            self.digital = response_dict.get("digital")
            self.foil_only = response_dict.get("foil_only")
            self.nonfoil_only = response_dict.get("nonfoil_only")
            self.icon_svg_uri = response_dict.get("icon_svg_uri")

        else:
            self.code = response_dict.get("code")
            self.name = response_dict.get("name")
            self.type = response_dict.get("type")
            self.border = response_dict.get("border")
            self.mkm_id = response_dict.get("mkm_id")
            self.mkm_name = response_dict.get("mkm_name")
            self.release_date = response_dict.get("releaseDate")
            self.gatherer_code = response_dict.get("gathererCode")
            self.magic_cards_info_code = response_dict.get("magicCardsInfoCode")
            self.booster = response_dict.get("booster")
            self.old_code = response_dict.get("oldCode")
            self.block = response_dict.get("block")
            self.online_only = response_dict.get("onlineOnly")

    def __hash__(self):
        return hash(self.name + self.code)

    def __eq__(self, other):
        return self.code == other.code

    def __ne__(self, other):
        return self.code != other.code

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        elif self.__lt__(other):
            return -1
        else:
            return 1

    def __str__(self):
        return self.name + "(" + self.code + ")"

    def __repr__(self):
        return self.name + "(" + self.code + ")"

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
        for key, val in kwargs.items():
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
        for key, val in kwargs.items():
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

    def download_images_from_scryfall(self, image_type="normal", dir_path=""):
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
            super().download_images_from_scryfall(image_type=image_type, dir_path=self.code + "\\")
        else:
            super().download_images_from_scryfall(image_type=image_type, dir_path=dir_path + self.code + "\\")

    def jprint(self):
        """Pretty-prints the json representation of this object."""

        print(self.json)

    @property
    def json(self):
        json_dict = {
            key: value for key, value in self.__dict__.items() if key not in {"_cards", "_sideboard", "creation_date"}
        }

        json_dict["cards"] = [json.loads(card.json) for card in self.cards]

        return json.dumps(json_dict, sort_keys=True, indent=4)
