import os
import sys
import time
import json
import glob
import requests
from tqdm import tqdm
from collections import namedtuple


s = requests.Session()
Card = namedtuple('Card', ['scryfallId', 'face', 'nonfoil', 'art_id'])


def get_url(url: str):
    ii = 3
    while ii > 0:
        try:
            return s.get(url)
        except:
            ii = ii - 1
            time.sleep(5)
    return None


def download_card(scryfallId: str, card_name: str, face: str):
    if os.path.exists(f'images/{card_name}'):
        return
    dir1 = scryfallId[0]
    dir2 = scryfallId[1]
    url = f'https://cards.scryfall.io/png/{face}/{dir1}/{dir2}/{scryfallId}.png'
    r = get_url(url)
    if r != None:
        open(f'images/{card_name}', 'wb').write(r.content)


def check_hires(scryfallId: str):
    r = get_url(f'https://api.scryfall.com/cards/{scryfallId}')
    if r != None:
        return r.json()['highres_image']
    return False


def download_images(database: str, card_type: str):
    if card_type not in ('cards', 'tokens'):
        raise Exception('Valid card types: [cards, tokens]')

    os.makedirs('images', exist_ok=True)
    # Load the JSON
    with open(database, 'r', encoding='utf-8') as f:
        cards = json.load(f)
        cards = cards['data']

    # Download
    # data is grouped by set
    for set_name, set_data in cards.items():
        if set_data['isOnlineOnly']:
            print(f'Set: {set_name} is OnlineOnly')
            continue
        print(f'Downloading set: {set_name}')
        downloaded_cards = set(map(os.path.basename, glob.glob(f'images/{set_name.lower()}-*')))
        set_cards = dict()
        unique_art_id = set()
        for card in tqdm(set_data[card_type], disable=len(set_data[card_type]) == 0):
            language  = card['language']
            number    = card['number']
            layout    = card['layout']
            nonfoil   = card['finishes'] != ['nonfoil']
            art_id    = card['identifiers']['scryfallIllustrationId']
            name      = card.get('faceName', card['name'])
            card_name = f'{set_name.lower()}-{number}-{name}.png'
            card_name = card_name.replace('//', '-')
            # add the art ID
            unique_art_id.add(art_id)
            # ignore card if exists, or language != english
            if card_name in downloaded_cards:
                continue
            if language != 'English':
                continue
            # get the face. Meld cards does not have back, all are front faces...
            if layout == 'meld':
               face = 'front'
            else:
               face = 'front' if card.get('side', 'a') == 'a' else 'back'
            # store card
            scryfallId = card['identifiers']['scryfallId']
            set_cards[card_name] = Card(
                scryfallId=scryfallId,
                face=face,
                nonfoil=nonfoil,
                art_id=art_id
            )
        for card_name, card in tqdm(set_cards.items(), disable=len(set_cards) == 0):
            if card.nonfoil and card.art_id in unique_art_id:
                continue
            # check if the card has HiRes image
            if check_hires(scryfallId=card.scryfallId):
                download_card(
                    card_name=card_name,
                    scryfallId=card.scryfallId,
                    face=card.face
                )

if __name__ == '__main__':
    download_images(sys.argv[1], sys.argv[2])
