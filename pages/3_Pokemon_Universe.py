import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pokémon Universe · PokéScope", page_icon="🌌", layout="wide")

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
"""

STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special_attack": "Special Attack",
    "special_defense": "Special Defense",
    "speed": "Speed",
}

ANALYSIS_COLUMN_NAMES = {
    "Attack": "attack",
    "Defense": "defense",
    "Speed": "speed",
    "HP": "hp",
    "Special Attack": "special_attack",
    "Special Defense": "special_defense",
    "Total Stats": "total_stats",
}

PRIMARY_CHART_COLOR = "#D62828"
SECONDARY_CHART_COLOR = "#1D4E89"


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


st.markdown(PAGE_CSS, unsafe_allow_html=True)

pokemon_data = load_pokemon_data()

st.markdown(
    """
    <div class="hero">
        <div class="pokeball"></div>
        <div>
            <h1>🌌 Pokémon Universe</h1>
            <p>What patterns exist across types and generations?</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(f"Every number on this page is calculated from all **{len(pokemon_data)} Pokémon** in the dataset.")

analysis_labels = list(ANALYSIS_COLUMN_NAMES.keys())

overview_tab, types_tab, generations_tab = st.tabs(["🌍 Overview", "🔥 Types", "🗓️ Generations"])

with overview_tab:
    strongest_stat_label = ""
    strongest_stat_average = 0
    for stat_column_name in STAT_LABELS:
        stat_average = pokemon_data[stat_column_name].mean()
        if stat_average > strongest_stat_average:
            strongest_stat_average = stat_average
            strongest_stat_label = STAT_LABELS[stat_column_name]

    average_weight = round(pokemon_data["weight_kg"].mean(), 1)
    average_height = round(pokemon_data["height_m"].mean(), 2)
    average_total_stats = round(pokemon_data["total_stats"].mean(), 1)

    strongest_column, weight_column, height_column, total_column = st.columns(4)
    strongest_column.metric("Strongest Average Stat", f"{strongest_stat_label} ({round(strongest_stat_average, 1)})")
    weight_column.metric("Average Weight", f"{average_weight} kg")
    height_column.metric("Average Height", f"{average_height} m")
    total_column.metric("Average Total Stats", average_total_stats)

    st.write("")
    histogram_column, top_five_column = st.columns([3, 2], gap="large")

    with histogram_column:
        total_stats_histogram = (
            alt.Chart(pokemon_data, title="How are total stats spread across all Pokémon?")
            .mark_bar(color=PRIMARY_CHART_COLOR)
            .encode(
                x=alt.X("total_stats:Q", bin=alt.Bin(maxbins=30), title="Total Stats"),
                y=alt.Y("count():Q", title="Number of Pokémon"),
                tooltip=[alt.Tooltip("count():Q", title="Number of Pokémon")],
            )
            .properties(height=360)
        )
        st.altair_chart(total_stats_histogram, width="stretch")

    with top_five_column:
        top_five_pokemon = pokemon_data.sort_values("total_stats", ascending=False).head(5)
        top_five_chart = (
            alt.Chart(top_five_pokemon, title="Top 5 Pokémon by Total Stats")
            .mark_bar(color=SECONDARY_CHART_COLOR, cornerRadiusEnd=6)
            .encode(
                x=alt.X("total_stats:Q", title="Total Stats"),
                y=alt.Y("name:N", title=None, sort="-x"),
                tooltip=[alt.Tooltip("name:N", title="Pokémon"), alt.Tooltip("total_stats:Q", title="Total Stats")],
            )
            .properties(height=360)
        )
        st.altair_chart(top_five_chart, width="stretch")

    with st.expander("ℹ️ What does “Total Stats” mean?"):
        st.write(
            "Total Stats is calculated by PokéScope as HP + Attack + Defense + Special Attack + "
            "Special Defense + Speed. It gives a quick overall picture of how strong a Pokémon's base stats are."
        )

