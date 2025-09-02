import pandas as pd

data = pd.read_csv("ALL_SETS.csv")

supporter_names = [
    "erika","misty","blaine","koga","giovanni","brock","sabrina","lt. surge",
    "budding expeditioner","blue","leaf",
    "cyrus","team galactic grunt","cynthia","volkner","dawn","mars",
    "irida","celestic town elder","barry","adaman",
    "iono","pokemon center lady","red","team rocket grunt",
    "acerola","illima","kiawe","guzma","lana","sophocles","mallow","lillie",
    "gladion","looker","lusamine","hau","penny",
    "will","lyra","silver","fisher","jasmine","hiker",
    "whitney","travelling merchant","morty",
    "professor's research"
]

CARD_TYPE_MAPPING = {
    'Metal': 'pokemon',
    'Dragon': 'pokemon',
    'Fire': 'pokemon',
    'Trainer': 'trainer',   # <-- fix here, it should map Trainer to trainer, not pokemon
    'Lightning': 'pokemon',
    'Darkness': 'pokemon',
    'Water': 'pokemon',
    'Grass': 'pokemon',
    'Psychic': 'pokemon',
    'Colorless': 'pokemon',
    'Fighting': 'pokemon'
}

# Map Pokémon typings to "pokemon"
data['card_type'] = data['card_type'].map(CARD_TYPE_MAPPING).fillna(data['card_type'])

# Mark supporters
data.loc[data['card_name'].str.lower().isin(supporter_names), 'card_type'] = 'supporter'

# Mark tools (leftover trainers that are not supporters)
data.loc[data['card_type'] == 'trainer', 'card_type'] = 'tool'

print(data['card_type'].value_counts())

data.to_csv("ALL_SETS_CLEANED.csv", index=False)
