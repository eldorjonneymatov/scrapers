import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


def get_player_ratings(data):

    rank_data = data.find('div', class_='master-players-rating-rank')
    rank = int(rank_data.text.split('#')[-1].strip())
    
    ratings = data.select('.master-players-rating-player-rank')
    return [rank] + [int(rating.text) for rating in ratings]


def get_player_profile_info(data):
    result = {}
    default_avatar_url = "https://www.chess.com/bundles/web/images/user-image.svg"
    result['avatar_url'] = data.find('img').get('data-src', default_avatar_url)
    
    title = data.find('span')
    if title: 
        result['title'] = title.text
    
    result['country'] = data.select('.country-flags-component')[0]['v-tooltip'].split()[-1]
    
    profile_data = data.find('a', class_='master-players-rating-username')
    result['url'] = profile_data['href']
    result['name'] = profile_data.text.strip()
    result['username'] = result['url'].split('/')[-1]

    return result


def single_page_scraper(page_data, output_file):
    all_players_info = page_data.select('tbody tr')
    if all_players_info:
        for player_info in all_players_info:
            profile_data = player_info.find('div', 'master-players-rating-user-wrapper')
            player = get_player_profile_info(profile_data)
            
            rank, classic_rating, rapid_rating, blitz_rating = get_player_ratings(player_info)
            player.update({
                'rank':rank,
                'classic_rating':classic_rating,
                'rapid_rating':rapid_rating, 
                'blitz_rating':blitz_rating 
            })
            json.dump(player, output_file)
    else:
        raise StopIteration
    

def chess_rating_scraper():
    url = 'https://www.chess.com/ratings'
    page_no = 1
    with open('ratings.json', 'w') as f:
        while True:
            try:
                tqdm.write(f"page: {page_no}", end='\r')                
                html_data = requests.get(f'{url}?page={page_no}').text
                data = BeautifulSoup(html_data, 'lxml')
                single_page_scraper(data, f)
                page_no += 1
            except Exception as e:
                print(e)
                break

        
chess_rating_scraper()