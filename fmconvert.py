# by Snoops
# https://fminside.net/clubs
# Importing the regular expression and requests modules
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

# Function to read nations.txt and create a dictionary mapping countries to abbreviations
def read_nations():
    nation_dict = {}
    with open('nations.txt', 'r') as nations_file:
        for line in nations_file:
            parts = line.strip().split('\t', 1)
            if len(parts) == 2:
                abbreviation, country = parts
                nation_dict[country.strip()] = abbreviation
    return nation_dict

# Function to extract player information from a given profile URL
def extract_player_info(profile_url, nation_dict):
    try:
        # Sending an HTTP GET request to the provided URL
        response = requests.get(profile_url)

        # Checking if the response status code is 200 (OK)
        if response.status_code == 200:
            # Extracting the HTML content of the page
            content = response.text

            # Using regular expressions to find player name, age, and position
            name_match = re.search(r'<span class="key">Name<\/span><span class="value">(.*?)<\/span>', content)
            age_match = re.search(r'<span class="key">Age<\/span><span class="value">(.*?)<\/span>', content)
            position_match = re.search(r'<span class="desktop_positions">.*?position="(gk|dl|dc|dr|wbl|wbr|dm|ml|mc|mr|aml|amc|amr|st)".*?<\/span>', content, flags=re.DOTALL)

            # Initialize the position modifiers
            st_position_modifier = 0
            tk_position_modifier = 0
            ps_position_modifier = 0
            sh_position_modifier = 0

            # Check if position information is found and apply modifiers based on positions
            if position_match:
                if "gk" in position_match.group(1):
                    st_position_modifier = 1
                elif any(pos in position_match.group(1) for pos in ["dl", "dc", "dr", "wbl", "wbr"]):
                    tk_position_modifier = 1
                elif any(pos in position_match.group(1) for pos in ["dm", "ml", "mc", "mr", "aml", "amc", "amr"]):
                    ps_position_modifier = 1
                elif "st" in position_match.group(1):
                    sh_position_modifier = 1

            # Using a loop for player stats
            stat_names = [
                "acceleration", "aerial-reach", "aggression", "agility", "anticipation",
                "balance", "bravery", "command-of-area", "communication", "composure",
                "concentration", "corners", "crossing", "decisions", "determination",
                "dribbling", "eccentricity", "finishing", "first-touch", "flair",
                "free-kick-taking", "handling", "heading", "jumping-reach", "kicking",
                "leadership", "long-shots", "long-throws", "marking", "natural-fitness",
                "off-the-ball", "one-on-ones", "pace", "passing", "penalty-taking",
                "positioning", "punching-tendency", "reflexes", "rushing-out-tendency",
                "stamina", "strength", "tackling", "teamwork", "technique", "throwing",
                "vision", "work-rate"
            ]

            # Dictionary to store stat values
            player_stats = {}

            # Loop through the stat names and search for each in the content
            for stat_name in stat_names:
                stat_match = re.search(fr'<tr id="{stat_name}">\s*<td class="name">.*?<\/td>\s*<td class="stat value_(\d+)">\d+<\/td>\s*<\/tr>', content)
                player_stats[stat_name] = stat_match.group(1) if stat_match else "0"

            # Extracting the nationality information
            soup = BeautifulSoup(content, 'html.parser')
            player_info_div = soup.find('div', {'id': 'player_info'})
            player_div = player_info_div.find('div', {'id': 'player'})
            nationality_element = player_div.find('a', {'href': re.compile(r'/players/[a-z]+', re.I)})
            nation = nationality_element.get_text(strip=True) if nationality_element else "N/A"

            # Map the nation to its abbreviation using the dictionary
            nation_code = nation_dict.get(nation, "???")

            # Checking if player name information is found
            if name_match:
                # Extracting the full name from the match
                playername = name_match.group(1)

                # Processing the name to a standardized format and extract age
                processed_name = process_name(playername)
                age = age_match.group(1) if age_match else "0"

                # Calculate st_value
                st_stats_high = (
                    int(player_stats.get("agility", 0)) + int(player_stats.get("reflexes", 0))) * 5
                st_stats_mid = (
                    int(player_stats.get("anticipation", 0)) + int(player_stats.get("command-of-area", 0)) +
                    int(player_stats.get("concentration", 0)) + int(player_stats.get("kicking", 0)) +
                    int(player_stats.get("one-on-ones", 0)) + int(player_stats.get("positioning", 0))) * 3
                st_stats_low = (
                    int(player_stats.get("acceleration", 0)) + int(player_stats.get("aerial-reach", 0)) +
                    int(player_stats.get("decisions", 0)) + int(player_stats.get("first-touch", 0)) +
                    int(player_stats.get("handling", 0)) + int(player_stats.get("passing", 0)) +
                    int(player_stats.get("rushing-out-tendency", 0)) + int(player_stats.get("throwing", 0)) +
                    int(player_stats.get("vision", 0))) * 1
                st_value = round((st_stats_high + st_stats_mid + st_stats_low) / 37) + st_position_modifier

                # Calculate tk_value
                tk_stats_high = (
                    int(player_stats.get("composure", 0)) + int(player_stats.get("jumping-reach", 0)) +
                    int(player_stats.get("marking", 0)) + int(player_stats.get("stamina", 0)) +
                    int(player_stats.get("tackling", 0)) + int(player_stats.get("work-rate", 0))) * 5
                tk_stats_mid = (
                    int(player_stats.get("acceleration", 0)) + int(player_stats.get("concentration", 0)) +
                    int(player_stats.get("heading", 0)) + int(player_stats.get("off-the-ball", 0)) +
                    int(player_stats.get("pace", 0)) + int(player_stats.get("positioning", 0)) +
                    int(player_stats.get("strength", 0)) + int(player_stats.get("teamwork", 0))) * 3
                tk_stats_low = (
                    int(player_stats.get("aggression", 0)) + int(player_stats.get("agility", 0)) +
                    int(player_stats.get("anticipation", 0)) + int(player_stats.get("balance", 0)) +
                    int(player_stats.get("bravery", 0)) + int(player_stats.get("crossing", 0)) +
                    int(player_stats.get("decisions", 0)) + int(player_stats.get("dribbling", 0)) +
                    int(player_stats.get("first-touch", 0)) + int(player_stats.get("flair", 0)) +
                    int(player_stats.get("long-shots", 0)) + int(player_stats.get("passing", 0)) +
                    int(player_stats.get("technique", 0)) + int(player_stats.get("vision", 0))) * 1
                tk_value = round((tk_stats_high + tk_stats_mid + tk_stats_low) / 68) + tk_position_modifier

                # Calculate ps_value
                ps_stats_high = (
                    int(player_stats.get("crossing", 0)) + int(player_stats.get("passing", 0)) +
                    int(player_stats.get("stamina", 0)) + int(player_stats.get("work-rate", 0))) * 5
                ps_stats_mid = (
                    int(player_stats.get("acceleration", 0)) + int(player_stats.get("decisions", 0)) +
                    int(player_stats.get("heading", 0)) + int(player_stats.get("jumping-reach", 0)) +
                    int(player_stats.get("off-the-ball", 0)) + int(player_stats.get("pace", 0)) +
                    int(player_stats.get("positioning", 0)) + int(player_stats.get("tackling", 0)) +
                    int(player_stats.get("teamwork", 0)) + int(player_stats.get("technique", 0))) * 3
                ps_stats_low = (
                    int(player_stats.get("aggression", 0)) + int(player_stats.get("agility", 0)) +
                    int(player_stats.get("anticipation", 0)) + int(player_stats.get("balance", 0)) +
                    int(player_stats.get("bravery", 0)) + int(player_stats.get("composure", 0)) +
                    int(player_stats.get("concentration", 0)) + int(player_stats.get("dribbling", 0)) +
                    int(player_stats.get("finishing", 0)) + int(player_stats.get("first-touch", 0)) +
                    int(player_stats.get("flair", 0)) + int(player_stats.get("long-shots", 0)) +
                    int(player_stats.get("marking", 0)) + int(player_stats.get("strength", 0)) +
                    int(player_stats.get("vision", 0))) * 1
                ps_value = round((ps_stats_high + ps_stats_mid + ps_stats_low) / 65) + ps_position_modifier

                # Calculate sh_value
                sh_stats_high = (
                    int(player_stats.get("acceleration", 0)) + int(player_stats.get("finishing", 0)) +
                    int(player_stats.get("heading", 0)) + int(player_stats.get("long-shots", 0)) +
                    int(player_stats.get("pace", 0))) * 5
                sh_stats_mid = (
                    int(player_stats.get("aggression", 0)) + int(player_stats.get("bravery", 0)) +
                    int(player_stats.get("composure", 0)) + int(player_stats.get("decisions", 0)) +
                    int(player_stats.get("dribbling", 0)) + int(player_stats.get("first-touch", 0)) +
                    int(player_stats.get("off-the-ball", 0)) + int(player_stats.get("passing", 0)) +
                    int(player_stats.get("teamwork", 0)) + int(player_stats.get("technique", 0))) * 3
                sh_stats_low = (
                    int(player_stats.get("agility", 0)) + int(player_stats.get("anticipation", 0)) +
                    int(player_stats.get("balance", 0)) + int(player_stats.get("concentration", 0)) +
                    int(player_stats.get("flair", 0)) + int(player_stats.get("jumping-reach", 0)) +
                    int(player_stats.get("stamina", 0)) + int(player_stats.get("strength", 0)) +
                    int(player_stats.get("vision", 0)) + int(player_stats.get("work-rate", 0))) * 1
                sh_value = round((sh_stats_high + sh_stats_mid + sh_stats_low) / 65) + sh_position_modifier

                ag_value = player_stats.get("aggression")

                # Returning the processed name, age, nationality code, and stat values
                return processed_name, age, nation_code, st_value, tk_value, ps_value, sh_value, ag_value
    except Exception as e:
        # Returning a tuple with "N/A" values if an exception occurs
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

