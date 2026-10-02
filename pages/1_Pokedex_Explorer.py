import random  # used to pick a random pokemon

import altair as alt  # library for making the charts
import pandas as pd  # used to read and filter the csv data
import requests  # used to call the pokeapi
import streamlit as st  # used to build the web app

st.set_page_config(page_title="Pokédex Explorer · PokéScope", page_icon="🔎", layout="wide")  # sets tab title, icon and wide layout

PAGE_CSS = """
<style>
.hero {
    display: flex; align-items: center; gap: 1.4rem;
    background: linear-gradient(135deg, #D62828 0%, #8E1B1B 100%);
    padding: 1.6rem 2.2rem; border-radius: 24px; margin-bottom: 1.5rem;
}
.hero h1 { color: #FFFFFF; font-size: 2.6rem; margin: 0; padding: 0; }
.hero p { color: #FFF1F1; font-size: 1.2rem; margin: 0.2rem 0 0 0; }
.pokeball {
    min-width: 56px; height: 56px; border-radius: 50%; border: 4px solid #FFFFFF;
    background: linear-gradient(to bottom, #EE1515 0%, #EE1515 44%, #1F2430 44%, #1F2430 56%, #FFFFFF 56%);
}
.type-badge {
    display: inline-block; padding: 0.3rem 0.9rem; border-radius: 999px;
    font-weight: 700; font-size: 1rem; margin-right: 0.4rem;
}
.profile-facts { font-size: 1.1rem; line-height: 1.9; }
div[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #DDE2EC; border-radius: 16px; padding: 1rem 1.2rem;
}
</style>
"""  # css styling for the banner, pokeball, badges and metric boxes

TYPE_COLORS = {  # colour for each pokemon type badge
    "Normal": "#6D6D4E",
    "Fire": "#C62E0A",
    "Water": "#2A5FC9",
    "Electric": "#F7D02C",
    "Grass": "#3F7D20",
    "Ice": "#96D9D6",
    "Fighting": "#A0221B",
    "Poison": "#7B2D8B",
    "Ground": "#E2BF65",
    "Flying": "#5E4BB8",
    "Psychic": "#C2185B",
    "Bug": "#5F6E10",
    "Rock": "#7A6A20",
    "Ghost": "#5A4585",
    "Dragon": "#5A2FD6",
    "Dark": "#4A3B30",
    "Steel": "#B7B7CE",
    "Fairy": "#F4A6C8",
}

TYPES_WITH_DARK_TEXT = ["Electric", "Ice", "Ground", "Steel", "Fairy"]  # light colours that need dark text to be readable

STAT_LABELS = {  # csv column names matched to nice names for the user
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special_attack": "Special Attack",
    "special_defense": "Special Defense",
    "speed": "Speed",
}

API_STAT_LABELS = {  # same thing but for the api, which uses dashes in the names
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special-attack": "Special Attack",
    "special-defense": "Special Defense",
    "speed": "Speed",
}

SORT_COLUMN_NAMES = {  # sort options the user sees, matched to the csv column to sort by
    "Pokédex Number": "pokedex_number",
    "Total Stats": "total_stats",
    "Attack": "attack",
    "Defense": "defense",
    "Speed": "speed",
    "Base Experience": "base_experience",
}

TABLE_COLUMN_LABELS = {  # columns shown in the results table and their headings
    "pokedex_number": "Pokédex #",
    "name": "Name",
    "primary_type": "Primary Type",
    "secondary_type": "Secondary Type",
    "generation": "Generation",
    "base_experience": "Base Experience",
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "speed": "Speed",
    "total_stats": "Total Stats",
}


@st.cache_data  # saves the result so the csv isnt reloaded every time
def load_pokemon_data():  # function to load the pokemon data
    pokemon_data = pd.read_csv("data/pokemon_data.csv")  # reads the csv into a table
    pokemon_data["secondary_type"] = pokemon_data["secondary_type"].fillna("None")  # fills empty second types with "None"
    pokemon_data["total_stats"] = (  # makes a new column for total stats
        pokemon_data["hp"]  # adds hp
        + pokemon_data["attack"]  # plus attack
        + pokemon_data["defense"]  # plus defense
        + pokemon_data["special_attack"]  # plus special attack
        + pokemon_data["special_defense"]  # plus special defense
        + pokemon_data["speed"]  # plus speed
    )
    pokemon_data["generation_label"] = "Generation " + pokemon_data["generation"].astype(str)  # turns 1 into "Generation 1"
    return pokemon_data  # gives back the finished table


