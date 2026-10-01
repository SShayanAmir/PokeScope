import pandas as pd

BASE_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"
ENGLISH_LANGUAGE_ID = 9

pokemon = pd.read_csv(BASE_URL + "pokemon.csv")
species = pd.read_csv(BASE_URL + "pokemon_species.csv")
species_names = pd.read_csv(BASE_URL + "pokemon_species_names.csv")
pokemon_stats = pd.read_csv(BASE_URL + "pokemon_stats.csv")
stats = pd.read_csv(BASE_URL + "stats.csv")
pokemon_types = pd.read_csv(BASE_URL + "pokemon_types.csv")
types = pd.read_csv(BASE_URL + "types.csv")

pokemon = pokemon[pokemon["is_default"] == 1]
pokemon = pokemon[["id", "species_id", "height", "weight", "base_experience"]]

species = species[["id", "generation_id"]]
species = species.rename(columns={"id": "species_id", "generation_id": "generation"})
pokemon = pokemon.merge(species, on="species_id")

english_names = species_names[species_names["local_language_id"] == ENGLISH_LANGUAGE_ID]
english_names = english_names[["pokemon_species_id", "name"]]
english_names = english_names.rename(columns={"pokemon_species_id": "species_id"})
pokemon = pokemon.merge(english_names, on="species_id")

pokemon["height_m"] = pokemon["height"] / 10
pokemon["weight_kg"] = pokemon["weight"] / 10

stats = stats[["id", "identifier"]]
stats = stats.rename(columns={"id": "stat_id", "identifier": "stat_name"})
pokemon_stats = pokemon_stats.merge(stats, on="stat_id")
wide_stats = pokemon_stats.pivot(index="pokemon_id", columns="stat_name", values="base_stat")
wide_stats = wide_stats.reset_index()
wide_stats = wide_stats.rename(columns={
    "pokemon_id": "id",
    "special-attack": "special_attack",
    "special-defense": "special_defense",
})
wide_stats = wide_stats[["id", "hp", "attack", "defense", "special_attack", "special_defense", "speed"]]
pokemon = pokemon.merge(wide_stats, on="id")

types = types[["id", "identifier"]]
types = types.rename(columns={"id": "type_id", "identifier": "type_name"})
pokemon_types = pokemon_types.merge(types, on="type_id")
pokemon_types["type_name"] = pokemon_types["type_name"].str.capitalize()

primary_types = pokemon_types[pokemon_types["slot"] == 1]
primary_types = primary_types[["pokemon_id", "type_name"]]
primary_types = primary_types.rename(columns={"pokemon_id": "id", "type_name": "primary_type"})
pokemon = pokemon.merge(primary_types, on="id")

secondary_types = pokemon_types[pokemon_types["slot"] == 2]
secondary_types = secondary_types[["pokemon_id", "type_name"]]
secondary_types = secondary_types.rename(columns={"pokemon_id": "id", "type_name": "secondary_type"})
pokemon = pokemon.merge(secondary_types, on="id", how="left")
pokemon["secondary_type"] = pokemon["secondary_type"].fillna("None")

pokemon = pokemon.rename(columns={"id": "pokedex_number"})
pokemon = pokemon.sort_values("pokedex_number")

final_columns = [
    "pokedex_number",
    "name",
    "primary_type",
    "secondary_type",
    "generation",
    "height_m",
    "weight_kg",
    "base_experience",
    "hp",
    "attack",
    "defense",
    "special_attack",
    "special_defense",
    "speed",
]
pokemon = pokemon[final_columns]

pokemon.to_csv("data/pokemon_data.csv", index=False)
print("Saved", len(pokemon), "Pokémon to data/pokemon_data.csv")
