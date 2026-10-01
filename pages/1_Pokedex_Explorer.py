import random

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Pokédex Explorer · PokéScope", page_icon="🔎", layout="wide")

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
"""

TYPE_COLORS = {
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

TYPES_WITH_DARK_TEXT = ["Electric", "Ice", "Ground", "Steel", "Fairy"]

STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special_attack": "Special Attack",
    "special_defense": "Special Defense",
    "speed": "Speed",
}

API_STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special-attack": "Special Attack",
    "special-defense": "Special Defense",
    "speed": "Speed",
}

SORT_COLUMN_NAMES = {
    "Pokédex Number": "pokedex_number",
    "Total Stats": "total_stats",
    "Attack": "attack",
    "Defense": "defense",
    "Speed": "speed",
    "Base Experience": "base_experience",
}

TABLE_COLUMN_LABELS = {
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


@st.cache_data
def load_pokemon_data():
    pokemon_data = pd.read_csv("data/pokemon_data.csv")
    pokemon_data["secondary_type"] = pokemon_data["secondary_type"].fillna("None")
    pokemon_data["total_stats"] = (
        pokemon_data["hp"]
        + pokemon_data["attack"]
        + pokemon_data["defense"]
        + pokemon_data["special_attack"]
        + pokemon_data["special_defense"]
        + pokemon_data["speed"]
    )
    pokemon_data["generation_label"] = "Generation " + pokemon_data["generation"].astype(str)
    return pokemon_data


@st.cache_data
def get_pokemon_details(pokedex_number):
    api_url = "https://pokeapi.co/api/v2/pokemon/" + str(pokedex_number)
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    return response.json()


def make_type_badge(type_name):
    background_color = TYPE_COLORS.get(type_name, "#555555")
    text_color = "#FFFFFF"
    if type_name in TYPES_WITH_DARK_TEXT:
        text_color = "#1F2430"
    return f'<span class="type-badge" style="background:{background_color}; color:{text_color};">{type_name}</span>'


st.markdown(PAGE_CSS, unsafe_allow_html=True)

pokemon_data = load_pokemon_data()

if "selected_pokemon" not in st.session_state:
    st.session_state.selected_pokemon = "Pikachu"

st.markdown(
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

st.sidebar.header("🎛️ Filters")

type_options = sorted(pokemon_data["primary_type"].unique())
selected_types = st.sidebar.multiselect(
    "Type",
    type_options,
    help="Shows Pokémon that have any of the chosen types, as their first or second type.",
)

data_in_generation_order = pokemon_data.sort_values("generation")
generation_options = list(data_in_generation_order["generation_label"].unique())
selected_generations = st.sidebar.multiselect("Generation", generation_options)

highest_base_experience = int(pokemon_data["base_experience"].max())
minimum_base_experience = st.sidebar.slider(
    "Minimum Base Experience",
    min_value=0,
    max_value=highest_base_experience,
    value=0,
    step=10,
)

search_text = st.sidebar.text_input("Search by name", placeholder="e.g. Pikachu")

sort_label = st.sidebar.selectbox("Sort results by", list(SORT_COLUMN_NAMES.keys()))

st.sidebar.divider()
surprise_button_clicked = st.sidebar.button("🎲 Surprise Me", type="primary", width="stretch")
st.sidebar.caption("Picks a random Pokémon from your current results.")

filtered_data = pokemon_data.copy()

if len(selected_types) > 0:
    has_primary_type = filtered_data["primary_type"].isin(selected_types)
    has_secondary_type = filtered_data["secondary_type"].isin(selected_types)
    filtered_data = filtered_data[has_primary_type | has_secondary_type]

if len(selected_generations) > 0:
    filtered_data = filtered_data[filtered_data["generation_label"].isin(selected_generations)]

if minimum_base_experience > 0:
    filtered_data = filtered_data[filtered_data["base_experience"] >= minimum_base_experience]

if search_text != "":
    name_matches_search = filtered_data["name"].str.contains(search_text, case=False, regex=False)
    filtered_data = filtered_data[name_matches_search]

if filtered_data.empty:
    st.warning("No Pokémon match those filters. Try removing a filter or changing your search.")
    st.stop()

sort_column_name = SORT_COLUMN_NAMES[sort_label]
sort_ascending = False
if sort_label == "Pokédex Number":
    sort_ascending = True
sorted_data = filtered_data.sort_values(sort_column_name, ascending=sort_ascending)

result_pokemon_names = list(sorted_data["name"])

if surprise_button_clicked:
    st.session_state.selected_pokemon = random.choice(result_pokemon_names)

st.subheader("📋 Your results")

count_column, attack_column, defense_column, speed_column = st.columns(4)
count_column.metric("Matching Pokémon", len(filtered_data))
attack_column.metric("Average Attack", round(filtered_data["attack"].mean(), 1))
defense_column.metric("Average Defense", round(filtered_data["defense"].mean(), 1))
speed_column.metric("Average Speed", round(filtered_data["speed"].mean(), 1))

fastest_pokemon = filtered_data.sort_values("speed", ascending=False).iloc[0]
strongest_attack_pokemon = filtered_data.sort_values("attack", ascending=False).iloc[0]

fastest_column, strongest_column = st.columns(2)
fastest_column.info(f"⚡ **Fastest in these results:** {fastest_pokemon['name']} (Speed {fastest_pokemon['speed']})")
strongest_column.info(f"💪 **Strongest Attack in these results:** {strongest_attack_pokemon['name']} (Attack {strongest_attack_pokemon['attack']})")

results_table = sorted_data[list(TABLE_COLUMN_LABELS.keys())]
results_table = results_table.rename(columns=TABLE_COLUMN_LABELS)
st.dataframe(results_table, hide_index=True, height=360)

st.divider()

st.subheader("🪪 Selected Pokémon Profile")

default_index = 0
if st.session_state.selected_pokemon in result_pokemon_names:
    default_index = result_pokemon_names.index(st.session_state.selected_pokemon)

chosen_pokemon_name = st.selectbox("Choose a Pokémon from your results", result_pokemon_names, index=default_index)
st.session_state.selected_pokemon = chosen_pokemon_name

chosen_pokemon = sorted_data[sorted_data["name"] == chosen_pokemon_name].iloc[0]

try:
    api_details = get_pokemon_details(int(chosen_pokemon["pokedex_number"]))
except requests.exceptions.RequestException:
    api_details = None

artwork_url = None
ability_names = []
type_names = [chosen_pokemon["primary_type"]]
if chosen_pokemon["secondary_type"] != "None":
    type_names.append(chosen_pokemon["secondary_type"])
height_m = chosen_pokemon["height_m"]
weight_kg = chosen_pokemon["weight_kg"]
base_experience = chosen_pokemon["base_experience"]
stat_labels = []
stat_values = []
for stat_column_name in STAT_LABELS:
    stat_labels.append(STAT_LABELS[stat_column_name])
    stat_values.append(int(chosen_pokemon[stat_column_name]))

if api_details is None:
    st.error(
        "We couldn't reach PokéAPI right now, so the artwork and abilities are missing. "
        "The stats below come from the saved dataset. Please try again in a moment."
    )
else:
    artwork_url = api_details["sprites"]["other"]["official-artwork"]["front_default"]
    if artwork_url is None:
        artwork_url = api_details["sprites"]["front_default"]

    for ability_entry in api_details["abilities"]:
        ability_name = ability_entry["ability"]["name"].replace("-", " ").title()
        if ability_entry["is_hidden"]:
            ability_name = ability_name + " (hidden ability)"
        ability_names.append(ability_name)

    type_names = []
    for type_entry in api_details["types"]:
        type_names.append(type_entry["type"]["name"].capitalize())

    height_m = api_details["height"] / 10
    weight_kg = api_details["weight"] / 10
    base_experience = api_details["base_experience"]

    stat_labels = []
    stat_values = []
    for stat_entry in api_details["stats"]:
        api_stat_name = stat_entry["stat"]["name"]
        if api_stat_name in API_STAT_LABELS:
            stat_labels.append(API_STAT_LABELS[api_stat_name])
            stat_values.append(stat_entry["base_stat"])

type_badges_html = ""
for type_name in type_names:
    type_badges_html = type_badges_html + make_type_badge(type_name)

if len(ability_names) > 0:
    abilities_text = ", ".join(ability_names)
else:
    abilities_text = "Unavailable"

if pd.isna(base_experience):
    base_experience_text = "Unknown"
else:
    base_experience_text = str(int(base_experience))

with st.container(border=True):
    profile_column, stats_column = st.columns([2, 3], gap="large")

    with profile_column:
        st.header(f"#{chosen_pokemon['pokedex_number']} {chosen_pokemon_name}")
        st.markdown(type_badges_html, unsafe_allow_html=True)
        if artwork_url is not None:
            st.image(artwork_url, caption=f"Official artwork of {chosen_pokemon_name}", width=300)
        st.markdown(
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

    with stats_column:
        st.subheader("Base Stats")
        top_row = st.columns(3)
        bottom_row = st.columns(3)
        stat_metric_columns = top_row + bottom_row
        for stat_position in range(len(stat_labels)):
            stat_metric_columns[stat_position].metric(stat_labels[stat_position], stat_values[stat_position])

        total_stats = sum(stat_values)
        st.metric("Total Stats", total_stats)

        stats_chart_data = pd.DataFrame({"Stat": stat_labels, "Value": stat_values})
        stats_chart = (
            alt.Chart(stats_chart_data, title=f"Base stats of {chosen_pokemon_name}")
            .mark_bar(color="#D62828", cornerRadiusEnd=6)
            .encode(
                x=alt.X("Value:Q", title="Base stat value", scale=alt.Scale(domain=[0, 255])),
                y=alt.Y("Stat:N", title=None, sort=None),
                tooltip=["Stat", "Value"],
            )
            .properties(height=280)
        )
        st.altair_chart(stats_chart, width="stretch")

st.caption("Profile details are loaded live from PokéAPI (pokeapi.co). The results table uses the saved PokéAPI CSV dataset.")
