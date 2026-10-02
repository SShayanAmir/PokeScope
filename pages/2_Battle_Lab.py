import altair as alt  # library for making the charts
import pandas as pd  # used to read and work with the csv data
import requests  # used to call the pokeapi
import streamlit as st  # used to build the web app

st.set_page_config(page_title="Battle Lab · PokéScope", page_icon="⚔️", layout="wide")  # sets tab title, icon and wide layout

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

POKEMON_A_COLOR = "#D62828"  # red for pokemon a
POKEMON_B_COLOR = "#1D4E89"  # blue for pokemon b


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


@st.cache_data  # saves the result so it doesnt have to run again every time
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


def find_highest_stat(pokemon_row):  # function to find a pokemons best stat
    highest_stat_label = ""  # no stat name yet
    highest_stat_value = -1  # starts at -1 so the first stat always wins
    for stat_column_name in STAT_LABELS:  # goes through each of the 6 stats
        if pokemon_row[stat_column_name] > highest_stat_value:  # checks if this stat is bigger than the best so far
            highest_stat_value = pokemon_row[stat_column_name]  # saves the new best value
            highest_stat_label = STAT_LABELS[stat_column_name]  # saves the new best name
    return highest_stat_label, highest_stat_value  # gives back the best stat and its value


def show_pokemon_card(pokemon_row, card_label):  # function that draws one pokemon card
    pokemon_name = pokemon_row["name"]  # gets the pokemon name

    st.subheader(f"{card_label}: #{pokemon_row['pokedex_number']} {pokemon_name}")  # shows the card title

    type_badges_html = make_type_badge(pokemon_row["primary_type"])  # makes a badge for the first type
    if pokemon_row["secondary_type"] != "None":  # checks if it has a second type
        type_badges_html = type_badges_html + make_type_badge(pokemon_row["secondary_type"])  # adds a badge for the second type
    st.markdown(type_badges_html, unsafe_allow_html=True)  # shows the type badges

    try:  # tries to call the api
        api_details = get_pokemon_details(int(pokemon_row["pokedex_number"]))  # gets the pokemon details using its pokedex number
        artwork_url = api_details["sprites"]["other"]["official-artwork"]["front_default"]  # gets the official artwork link
    except requests.exceptions.RequestException:  # if the api call fails
        artwork_url = None  # no image then

    if artwork_url is None:  # if there is no image
        st.info("🖼️ Artwork couldn't be loaded from PokéAPI right now. The stats below still work.")  # shows a message instead
    else:  # otherwise
        st.image(artwork_url, caption=f"Official artwork of {pokemon_name}", width=240)  # shows the artwork

    top_row = st.columns(3)  # first row of 3 boxes
    bottom_row = st.columns(3)  # second row of 3 boxes
    stat_metric_columns = top_row + bottom_row  # joins them into one list of 6
    stat_position = 0  # starts at the first box
    for stat_column_name in STAT_LABELS:  # goes through each of the 6 stats
        stat_metric_columns[stat_position].metric(STAT_LABELS[stat_column_name], int(pokemon_row[stat_column_name]))  # shows the stat in its box
        stat_position = stat_position + 1  # moves to the next box

    total_stats = int(pokemon_row["total_stats"])  # gets the total stats
    average_stat = round(total_stats / 6, 1)  # works out the average of the 6 stats
    highest_stat_label, highest_stat_value = find_highest_stat(pokemon_row)  # finds the best stat

    total_column, average_column, highest_column = st.columns(3)  # makes 3 columns
    total_column.metric("Total Stats", total_stats)  # shows the total
    average_column.metric("Average Stat", average_stat)  # shows the average
    highest_column.metric("Highest Stat", f"{highest_stat_label} ({highest_stat_value})")  # shows the best stat


st.markdown(PAGE_CSS, unsafe_allow_html=True)

pokemon_data = load_pokemon_data()  # loads the data

if "selected_pokemon" not in st.session_state:  # checks if no pokemon is saved yet
    st.session_state.selected_pokemon = "Pikachu"  # sets pikachu as the starting pokemon

