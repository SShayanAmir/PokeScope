import altair as alt  # library for making the charts
import pandas as pd  # used to read and work with the csv data
import streamlit as st  # used to build the web app

st.set_page_config(page_title="Pokémon Universe · PokéScope", page_icon="🌌", layout="wide")  # sets tab title, icon and wide layout

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
div[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #DDE2EC; border-radius: 16px; padding: 1rem 1.2rem;
}
button[data-baseweb="tab"] p { font-size: 1.15rem; font-weight: 600; }
</style>
"""  # css styling for the page

STAT_LABELS = {  # csv column names matched to nice names for the user
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special_attack": "Special Attack",
    "special_defense": "Special Defense",
    "speed": "Speed",
}

ANALYSIS_COLUMN_NAMES = {  # dropdown options matched to the csv columns
    "Attack": "attack",
    "Defense": "defense",
    "Speed": "speed",
    "HP": "hp",
    "Special Attack": "special_attack",
    "Special Defense": "special_defense",
    "Total Stats": "total_stats",
}

PRIMARY_CHART_COLOR = "#D62828"  # red for the main charts
SECONDARY_CHART_COLOR = "#1D4E89"  # blue for the other charts


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


st.markdown(PAGE_CSS, unsafe_allow_html=True)  # applies the css to the page

pokemon_data = load_pokemon_data()  # loads the data

st.markdown(  # shows this html block on the page
    """
    <div class="hero">
        <div class="pokeball"></div>
        <div>
            <h1>🌌 Pokémon Universe</h1>
            <p>What patterns exist across types and generations?</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,  # lets streamlit show the html
)

st.write(f"Every number on this page is calculated from all **{len(pokemon_data)} Pokémon** in the dataset.")  # says how many pokemon are used

analysis_labels = list(ANALYSIS_COLUMN_NAMES.keys())  # list of the dropdown options

overview_tab, types_tab, generations_tab = st.tabs(["🌍 Overview", "🔥 Types", "🗓️ Generations"])  # makes the 3 tabs

with overview_tab:  # everything in the overview tab
    strongest_stat_label = ""  # no stat name yet
    strongest_stat_average = 0  # starts at 0
    for stat_column_name in STAT_LABELS:  # goes through each of the 6 stats
        stat_average = pokemon_data[stat_column_name].mean()  # works out the average of this stat
        if stat_average > strongest_stat_average:  # checks if it is the biggest so far
            strongest_stat_average = stat_average  # saves the new biggest average
            strongest_stat_label = STAT_LABELS[stat_column_name]  # saves its name

    average_weight = round(pokemon_data["weight_kg"].mean(), 1)  # average weight
    average_height = round(pokemon_data["height_m"].mean(), 2)  # average height
    average_total_stats = round(pokemon_data["total_stats"].mean(), 1)  # average total stats

    strongest_column, weight_column, height_column, total_column = st.columns(4)  # makes 4 columns
    strongest_column.metric("Strongest Average Stat", f"{strongest_stat_label} ({round(strongest_stat_average, 1)})")  # shows the strongest stat
    weight_column.metric("Average Weight", f"{average_weight} kg")  # shows the average weight
    height_column.metric("Average Height", f"{average_height} m")  # shows the average height
    total_column.metric("Average Total Stats", average_total_stats)  # shows the average total stats

    st.write("")  # adds a bit of empty space
    histogram_column, top_five_column = st.columns([3, 2], gap="large")  # 2 columns, the left one is wider

    with histogram_column:  # left column
        total_stats_histogram = (  # builds the histogram
            alt.Chart(pokemon_data, title="How are total stats spread across all Pokémon?")  # uses all the data and adds a title
            .mark_bar(color=PRIMARY_CHART_COLOR)  # red bars
            .encode(  # says what goes where
                x=alt.X("total_stats:Q", bin=alt.Bin(maxbins=30), title="Total Stats"),  # groups total stats into ranges
                y=alt.Y("count():Q", title="Number of Pokémon"),  # counts the pokemon in each range
                tooltip=[alt.Tooltip("count():Q", title="Number of Pokémon")],  # shows the count when you hover
            )
            .properties(height=360)  # sets the chart height
        )
        st.altair_chart(total_stats_histogram, width="stretch")  # shows the histogram

    with top_five_column:  # right column
        top_five_pokemon = pokemon_data.sort_values("total_stats", ascending=False).head(5)  # gets the 5 pokemon with the highest total
        top_five_chart = (  # builds the top 5 chart
            alt.Chart(top_five_pokemon, title="Top 5 Pokémon by Total Stats")  # uses the top 5 and adds a title
            .mark_bar(color=SECONDARY_CHART_COLOR, cornerRadiusEnd=6)  # blue bars with rounded ends
            .encode(  # says what goes where
                x=alt.X("total_stats:Q", title="Total Stats"),  # total stats on the x axis
                y=alt.Y("name:N", title=None, sort="-x"),  # names on the y axis, biggest first
                tooltip=[alt.Tooltip("name:N", title="Pokémon"), alt.Tooltip("total_stats:Q", title="Total Stats")],  # shows name and total when you hover
            )
            .properties(height=360)  # sets the chart height
        )
        st.altair_chart(top_five_chart, width="stretch")  # shows the chart

    with st.expander("ℹ️ What does “Total Stats” mean?"):  # section that opens when clicked
        st.write(  # shows some text on the page
            "Total Stats is calculated by PokéScope as HP + Attack + Defense + Special Attack + "
            "Special Defense + Speed. It gives a quick overall picture of how strong a Pokémon's base stats are."
        )

