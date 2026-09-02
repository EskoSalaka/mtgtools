import datetime
import json
import uuid
import warnings

from persistent import Persistent
from persistent.list import PersistentList
from mtgtools.PSet import PSet


class PSetList(Persistent):
    """PSetList is a persistent set list object that mostly acts just like a normal Python list for PSet objects.
    These lists can be saved in the database just like any other persistent objects. It can optionally be initialized
    with another list of PSet objects and a name. Additionally, it will also have an attribute 'creation_date' and
    a unique uuid attribute 'id'. PSetLists are considered equal if they have the same 'id'.

    Except for the usual list methods like 'extend' and 'append', the PCardList is functional in style, meaning that
    calling any of the other filtering or querying methods return new PCardList objects leaving the original untouched.

    args:
        sets (PSetList, PersistentList[PSet], list[PSet], tuple[PSet]): Initial sets of the list.
        name (str): Name of the set list.
    """

    def __init__(self, sets=None, name=""):
        if isinstance(sets, PSetList):
            self._sets = PersistentList(sets.sets)
        elif isinstance(sets, (PersistentList, list, tuple)):
            self._sets = PersistentList(sets)
        elif not sets:
            self._sets = PersistentList()
        else:
            raise TypeError

        self.name = name
        self.creation_date = datetime.datetime.now()
        self.id = uuid.uuid4()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._sets.__getitem__(item)
        else:
            return PSetList(self._sets.__getitem__(item))

    def __setitem__(self, key, value):
        self._sets.__setitem__(key, value)

    def __iter__(self):
        return iter(self._sets)

    def __str__(self):
        return str(self._sets)

    def __repr__(self):
        return repr(self._sets)

    def __add__(self, other):
        if isinstance(other, PSetList):
            return PSetList(self.sets + other.sets)
        elif isinstance(other, (PersistentList, list, tuple)):
            return PSetList(self.sets + other)
        elif isinstance(other, PSet):
            new_sets = PersistentList(self.sets)
            new_sets.append(other)
            return PSetList(new_sets)
        else:
            raise TypeError

    def __radd__(self, other):
        if isinstance(other, PSetList):
            return PSetList(self.sets + other.sets)
        elif isinstance(other, (PersistentList, list, tuple)):
            return PSetList(self.sets + other)
        elif isinstance(other, PSet):
            new_sets = PersistentList(self.sets)
            new_sets.append(other)
            return PSetList(new_sets)
        else:
            raise TypeError

    def __iadd__(self, other):
        if isinstance(other, PSetList):
            return PSetList(self.sets + other.sets)
        elif isinstance(other, (PersistentList, list, tuple)):
            return PSetList(self.sets + other)
        elif isinstance(other, PSet):
            new_sets = PersistentList(self.sets)
            new_sets.append(other)
            return PSetList(new_sets)
        else:
            raise TypeError

    def __len__(self):
        return len(self.sets)

    def __contains__(self, pset):
        return self.sets.__contains__(pset)

    def __eq__(self, other):
        if isinstance(other, PSetList):
            return self.id == other.id

    def __reversed__(self):
        return reversed(self._sets)

    def append(self, pset):
        """Appends the given set object to this list in-place.

        Args:
            pset (PSet): The set object to append.
        """
        self.sets.append(pset)

    def extend(self, psets):
        """Extends the list with a list of set objects in-place.

        Args:
            psets (PSetList, list, tuple, PersistentList): A PSetList, PersistentList, list or a tuple of
                set objects to extend this list with.
        """
        if isinstance(psets, PSetList):
            self.sets.extend(psets.sets)
        elif isinstance(psets, (PersistentList, list, tuple)):
            self.sets.extend(psets)
        else:
            raise TypeError

    def insert(self, index, pset):
        """Inserts a set object to a given index in this list in-place.

        Args:
            pset (PSet): The set object to be inserted in the given index in this list.
            index (int): The index to insert the given set object.
        """
        self._sets.insert(index, pset)

    def index(self, pset):
        """Returns the index where the given set object is located in this list.

        Args:
            pset (PSet): The set object to be searched.
        """
        return self._sets.index(pset)

    def clear(self):
        """Clears this list."""
        self._sets.clear()

    def remove(self, pset):
        """Removes a given set from this list in-place.

        Args:
            pset (PSet): A set object to remove from this list.
        """
        self._sets.remove(pset)

    def pop(self, index):
        """Removes a set from a given index from this list in-place.

        Args:
            index (int): An index to remove a set from.
        """
        return self._sets.pop(index)

    def count(self, pset):
        """Returns the number of given set objects in this list. Sets are considered same if they have the same code.

        Args:
            pset (pset): A set object to count.

        Returns:
            int: The number of given set objects in this list
        """
        return self._sets.count(pset)

    def sort(self, func):
        """Sorts the sets of this list with a given function in-place. The given function should return some
        attribute of a set object by which this list is sorted.

        Args:
            func: A function to sort this list with.
        """
        self._sets.sort(key=func)

    def filter(self, func):
        """Filters the sets of this list with a given function in-place. The new list contains all the cards
        for which the given function returns True.

        Args:
            func: A function to filter with.
        """
        self._sets.filter(key=func)

    def sorted(self, func):
        """Returns a new list with the sets of this list sorted with a given function. The given function should return
        some attribute of a set object by which this list is sorted.

        Args:
            func: A function to sort this list with.

        Returns:
            PCardList: A new instance of this list sorted.

        """
        return PSetList(sorted(self.sets, key=func))

    def filtered(self, func):
        """Returns a new list filtered with a given function. The new list contains all the sets
        for which the given function returns True.

        Args:
            func: A function to filter with.

        Returns:
            PCardList: A new instance of this list filtered.

        """
        return PSetList(list(filter(func, self.sets)))

    def where(self, invert=False, **kwargs):
        """Returns a new list of sets for which any of the given keyword arguments match partly or completely with the
        attributes of the sets in this list. The arguments should be any set attribute names such as 'name',
        'type' and 'block'. String attributes are case insensitive and it is enough that the argument is a
        substring. For list arguments the order does not matter and it is enough for one of the elements to match.

        The search can also be inverted by setting invert=True so that all the cards NOT matching will be returned.

        Note that searching for Null arguments is not supported.

        Args:
            invert: If True, a list of sets NOT matching the arguments is returned.
            **kwargs: Arguments to match with the attributes of this list's sets.

        Returns:
            bool: A new list of sets for which any of the given keyword arguments match partly or completely.
        """
        del_keys = []

        for key, val in kwargs.items():
            if not val:
                msg = "Ignoring an empty or null value for keyword {}. Null or empty values are not supported."
                warnings.warn(msg.format(key))
                del_keys.append(key)
            elif len(self.sets) == 0:
                msg = "Searching an empty list."
                warnings.warn(msg)
            elif not hasattr(self.sets[0], key):
                msg = "Ignoring an unrecognized keyword {}. Make sure you are using correct api type and spelling."
                warnings.warn(msg.format(key))
                del_keys.append(key)

        for key in del_keys:
            del kwargs[key]

        if not invert:
            return PSetList([pset for pset in self if pset.matches_any(**kwargs)])
        else:
            return PSetList([pset for pset in self if not pset.matches_any(**kwargs)])

    def where_exactly(self, invert=False, **kwargs):
        """Returns a new list of sets for which all of the given keyword arguments match completely with the attributes
        of the sets in this list. The arguments should be any set attribute names such as 'name', 'type' and 'block'.
        String attributes are case insensitive and must match exactly. For list arguments the order does not
        matter and and each element must match exactly.

        The search can also be inverted by setting invert=True so that all the cards NOT matching will be returned.

        Note that searching for Null arguments is not supported.

        Args:
            invert: If True, a list of sets NOT matching the arguments is returned.
            **kwargs: Arguments to match with the attributes of this list's cards.

        Returns:
            bool: A new list of sets for which all of the given keyword arguments match completely.
        """
        del_keys = []

        for key, val in kwargs.items():
            if not val:
                msg = "Ignoring an empty or null value for keyword {}. Null or empty values are not supported."
                warnings.warn(msg.format(key))
                del_keys.append(key)
            elif len(self.sets) == 0:
                msg = "Searching an empty list."
                warnings.warn(msg)
            elif not hasattr(self.sets[0], key):
                msg = "Ignoring an unrecognized keyword {}. Make sure you are using correct api type and spelling."
                warnings.warn(msg.format(key))
                del_keys.append(key)

        for key in del_keys:
            del kwargs[key]

        if not invert:
            return PSetList([pset for pset in self if pset.matches_all(**kwargs)])
        else:
            return PSetList([pset for pset in self if not pset.matches_all(**kwargs)])

    def pprint(self):
        """Prints out the contents of this list in a nice readable way."""
        print(self.pprint_str())

    def pprint_str(self):
        """Returns a nice readable string of the contents of this list.

        Returns:
            str: a string of the contents of this list in a nice readable format.
        """

        if len(self) == 0:
            if self.name:
                return 'Empty set list "{}" created at {}\n'.format(self.name, str(self.creation_date))
            else:
                return "Unnamed empty set list created at {}\n".format(self.creation_date)

        pp_str = ""

        if self.name:
            pp_str += 'Set list "{}" created at {}\n'.format(self.name, str(self.creation_date))
        else:
            pp_str += "Unnamed set list created at {}\n".format(self.creation_date)

        longest_name = max(len(pset.name) for pset in self.sets)
        longest_type = max(len(getattr(pset, "set_type", getattr(pset, "type", ""))) for pset in self.sets)
        longest_block = max(len(pset.block) if pset.block else 0 for pset in self.sets)
        longest_code = max(len(pset.code) if pset.code else 0 for pset in self.sets)

        pp_str += "-" * (longest_name + longest_type + longest_block + longest_code + 17)
        pp_str += "\n"

        format_str = "{name:{w1}s}   {code:{w2}s}   {block:{w3}s}   {type:{w4}s}   {cards}\n"
        pp_str += format_str.format(
            name="Set",
            w1=longest_name,
            code="Code",
            w2=longest_code,
            block="Block",
            w3=longest_block,
            type="Type",
            w4=longest_type,
            cards="Cards",
        )
        pp_str += "-" * (longest_name + longest_type + longest_block + longest_code + 17)
        pp_str += "\n"

        for pset in self.sets:
            format_str = "{name:{w1}s}   {code:{w2}s}   {block:{w3}s}   {type:{w4}s}   {cards}\n"
            pp_str += format_str.format(
                name=pset.name,
                w1=longest_name,
                code=pset.code,
                w2=longest_code,
                block=pset.block if pset.block else "",
                w3=longest_block,
                type=getattr(pset, "set_type", getattr(pset, "type", "")),
                w4=longest_type,
                cards=len(pset),
            )

        return pp_str

    def jprint(self):
        """Prints out the contents of this list in a nice readable JSON format."""
        print(self.json)

    @property
    def api_type(self):
        try:
            return self.sets[0].api_type
        except IndexError:
            return "unspecified"

    @property
    def len(self):
        """Returns the number of sets in this list. Works the same as the in-built len()
        function acting on this PSetList."""
        return self.__len__()

    @property
    def first(self):
        """Returns the first set in this PSetList, or None if the list is empty."""
        try:
            return self._sets[0]
        except IndexError:
            return None

    @property
    def last(self):
        """Returns the last set in this PSetList, or None if the list is empty."""
        try:
            return self._sets[-1]
        except IndexError:
            return None

    @property
    def json(self):
        return json.dumps({"sets": [json.loads(pset.json) for pset in self.sets]}, sort_keys=True, indent=4)

    @property
    def sets(self):
        return self._sets

    @sets.setter
    def sets(self, sets):
        if isinstance(sets, PSetList):
            self._sets = PersistentList(sets.sets)
        elif isinstance(sets, (list, PersistentList, tuple)):
            self._sets = PersistentList(sets)
        elif not sets:
            self._sets = PersistentList()
        else:
            raise TypeError
