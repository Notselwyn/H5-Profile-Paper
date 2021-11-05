#from sklearn.model_selection import train_test_split
from sklearn import tree
import pandas as pd
import pickle
import graphviz
import re


dataframe = pd.read_csv("tictactoe_dataset.csv", dtype=str)

# don't split dataset: doing manual checking so train / test split is unimportant
#train, test = train_test_split(dataframe, test_size=0.03, random_state=3123)
model = tree.DecisionTreeClassifier(max_depth=20)
model.fit(tuple(tuple(int(y) for y in x) for x in dataframe['state']), tuple(int(x) for x in dataframe['best']))

succeeded = 0
p = 1
for a in range(3):  # optimized™
    for b in range(3):
        for c in range(3):
            for d in range(3):
                for e in range(3):
                    for f in range(3):
                        for g in range(3):
                            for h in range(3):
                                for i in range(3):
                                    if int(model.predict([(a, b, c, d, e, f, g, h, i)])[0]) == int(dataframe.loc[dataframe['state'] == str(a) + str(b) + str(c) + str(d) + str(e) + str(f) + str(g) + str(h) + str(i)]['best']):
                                        succeeded += 1
                                    p += 1
            print(f"success rate: {round(succeeded / p * 100, 1)}%" + " " * 3, end="\r")

with open("supervised_tictactoe.pkl", "wb") as f:
    pickle.dump(model, f)

dot_data = tree.export_graphviz(model, out_file=None, filled=True, rounded=True, special_characters=True, fontname="arial", label="all", proportion=True, max_depth=4)
graph = graphviz.Source(re.sub(r'<br/>value = \[.*\d\]', '', str(dot_data)))
graph.render("figure_tree", view=True, format='svg', cleanup=True)