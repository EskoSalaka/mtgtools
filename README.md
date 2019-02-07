# mtgtools

mtgtools is a collection of tools for easy handling of **Magic: The Gathering** data on your computer. The card data
can be easily downloaded from **Scryfall** API or **magicthegathering.io** API and it is saved in a ZODB - database,
which is a native object database for Python. Everything is simply in Python, so no knowledge of SQL or the likes is needed to work with the database.

## Features

- Easily download, update and save Magic: The Gathering card and set data from Scryfall and/or magicthegathering.io to
  a local ZODB database (native object database for Python). Updating the database from scratch usually takes about 2
  minutes on my computer.

- Easily iterate, filter, sort, group and handle card lists, sets and decks. The usual searching methods on the whole
  card database of 40k cards take about 0.15s on my computer.

- Save your own card lists and decks in a database in pure Python.

- Read and write card lists or decks from files.

- Generate random samples, random cards, booster packs etc. from any lists of cards.

- Download card images of the type of your choice from Scryfall.

- Create proxy image sheets from lists of cards using Scryfall.

## Requirements

- **Python 3.5** - mtgtools is tested on Python 3.5 but will probably also work on later versions

- **ZODB** - Can be installed with `pip install zodb`. More info in http://www.zodb.org/en/latest/.

- **requests** - Can be installed with `pip install requests`. More info in https://pypi.org/project/requests/.

- **PIL** - Not necessary, but needed for creating proxy image sheets. Can be installed with `pip install pillow`

## Scryfall vs magicthegathering.io

At the moment there exists two different kind of APIs for mtg data, Scryfall and magicthegathering.io. They are
structured in different ways and both have pros and cons. For example Scryfall cards contain attribute `card_faces`
where as the faces in mtgio are separate cards.

At the moment Scryfall has a more extensive database with more useful data like prices and purchase uris and also hosts
good quality card images, so in my opinion it is more useful of the two.

## Installing

mtgtools can be simply installed with `pip install mtgtools`.

## Usage guide

### Persistent card, set and card list objects

Working with the database mostly revolves around working with the following persistent card and card list objects. Data
persistence in this case basically means that ZODB will automatically detect when these objects are accessed and
modified and saves the according changes automatically when transactions have been committed.

A good guide on ZODB can for example be found here: https://media.readthedocs.org/pdf/zodborg/latest/zodborg.pdf

#### **PCard**

`PCard` is a simple persistent dataclass representing Magic: the Gathering cards with their characteristic
attributes. It is constructed simply with a json response dictionary from either magicthegathering.io or Scryfall
API, so `PCard` has all the attributes matching the responses' keys and values.

Note, that the attributes `power`, `toughness` and `loyalty` are saved as strings since they might contain characters
like '\*' or 'X'. For convenience, the card objects will also contain numerical versions of these attributes:
`power_num`, `toughness_num` and `loyalty_num`. This makes searching much easier in many cases. After stripping away
these non-digit characters, the remaining numbers will be in the numerical version of the attribute. If nothing is left
after stripping, the numerical version will be 0.

Another difference between Scryfall and mtgio is that in mtgio API attribute names are in camelCase style. For the
purpose of consistency, the attributes in this software are transformed into snake_case which makes many of the
attributes identical to the ones in Scryfall. For example, the attribute `manaCost` from mtgio has been changed to
`mana_cost` which is the same as in Scryfall.

For more information on what attributes cards have, read
https://scryfall.com/docs/api/cards for Scryfall card objects and
https://docs.magicthegathering.io/#api_v1cards_list for magicthegathering.io card objects.

#### **PCardList**

`PCardList` is a persistent card list or deck object that mostly acts just like a normal Python list for `PCard`
objects. These lists can be saved in the database just like any other persistent objects, and a `PCardList` is used
as a container for all the cards in the database.

`PCardList` has many useful methods for querying, filtering, sorting and grouping it's contents and creating new card
lists by combining other card lists in various ways. It also contains other handy methods like downloading the images
of it's cards from Scryfall, creating proxy image sheets from it's cards, printing out it's contents in a readable
way and creating deck-like strings or files of it's contents.

Except for the usual in-place list methods like `extend`, `append` and `remove` the `PCardList` is functional in
style, meaning that calling any of the other filtering or querying methods return new `PCardList` objects leaving the
original untouched.

`PCardList` can also be used as a deck by adding cards to it's `sideboard`. Having cards in the sideboard
changes some functionalities of the methods like `deck_str` in which now also the sideboard cards are added. Images
are downloaded and proxies created for both the cards and the sideboard. However, Having cards in the 'sideboard'
does not change the behavior of the crucial internal methods like `len`, `getitem` or `setitem`,
so basically the cards in the sideboard are a kind of an extra.

#### **PSet**

`Pset` is a simple Persistent dataclass representing Magic: The Gathering sets with their characteristic
attributes. It is constructed simply with a json response dictionary from either magicthegathering.io or Scryfall
API, so **PSet** has all the attributes matching the responses' keys and values.

