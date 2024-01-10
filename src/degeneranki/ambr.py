 
import requests

data_url = f"https://api.ambr.top/v2/en/{}"
image_url = f"https://api.ambr.top/assets/UI/{}.png"

class Character:
    
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.rarity = data['rank']
        self.icon = image_url.format(data['icon'])
        self.gacha = self.icon.replace('AvatarIcon', 'Gacha_AvatarImg')

class Weapon:
    
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.rarity = data['rank']
        self.icon = image_url.format(data['icon'])

def _request_data(api_endpoint):
    response = requests.get(data_url.format(api_endpoint)
    return response.json()

def get_characters():
    return _request_data("avatar")

def get_weapons():
    return _request_data("weapon")

def get_character_details(id):
    return _request_data("avatar/{}".format(id))

def get_weapon_details(id):
    return _request_data("weapon/{}".format(id))
