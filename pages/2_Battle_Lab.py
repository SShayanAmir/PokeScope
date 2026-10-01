import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Battle Lab · PokéScope", page_icon="⚔️", layout="wide")

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

POKEMON_A_COLOR = "#D62828"
POKEMON_B_COLOR = "#1D4E89"


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


def find_highest_stat(pokemon_row):
    highest_stat_label = ""
    highest_stat_value = -1
    for stat_column_name in STAT_LABELS:
        if pokemon_row[stat_column_name] > highest_stat_value:
            highest_stat_value = pokemon_row[stat_column_name]
            highest_stat_label = STAT_LABELS[stat_column_name]
    return highest_stat_label, highest_stat_value


def show_pokemon_card(pokemon_row, card_label):
    pokemon_name = pokemon_row["name"]

    st.subheader(f"{card_label}: #{pokemon_row['pokedex_number']} {pokemon_name}")

    type_badges_html = make_type_badge(pokemon_row["primary_type"])
    if pokemon_row["secondary_type"] != "None":
        type_badges_html = type_badges_html + make_type_badge(pokemon_row["secondary_type"])
    st.markdown(type_badges_html, unsafe_allow_html=True)

    try:
        api_details = get_pokemon_details(int(pokemon_row["pokedex_number"]))
        artwork_url = api_details["sprites"]["other"]["official-artwork"]["front_default"]
    except requests.exceptions.RequestException:
        artwork_url = None

    if artwork_url is None:
        st.info("🖼️ Artwork couldn't be loaded from PokéAPI right now. The stats below still work.")
    else:
        st.image(artwork_url, caption=f"Official artwork of {pokemon_name}", width=240)

    top_row = st.columns(3)
    bottom_row = st.columns(3)
    stat_metric_columns = top_row + bottom_row
    stat_position = 0
    for stat_column_name in STAT_LABELS:
        stat_metric_columns[stat_position].metric(STAT_LABELS[stat_column_name], int(pokemon_row[stat_column_name]))
        stat_position = stat_position + 1

    total_stats = int(pokemon_row["total_stats"])
    average_stat = round(total_stats / 6, 1)
    highest_stat_label, highest_stat_value = find_highest_stat(pokemon_row)

    total_column, average_column, highest_column = st.columns(3)
    total_column.metric("Total Stats", total_stats)
    average_column.metric("Average Stat", average_stat)
    highest_column.metric("Highest Stat", f"{highest_stat_label} ({highest_stat_value})")


st.markdown(PAGE_CSS, unsafe_allow_html=True)

pokemon_data = load_pokemon_data()

if "selected_pokemon" not in st.session_state:
    st.session_state.selected_pokemon = "Pikachu"

st.markdown(
    """
    <div class="hero">
        <div class="pokeball"></div>
        <div>
            <h1>⚔️ Battle Lab</h1>
            <p>How do two specific Pokémon compare?</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Pick two Pokémon to compare their base stats side by side. "
    "**Pokémon A** starts as your current Pokémon from the other pages."
)

all_pokemon_names = list(pokemon_data["name"])

default_index_a = 0
if st.session_state.selected_pokemon in all_pokemon_names:
    default_index_a = all_pokemon_names.index(st.session_state.selected_pokemon)

default_index_b = 1
if "Charizard" in all_pokemon_names:
    default_index_b = all_pokemon_names.index("Charizard")

picker_a_column, picker_b_column = st.columns(2)
pokemon_a_name = picker_a_column.selectbox("🔴 Pokémon A", all_pokemon_names, index=default_index_a)
pokemon_b_name = picker_b_column.selectbox("🔵 Pokémon B", all_pokemon_names, index=default_index_b)

st.session_state.selected_pokemon = pokemon_a_name

if pokemon_a_name == pokemon_b_name:
    st.info(f"You picked {pokemon_a_name} twice. Choose two different Pokémon to see a comparison.")
    st.stop()

pokemon_a = pokemon_data[pokemon_data["name"] == pokemon_a_name].iloc[0]
pokemon_b = pokemon_data[pokemon_data["name"] == pokemon_b_name].iloc[0]

st.divider()

card_a_column, card_b_column = st.columns(2, gap="large")
with card_a_column:
    with st.container(border=True):
        show_pokemon_card(pokemon_a, "🔴 A")
with card_b_column:
    with st.container(border=True):
        show_pokemon_card(pokemon_b, "🔵 B")

st.divider()

st.header("📊 Stat-by-stat comparison")

comparison_rows = []
stats_won_by_a = 0
stats_won_by_b = 0
for stat_column_name in STAT_LABELS:
    stat_label = STAT_LABELS[stat_column_name]
    stat_value_a = int(pokemon_a[stat_column_name])
    stat_value_b = int(pokemon_b[stat_column_name])
    comparison_rows.append({"Stat": stat_label, "Pokemon": pokemon_a_name, "Value": stat_value_a})
    comparison_rows.append({"Stat": stat_label, "Pokemon": pokemon_b_name, "Value": stat_value_b})
    if stat_value_a > stat_value_b:
        stats_won_by_a = stats_won_by_a + 1
    if stat_value_b > stat_value_a:
        stats_won_by_b = stats_won_by_b + 1

comparison_chart_data = pd.DataFrame(comparison_rows)

comparison_chart = (
    alt.Chart(comparison_chart_data, title=f"Base stats: {pokemon_a_name} vs {pokemon_b_name}")
    .mark_bar(cornerRadiusEnd=4)
    .encode(
        x=alt.X("Value:Q", title="Base stat value"),
        y=alt.Y("Stat:N", title=None, sort=list(STAT_LABELS.values())),
        yOffset=alt.YOffset("Pokemon:N", sort=[pokemon_a_name, pokemon_b_name]),
        color=alt.Color(
            "Pokemon:N",
            title="Pokémon",
            scale=alt.Scale(domain=[pokemon_a_name, pokemon_b_name], range=[POKEMON_A_COLOR, POKEMON_B_COLOR]),
            legend=alt.Legend(orient="top"),
        ),
        tooltip=["Pokemon", "Stat", "Value"],
    )
    .properties(height=420)
)
st.altair_chart(comparison_chart, width="stretch")

st.header("🏆 Stat Advantage")

total_stats_a = int(pokemon_a["total_stats"])
total_stats_b = int(pokemon_b["total_stats"])
total_stats_difference = abs(total_stats_a - total_stats_b)

difference_column, a_wins_column, b_wins_column = st.columns(3)
difference_column.metric("Total Stats Difference", total_stats_difference)
a_wins_column.metric(f"Stats where {pokemon_a_name} is higher", f"{stats_won_by_a} of 6")
b_wins_column.metric(f"Stats where {pokemon_b_name} is higher", f"{stats_won_by_b} of 6")

if total_stats_a > total_stats_b:
    st.success(f"🔴 **{pokemon_a_name}** has the stat advantage: {total_stats_a} total vs {total_stats_b}, which is {total_stats_difference} points higher.")
elif total_stats_b > total_stats_a:
    st.success(f"🔵 **{pokemon_b_name}** has the stat advantage: {total_stats_b} total vs {total_stats_a}, which is {total_stats_difference} points higher.")
else:
    st.success(f"It's a tie! {pokemon_a_name} and {pokemon_b_name} both have {total_stats_a} total stats.")

st.caption(
    "Stat Advantage only compares the sum of the six base stats. It does **not** predict who would win a real "
    "Pokémon battle, which also depends on types, moves, abilities, levels and strategy."
)
