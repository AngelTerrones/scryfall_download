import os
import sys
import time
import json
import glob
import requests
from tqdm import tqdm
from collections import namedtuple


s = requests.Session()
Card = namedtuple('Card', ['scryfallId', 'face'])


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


def download_images(database):
    os.makedirs('images', exist_ok=True)
    # Load the JSON
    with open(database, 'r', encoding='utf-8') as f:
        cards = json.load(f)
        cards = cards['data']

    # Download
    # data is grouped by set
    for set_name, set_data in cards.items():
        print(f'Downloading set: {set_name}')
        downloaded_cards = set(map(os.path.basename, glob.glob(f'images/{set_name.lower()}-*')))
        set_cards = dict()
        for card in tqdm(set_data['cards']):
            number    = card['number']
            name      = card.get('faceName', card['name'])
            card_name = f'{set_name.lower()}-{number}-{name}.png'
            card_name = card_name.replace('//', '-')
            if card_name in downloaded_cards:
                continue
            if card['language'] != 'English':
                continue
            side       = card.get('side', 'a')
            face       = 'front' if side == 'a' else 'back'
            scryfallId = card['identifiers']['scryfallId']
            set_cards[card_name] = Card(scryfallId=scryfallId, face=face)
        disable = len(set_cards) == 0
        for card_name, card in tqdm(set_cards.items(), disable=disable):
            # check if the card has hires image
            if check_hires(scryfallId=card.scryfallId):
                download_card(
                    scryfallId=scryfallId,
                    card_name=card_name,
                    face=card.face
                )

if __name__ == '__main__':
    download_images(sys.argv[1])