# Function to process the player name
def process_name(playername):
    # Replace non-English letters with English equivalents and remove special characters
    cleaned_name = re.sub(r'[^a-zA-Z \'-]', '', unidecode(playername))

    # Splitting the name into words
    words = cleaned_name.split()

    # Checking the number of words in the name
    if len(words) == 1:
        processed_name = words[0]
    else:
        # If more than one word, using the first letter of the first word as the first name
        # and the remaining words as the surname
        first_name = words[0][0]
        surname = '_'.join(
            (
                word
                if i == 0
                else word
            )
            for i, word in enumerate(words[1:])
        )
        processed_name = f"{first_name}_{surname}"

    # Limiting the length of the final name to 13 characters
    #processed_name = processed_name[:13]

    return processed_name

# Function to extract player URLs from the team page
def extract_player_urls(team_url):
    try:
        # Sending an HTTP GET request to the team URL
        response = requests.get(team_url)

        # Checking if the response status code is 200 (OK)
        if response.status_code == 200:
            # Extracting the HTML content of the page
            content = response.text

            # Using a regular expression to find player URLs
            player_urls = re.findall(r'<a title=".*?" href="(/players/.*?)">', content)

            # Returning the list of player URLs
            return player_urls
    except Exception as e:
        # Returning an empty list if an exception occurs
        return []

