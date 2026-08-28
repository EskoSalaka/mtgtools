import json
import textwrap
import uuid

from persistent import Persistent
from persistent.list import PersistentList

from mtgtools.PCardList import PCardList


class PRuling(Persistent):
    """PRuling is a Persistent class that represents an oracle ruling, WotC set release note or a Scryfall note for
    a card. The rulings contain the following attributes:

    object: str - A content type for this object, always ruling
    oracle_id: str(UUID) -  The Oracle ID of the card this ruling is associated with
    source: str -  	A computer-readable string indicating which company produced this ruling, either wotc or scryfall
    published_at: str(ISO 8601) - The date and time when this ruling was published
    comment: str - The text of the ruling


    Additionally, the PRulings contain the PCardList of the cards that are associated with the ruling.
    """

    _cards = None

    def __init__(self, response_dict):
        self.id = uuid.uuid4()
        self.object = response_dict.get("object")
        self.oracle_id = response_dict.get("oracle_id")
        self.source = response_dict.get("source")
        self.published_at = response_dict.get("published_at")
        self.comment = response_dict.get("comment")

        self._cards = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, PRuling):
            return self.id == other.id

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.comment

    def __repr__(self):
        return self.comment

    def update(self, response_dict):
        for key, value in response_dict.items():
            setattr(self, key, value)

    def pprint_str(self, expanded=False):
        """Returns a copy-pasteable string representation of the PRuling object. If expanded is True,
        the string representation will include the source, published_at, and associated cards of the ruling.
        """
        pprint_str = "\n"

        if expanded:
            pprint_str += "Source: {}\n".format(self.source)
        if expanded:
            pprint_str += "Published at: {}\n".format(self.published_at)

        if expanded:
            pprint_str += "Associated cards:"

            if not self.cards or len(self.cards) == 0:
                pprint_str += "No associated cards.\n\n"
            else:
                card_name = self.cards[0].name
                pprint_str += " {} ({} cards) ({})\n\n".format(
                    card_name, len(self.cards), ", ".join([card.set for card in self.cards])
                )

        pprint_str += textwrap.fill(self.comment, width=60)

        return pprint_str

    def pprint(self, expanded=False):
        """Prints a copy-pasteable string representation of the PRuling object. If expanded is True,
        the string representation will include the source, published_at, and associated cards of the ruling.
        """
        print(self.pprint_str(expanded=expanded))

    def jprint(self):
        """Prints a JSON representation of the PRuling object."""
        print(self.json)

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        if isinstance(cards, (PCardList, list, tuple, PersistentList)):
            self._cards = PCardList(cards, name="Ruling: {}".format(self.oracle_id))
        elif cards is None:
            self._cards = None
        else:
            raise TypeError("cards must be a PCardList, list, tuple, or PersistentList")

    @property
    def json(self):
        return json.dumps(
            self,
            default=lambda o: {key: value for key, value in o.__dict__.items() if key not in ("_cards", "id")},
            sort_keys=True,
            indent=4,
        )
