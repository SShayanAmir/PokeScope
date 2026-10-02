import random  # used to pick a random pokemon

import pandas as pd  # used to read and work with the csv data
import streamlit as st  # used to build the web app

st.set_page_config(page_title="PokéScope", page_icon="🔴", layout="wide")  # sets tab title, icon and wide layout

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
"""  # css styling for the page

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


@st.cache_data  # saves the result so it doesnt have to run again every time
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
    return pokemon_data  # gives back the finished table


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

st.markdown(  # shows this html block on the page
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

st.header("🧭 Why PokéScope?")  # heading for the problem statement
st.markdown(  # shows this html block on the page
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

st.write("")  # adds a bit of empty space
st.header("✨ What you can do")  # heading for the feature cards

explore_column, compare_column, discover_column = st.columns(3)  # makes 3 columns for the cards

with explore_column:  # first column
    st.markdown(  # shows this html block on the page
        """
        <div class="card">
        <h3>🔎 Explore Pokémon</h3>
        <p>Filter by type, generation and base experience, search by name,
        and open a live profile with official artwork and abilities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Pokedex_Explorer.py", label="Open the Pokédex Explorer", icon="🔎")  # link to the explorer page

with compare_column:  # second column
    st.markdown(  # shows this html block on the page
        """
        <div class="card">
        <h3>⚔️ Compare Pokémon</h3>
        <p>Put two Pokémon side by side in the Battle Lab and see which one
        has the stronger stats, one stat at a time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Battle_Lab.py", label="Open the Battle Lab", icon="⚔️")  # link to the battle lab page

with discover_column:  # third column
    st.markdown(  # shows this html block on the page
        """
        <div class="card">
        <h3>🌌 Discover Patterns</h3>
        <p>See how stats change across types and generations in the
        Pokémon Universe, using averages over every Pokémon.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Pokemon_Universe.py", label="Open the Pokémon Universe", icon="🌌")  # link to the universe page

st.divider()  # line across the page

st.header("📊 Dataset at a Glance")  # heading for the summary numbers

total_pokemon_count = len(pokemon_data)  # counts how many pokemon there are
number_of_types = pokemon_data["primary_type"].nunique()  # counts how many different types there are
number_of_generations = pokemon_data["generation"].nunique()  # counts how many generations there are
average_base_experience = round(pokemon_data["base_experience"].mean(), 1)  # works out the average base experience

total_column, types_column, generations_column, experience_column = st.columns(4)  # makes 4 columns side by side
total_column.metric("Total Pokémon", total_pokemon_count)  # shows the total pokemon
types_column.metric("Number of Types", number_of_types)  # shows the number of types
generations_column.metric("Number of Generations", number_of_generations)  # shows the number of generations
experience_column.metric("Average Base Experience", average_base_experience)  # shows the average base experience

st.divider()  # line across the page

st.header("🎲 Feeling lucky?")  # heading for the surprise me part
st.write(  # shows some text on the page
    "Pick a random Pokémon. It becomes your **current Pokémon**, and it will already be selected "
    "when you open the Pokédex Explorer profile or the Battle Lab."
)

if st.button("🎲 Surprise Me", type="primary"):  # runs when surprise me is clicked
    all_pokemon_names = list(pokemon_data["name"])  # makes a list of every pokemon name
    st.session_state.selected_pokemon = random.choice(all_pokemon_names)  # saves a random pokemon so other pages can use it

current_pokemon_name = st.session_state.selected_pokemon  # gets the saved pokemon name
matching_rows = pokemon_data[pokemon_data["name"] == current_pokemon_name]  # finds that pokemon in the data
 
if matching_rows.empty:  # checks if it wasnt found
    st.info("Your current Pokémon could not be found in the dataset.")  # shows a message instead of crashing
else:
    current_pokemon = matching_rows.iloc[0]  # gets the row for that pokemon
    type_badges_html = make_type_badge(current_pokemon["primary_type"])  # makes a badge for the first type
    if current_pokemon["secondary_type"] != "None":  # checks if it has a second type
        type_badges_html = type_badges_html + make_type_badge(current_pokemon["secondary_type"])  # adds a badge for the second type

    with st.container(border=True):  # puts this part inside a box
        name_column, total_stats_column, generation_column = st.columns([2, 1, 1])  # 3 columns, the first one is wider
        with name_column:  # first column
            st.subheader(f"Current Pokémon: #{current_pokemon['pokedex_number']} {current_pokemon_name}")  # shows the number and name
            st.markdown(type_badges_html, unsafe_allow_html=True)  # shows the type badges
        total_stats_column.metric("Total Stats", int(current_pokemon["total_stats"]))  # shows the total stats
        generation_column.metric("Generation", int(current_pokemon["generation"]))  # shows the generation
        st.page_link("pages/1_Pokedex_Explorer.py", label=f"See {current_pokemon_name}'s full profile", icon="➡️")  # link to see the full profile

st.divider()  # line across the page

with st.expander("📚 Where does the data come from?"):  # section that opens when clicked
    st.markdown(  # shows this html block on the page
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
