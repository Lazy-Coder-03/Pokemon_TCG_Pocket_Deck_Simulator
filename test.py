import pandas as pd

data = pd.read_csv("ALL_SETS.csv")

cardType=data['card_type'].tolist()

print(set(cardType))