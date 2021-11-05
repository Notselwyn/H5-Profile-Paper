from sklearn import tree
import pandas as pd
import pickle
import graphviz
import re
from itertools import product

dataframe = pd.read_csv("../tictactoe_dataset.csv", dtype=str)
model = tree.DecisionTreeClassifier(max_depth=20)
model.fit(tuple(tuple(int(y) for y in x) for x in dataframe['state']), tuple(int(x) for x in dataframe['best']))
best_list = tuple(dataframe['best'].astype(int).to_list())
print(f"accuracy: {round(sum(map(lambda x: x[1] == best_list[x[0]], enumerate(model.predict([*product(range(3), repeat=9)])))) / 196.83, 1)}%")

with open("supervised_tictactoe.pkl", "wb") as f:
    pickle.dump(model, f)

dot_data = tree.export_graphviz(model, out_file=None, filled=True, rounded=True, special_characters=True, fontname="arial", label="all", proportion=True, max_depth=4)
graph = graphviz.Source(re.sub(r'<br/>value = \[.*\d\]', '', str(dot_data)))
graph.render("figure_tree", view=True, format='svg', cleanup=True)