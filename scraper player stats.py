# Python library used for scraping and HTML parsing
import cloudscraper
from bs4 import BeautifulSoup

# URL that will be scraped
url = "https://fbref.com/en/matches/a50ce74d/Bayern-Munich-Werder-Bremen-September-26-2025-Bundesliga"
matchid = 6  # Hardcode matchid. ID for the match in my database


scraper = cloudscraper.create_scraper() # creates a Cloudflare-aware scraper session
response = scraper.get(url) # Downlooads page html
soup = BeautifulSoup(response.text, "html.parser") # parses page intr structured format to navigate

# This loop finds the table with caption Werder Bremen Player Stats
werder_table = None
for table in soup.find_all("table"):
    caption = table.find("caption")
    if caption and "Werder Bremen Player Stats" in caption.get_text():
        werder_table = table # Stores correct table in werder_table
        break

if not werder_table: # stops if Werder Bremen is not found and displays error message
    raise Exception("❌ Could not find Werder Bremen stats table")

# each player stat appears as table row in table body
rows = werder_table.find("tbody").find_all("tr") # rows is a list of all player rows

# dict connects players to their playerid in my SQL Database via their names
name_to_id = {
    "karl jakob hein": 1,
    "mio backhaus": 3,
    "markus kolke": 4,
    "stefan smarkalev": 5,
    "marco friedl": 6,
    "maximilian wöber": 7,
    "niklas stark": 8,
    "amos pieper": 9,
    "julian malatini": 10,
    "abdoul coulibaly": 11,
    "mick schmetgens": 12,
    "felix agu": 13,
    "olivier deman": 14,
    "yukinari sugawara": 15,
    "mitchell weiser": 16,
    "isaac schmidt": 17,
    "senne lynen": 18,
    "skelly alvero": 19,
    "wesley adeh": 20,
    "jens stage": 21,
    "leonardo bittencourt": 22,
    "romano schmid": 23,
    "cameron puertas": 24,
    "patrice čović": 25,
    "isak hansen-aarøen": 26,
    "samuel mbangula": 27,
    "marco grüll": 28,
    "justin njinmah": 29,
    "victor boniface": 30,
    "keke maximilian topp": 31,
    "salim musah": 32,
}

players = [] # stores player data
scraped_players = set() # stores players found in table, to figure out which players were not found

# Extract stats for players
for row in rows:
    player_name = row.find("th").get_text(strip=True).lower() # get_text() removes extra space | .lower() enables matching even if capitalization differs.
    playerid = name_to_id.get(player_name)

    if not playerid:
        print(f"⚠️ Skipping {player_name}, not in DB map") # Skips if player is not in dictionary
        continue

    # Extracts values for the given stats, return 0 if stat is missing
    def get_stat(stat):
        cell = row.find("td", {"data-stat": stat})
        return cell.get_text(strip=True) if cell else "0"

    goals = int(get_stat("goals") or 0)
    assists = int(get_stat("assists") or 0)
    yellowcards = int(get_stat("cards_yellow") or 0)
    redcards = int(get_stat("cards_red") or 0)
    shots = int(get_stat("shots") or 0)
    passaccuracy = float(get_stat("passes_pct") or 0)
    passes = int(get_stat("passes") or 0)
    crosses = int(get_stat("crosses") or 0)
    minutesplayed = int(get_stat("minutes") or 0)

    # adds player and all their collected stats to players list
    players.append(
        (playerid, goals, assists, yellowcards, redcards, shots, passaccuracy, passes, crosses, minutesplayed)
    )
    scraped_players.add(playerid)   # add player so scraped_players

# This loops gives all players that are not in FBref table the stats 0 since they did not play that game
for pid in name_to_id.values():
    if pid not in scraped_players:
        players.append((pid, 0, 0, 0, 0, 0, 0.0, 0, 0, 0))

# Prints the finished SQL query
for p in players:
    (playerid, goals, assists, yellowcards, redcards, shots, passaccuracy, passes, crosses, minutesplayed) = p
    query = f"""
    insert into playermatchstats 
    (playerid, matchid, minutesplayed, goals, assists, yellowcards, redcards, shots, passaccuracy, passes, crosses)
    values ({playerid}, {matchid}, {minutesplayed}, {goals}, {assists}, {yellowcards}, {redcards}, {shots}, {passaccuracy}, {passes}, {crosses});
    """
    print(query)
