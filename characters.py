import requests
from bs4 import BeautifulSoup
import mongo_connetion

db = mongo_connetion.get_mongo_connection()

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://yokkohama.tistory.com/392',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

characters = soup.select('.txc-table > tbody > tr > td > p > span')
for character in characters:
    db.characters.insert_one({'trait' : character.text})