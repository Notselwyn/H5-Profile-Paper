#from sklearn.model_selection import train_test_split
from sklearn import tree
import pandas as pd
import pickle
import graphviz
import re
from itertools import product


dataframe = pd.read_csv("../tictactoe_dataset.csv", dtype=str)

# don't split dataset: doing manual checking so train / test split is unimportant
#train, test = train_test_split(dataframe, test_size=0.03, random_state=3123)
model = tree.DecisionTreeClassifier(max_depth=20)
model.fit(tuple(tuple(int(y) for y in x) for x in dataframe['state']), tuple(int(x) for x in dataframe['best']))

succeeded = 0
p = 0
prod_len = 3**9
old_frac = 0
for i in product(range(3), repeat=9):
    if int(model.predict([i])[0]) == int(dataframe.loc[dataframe['state'] == "".join(map(str, i))]['best']):
        succeeded += 1
    p += 1
    if old_frac != (old_frac := p / prod_len):
        print(f"success rate: {round(succeeded / p * 100, 1)}%; progression: {round(old_frac * 100, 1)}%" + " " * 6, end="\r")

with open("supervised_tictactoe.pkl", "wb") as f:
    pickle.dump(model, f)

dot_data = tree.export_graphviz(model, out_file=None, filled=True, rounded=True, special_characters=True, fontname="arial", label="all", proportion=True, max_depth=4)
graph = graphviz.Source(re.sub(r'<br/>value = \[.*\d\]', '', str(dot_data)))
graph.render("figure_tree", view=True, format='svg', cleanup=True)