# Main function to execute the script
def main():
    # Read the nations.txt file and create a dictionary
    nation_dict = read_nations()

    while True:
        # Taking user input for the team page URL
        team_url = input("Enter the team page URL (press Enter to exit): ").strip()

        # Checking if the input is empty (user wants to exit)
        if not team_url:
            break

        # Taking user input for the desired filename
        filename = input("Enter the desired filename (normally a 3-letter team name abbreviation): ").strip()

        # Extracting player URLs from the team page
        player_urls = extract_player_urls(team_url)

        # Iterating over player URLs and extracting player information
        for player_url in player_urls:
            # Constructing the full player URL
            full_player_url = f"https://fminside.net{player_url}"

            # Extracting player information from the player URL
            playername, age, nation_code, st_value, tk_value, ps_value, sh_value, ag_value = extract_player_info(full_player_url, nation_dict)

            # Checking if player information is extracted
            if playername:
                # Writing the extracted information to a file with the specified filename
                with open(f'{filename}.txt', 'a+') as file:
                    # Move the file pointer to the beginning
                    file.seek(0)

                    # Checking if the first two lines already exist in the file
                    if not any("Name         Age Nat St Tk Ps Sh Ag KAb TAb PAb SAb Gam Sub  Min Mom Sav Con Ktk Kps Sht Gls Ass  DP Inj Sus Fit" in line for line in file):
                        # Writing the header lines to the file
                        file.write(f"Name         Age Nat St Tk Ps Sh Ag KAb TAb PAb SAb Gam Sub  Min Mom Sav Con Ktk Kps Sht Gls Ass  DP Inj Sus Fit\n")
                        file.write(f"{'-' * 112}\n")

                    # Checking if the player entry already exists in the file
                    if not any(playername in line for line in file):
                        # Move the file pointer to the end for appending
                        file.seek(0, 2)

                        # Writing the player details to the file
                        file.write(f"{playername.ljust(13)} {age.ljust(2)} {nation_code} {str(st_value).rjust(2)} {str(tk_value).rjust(2)} {str(ps_value).rjust(2)} {str(sh_value).rjust(2)} {ag_value.rjust(2)} 300 300 300 300   0   0    0   0   0   0   0   0   0   0   0   0   0   0 100\n")

# Checking if the script is executed as the main program
if __name__ == "__main__":
    # Calling the main function to start the script
    main()
