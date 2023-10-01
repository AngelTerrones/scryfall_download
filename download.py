import os
import sys
import json
import requests
from tqdm import tqdm


def card_exists(card_name: str):
    return os.path.exists(f'images/{card_name}')

def download_card(scryfallId: str, card_name: str, face: str):
    if os.path.exists(f'images/{card_name}'):
        return
    dir1 = scryfallId[0]
    dir2 = scryfallId[1]
    url = f'https://cards.scryfall.io/png/{face}/{dir1}/{dir2}/{scryfallId}.png'
    r = requests.get(url)
    open(f'images/{card_name}', 'wb').write(r.content)


def check_hires(scryfallId: str):
    r = requests.get(f'https://api.scryfall.com/cards/{scryfallId}')
    return r.json()['highres_image']


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
        for card in tqdm(set_data['cards']):
            number    = card['number']
            name      = card.get('faceName', card['name'])
            card_name = f'{set_name.lower()}-{number}-{name}.png'
            card_name = card_name.replace('//', '-')
            if card_exists(card_name=card_name):
                continue
            side       = card.get('side', 'a')
            face       = 'front' if side == 'a' else 'back'
            scryfallId = card['identifiers']['scryfallId']
            # check if the card has hires image
            if check_hires(scryfallId=scryfallId):
                download_card(
                    scryfallId=scryfallId,
                    card_name=card_name,
                    face=face
                )

if __name__ == '__main__':
    download_images(sys.argv[1])
