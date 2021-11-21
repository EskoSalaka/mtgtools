import asyncio
import concurrent.futures
import math
import sys
import requests

from urllib.error import URLError

from mtgtools.PSet import PSet
from mtgtools.PSetList import PSetList
from mtgtools.PCard import PCard

mtgio_sets_url = 'https://api.magicthegathering.io/v1/sets/'
mtgio_cards_url = 'https://api.magicthegathering.io/v1/cards'
mtgio_cards_page_url = 'https://api.magicthegathering.io/v1/cards?page={}'

scryfall_sets_url = 'https://api.scryfall.com/sets'
scryfall_card_search_url = 'https://api.scryfall.com/cards/search?include_extras=true&order=set&page={}&q=e%3A{}&unique=prints'
scryfall_bulk_data_url = 'https://api.scryfall.com/bulk-data'


def get_response_json(url, headers=None):
    try:
        return requests.get(url, headers=headers).json()
    except URLError as err:
        print('Warning: Something went wrong with requesting url {}: '.format(url) + str(err))
        return {}


def get_scryfall_card_bulks(headers=None):
    return get_response_json(scryfall_bulk_data_url, headers)


def download_scryfall_bulk_data(url, headers=None):
    return get_response_json(url, headers)


def process_card_page_response(card_page_uri, data_identifier, headers=None):
    response_json = get_response_json(card_page_uri, headers)

    if response_json:
        if data_identifier in response_json:
            return [PCard(card_json) for card_json in response_json[data_identifier]]
    return []


def get_tot_mtgio_cards():
    try:
        return int(requests.get(mtgio_cards_url, headers={'User-Agent': 'Mozilla/5.0'}).headers.get('Total-Count'))
    except URLError as err:
        print('Something went wrong with requesting url {}: '.format(mtgio_cards_url) + str(err))
        return 0


def process_scryfall_sets(current_sets):
    current_set_codes = [pset.code for pset in current_sets]
    set_response_dicts = get_response_json(scryfall_sets_url)['data']

    for set_response_dict in set_response_dicts:
        if set_response_dict['code'] in current_set_codes:
            current_sets.where_exactly(code=set_response_dict['code'])[0].update(set_response_dict)
        else:
            current_sets.append(PSet(set_response_dict))

    obsolete_sets = PSetList()
    api_set_codes = [set_response_dict['code'] for set_response_dict in set_response_dicts]

    for current_set_code in current_set_codes:
        if current_set_code not in api_set_codes:
            obsolete_sets.append(current_sets.where(code=current_set_code)[0])

    if len(obsolete_sets) > 0:
        print('-----------------------------------------------------------------------------------------------')
        print('The following sets are no longer found to be in the API possibly because their codes \n'
              'have been changed or they have been completely removed. These set objects in your local database \n'
              'will persist as they are if they are saved somewhere else but they are removed from main list. The \n'
              'card objects they contain are updated as normal')

        for obsolete_set in obsolete_sets:
            print('--- ', obsolete_set, ' ---')
            current_sets.remove(obsolete_set)

        print('-----------------------------------------------------------------------------------------------')

    return obsolete_sets


def process_mtgio_sets(sets):
    current_set_codes = [pset.code for pset in sets]
    set_response_dicts = get_response_json(mtgio_sets_url, headers={'User-Agent': 'Mozilla/5.0'})['sets']

    for set_response_dict in set_response_dicts:
        if set_response_dict['code'] in current_set_codes:
            sets.where_exactly(code=set_response_dict['code'])[0].update(set_response_dict)
        else:
            sets.append(PSet(set_response_dict))

    obsolete_sets = PSetList()
    api_set_codes = [set_response_dict['code'] for set_response_dict in set_response_dicts]

    for current_set_code in current_set_codes:
        if current_set_code not in api_set_codes:
            obsolete_sets.append(sets.where(code=current_set_code)[0])

    if len(obsolete_sets) > 0:
        print('-----------------------------------------------------------------------------------------------')
        print('The following sets are no longer found to be in the API possibly because their codes \n'
              'have been changed or they have been completely removed. These set objects in your local database \n'
              'will persist as they are if they are saved somewhere else but they are removed from main list. The \n'
              'card objects they contain are updated as normal')

        for obsolete_set in obsolete_sets:
            print('--- ', obsolete_set, ' ---')
            sets.remove(obsolete_set)

        print('-----------------------------------------------------------------------------------------------')

    return obsolete_sets


def process_mtgio_cards(sets, cards, verbose=True, workers=8):
    pages = int(math.ceil(get_tot_mtgio_cards() / 100))
    card_page_uris = [mtgio_cards_page_url.format(page) for page in range(1, pages + 1)]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_cards(sets, cards, card_page_uris, 'cards', verbose=verbose, workers=workers))
    loop.close()


def process_scryfall_cards(sets, cards, verbose=True, workers=8):
    card_page_uris = []
    for current_set in sets:
        card_page_uris.extend([scryfall_card_search_url.format(page, current_set.code) for page in
                               range(1, int(math.ceil(current_set.card_count / 175)) + 1)])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_cards(sets, cards, card_page_uris, 'data', verbose=verbose, workers=workers))
    loop.close()


async def process_cards(sets, cards, card_page_uris, data_identifier, verbose=True, workers=8):
    card_index = cards.create_id_index()
    set_index = {pset.code: pset for pset in sets}
    tot_requests = len(card_page_uris)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        loop = asyncio.get_event_loop()

        calls = []
        for card_page_uri in card_page_uris:
            if verbose:
                sys.stdout.write('\rSending requests: [{} / {}]'.format(len(calls) + 1, tot_requests))
            calls.append(loop.run_in_executor(executor, process_card_page_response, card_page_uri, data_identifier))
            await asyncio.sleep(0.1)

        processed = 0
        for future in asyncio.as_completed(calls):
            response_cards = await future

            for card in response_cards:
                if card.id not in card_index:
                    cards.append(card)

                    # Check for set not found
                    pset = set_index.get(card.set)
                    if pset is not None:
                        pset._cards.append(card)
                else:
                    card_index[card.id].update(card.__dict__)

            processed += 1
            if verbose:
                sys.stdout.write('\rProcessing responses: [{} / {}]'.format(processed, tot_requests))


def process_cards_bulk(sets, cards, bulk_card_data, verbose=True):
    card_index = cards.create_id_index()
    set_index = {pset.code: pset for pset in sets}
    tot_cards = len(bulk_card_data)

    processed = 0
    for card_json in bulk_card_data:
        if card_json['id'] not in card_index:
            processed_card = PCard(card_json)
            cards.append(processed_card)

            # Check for set not found
            pset = set_index.get(processed_card.set)
            if pset is not None:
                pset._cards.append(processed_card)
        else:
            card_index[card_json['id']].update(card_json)

        processed += 1
        if verbose:
            sys.stdout.write('\rProcessing card: [{} / {}]'.format(processed, tot_cards))
