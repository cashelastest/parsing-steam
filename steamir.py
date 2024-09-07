import requests
import re
from bs4 import BeautifulSoup
import psycopg2
conn = psycopg2.connect(dbname = "Post", user = "postgres", password = "", host = "localhost", port = 5432)
c = conn.cursor()
def insert(values):
    

    postgres_insert_query = """ INSERT INTO post(game_id,title, description, price_initial, price_final, photo, is_posted,players) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
    c.execute(postgres_insert_query, values)
    conn.commit()
    print("ok")
def select(verbose=True):
    c.execute("""SELECT game_id FROM post""")
    
    i = []
    for row in c.fetchall():
        
        game_id = int(' '.join(map(str, row)))
        i.append(game_id)
        print(i)
    return i 


CLEANR = re.compile('<.*?>') 
def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def search_steam_game(game_title):
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    data = response.json()

    apps = data['applist']['apps']
    for app in apps:
        if app['name'].lower() == game_title.lower():
            return app['appid']
    return "Game not found."

def get_game_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=ukrainian"
    response = requests.get(url)
    data = response.json()
    try:
        if data[str(app_id)]['success']:
            game_data = data[str(app_id)]['data']
            name = game_data['name']
            description = game_data['short_description']
            price_final = game_data['price_overview']['final_formatted']
            price_intial = f"{int(game_data['price_overview']['initial']/100)}"+"₴"
            photo = game_data['header_image']

            return {
                'name': name,
                'description': cleanhtml(description),
                'price_final': price_final,
                'price_intial': price_intial,
                "photo":photo
            }
        else:
            return 'details not found'
    except:
            return {
                'name': 0,
                'description': 0,
                'price_final': 0,
                'price_intial': 0,
            }

def get_player_count(appid):
    url = f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}'
    response = requests.get(url)
    data = response.json()
    try:
        player_count = int(data['response']['player_count']) *(-1)
    except:
        print("EEEEEEEEEEEEEEERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        player_count = 0
    return player_count


def main ():
    api_key = 'ee8a3578d6be6dde8c2855abc9ffb45145fbd704'


    discounts_url = f'https://api.isthereanydeal.com/v01/deals/list/?key={api_key}&limit=32000'

    # Making the request
    response = requests.get(discounts_url)

    # Print the status code to check if the request was successful
    print(f"Status Code: {response.status_code}")

    # Print the raw response text for debugging
    print(f"Raw Response: {response.text}")

    # Ensure the response is valid JSON
    try:
        data = response.json()
        
    except ValueError as e:
        print("Response is not valid JSON")
        print(e)
        data = {}

    # Checking if data is available

    print(discounts_url)

    deals = data.get('list', [])
    number = 0
    accept = 0
    used_games_id = select()
    if deals:
        for deal in deals:
            number +=1
            
            title = deal.get('title', 'N/A')
            store = deal.get('shop', {}).get('name', 'N/A')
            if store!="Steam":
                print('No Steam market for thi sale')
                continue 
            game = search_steam_game(title)
            if game in used_games_id:
                print("Game is already in db")
                continue
            popularity = get_player_count(game)
            print(f"title: {title}")
            if popularity == 0:
                print(f"popularity: No players")
            else:
                print(f"popularity: {popularity}")
            print(number)
            if popularity>-5:
                continue
            info = get_game_details(game)
            try:
                values = [game, title, info['description'], info["price_intial"], info['price_final'], info["photo"],0, popularity]
                insert(values)
            except:
                print('Error in request. Continue')
            print(f"id: {game}")
            print(f"title: {title}")
            print(f"info: {info}")
            print(f"popularity: {popularity}")
            accept+=1
            print(accept)

            

    else:
        # If 'data' is not in the response, print the entire response
        print("Failed to retrieve data.")
        print("Response JSON structure:")
    #    print(data)

while True:
    main()