st.markdown(  # shows this html block on the page
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

st.write(  # shows some text on the page
    "Pick two Pokémon to compare their base stats side by side. "
    "**Pokémon A** starts as your current Pokémon from the other pages."
)

all_pokemon_names = list(pokemon_data["name"])  # makes a list of every pokemon name

default_index_a = 0  # pokemon a starts on the first pokemon by default
if st.session_state.selected_pokemon in all_pokemon_names:  # checks if there is a saved pokemon
    default_index_a = all_pokemon_names.index(st.session_state.selected_pokemon)  # uses the saved pokemon for pokemon a

default_index_b = 1  # pokemon b starts on the second pokemon by default
if "Charizard" in all_pokemon_names:  # checks if charizard is in the list
    default_index_b = all_pokemon_names.index("Charizard")  # uses charizard for pokemon b

picker_a_column, picker_b_column = st.columns(2)  # makes 2 columns for the dropdowns
pokemon_a_name = picker_a_column.selectbox("🔴 Pokémon A", all_pokemon_names, index=default_index_a)  # dropdown for pokemon a
pokemon_b_name = picker_b_column.selectbox("🔵 Pokémon B", all_pokemon_names, index=default_index_b)  # dropdown for pokemon b

st.session_state.selected_pokemon = pokemon_a_name  # saves pokemon a so other pages can use it

if pokemon_a_name == pokemon_b_name:  # checks if the same pokemon was picked twice
    st.info(f"You picked {pokemon_a_name} twice. Choose two different Pokémon to see a comparison.")  # shows a message
    st.stop()  # stops the page here

pokemon_a = pokemon_data[pokemon_data["name"] == pokemon_a_name].iloc[0]  # gets the row for pokemon a
pokemon_b = pokemon_data[pokemon_data["name"] == pokemon_b_name].iloc[0]  # gets the row for pokemon b

st.divider()  # line across the page

card_a_column, card_b_column = st.columns(2, gap="large")  # makes 2 columns for the cards
with card_a_column:  # left column
    with st.container(border=True):  # puts the card inside a box
        show_pokemon_card(pokemon_a, "🔴 A")  # draws the card for pokemon a
with card_b_column:  # right column
    with st.container(border=True):  # puts the card inside a box
        show_pokemon_card(pokemon_b, "🔵 B")  # draws the card for pokemon b

st.divider()  # line across the page

st.header("📊 Stat-by-stat comparison")  # heading for the chart

comparison_rows = []  # empty list for the chart rows
stats_won_by_a = 0  # counts stats where a is higher
stats_won_by_b = 0  # counts stats where b is higher
for stat_column_name in STAT_LABELS:  # goes through each of the 6 stats
    stat_label = STAT_LABELS[stat_column_name]  # gets the nice stat name
    stat_value_a = int(pokemon_a[stat_column_name])  # gets pokemon a's value
    stat_value_b = int(pokemon_b[stat_column_name])  # gets pokemon b's value
    comparison_rows.append({"Stat": stat_label, "Pokemon": pokemon_a_name, "Value": stat_value_a})  # adds a row for pokemon a
    comparison_rows.append({"Stat": stat_label, "Pokemon": pokemon_b_name, "Value": stat_value_b})  # adds a row for pokemon b
    if stat_value_a > stat_value_b:  # if a is higher
        stats_won_by_a = stats_won_by_a + 1  # add one to a's count
    if stat_value_b > stat_value_a:  # if b is higher
        stats_won_by_b = stats_won_by_b + 1  # add one to b's count

comparison_chart_data = pd.DataFrame(comparison_rows)  # turns the rows into a table for the chart

comparison_chart = (  # builds the comparison chart
    alt.Chart(comparison_chart_data, title=f"Base stats: {pokemon_a_name} vs {pokemon_b_name}")  # uses the table and adds a title
    .mark_bar(cornerRadiusEnd=4)  # bar chart with rounded ends
    .encode(  # says what goes where
        x=alt.X("Value:Q", title="Base stat value"),  # values on the x axis
        y=alt.Y("Stat:N", title=None, sort=list(STAT_LABELS.values())),  # stat names on the y axis in normal order
        yOffset=alt.YOffset("Pokemon:N", sort=[pokemon_a_name, pokemon_b_name]),  # puts the two bars next to each other
        color=alt.Color(  # colours the bars by pokemon
            "Pokemon:N",  # uses the pokemon column for the colour
            title="Pokémon",  # legend title
            scale=alt.Scale(domain=[pokemon_a_name, pokemon_b_name], range=[POKEMON_A_COLOR, POKEMON_B_COLOR]),  # a is red and b is blue
            legend=alt.Legend(orient="top"),  # puts the legend on top
        ),
        tooltip=["Pokemon", "Stat", "Value"],  # shows the numbers when you hover
    )
    .properties(height=420)  # sets the chart height
)
st.altair_chart(comparison_chart, width="stretch")  # shows the chart

st.header("🏆 Stat Advantage")  # heading for the result

total_stats_a = int(pokemon_a["total_stats"])  # total stats for a
total_stats_b = int(pokemon_b["total_stats"])  # total stats for b
total_stats_difference = abs(total_stats_a - total_stats_b)  # difference between them, always positive
 
difference_column, a_wins_column, b_wins_column = st.columns(3)  # makes 3 columns
difference_column.metric("Total Stats Difference", total_stats_difference)  # shows the difference
a_wins_column.metric(f"Stats where {pokemon_a_name} is higher", f"{stats_won_by_a} of 6")  # shows how many stats a wins
b_wins_column.metric(f"Stats where {pokemon_b_name} is higher", f"{stats_won_by_b} of 6")  # shows how many stats b wins

if total_stats_a > total_stats_b:  # if a has the higher total
    st.success(f"🔴 **{pokemon_a_name}** has the stat advantage: {total_stats_a} total vs {total_stats_b}, which is {total_stats_difference} points higher.")  # says a has the advantage
elif total_stats_b > total_stats_a:  # if b has the higher total
    st.success(f"🔵 **{pokemon_b_name}** has the stat advantage: {total_stats_b} total vs {total_stats_a}, which is {total_stats_difference} points higher.")  # says b has the advantage
else:  # otherwise
    st.success(f"It's a tie! {pokemon_a_name} and {pokemon_b_name} both have {total_stats_a} total stats.")  # says its a tie

st.caption(  # small note at the bottom
    "Stat Advantage only compares the sum of the six base stats. It does **not** predict who would win a real "
    "Pokémon battle, which also depends on types, moves, abilities, levels and strategy."
)
