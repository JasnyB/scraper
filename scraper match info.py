# IMPORTING LIBRARIES
import cloudscraper
from bs4 import BeautifulSoup #BeautifulSoup used to parse HTML into a tree structure

import re
from datetime import datetime   # to convert the date extracted from the header into 'yyyy-mm-dd' to match SQL DateTime format

# FBref URL has to be swapped to correct link for each match
url = "https://fbref.com/en/matches/a7e96019/Werder-Bremen-Freiburg-September-20-2025-Bundesliga"

# Cloudflare-aware request 
scraper = cloudscraper.create_scraper() # creates a fake browser session to bypass cloudflare check
response = scraper.get(url) # downlaods the HTML of match page
soup = BeautifulSoup(response.text, "html.parser") # turns HTML string into structured object to be searched


# Extracts the <h1> which contains the infor about the match, such as date, teams and away/home
header = soup.find("h1").get_text(" ", strip=True)
# .find('h1') finds the first <h1> tag in the HTML
# .get_text(' ', strip=True) extracts just the text inside the tag and strips space.

# Uses regex to split the headline into teams and date
m = re.search(r"^(.*?)\s+Match (?:Report|Preview)\s*[–-]\s*(.*)$", header)
if not m:
    raise Exception(f"couldn't parse header: {header}")

teams_part, date_part = m.group(1), m.group(2)
# m.group(1) = team vs team
# m.group(2) = date

# teams
home_team, away_team = [t.strip() for t in teams_part.split(" vs. ", 1)]
# .split(' vs. ', 1) splits the string into [home, away]. The team that comes first is the home team.
# .strip() removes extra spaces

# Decides if Werder Bremen is Home or Away and marks it.
homeaway = "home" if home_team.lower() == "werder bremen" else "away"

# makes opponent home or away
opponent = away_team if homeaway == "home" else home_team

# converts the date to the SQL format yyyy-mm-dd
matchdate = datetime.strptime(date_part, "%A %B %d, %Y").strftime("%Y-%m-%d")

# Extracrs competition from URL
competition = url.rstrip("/").split("-")[-1].lower()  # "bundesliga", "dfb-pokal", etc.

# Score has to be hard coded for now as the score is not in the header on FBref. Will be fixed in later.
# But for now this is fine as it still speeds up the process tremendously for me.
score = "0-3"

# escape single quotes for SQL
def esc(s: str) -> str:
    return s.replace("'", "''")


# Prints the query so i can copy paste it in SQL
query_match = f"""
insert into matches (matchdate, opponent, homeaway, competition, score)
values ('{matchdate}', '{esc(opponent)}', '{homeaway}', '{competition}', '{score}');
"""
print("Match insert query:")
print(query_match)