@st.cache_data  # saves each api result so the same pokemon isnt downloaded twice
def get_pokemon_details(pokedex_number):  # function to get one pokemon from the api
    api_url = "https://pokeapi.co/api/v2/pokemon/" + str(pokedex_number)  # builds the api link using the pokedex number
    response = requests.get(api_url, timeout=10)  # sends the request and waits up to 10 seconds
    response.raise_for_status()  # gives an error if the request failed
    return response.json()  # turns the reply into a python dictionary


def make_type_badge(type_name):  # function that makes a coloured type label
    background_color = TYPE_COLORS.get(type_name, "#555555")  # gets the type colour, or grey if not found
    text_color = "#FFFFFF"  # white text by default
    if type_name in TYPES_WITH_DARK_TEXT:  # checks if the colour is a light one
        text_color = "#1F2430"  # uses dark text instead
    return f'<span class="type-badge" style="background:{background_color}; color:{text_color};">{type_name}</span>'  # returns the badge as html


st.markdown(PAGE_CSS, unsafe_allow_html=True)  # applies the css to the page

pokemon_data = load_pokemon_data()  # loads the data

if "selected_pokemon" not in st.session_state:  # checks if no pokemon is saved yet
    st.session_state.selected_pokemon = "Pikachu"  # sets pikachu as the starting pokemon

