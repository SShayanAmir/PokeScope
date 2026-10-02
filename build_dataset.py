import pandas as pd  # used to read and combine the csv files

BASE_URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"  # where the official pokeapi csv files are
ENGLISH_LANGUAGE_ID = 9  # language id for english names
 
pokemon = pd.read_csv(BASE_URL + "pokemon.csv")  # main pokemon file
species = pd.read_csv(BASE_URL + "pokemon_species.csv")  # has the generation
species_names = pd.read_csv(BASE_URL + "pokemon_species_names.csv")  # has the proper names
pokemon_stats = pd.read_csv(BASE_URL + "pokemon_stats.csv")  # has the stats
stats = pd.read_csv(BASE_URL + "stats.csv")  # has the stat names
pokemon_types = pd.read_csv(BASE_URL + "pokemon_types.csv")  # says which types each pokemon has
types = pd.read_csv(BASE_URL + "types.csv")  # has the type names

pokemon = pokemon[pokemon["is_default"] == 1]  # keeps only the normal form of each pokemon
pokemon = pokemon[["id", "species_id", "height", "weight", "base_experience"]]  # keeps only the columns we need

species = species[["id", "generation_id"]]  # keeps the id and generation
species = species.rename(columns={"id": "species_id", "generation_id": "generation"})  # renames the columns
pokemon = pokemon.merge(species, on="species_id")  # adds the generation to each pokemon

english_names = species_names[species_names["local_language_id"] == ENGLISH_LANGUAGE_ID]  # keeps only the english names
english_names = english_names[["pokemon_species_id", "name"]]  # keeps the id and name
english_names = english_names.rename(columns={"pokemon_species_id": "species_id"})  # renames the id column
pokemon = pokemon.merge(english_names, on="species_id")  # adds the name to each pokemon

pokemon["height_m"] = pokemon["height"] / 10  # changes height to metres
pokemon["weight_kg"] = pokemon["weight"] / 10  # changes weight to kilograms

stats = stats[["id", "identifier"]]  # keeps the stat id and name
stats = stats.rename(columns={"id": "stat_id", "identifier": "stat_name"})  # renames the columns
pokemon_stats = pokemon_stats.merge(stats, on="stat_id")  # adds the stat names
wide_stats = pokemon_stats.pivot(index="pokemon_id", columns="stat_name", values="base_stat")  # turns the stat rows into columns
wide_stats = wide_stats.reset_index()  # makes the id a normal column again
wide_stats = wide_stats.rename(columns={  # renames the columns to match
    "pokemon_id": "id",
    "special-attack": "special_attack",
    "special-defense": "special_defense",
})
wide_stats = wide_stats[["id", "hp", "attack", "defense", "special_attack", "special_defense", "speed"]]  # keeps the 6 stats
pokemon = pokemon.merge(wide_stats, on="id")  # adds the stats to each pokemon

types = types[["id", "identifier"]]  # keeps the type id and name
types = types.rename(columns={"id": "type_id", "identifier": "type_name"})  # renames the columns
pokemon_types = pokemon_types.merge(types, on="type_id")  # adds the type names
pokemon_types["type_name"] = pokemon_types["type_name"].str.capitalize()  # capitalises the type names

primary_types = pokemon_types[pokemon_types["slot"] == 1]  # slot 1 is the first type
primary_types = primary_types[["pokemon_id", "type_name"]]  # keeps the id and type
primary_types = primary_types.rename(columns={"pokemon_id": "id", "type_name": "primary_type"})  # renames the columns
pokemon = pokemon.merge(primary_types, on="id")  # adds the first type

secondary_types = pokemon_types[pokemon_types["slot"] == 2]  # slot 2 is the second type
secondary_types = secondary_types[["pokemon_id", "type_name"]]  # keeps the id and type
secondary_types = secondary_types.rename(columns={"pokemon_id": "id", "type_name": "secondary_type"})  # renames the columns
pokemon = pokemon.merge(secondary_types, on="id", how="left")  # adds the second type but keeps pokemon without one
pokemon["secondary_type"] = pokemon["secondary_type"].fillna("None")  # puts "None" if there is no second type

pokemon = pokemon.rename(columns={"id": "pokedex_number"})  # renames id to pokedex number
pokemon = pokemon.sort_values("pokedex_number")  # sorts by pokedex number

final_columns = [  # the columns for the final csv
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
pokemon = pokemon[final_columns]  # keeps only those columns

pokemon.to_csv("data/pokemon_data.csv", index=False)  # saves the final csv
print("Saved", len(pokemon), "Pokémon to data/pokemon_data.csv")  # prints how many pokemon were saved