For more information on what attributes sets have, read
https://scryfall.com/docs/api/sets for Scryfall set objects and
https://docs.magicthegathering.io/#api_v1sets_list for magicthegathering.io set objects.

Additionally, `PSet` inherits from `PCardList` and it also contains all the cards of the set. Working with `PSet`
by for example querying it's cards returns new `PCardList` objects is safe for the set leaving it untouched.

#### **PSetList**

`PSetList` is a persistent set list object that mostly acts just like a normal Python list for `Pset` objects.
These lists can be saved in the database just like any other persistent objects. `PSetList` contains handy methods for
querying the sets it contains but in most cases it is only useful as a container database. It works very similarly
to `PCardList` except that they hold sets rather than cards.

### Working with the database

#### Opening/creating databases

An existing database can be opened simply with

```
>>> from mtgtools.MtgDB import MtgDB
>>> mtg_db = MtgDB('my_db.fs')
```

If no storage in the given path is found, a new empty database is automatically created.

Now that the connection to the database is open, the `mtg_db` will contain all the needed ZODB-related objects
`storage`, `connection`, `database` and `root` (more about these in http://www.zodb.org/en/latest/reference/index.html).
The cards and sets can now be found in the `root` of the database with

```
>>> scryfall_cards = mtg_db.root.scryfall_cards
>>> scryfall_sets = mtg_db.root.scryfall_sets
```

and

```
>>> mtgio_cards = mtg_db.root.mtgio_cards
>>> mtgio_sets = mtg_db.root.mtgio_sets

```

All the cards are saved as a `PCardList` and all the sets are saved as a `PSetList`. The root acts as a
boot-strapping point and a top-level container for all the objects in the database.

```
>>> print(mtg_db.root)

<root: mtgio_cards mtgio_sets scryfall_cards scryfall_sets>
```

The above method for accessing the database objects is a convenience, and you can also access the root mapping with

```
>>> root_mapping = tool.connection.root()
>>> print([key for key in root_mapping.keys()])

['scryfall_sets', 'mtgio_cards', 'scryfall_cards', 'mtgio_sets']

>>> print('scryfall_cards' in root_mapping)

True
```

#### Updating

Building the database from scratch from Scryfall and mtgio is simply done with

```
my_db.scryfall_update()
my_db.mtgio_update()
```

The update downloads and saves all new card and set data and also updates any changes to the existing data. This is
also useful when updating for example the price and legality attributes of the Scryfall cards which might often change.

Building the database from scratch takes about few minutes to complete and it is mostly affected by the API request
limits which are 10 request per second for Scryfall and 5000 requests per hour for magicthegathering.io. About 10
requests per second are sent during updating which should comply with the Scryfall limits, and with magicthegathering.io
you have to make sure not to run the update too many times per hour.

### Working with card lists

#### Querying, filtering and sorting

`PCardList` has two handy methods for "querying" its contents which return new `PCardList` objects:<br/>

`where(invert=False, search_all_faces=False, **kwargs)`

and

`where_exactly(invert=False, search_all_faces=False, **kwargs)`

`where`, the looser method, returns a new `PCardList` for which _ANY of the given keyword arguments match 'loosely'_
with the attributes of the cards in this list. The arguments should be any card attribute names such as
'_power_', '_toughness_' and '_name_'.

String attributes are case insensitive and it is enough that the argument is a substring of the attribute.

For list attributes the _**order does not matter**_ and it is enough for _**one of the elements to match exactly**_.

For convenience, for numerical attributes it is enough that the argument is _**larger or equal**_ to the attribute.

`where_exactly`, the stricter method, returns a new list of cards for which _**ALL the given keyword arguments match
completely**_ with the attributes of the cards in this list.

For both of these methods, the results can be inverted to return all the cards NOT matching the arguments by setting
`invert=True`.

For Scryfall cards, which sometimes have the `card_faces` attribute, normally only the first face of the card
(the normal face you would play) is considered when matching arguments. By setting `search_all_faces=True` the arguments
can now also match with any possible faces of the cards.

Let's start by getting all the Scryfall cards and sets of the database:

```
>>> from mtgtools.MtgDB import MtgDB

>>> mtg_db = MtgDB('my_db.fs')
>>> cards = mtg_db.root.scryfall_cards
>>> sets = mtg_db.root.scryfall_sets
```

Some basic searching:

```
>>> werebears = cards.where_exactly(name='Werebear')
>>> print(werebears)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody)]

>>> print(len(werebears))

4
```

Turns out that there are 4 different Werebear cards in 4 different sets. Lets get the single card from Odyssey:

```
>>> ody_werebear = cards.where_exactly(name='Werebear', set='ody')[0]
>>> print(ody_werebear)

Werebear (ody)

>>> print(ody_werebear.name, ody_werebear.set, ody_werebear.set_name, ody_werebear.power, ody_werebear.toughness)

Werebear ody Odyssey 1 1

>>>print(ody_werebear.oracle_text)

{T}: Add {G}.
Threshold — Werebear gets +3/+3 as long as seven or more cards are in your graveyard.
```

Note, that in this case using `cards.where_(name='Werebear', set='ody')` would not only return the Werebears but ALSO
all the other cards from the set 'ody' since `where` returns the cards for which ANY of the given keyword arguments
match partly or completely.

Also note, that for `where` it is enough for the arguments match only partly. For example with string arguments like
`name`, `type_line`, and `oracle_text` it is enough for the argument to be a substring of the cards' attribute in
question:

```
>>> werebears = cards.where(name='wereb')
>>> print(werebears)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody)]

>>> print(cards.where(oracle_text='12 damage'))

[Everythingamajig (ust), Tower of Calamities (som)]
```

Querying and other operations return new lists so we can also chain multiple queries together. One of he previous
examples with chaining:

```
>>> ody_werebear = cards.where_exactly(name='Werebear').where_exactly(set='ody')[0]
>>> print(ody_werebear.uri)

https://scryfall.com/card/ody/282?utm_source=api
```

If the above methods are not enough to find what you need, then there is also the `filtered` - method which works
quite like the usual `filter` - method for Python lists. `filtered` takes a function object and returns a new list
containing all the cards of the list for which the given function returns True. Lambda functions are very convenient
with this method. For example, we can find the Odyssey _Werebear_ by filtering our cards in the following way:

```
>>> ody_werebear = cards.filtered(lambda card: card.name == 'Werebear' and card.set == 'ody')
>>> print(ody_werebear)

[Werebear (ody)]
```

The card list can be sorted with the `sorted` - method, which works quite like the usual `sort` - method for Python
lists. It takes a function object which should return some attributes of card objects by which this list is sorted.
For example sorting by set codes:

```
>>> werebears = cards.where_exactly(name='Werebear')
>>> print(werebears)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody)]
>>> sorted_werebears = werebears.sorted(lambda card: card.set)
>>> print(sorted_werebears)

[Werebear (ema), Werebear (ody), Werebear (td0), Werebear (wc02)]
```

Finally, the card objects in `PCardList` are stored in it's `cards` - attribute, in a `PersistentList` which can also
be accessed directly.

#### Creating and combining lists

`PCardList` acts like normal Python list so we can use normal indexing and slicing. You can also create empty lists:

```
>>> werebears = cards.where_exactly(name='Werebear')
>>> print(werebears[1:3])

[Werebear (td0), Werebear (wc02)]

>>> print(len(werebears[1:3]))

2

>>> print(werebears[-1])

Werebear (ody)

>>> from mtgtools.PCardList import PCardList
>>> new_empty_list = PCardList()
>>> print(new_empty_list)

[]

>>> print(len(new_empty_list))

0
```

Cards can be easily combined with addition. Addition works with lists and single card objects:

```
>>> werebears = cards.where_exactly(name='Werebear')
>>> wild_mongrels = cards.where_exactly(name='Wild Mongrel')
>>> two_bears_One_mongrel = werebears + wild_mongrels[0]
>>> print(two_bears_One_mongrel)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody), Wild Mongrel (gvl)]

Two_bears_two_mongrels = werebears[0:2] + wild_mongrels[0:2]
print(Two_bears_two_mongrels)

[Werebear (ema), Werebear (td0), Wild Mongrel (gvl), Wild Mongrel (vma)]
```

Another way of combining lists is to append cards to an existing list. Note, that this will actually change the list
instead of creating another one:

```
>>> werebears = cards.where_exactly(name='Werebear')
>>> one_mongrel = cards.where_exactly(name='Wild Mongrel')[0]
>>> werebears.append(one_mongrel)
>>> print(werebears)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody), Wild Mongrel (gvl)]
```

Cards can be removed from lists with subtraction or with the common list method `remove`. Subtraction works with lists
and single card objects and it is basically the same as set subtraction:

```
>>> werebears = cards.where_exactly(name='Werebear')
>>> wild_mongrels = cards.where_exactly(name='Wild Mongrel')
>>> two_bears_One_mongrel = werebears + wild_mongrels[0]
>>> print(two_bears_One_mongrel)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody), Wild Mongrel (gvl)]

>>> only_bears = two_bears_One_mongrel - wild_mongrels
>>> print(only_bears)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody)]

>>> only_bears = two_bears_One_mongrel - wild_mongrels[0]
>>> print(only_bears)

[Werebear (ema), Werebear (td0), Werebear (wc02), Werebear (ody)]
```

Cards in the lists can be multiplied. This is for example handy for getting playsets of certain cards (note, that
you have to multiply lists, not card objects):

```
>>> playset_of_bears = 4 * cards.where_exactly(name='Werebear')[0:1]
>>> print(playset_of_bears)

[Werebear (ema), Werebear (ema), Werebear (ema), Werebear (ema)]

>>> bear_and_arena = PCardList() + cards.where_exactly(name='Werebear')[0] + cards.where_exactly(name='Arena')[0]
>>> playset_of_bears_and_arenas = 4 * bear_and_arena
>>> playset_of_bears_and_arenas.pprint()

Unnamed card list created at 2018-07-18 14:51:23.759658
------------------------------------------------------------------
Card         Set   Type                          Cost     Rarity
------------------------------------------------------------------
4 Arena      tsb   Land                                   rare
4 Werebear   ema   Creature - Human Bear Druid   {1}{G}   common
```

#### Working with multifaced cards from Scryfall

As mentioned earlier, some cards in Scryfall have multiple faces. These are for example flip-cards like
'_Akki Lavarunner // Tok-Tok, Volcano Born_' and transform-cards like '_Accursed Witch // Infectious Curse_'. In some
cases some attributes of these cards are only located inside the `card_faces` - dict attribute of the cards.
In other cases the card itself might have non-null attribute and the same attribute with a different value in one of
it's card faces.

For example, the `name` attribute of the _'Akki Lavarunner'_ card object is '_Akki Lavarunner // Tok-Tok, Volcano Born_'
the `name` attribute of it's first card face is _'Akki Lavarunner'_ and the `name` attribute of it's second card face is
'_Tok-Tok, Volcano Born_'. Similarly, the `mana_cost` - attribute of the card '_Accursed Witch // Infectious Curse_' is
null, but the the `mana_cost` - attribute of it's first card face is '_{3}{B}'_ which is what we would expect from this
card. For that reason, by default the first card face is also matched if it is non-null.

If you want to search all faces of the card you must set `search_all_faces=True` when querying. It might take some trial
and error at first to get what you exactly want.

```
>>> multifaced_cards = 2 * cards.where_exactly(name='Akki Lavarunner // Tok-Tok, Volcano Born')[0:1]
>>> multifaced_cards += 2 * cards.where_exactly(name='Accursed Witch // Infectious Curse')[0:1]
>>> print(multifaced_cards.where(type_line='Enchantment'))

[Accursed Witch // Infectious Curse (soi), Accursed Witch // Infectious Curse (soi)]

>>> print(multifaced_cards.where(power='2', toughness='2', search_all_faces=True).where(colors='R'))

[Akki Lavarunner // Tok-Tok, Volcano Born (chk), Akki Lavarunner // Tok-Tok, Volcano Born (chk)]
```

#### Grouping cards

Cards in the lists can be grouped in various ways like color, type or converted mana cost. Grouping
returns dicts with group identities as keys and cards lists corresponding the group as values. When grouping by color or
color identity, the keys will always have an alphabetical order like 'BR' and 'GUW' instead of the normal
'WUBRG' - order.

```
>>> some_cards = 2 * cards.where_exactly(name='Werebear')[:1] + 2 * cards.where_exactly(name='Firebolt')[:1]
>>> some_cards += 2 * cards.where_exactly(name='Forest')[:1] + 2 * cards.where_exactly(name='Act of Treason')[:1]
>>> csome_cards += 2 * cards.where_exactly(name='Bristling Boar')[:1] + 2 * cards.where_exactly(name='Cleansing Nova')[:1]

>>> for (key, val) in some_cards.grouped_by_converted_mana_cost().items():
        print(key,':', val)

0.0 : [Forest (pss3), Forest (pss3)]
2.0 : [Werebear (ema), Werebear (ema)]
3.0 : [Act of Treason (m19), Act of Treason (m19)]
4.0 : [Arcades, the Strategist (m19), Arcades, the Strategist (m19), Bristling Boar (m19), Bristling Boar (m19)]
5.0 : [Cleansing Nova (m19), Cleansing Nova (m19)]

>>> for (key, val) in some_cards.grouped_by_color().items():
        print(key, ':', val)

    : [Forest (pss3), Forest (pss3)]
GUW : [Arcades, the Strategist (m19), Arcades, the Strategist (m19)]
W   : [Cleansing Nova (m19), Cleansing Nova (m19)]
G   : [Werebear (ema), Werebear (ema), Bristling Boar (m19), Bristling Boar (m19)]
R   : [Act of Treason (m19), Act of Treason (m19)]
```

The `grouped_by_id` - method is useful for fast retrieval of multiples of card objects from the list. Each different
card contains a unique `id` attribute by which the ones in the list can be quickly retrieved by grouping them.

You can also create a special kind of grouping, or a kind of an "index", of the cards in the list by using the method
`create_id_index` which returns a persistent BTree object. In practice you can use BTrees quite like normal Python dict
and these can also be handily saved in the database as indexes.

#### Reading cards from files and strings

Cards can also be retrieved from the database (and from any other card lists) by reading them from list-like strings
and text files by using the `PCardList` - methods `from_str` and `from_file` which build new card lists of the cards
found in the list. The accepted format of the strings and text files is similar to the standard Apperentice and MWS
deck lists:

```
//Creatures (8)
1 Wild Mongrel [od]
4 Aquamoeba (od)
2 Werebear
noose constrictor

//Enchantments (1)
1 [ULG] rancor

//Sideboard (1)

SB: 2 Werebear
...
```

Comment lines can be specified with '//', possible desired sets can be specified with either '(set_code)'
or '[set_code]' and sideboard cards with the prefix 'SB:'. The set brackets can be anywhere but the desired number
of cards must come before the name of the card. If no matching set is found, a card from a random set is returned.

Note, that this method is useful with the whole database of cards rather than a small list.

```
>>> my_deck1 = cards.from_str("""
3 Raging Ravine
1 Wooded Foothills
4 Verdant Catacombs
1 Stomping Ground
2 Overgrown Tomb
1 Blood Crypt
4 Blackcleave Cliffs
2 Swamp
1 Forest
4 Bloodstained Mire

2 Huntmaster of the Fells
4 Dark Confidant
2 Scavenging Ooze
4 Tarmogoyf
1 Fulminator Mage

1 Chandra, Torch of Defiance
4 Liliana of the Veil

1 Kolaghan's Command
4 Lightning Bolt
3 Terminate
3 Thoughtseize
2 Abrupt Decay
3 Inquisition of Kozilek

1 Fatal Push

1 Blooming Marsh
1 Kalitas, Traitor of Ghet

//Sideboard
SB: 3 Fulminator Mage
SB: 2 Collective Brutality
SB: 1 Anger of the Gods
SB: 1 Kolaghan's Command
SB: 2 Ancient Grudge
SB: 1 Maelstrom Pulse
SB: 1 Liliana, the Last Hope
SB: 2 Surgical Extraction
SB: 1 Rakdos Charm
SB: 1 Damnation""")

>>> print(my_deck1.deck_str())

// Lands (24)
3 Raging Ravine [wwk]
1 Wooded Foothills [g09]
4 Verdant Catacombs [zen]
1 Stomping Ground [exp]
2 Overgrown Tomb [rtr]
1 Blood Crypt [dis]
4 Blackcleave Cliffs [som]
2 Swamp [td0]
1 Forest [ice]
4 Bloodstained Mire [g09]
1 Blooming Marsh [kld]

// Creatures (14)
4 Dark Confidant [mma]
2 Scavenging Ooze [cmd]
4 Tarmogoyf [mm3]
1 Fulminator Mage [shm]
2 Huntmaster of the Fells // Ravager of the Fells [dka]
1 Kalitas, Traitor of Ghet [pogw]

// Instants (11)
1 Kolaghan's Command [pdtk]
4 Lightning Bolt [mm2]
3 Terminate [cmd]
2 Abrupt Decay [prm]
1 Fatal Push [f17]

// Sorceries (6)
3 Thoughtseize [ima]
3 Inquisition of Kozilek [cn2]

// Planeswalkers (5)
4 Liliana of the Veil [isd]
1 Chandra, Torch of Defiance [ps18]

// Sideboard (15)
SB:3 Fulminator Mage [mm2]
SB:2 Collective Brutality [pemn]
SB:1 Anger of the Gods [ima]
SB:1 Kolaghan's Command [dtk]
SB:2 Ancient Grudge [tsp]
SB:1 Maelstrom Pulse [mma]
SB:1 Liliana, the Last Hope [emn]
SB:2 Surgical Extraction [prm]
SB:1 Rakdos Charm [c17]
SB:1 Damnation [prm]
```

You can also structure the deck strings in different ways. For example by color and without set codes:

```
>>> print(my_deck.deck_str(group_by='color', add_set_codes=False))

// Black (16)
3 Inquisition of Kozilek
1 Kalitas, Traitor of Ghet
4 Liliana of the Veil
3 Thoughtseize
4 Dark Confidant
1 Fatal Push

// Colorless (24)
2 Overgrown Tomb
1 Wooded Foothills
2 Swamp
3 Raging Ravine
1 Stomping Ground
1 Blooming Marsh
4 Blackcleave Cliffs
4 Bloodstained Mire
4 Verdant Catacombs
1 Forest
1 Blood Crypt

// Red (5)
1 Chandra, Torch of Defiance
4 Lightning Bolt

// Multicolor (9)
2 Abrupt Decay
1 Fulminator Mage
2 Huntmaster of the Fells // Ravager of the Fells
1 Kolaghan's Command
3 Terminate

// Green (6)
4 Tarmogoyf
2 Scavenging Ooze

// Sideboard (15)
SB: 2 Surgical Extraction
SB: 1 Damnation
SB: 1 Maelstrom Pulse
SB: 1 Kolaghan's Command
SB: 2 Collective Brutality
SB: 1 Rakdos Charm
SB: 1 Anger of the Gods
SB: 2 Ancient Grudge
SB: 3 Fulminator Mage
SB: 1 Liliana, the Last Hope
```

`from_file` works exactly the same way except it reads the contents from a text file.

#### More examples

We can use the looser `where` to look for cards with for example certain power or toughness by using the fact that
for numerical attributes it is enough for the argument to be equal or larger. Note, that for `power`, `toughness` and
`loyalty` you can use the numerical versions `power_num`, `touhness_num` and `loyalty_num`.

Creatures in Odyssey with power > 5:

```
>>> ody = sets.where_exactly(code='ody')[0]
>>> ody.creatures().where(power_num=5, invert=True).pprint()

Unnamed card list created at 2018-07-20 15:32:59.202900
---------------------------------------------------------------------------------------
Card                    Set   Type                                   Cost        Rarity
---------------------------------------------------------------------------------------
1 Amugaba               ody   Creature - Illusion                    {5}{U}{U}   rare
1 Kamahl, Pit Fighter   ody   Legendary Creature - Human Barbarian   {4}{R}{R}   rare
1 Ashen Firebeast       ody   Creature - Elemental Beast             {6}{R}{R}   rare
```

White creatures Not including multicolors in Odyssey with power <= 2 AND toughness <= 2:

```
>>> ody = sets.where_exactly(code='ody')[0]
>>> ody.creatures().where(power_num=2).where(toughness_num=2).where_exactly(colors='W').pprint()

Unnamed card list created at 2018-07-20 16:03:08.122375 with a total of 20 cards
------------------------------------------------------------------------------------------
Card                      Set   Type                                Cost        Rarity
------------------------------------------------------------------------------------------
1 Mystic Crusader         ody   Creature - Human Nomad Mystic       {1}{W}{W}   rare
1 Beloved Chaplain        ody   Creature - Human Cleric             {1}{W}      uncommon
1 Devoted Caretaker       ody   Creature - Human Cleric             {W}         rare
1 Confessor               ody   Creature - Human Cleric             {W}         common
1 Dogged Hunter           ody   Creature - Human Nomad              {2}{W}      rare
1 Tireless Tribe          ody   Creature - Human Nomad              {W}         common
1 Soulcatcher             ody   Creature - Bird Soldier             {1}{W}      uncommon
1 Master Apothecary       ody   Creature - Human Cleric             {W}{W}{W}   rare
1 Aven Archer             ody   Creature - Bird Soldier Archer      {3}{W}{W}   uncommon
1 Lieutenant Kirtar       ody   Legendary Creature - Bird Soldier   {1}{W}{W}   rare
1 Nomad Decoy             ody   Creature - Human Nomad              {2}{W}      uncommon
1 Mystic Penitent         ody   Creature - Human Nomad Mystic       {W}         uncommon
1 Cantivore               ody   Creature - Lhurgoyf                 {1}{W}{W}   rare
1 Aven Cloudchaser        ody   Creature - Bird Soldier             {3}{W}      common
1 Hallowed Healer         ody   Creature - Human Cleric             {2}{W}      common
1 Pianna, Nomad Captain   ody   Legendary Creature - Human Nomad    {1}{W}{W}   rare
1 Auramancer              ody   Creature - Human Wizard             {2}{W}      common
1 Mystic Visionary        ody   Creature - Human Nomad Mystic       {1}{W}      common
1 Dedicated Martyr        ody   Creature - Human Cleric             {W}         common
1 Patrol Hound            ody   Creature - Hound                    {1}{W}      common
```

Auras in Odyssey with cmc <= 2:

```
>>> ody = sets.where_exactly(code='ody')[0]
>>> ody.where(cmc=2).where(type_line='aura').pprint()

Unnamed card list created at 2018-07-20 16:05:48.340844 with a total of 7 cards
-------------------------------------------------------------------
Card                 Set   Type                 Cost     Rarity
-------------------------------------------------------------------
1 Aboshan's Desire   ody   Enchantment - Aura   {U}      common
1 Psionic Gift       ody   Enchantment - Aura   {1}{U}   common
1 Primal Frenzy      ody   Enchantment - Aura   {G}      common
1 Immobilizing Ink   ody   Enchantment - Aura   {1}{U}   common
1 Druid's Call       ody   Enchantment - Aura   {1}{G}   uncommon
1 Kirtar's Desire    ody   Enchantment - Aura   {W}      common
1 Kamahl's Desire    ody   Enchantment - Aura   {1}{R}   common
```

### Saving your own things in the database

A good guide about saving things in ZODB can be found here:
http://www.zodb.org/en/latest/guide/writing-persistent-objects.html

Any objects mentioned above are already Persistent, so they can be conveniently saved. For example any `PCardList`
objects can easily be saved with

```
>>> my_favourite_cards = cards.where_exactly(name='Counterspell', set='plgm') + cards.where_exactly(name='Cancel', set='p10')
>>> my_favourite_cards.name = 'My fav cards'
>>> mtg_db.root.my_favourite_cards = my_favourite_cards
>>> mtg_db.commit()
```

You can then easily later append more cards with

```
>>> mtg_db.root.my_favourite_cards.append(cards.where_exactly(name='Mana drain')[0])
>>> mtg_db.commit()
```

and access them later with

```
>>> my_fav_cards = mtg_db.root.my_favourite_cards
>>> my_fav_cards.pprint()

Card list "My fav cards" created at 2018-07-18 18:36:54.135282
-----------------------------------------------------
Card             Set    Type      Cost        Rarity
-----------------------------------------------------
1 Counterspell   plgm   Instant   {U}{U}      rare
1 Cancel         p10    Instant   {1}{U}{U}   rare
1 Mana Drain     ima    Instant   {U}{U}      mythic
```

You can similarly save decks or other card lists for example by using a `PersistentList` which works almost like a
normal Python list:

```
>>> from persistent.list import PersistentList

>>> my_deck1 = cards.from_str("""
3 Raging Ravine
1 Wooded Foothills
4 Verdant Catacombs
1 Stomping Ground
2 Overgrown Tomb
1 Blood Crypt
4 Blackcleave Cliffs
2 Swamp
1 Forest
4 Bloodstained Mire

2 Huntmaster of the Fells
4 Dark Confidant
2 Scavenging Ooze
4 Tarmogoyf
1 Fulminator Mage

1 Chandra, Torch of Defiance
4 Liliana of the Veil

1 Kolaghan's Command
4 Lightning Bolt
3 Terminate
3 Thoughtseize
2 Abrupt Decay
3 Inquisition of Kozilek

1 Fatal Push

1 Blooming Marsh
1 Kalitas, Traitor of Ghet

//Sideboard
SB: 3 Fulminator Mage
SB: 2 Collective Brutality
SB: 1 Anger of the Gods
SB: 1 Kolaghan's Command
SB: 2 Ancient Grudge
SB: 1 Maelstrom Pulse
SB: 1 Liliana, the Last Hope
SB: 2 Surgical Extraction
SB: 1 Rakdos Charm
SB: 1 Damnation""")

>>> my_deck2 = cards.from_str("""
//Main
4 Baral, Chief of Compliance
4 Desperate Ritual
4 Gifts Ungiven
2 Goblin Electromancer
3 Grapeshot
4 Island
4 Manamorphose
1 Mountain
1 Noxious Revival
3 Opt
2 Past in Flames
4 Pyretic Ritual
2 Remand
1 Repeal
4 Serum Visions
4 Shivan Reef
4 Sleight of Hand
4 Spirebluff Canal
4 Steam Vents
1 Unsubstantiate

//Sideboard
SB: 1 Abrade
SB: 1 Echoing Truth
SB: 1 Empty the Warrens
SB: 1 Gigadrowse
SB: 3 Lightning Bolt
SB: 4 Pieces of the Puzzle
SB: 2 Pyromancer Ascension
SB: 1 Shattering Spree
SB: 1 Wipe Away
""")
>>> my_decks = PersistentList(my_deck1, my_deck2)
>>> mtg_db.root.my_decks = my_decks
>>> mtg_db.commit()
```

and then later on you can append more lists and access them the same way with single cards.

Another thing you might want to save in the database is for example an index of cards for faster retrieval. An 'index'
in this case would be a fast persistent dict like BTree where the keys are some unique identifiers. For `PCardList`,
there already exists the method `create_id_index` which returns a `BTree` in which the cards are indexed by their unique
'id' values and each id maps to a single card object found in the original list. This is handy if called on the whole
database and saved:

```
>>> my_card_index = cards.create_id_index()
>>> mtg_db.root.my_card_index = my_card_index
>>> mtg_db.commit()
```

Now single cards can be retrieved very speedily from the index by using their `id`'s:

```
>>> print(mtg_db.root.my_card_index['0a448077-3b1f-4efd-a606-e3ff40fe1621'])

Counterspell (wc00)
```

Similarly, the index can also be used to speedily check if some object exists in the database.

`PCardList` objects have a similar unique id so they are also simple to index if needed.

### Working with sets and set lists

`PSet` and `PSetList` work very similarly to `PCard` and `PCardList`. The difference is that `PSet`
is also a `PCardList` and contains a set of it's own characteristic Magic: The Gathering set attributes. `PSetList`
objects can be searched, filtered and sorted exactly like `PCardList` objects by using the methods `where`,
`where_exactly`, `filtered` and `sorted` which similarly return new `PSetList` objects.

The sets are saved in the database as a `PSetList`.

#### Some examples

Sets in Masques block:

```
>>> sets.where(block='Masques').pprint()

Unnamed set list created at 2018-07-18 13:39:44.602675
-----------------------------------------------------
Set                 Code  Block     Type        Cards
-----------------------------------------------------
Prophecy            pcy   Masques   expansion   143
Nemesis             nem   Masques   expansion   143
Mercadian Masques   mmq   Masques   expansion   350
```

All the sets containing a Negate:

```
>> sets.filtered(lambda pset: any(pset.where_exactly(name='Negate'))).pprint()

Unnamed set list created at 2018-07-18 13:39:52.329598
---------------------------------------------------------------------------------
Set                          Code  Block                 Type               Cards
---------------------------------------------------------------------------------
Signature Spellbook: Jace    ss1                         spellbook          8
Battlebond                   bbd                         draft_innovation   256
Rivals of Ixalan             rix   Ixalan                expansion          205
Aether Revolt                aer   Kaladesh              expansion          194
Conspiracy: Take the Crown   cn2                         draft_innovation   222
Oath of the Gatewatch        ogw   Battle for Zendikar   expansion          186
Magic Origins                ori                         core               288
Dragons of Tarkir            dtk   Khans of Tarkir       expansion          264
Magic 2015                   m15                         core               284
Magic 2014                   m14                         core               249
Magic 2013                   m13                         core               249
Magic 2012                   m12                         core               249
Magic 2011                   m11                         core               249
Duels of the Planeswalkers   dpa                         box                113
Magic 2010                   m10                         core               249
Magic Player Rewards 2009    p09                         promo              9
Morningtide                  mor   Lorwyn                expansion          150
Magic Online Promos          prm                         promo              1198
```

Normal standard-legal sets without promos:

```
>>> standard_sets = sets.where(set_type='promo', invert=True)
>>> def standard_legal(pset):
        return len(pset) and len(pset) == len(
            pset.filtered(lambda card: card.legalities['standard'] == 'legal' or card.legalities['standard'] == 'banned')
        )

>>> standard_sets.filtered(standard_legal).pprint()

Unnamed set list created at 2018-07-23 12:33:31.340701
--------------------------------------------------------
Set                   Code  Block      Type        Cards
--------------------------------------------------------
Core Set 2019         m19              core        314
Dominaria             dom              expansion   280
Rivals of Ixalan      rix   Ixalan     expansion   205
Ixalan                xln   Ixalan     expansion   289
Hour of Devastation   hou   Amonkhet   expansion   209
Amonkhet              akh   Amonkhet   expansion   287
Welcome Deck 2017     w17              starter     30
Aether Revolt         aer   Kaladesh   expansion   194
Kaladesh              kld   Kaladesh   expansion   274
```

### What else can you do with cards and sets?

The rest of the methods and functionalities are quite self explanatory and well documented, so they don't need further
guidance. You can for example create random booster packs from card lists with `random_pack`, download images from
Scryfall with `download_images_from_scryfall`, create sheets of proxy images of cards from Scryfall with
`create_proxies`, turn your lists back to JSON with `json` and many more things.

## Notes and possible problems

#### Possible bugs

The tools are somewhat decently tested for Scryfall data but some bugs and weird behavior are to be expected,
especially with some special cards.

Currently, the data from magicthegathering.io is not tested but it should still work quite like Scryfall data. If you
are using mtgio, be mindful of the differences between them.

#### Some things about the database

- Be mindful when using multiple different storages and formatting/re-updating old ones when you have saved your own
  lists. If something goes wrong and the old objects in the base of the database get replaced by new objects, the old
  objects which have references in your own saved lists don't function in the same way anymore. This is because the newly
  created object instances are not equal to the old ones in the database even though they have the same id's. Make sure
  you back up the old databases before updates. At the moment there is no good support for recovery.

- The first time you access any objects in the database after opening it takes a lot of time. This is because the data
  is not yet cached at that point. When the data is cached, the objects are actually retrieved from the cache without
  database interactions, which is fast.

- The database can't be used from multiple threads by default. `Storage` and `DB` instances can, but to use transactions
  and object access you must use different connections and transaction managers for each thread.

- Objects can be used as keys in a dictionary but it might be slow.

- Some attributes of the objects like lists and dicts, (for example `colors` and `card_faces`) are not immutable.
  ZODB does not automatically recognize changes to these kinds of attributes. When changing values inside an object's
  mutable attributes, you must manually set the object's `_p_changed` attribute to `True` before calling `commit`. Often
  simpler way is to just use assignment or `setattr` instead of changing something inside the attribute. In this case,
  when the whole attribute is reassigned, ZODB will recognize this and changes are saved when committing.

## Authors

**Esko-Kalervo Salaka**

## License

Copyright © 2018 Esko-Kalervo Salaka.
All rights reserved.

Zope Public License (ZPL) Version 2.1

A copyright notice accompanies this license document that identifies the
copyright holders.

This license has been certified as open source. It has also been designated as
GPL compatible by the Free Software Foundation (FSF).

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions in source code must retain the accompanying copyright
   notice, this list of conditions, and the following disclaimer.

2. Redistributions in binary form must reproduce the accompanying copyright
   notice, this list of conditions, and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Names of the copyright holders must not be used to endorse or promote
   products derived from this software without prior written permission from the
   copyright holders.

4. The right to distribute this software or to use it for any purpose does not
   give you the right to use Servicemarks (sm) or Trademarks (tm) of the
   copyright
   holders. Use of them is covered by separate agreement with the copyright
   holders.

5. If any files are modified, you must cause the modified files to carry
   prominent notices stating that you changed the files and the date of any
   change.

Disclaimer

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ''AS IS'' AND ANY EXPRESSED
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Acknowledgments

This software uses ZODB, a native object database for Python, which is a
copyright © by Zope Foundation and Contributors.

This software uses Scryfall's rest-like API which is a copyright © by Scryfall LLC.

This software uses rest-like API of magicthegathering.io which is a copyright © by Andrew Backes.

This software uses the Python Imaging Library (PIL) which is a copyright © 1997-2011 by Secret Labs AB and
copyright © 1995-2011 by Fredrik Lundh

All the graphical and literal information and data related to Magic: The Gathering which can be handled with this
software, such as card information and card images, is copyright © of Wizards of the Coast LLC, a
Hasbro inc. subsidiary.

This software is in no way endorsed or promoted by Scryfall, Zope Foundation, magicthegathering.io or
Wizards of the Coast.

This software is free and is created for the purpose of creating new Magic: The Gathering content and software, and
just for fun.