st.markdown(  # shows the red banner at the top
    """
    <div class="hero">
        <div class="pokeball"></div>
        <div>
            <h1>🔎 Pokédex Explorer</h1>
            <p>Which Pokémon match what I'm looking for?</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("🎛️ Filters")  # heading at the top of the sidebar

type_options = sorted(pokemon_data["primary_type"].unique())  # gets every type once, in alphabetical order
selected_types = st.sidebar.multiselect(  # type filter where you can pick more than one
    "Type",  # label for the filter
    type_options,  # the types to choose from
    help="Shows Pokémon that have any of the chosen types, as their first or second type.",  # little help tooltip
)

data_in_generation_order = pokemon_data.sort_values("generation")  # sorts the data by generation number
generation_options = list(data_in_generation_order["generation_label"].unique())  # gets each generation once, in order
selected_generations = st.sidebar.multiselect("Generation", generation_options)  # generation filter

highest_base_experience = int(pokemon_data["base_experience"].max())  # finds the highest base experience
minimum_base_experience = st.sidebar.slider(  # slider for minimum base experience
    "Minimum Base Experience",  # label for the slider
    min_value=0,  # lowest value
    max_value=highest_base_experience,  # highest value
    value=0,  # starts at 0
    step=10,  # moves in steps of 10
)

search_text = st.sidebar.text_input("Search by name", placeholder="e.g. Pikachu")  # search box for pokemon names

sort_label = st.sidebar.selectbox("Sort results by", list(SORT_COLUMN_NAMES.keys()))  # dropdown to choose how to sort

st.sidebar.divider()  # line in the sidebar
surprise_button_clicked = st.sidebar.button("🎲 Surprise Me", type="primary", width="stretch")  # true when the button is clicked
st.sidebar.caption("Picks a random Pokémon from your current results.")  # small text under the button

filtered_data = pokemon_data.copy()  # makes a copy so the original data isnt changed

if len(selected_types) > 0:  # only filters if a type was picked
    has_primary_type = filtered_data["primary_type"].isin(selected_types)  # true if the first type matches
    has_secondary_type = filtered_data["secondary_type"].isin(selected_types)  # true if the second type matches
    filtered_data = filtered_data[has_primary_type | has_secondary_type]  # keeps pokemon where either type matches

if len(selected_generations) > 0:  # only filters if a generation was picked
    filtered_data = filtered_data[filtered_data["generation_label"].isin(selected_generations)]  # keeps the chosen generations

if minimum_base_experience > 0:  # only filters if the slider was moved
    filtered_data = filtered_data[filtered_data["base_experience"] >= minimum_base_experience]  # keeps pokemon above the slider value

if search_text != "":  # only searches if something was typed
    name_matches_search = filtered_data["name"].str.contains(search_text, case=False, regex=False)  # true if the name contains the search
    filtered_data = filtered_data[name_matches_search]  # keeps the matching names

if filtered_data.empty:  # checks if nothing matched
    st.warning("No Pokémon match those filters. Try removing a filter or changing your search.")  # shows a warning
    st.stop()  # stops the page so nothing breaks

sort_column_name = SORT_COLUMN_NAMES[sort_label]  # gets the column to sort by
sort_ascending = False  # sorts highest first by default
if sort_label == "Pokédex Number":  # pokedex number should go low to high
    sort_ascending = True  # so sort lowest first
sorted_data = filtered_data.sort_values(sort_column_name, ascending=sort_ascending)  # sorts the results

result_pokemon_names = list(sorted_data["name"])  # list of names in the results

if surprise_button_clicked:  # if surprise me was clicked
    st.session_state.selected_pokemon = random.choice(result_pokemon_names)  # saves a random pokemon from the results

st.subheader("📋 Your results")  # heading for the results

count_column, attack_column, defense_column, speed_column = st.columns(4)  # makes 4 columns side by side
count_column.metric("Matching Pokémon", len(filtered_data))  # shows how many pokemon matched
attack_column.metric("Average Attack", round(filtered_data["attack"].mean(), 1))  # shows the average attack
defense_column.metric("Average Defense", round(filtered_data["defense"].mean(), 1))  # shows the average defense
speed_column.metric("Average Speed", round(filtered_data["speed"].mean(), 1))  # shows the average speed

fastest_pokemon = filtered_data.sort_values("speed", ascending=False).iloc[0]  # sorts by speed and takes the top one
strongest_attack_pokemon = filtered_data.sort_values("attack", ascending=False).iloc[0]  # sorts by attack and takes the top one

fastest_column, strongest_column = st.columns(2)  # makes 2 columns
fastest_column.info(f"⚡ **Fastest in these results:** {fastest_pokemon['name']} (Speed {fastest_pokemon['speed']})")  # shows the fastest pokemon
strongest_column.info(f"💪 **Strongest Attack in these results:** {strongest_attack_pokemon['name']} (Attack {strongest_attack_pokemon['attack']})")  # shows the strongest attacker

results_table = sorted_data[list(TABLE_COLUMN_LABELS.keys())]  # keeps only the useful columns
results_table = results_table.rename(columns=TABLE_COLUMN_LABELS)  # renames the columns to nicer names
st.dataframe(results_table, hide_index=True, height=360)  # shows the results table

st.divider()  # line across the page

st.subheader("🪪 Selected Pokémon Profile")  # heading for the profile

default_index = 0  # dropdown starts on the first pokemon by default
if st.session_state.selected_pokemon in result_pokemon_names:  # checks if the saved pokemon is in the results
    default_index = result_pokemon_names.index(st.session_state.selected_pokemon)  # finds its position in the list

chosen_pokemon_name = st.selectbox("Choose a Pokémon from your results", result_pokemon_names, index=default_index)  # dropdown to pick a pokemon
st.session_state.selected_pokemon = chosen_pokemon_name  # saves the choice so other pages can use it

chosen_pokemon = sorted_data[sorted_data["name"] == chosen_pokemon_name].iloc[0]  # gets the row for the chosen pokemon

try:  # tries to call the api
    api_details = get_pokemon_details(int(chosen_pokemon["pokedex_number"]))  # gets the pokemon details using its pokedex number
except requests.exceptions.RequestException:  # if the api call fails
    api_details = None  # sets it to none instead of crashing

artwork_url = None  # no image yet
ability_names = []  # empty list for abilities
type_names = [chosen_pokemon["primary_type"]]  # starts with the first type from the csv
if chosen_pokemon["secondary_type"] != "None":  # checks if it has a second type
    type_names.append(chosen_pokemon["secondary_type"])  # adds the second type
height_m = chosen_pokemon["height_m"]  # height from the csv
weight_kg = chosen_pokemon["weight_kg"]  # weight from the csv
base_experience = chosen_pokemon["base_experience"]  # base experience from the csv
stat_labels = []  # empty list for stat names
stat_values = []  # empty list for stat numbers
for stat_column_name in STAT_LABELS:  # goes through each of the 6 stats
    stat_labels.append(STAT_LABELS[stat_column_name])  # adds the stat name
    stat_values.append(int(chosen_pokemon[stat_column_name]))  # adds the stat value

if api_details is None:  # if the api didnt work
    st.error(  # shows an error message
        "We couldn't reach PokéAPI right now, so the artwork and abilities are missing. "
        "The stats below come from the saved dataset. Please try again in a moment."
    )
else:  # if the api worked
    artwork_url = api_details["sprites"]["other"]["official-artwork"]["front_default"]  # gets the official artwork link
    if artwork_url is None:  # if there is no official artwork
        artwork_url = api_details["sprites"]["front_default"]  # uses the normal sprite instead

    for ability_entry in api_details["abilities"]:  # goes through each ability
        ability_name = ability_entry["ability"]["name"].replace("-", " ").title()  # makes the name look nice
        if ability_entry["is_hidden"]:  # checks if it is a hidden ability
            ability_name = ability_name + " (hidden ability)"  # adds a note to it
        ability_names.append(ability_name)  # adds it to the list

    type_names = []  # clears the types so they arent doubled
    for type_entry in api_details["types"]:  # goes through each type
        type_names.append(type_entry["type"]["name"].capitalize())  # adds the type with a capital letter

    height_m = api_details["height"] / 10  # changes height to metres
    weight_kg = api_details["weight"] / 10  # changes weight to kilograms
    base_experience = api_details["base_experience"]  # gets base experience from the api

    stat_labels = []  # clears the stat names
    stat_values = []  # clears the stat numbers
    for stat_entry in api_details["stats"]:  # goes through each stat from the api
        api_stat_name = stat_entry["stat"]["name"]  # gets the api name of the stat
        if api_stat_name in API_STAT_LABELS:  # checks if it is one of our 6 stats
            stat_labels.append(API_STAT_LABELS[api_stat_name])  # adds the nice name
            stat_values.append(stat_entry["base_stat"])  # adds the value

type_badges_html = ""  # starts with no badges
for type_name in type_names:  # goes through each type
    type_badges_html = type_badges_html + make_type_badge(type_name)  # adds a badge for it

if len(ability_names) > 0:  # if there are abilities
    abilities_text = ", ".join(ability_names)  # joins them with commas
else:  # if there are none
    abilities_text = "Unavailable"  # shows unavailable instead

if pd.isna(base_experience):  # checks if base experience is missing
    base_experience_text = "Unknown"  # shows unknown
else:  # if it exists
    base_experience_text = str(int(base_experience))  # turns it into text

with st.container(border=True):  # puts the profile inside a box
    profile_column, stats_column = st.columns([2, 3], gap="large")  # 2 columns, the right one is wider

    with profile_column:  # left column
        st.header(f"#{chosen_pokemon['pokedex_number']} {chosen_pokemon_name}")  # shows the number and name
        st.markdown(type_badges_html, unsafe_allow_html=True)  # shows the type badges
        if artwork_url is not None:  # only if there is an image
            st.image(artwork_url, caption=f"Official artwork of {chosen_pokemon_name}", width=300)  # shows the artwork
        st.markdown(  # shows height, weight, abilities and more
            f"""
            <div class="profile-facts">
            📏 <b>Height:</b> {height_m} m<br>
            ⚖️ <b>Weight:</b> {weight_kg} kg<br>
            ✨ <b>Abilities:</b> {abilities_text}<br>
            🎓 <b>Base Experience:</b> {base_experience_text}<br>
            🗓️ <b>Generation:</b> {chosen_pokemon['generation']}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with stats_column:  # right column
        st.subheader("Base Stats")  # heading for the stats
        top_row = st.columns(3)  # first row of 3 boxes
        bottom_row = st.columns(3)  # second row of 3 boxes
        stat_metric_columns = top_row + bottom_row  # joins them into one list of 6
        for stat_position in range(len(stat_labels)):  # goes through positions 0 to 5
            stat_metric_columns[stat_position].metric(stat_labels[stat_position], stat_values[stat_position])  # shows each stat in its box

        total_stats = sum(stat_values)  # adds up all 6 stats
        st.metric("Total Stats", total_stats)  # shows the total

        stats_chart_data = pd.DataFrame({"Stat": stat_labels, "Value": stat_values})  # makes a small table for the chart
        stats_chart = (  # builds the bar chart
            alt.Chart(stats_chart_data, title=f"Base stats of {chosen_pokemon_name}")  # uses the table and adds a title
            .mark_bar(color="#D62828", cornerRadiusEnd=6)  # red bars with rounded ends
            .encode(
                x=alt.X("Value:Q", title="Base stat value", scale=alt.Scale(domain=[0, 255])),  # values on the x axis from 0 to 255
                y=alt.Y("Stat:N", title=None, sort=None),  # stat names on the y axis in normal order
                tooltip=["Stat", "Value"],  # shows the numbers when you hover
            )
            .properties(height=280)  # sets the chart height
        )
        st.altair_chart(stats_chart, width="stretch")  # shows the chart

st.caption("Profile details are loaded live from PokéAPI (pokeapi.co). The results table uses the saved PokéAPI CSV dataset.")  # small note about where the data comes from