with types_tab:
    st.subheader("Which types are strongest in each stat?")
    type_stat_label = st.selectbox("Statistic to compare across types", analysis_labels)
    type_stat_column_name = ANALYSIS_COLUMN_NAMES[type_stat_label]

    type_averages = pokemon_data.groupby("primary_type")[type_stat_column_name].mean().reset_index()
    type_averages.columns = ["Type", "Average"]
    type_averages["Average"] = type_averages["Average"].round(1)
    type_averages = type_averages.sort_values("Average", ascending=False)

    highest_type = type_averages.iloc[0]
    lowest_type = type_averages.iloc[-1]

    best_column, worst_column = st.columns(2)
    best_column.metric(f"Highest Average {type_stat_label}", f"{highest_type['Type']} ({highest_type['Average']})")
    worst_column.metric(f"Lowest Average {type_stat_label}", f"{lowest_type['Type']} ({lowest_type['Average']})")

    type_chart = (
        alt.Chart(type_averages, title=f"Average {type_stat_label} by primary type")
        .mark_bar(color=PRIMARY_CHART_COLOR, cornerRadiusEnd=6)
        .encode(
            x=alt.X("Average:Q", title=f"Average {type_stat_label}"),
            y=alt.Y("Type:N", title="Primary Type", sort="-x"),
            tooltip=["Type", "Average"],
        )
        .properties(height=520)
    )
    st.altair_chart(type_chart, width="stretch")

    with st.expander("📋 See the numbers as a table"):
        st.dataframe(type_averages, hide_index=True)
        st.caption("Each Pokémon is counted once, using its first (primary) type.")

with generations_tab:
    st.subheader("How have Pokémon changed between generations?")
    generation_stat_label = st.selectbox(
        "Statistic to compare across generations",
        analysis_labels,
        index=analysis_labels.index("Total Stats"),
    )
    generation_stat_column_name = ANALYSIS_COLUMN_NAMES[generation_stat_label]

    generation_averages = pokemon_data.groupby("generation")[generation_stat_column_name].mean().reset_index()
    generation_averages.columns = ["Generation", "Average"]
    generation_averages["Average"] = generation_averages["Average"].round(1)

    generation_counts = pokemon_data.groupby("generation")["name"].count().reset_index()
    generation_counts.columns = ["Generation", "Number of Pokémon"]

    highest_generation = generation_averages.sort_values("Average", ascending=False).iloc[0]
    biggest_generation = generation_counts.sort_values("Number of Pokémon", ascending=False).iloc[0]

    trivia_one_column, trivia_two_column = st.columns(2)
    trivia_one_column.info(
        f"💡 Generation {int(highest_generation['Generation'])} has the highest average "
        f"{generation_stat_label} ({highest_generation['Average']})."
    )
    trivia_two_column.info(
        f"💡 Generation {int(biggest_generation['Generation'])} introduced the most Pokémon "
        f"({int(biggest_generation['Number of Pokémon'])})."
    )

    average_column, count_column = st.columns(2, gap="large")

    with average_column:
        generation_average_chart = (
            alt.Chart(generation_averages, title=f"Average {generation_stat_label} by generation")
            .mark_bar(color=PRIMARY_CHART_COLOR, cornerRadiusEnd=6)
            .encode(
                x=alt.X("Generation:O", title="Generation", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Average:Q", title=f"Average {generation_stat_label}"),
                tooltip=["Generation", "Average"],
            )
            .properties(height=380)
        )
        st.altair_chart(generation_average_chart, width="stretch")

    with count_column:
        generation_count_chart = (
            alt.Chart(generation_counts, title="Number of new Pokémon per generation")
            .mark_bar(color=SECONDARY_CHART_COLOR, cornerRadiusEnd=6)
            .encode(
                x=alt.X("Generation:O", title="Generation", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Number of Pokémon:Q", title="Number of Pokémon"),
                tooltip=["Generation", "Number of Pokémon"],
            )
            .properties(height=380)
        )
        st.altair_chart(generation_count_chart, width="stretch")
