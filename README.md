# PokéScope: Interactive Pokémon Explorer
PokéScope is a multi-page Streamlit app for exploring, filtering, comparing and analyzing Pokémon. It combines an open-source Pokémon dataset (CSV) with live details from the free PokéAPI.

## Problem Statement

**Who it's for:** Pokémon players and fans, who have more than a thousand Pokémon to choose from, each with different types, physical characteristics, abilities, and battle statistics.

**The problem:** Comparing Pokémon or discovering patterns across generations is difficult when information is presented one Pokémon at a time.

**Why it matters:** Choosing which Pokémon to use, or simply understanding how they differ, means flipping between many separate entries and trying to remember the numbers, so good options and interesting patterns are easy to miss.

PokéScope provides an interactive way to explore, filter, compare, and analyze Pokémon, while retrieving detailed information from the live PokéAPI.

## Dataset Source
`data/pokemon_data.csv` was built from the official open-source [PokéAPI CSV files](https://github.com/PokeAPI/pokeapi/tree/master/data/v2/csv) by running `python build_dataset.py`. The script:

1. Loads `pokemon.csv` and keeps only default forms (`is_default == 1`), giving one entry per species (1,025 Pokémon).
2. Adds the generation from `pokemon_species.csv` and the English name from `pokemon_species_names.csv`.
3. Converts height from decimetres to metres and weight from hectograms to kilograms (divides both by 10).
4. Adds the six base stats from `pokemon_stats.csv` and `stats.csv`, turning them into one column per stat.
5. Adds the primary and secondary types from `pokemon_types.csv` and `types.csv`.

No values were typed in by hand. Total Stats is not stored in the CSV; the app calculates it.

## API Source

[PokéAPI](https://pokeapi.co/). This is a free API with no key and no sign-up. The app calls `https://pokeapi.co/api/v2/pokemon/{pokedex_number}` with `requests.get()` to load official artwork, abilities, types, height, weight and stats. Calls are cached with `@st.cache_data`, and the app shows a friendly message if the API can't be reached.