with types_tab:  # everything in the types tab
    st.subheader("Which types are strongest in each stat?")  # heading for the tab
    type_stat_label = st.selectbox("Statistic to compare across types", analysis_labels)  # dropdown to pick a stat
    type_stat_column_name = ANALYSIS_COLUMN_NAMES[type_stat_label]  # gets the csv column for that stat

    type_averages = pokemon_data.groupby("primary_type")[type_stat_column_name].mean().reset_index()  # groups by type and gets the average
    type_averages.columns = ["Type", "Average"]  # renames the columns
    type_averages["Average"] = type_averages["Average"].round(1)  # rounds to 1 decimal
    type_averages = type_averages.sort_values("Average", ascending=False)  # sorts highest first

    highest_type = type_averages.iloc[0]  # first row is the highest
    lowest_type = type_averages.iloc[-1]  # last row is the lowest

    best_column, worst_column = st.columns(2)  # makes 2 columns
    best_column.metric(f"Highest Average {type_stat_label}", f"{highest_type['Type']} ({highest_type['Average']})")  # shows the highest type
    worst_column.metric(f"Lowest Average {type_stat_label}", f"{lowest_type['Type']} ({lowest_type['Average']})")  # shows the lowest type

    type_chart = (  # builds the type chart
        alt.Chart(type_averages, title=f"Average {type_stat_label} by primary type")  # uses the averages and adds a title
        .mark_bar(color=PRIMARY_CHART_COLOR, cornerRadiusEnd=6)  # red bars with rounded ends
        .encode(  # says what goes where
            x=alt.X("Average:Q", title=f"Average {type_stat_label}"),  # averages on the x axis
            y=alt.Y("Type:N", title="Primary Type", sort="-x"),  # types on the y axis, highest first
            tooltip=["Type", "Average"],  # shows the numbers when you hover
        ) 
        .properties(height=520)  # sets the chart height
    )
    st.altair_chart(type_chart, width="stretch")  # shows the chart

    with st.expander("📋 See the numbers as a table"):  # section that opens when clicked
        st.dataframe(type_averages, hide_index=True)  # shows the averages as a table
        st.caption("Each Pokémon is counted once, using its first (primary) type.")  # small note under the table

with generations_tab:  # everything in the generations tab
    st.subheader("How have Pokémon changed between generations?")  # heading for the tab
    generation_stat_label = st.selectbox(  # dropdown to pick a stat
        "Statistic to compare across generations",  # label for the dropdown
        analysis_labels,  # the options
        index=analysis_labels.index("Total Stats"),  # starts on total stats
    )
    generation_stat_column_name = ANALYSIS_COLUMN_NAMES[generation_stat_label]  # gets the csv column for that stat

    generation_averages = pokemon_data.groupby("generation")[generation_stat_column_name].mean().reset_index()  # groups by generation and gets the average
    generation_averages.columns = ["Generation", "Average"]  # renames the columns
    generation_averages["Average"] = generation_averages["Average"].round(1)  # rounds to 1 decimal

    generation_counts = pokemon_data.groupby("generation")["name"].count().reset_index()  # counts the pokemon in each generation
    generation_counts.columns = ["Generation", "Number of Pokémon"]  # renames the columns

    highest_generation = generation_averages.sort_values("Average", ascending=False).iloc[0]  # finds the generation with the highest average
    biggest_generation = generation_counts.sort_values("Number of Pokémon", ascending=False).iloc[0]  # finds the generation with the most pokemon

    trivia_one_column, trivia_two_column = st.columns(2)  # makes 2 columns
    trivia_one_column.info(  # shows the first fact
        f"💡 Generation {int(highest_generation['Generation'])} has the highest average "
        f"{generation_stat_label} ({highest_generation['Average']})."
    )
    trivia_two_column.info(  # shows the second fact
        f"💡 Generation {int(biggest_generation['Generation'])} introduced the most Pokémon "
        f"({int(biggest_generation['Number of Pokémon'])})."
    )

    average_column, count_column = st.columns(2, gap="large")  # makes 2 columns for the charts

    with average_column:  # left column
        generation_average_chart = (  # builds the average chart
            alt.Chart(generation_averages, title=f"Average {generation_stat_label} by generation")  # uses the averages and adds a title
            .mark_bar(color=PRIMARY_CHART_COLOR, cornerRadiusEnd=6)  # red bars with rounded ends
            .encode(  # says what goes where
                x=alt.X("Generation:O", title="Generation", axis=alt.Axis(labelAngle=0)),  # generations on the x axis in order
                y=alt.Y("Average:Q", title=f"Average {generation_stat_label}"),  # averages on the y axis
                tooltip=["Generation", "Average"],  # shows the numbers when you hover
            )
            .properties(height=380)  # sets the chart height
        )
        st.altair_chart(generation_average_chart, width="stretch")  # shows the chart

    with count_column:  # right column
        generation_count_chart = (  # builds the count chart
            alt.Chart(generation_counts, title="Number of new Pokémon per generation")  # uses the counts and adds a title
            .mark_bar(color=SECONDARY_CHART_COLOR, cornerRadiusEnd=6)  # blue bars with rounded ends
            .encode(  # says what goes where
                x=alt.X("Generation:O", title="Generation", axis=alt.Axis(labelAngle=0)),  # generations on the x axis in order
                y=alt.Y("Number of Pokémon:Q", title="Number of Pokémon"),  # counts on the y axis
                tooltip=["Generation", "Number of Pokémon"],  # shows the numbers when you hover
            )
            .properties(height=380)  # sets the chart height
        )
        st.altair_chart(generation_count_chart, width="stretch")  # shows the chart
