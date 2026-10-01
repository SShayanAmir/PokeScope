import random

import pandas as pd
import streamlit as st

st.set_page_config(page_title="PokéScope", page_icon="🔴", layout="wide")

PAGE_CSS = """
<style>
.hero {
    display: flex; align-items: center; gap: 1.4rem;
    background: linear-gradient(135deg, #D62828 0%, #8E1B1B 100%);
    padding: 2rem 2.4rem; border-radius: 24px; margin-bottom: 1.5rem;
}
.hero h1 { color: #FFFFFF; font-size: 3rem; margin: 0; padding: 0; }
.hero p { color: #FFF1F1; font-size: 1.3rem; margin: 0.2rem 0 0 0; }
.pokeball {
    min-width: 64px; height: 64px; border-radius: 50%; border: 4px solid #FFFFFF;
    background: linear-gradient(to bottom, #EE1515 0%, #EE1515 44%, #1F2430 44%, #1F2430 56%, #FFFFFF 56%);
}
.card {
    background: #FFFFFF; border: 1px solid #DDE2EC; border-radius: 18px;
    padding: 1.4rem 1.5rem; height: 100%; box-shadow: 0 2px 10px rgba(31, 36, 48, 0.06);
}
.card h3 { margin-top: 0; }
.card p { font-size: 1.05rem; color: #3A4150; }
.problem {
    background: #FFF8E1; border-left: 6px solid #E0A800; border-radius: 14px;
    padding: 1.2rem 1.5rem; font-size: 1.12rem; color: #1F2430;
}
.type-badge {
    display: inline-block; padding: 0.3rem 0.9rem; border-radius: 999px;
    font-weight: 700; font-size: 1rem; margin-right: 0.4rem;
}
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
    return pokemon_data


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
            <h1>PokéScope</h1>
            <p>Explore. Compare. Discover.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.header("🧭 Why PokéScope?")
st.markdown(
    """
    <div class="problem">
    <b>Who it's for:</b> Pokémon players and fans, who have more than a thousand Pokémon to choose from,
    each with different types, physical characteristics, abilities, and battle statistics.<br><br>
    <b>The problem:</b> Comparing Pokémon or discovering patterns across generations is difficult
    when information is presented one Pokémon at a time.<br><br>
    <b>Why it matters:</b> Choosing which Pokémon to use, or simply understanding how they differ,
    means flipping between many separate entries and trying to remember the numbers, so good options
    and interesting patterns are easy to miss.<br><br>
    <b>PokéScope</b> provides an interactive way to explore, filter, compare, and analyze Pokémon,
    while retrieving detailed information from the live PokéAPI.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.header("✨ What you can do")

explore_column, compare_column, discover_column = st.columns(3)

with explore_column:
    st.markdown(
        """
        <div class="card">
        <h3>🔎 Explore Pokémon</h3>
        <p>Filter by type, generation and base experience, search by name,
        and open a live profile with official artwork and abilities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Pokedex_Explorer.py", label="Open the Pokédex Explorer", icon="🔎")

with compare_column:
    st.markdown(
        """
        <div class="card">
        <h3>⚔️ Compare Pokémon</h3>
        <p>Put two Pokémon side by side in the Battle Lab and see which one
        has the stronger stats, one stat at a time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Battle_Lab.py", label="Open the Battle Lab", icon="⚔️")

with discover_column:
    st.markdown(
        """
        <div class="card">
        <h3>🌌 Discover Patterns</h3>
        <p>See how stats change across types and generations in the
        Pokémon Universe, using averages over every Pokémon.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Pokemon_Universe.py", label="Open the Pokémon Universe", icon="🌌")

st.divider()

st.header("📊 Dataset at a Glance")

total_pokemon_count = len(pokemon_data)
number_of_types = pokemon_data["primary_type"].nunique()
number_of_generations = pokemon_data["generation"].nunique()
average_base_experience = round(pokemon_data["base_experience"].mean(), 1)

total_column, types_column, generations_column, experience_column = st.columns(4)
total_column.metric("Total Pokémon", total_pokemon_count)
types_column.metric("Number of Types", number_of_types)
generations_column.metric("Number of Generations", number_of_generations)
experience_column.metric("Average Base Experience", average_base_experience)

st.divider()

st.header("🎲 Feeling lucky?")
st.write(
    "Pick a random Pokémon. It becomes your **current Pokémon**, and it will already be selected "
    "when you open the Pokédex Explorer profile or the Battle Lab."
)

if st.button("🎲 Surprise Me", type="primary"):
    all_pokemon_names = list(pokemon_data["name"])
    st.session_state.selected_pokemon = random.choice(all_pokemon_names)

current_pokemon_name = st.session_state.selected_pokemon
matching_rows = pokemon_data[pokemon_data["name"] == current_pokemon_name]

if matching_rows.empty:
    st.info("Your current Pokémon could not be found in the dataset.")
else:
    current_pokemon = matching_rows.iloc[0]
    type_badges_html = make_type_badge(current_pokemon["primary_type"])
    if current_pokemon["secondary_type"] != "None":
        type_badges_html = type_badges_html + make_type_badge(current_pokemon["secondary_type"])

    with st.container(border=True):
        name_column, total_stats_column, generation_column = st.columns([2, 1, 1])
        with name_column:
            st.subheader(f"Current Pokémon: #{current_pokemon['pokedex_number']} {current_pokemon_name}")
            st.markdown(type_badges_html, unsafe_allow_html=True)
        total_stats_column.metric("Total Stats", int(current_pokemon["total_stats"]))
        generation_column.metric("Generation", int(current_pokemon["generation"]))
        st.page_link("pages/1_Pokedex_Explorer.py", label=f"See {current_pokemon_name}'s full profile", icon="➡️")

st.divider()

with st.expander("📚 Where does the data come from?"):
    st.markdown(
        """
        **1. PokéAPI open-source dataset (CSV)**
        The table of Pokémon, types, generations and base stats comes from the official CSV files
        in the [PokéAPI GitHub repository](https://github.com/PokeAPI/pokeapi/tree/master/data/v2/csv).
        They were combined once into `data/pokemon_data.csv`. It includes one entry per Pokémon species,
        in its default form.

        **2. PokéAPI live API**
        When you open a Pokémon's profile or compare Pokémon, PokéScope asks the free
        [PokéAPI](https://pokeapi.co/) for extra details, such as official artwork and abilities.
        No account or API key is needed.
        """
    )
