# %%
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:95% !important; }</style>"))
%config InlineBackend.figure_format = 'retina'

# %%


# %%
import plotly.graph_objs as go
import plotly

# %%
import pickle

# %%
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA

from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn import svm

from matplotlib import pyplot as plt
%matplotlib inline

# %%
from sklearn.cluster import DBSCAN, SpectralClustering, MeanShift
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans

plt.style.use("seaborn")
%matplotlib inline

# %%
from scipy import stats

# %%
pca_features_X = pd.read_pickle('./results/pca_results.pkl')

# %%
pca_features_X

# %%
pca_labels = pd.read_pickle('./results/kmeans_results.pkl')

# %%
pca_labels

# %%
color_dict = {0:'cyan', 1: 'darkorange' , 2: 'green', 3:'chocolate', 4:'red', 5: 'gold', 6: 'hotpink', 7:'dodgerblue', 8:'limegreen', 9: 'blueviolet'}

# %%
color_labels = [color_dict[i] for i in pca_labels]

# %%
# color_labels

# %%
df_data_min = pd.read_pickle('./data/df_data_added_min.pkl')


# %%
df_data_min

# %%
players_series = df_data_min.reset_index().Player

# %%
players_lst = players_series.to_list()

# %%
players_str = ', '.join(sorted(players_lst))

# %%
players_str

# %%
pca_features_array = pca_features_X.to_numpy()

# %%
x, y, z = pca_features_array
trace1 = go.Scatter3d(
    hovertext=players_lst,
    ids=players_series,
    legendgroup=None,
    name=None,
    opacity=0.8,
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
    color=color_labels,
    line=dict(color='black', width=1)
        ))
data = [trace1]
layout = go.Layout(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    )
)
fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig)

# %%
result = pd.read_pickle('./results/player_results.pkl')

# %%
df_data_min['W'] = pd.to_numeric(df_data_min['W'], errors="coerce")

# %%
group0, group1, group2, group3, group4, group5, group6, group7, group8, group9 = result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9]

# %%
df_data_group0, df_data_group1, df_data_group2, df_data_group3, df_data_group4, df_data_group5, df_data_group6, df_data_group7, df_data_group8, df_data_group9 = [df_data_min.loc[eval('group' + str(i))] for i in range(len(result))]

# %%
cols = df_data_group1.columns.to_list()[5:]
', '.join(sorted(cols))

# %%
len(cols)

# %%
# group1_catch_shoot = df_data_group1['Catch Shoot Freq'].to_numpy()

# %%
groups_of_interest = [0, 2, 3, 7, 8]

# %%
from matplotlib import pyplot

# %%
group_other = [eval('group' + str(i)) for i in range(10) if i != 1]

# %%
group_other = [player for lst in group_other for player in lst]

# %%
def plot_all_groups(col_name, group_num):
    a4_dims = (11.7, 8.27)
    fig, ax = pyplot.subplots(figsize=a4_dims)
    plot_graph = [sns.distplot(eval('df_data_group' + str(i))[col_name].to_numpy(), norm_hist=True, label= 'group' + str(i)) for i in groups_of_interest]
    plt.legend(['Group ' + str(num + 1) for num in groups_of_interest])

# %%
def plot_one_vs_rest(col_name, group_num):
    colors = ['blue', 'red']
    a4_dims = (11.7, 8.27)
    fig, ax = pyplot.subplots(figsize=a4_dims)
    sns.distplot(eval('df_data_group' + str(group_num))[col_name].to_numpy(), norm_hist=True, label= 'group' + str(group_num), color='blue')
    group_other = [eval('group' + str(i)) for i in range(10) if i != group_num]
    group_other = [player for lst in group_other for player in lst]
    df_group_other = df_data_min.loc[group_other]
#     print(df_group_other)
    sns.distplot(df_group_other[col_name].to_numpy(), norm_hist=True, label= 'group other', color='red')
    plt.legend(['Group ' + str(group_num + 1), 'Rest'])

# %%
group1_plot = plot_one_vs_rest('Defense Isolation Shot Frequency', 0)

# %%
group2_plot = plot_one_vs_rest('Offense Post Up Frequency', 1)

# %%
group3_plot = plot_one_vs_rest('Catch Shoot Frequency', 2)

# %%
group4_plot = plot_one_vs_rest('Defense Pick & Roll Ball Handler Frequency', 3)

# %%
group5_plot = plot_one_vs_rest('Average Seconds Per Touch', 4)

# %%
group6_plot = plot_one_vs_rest('Fast Break Frequency', 5)

# %%
group7_plot = plot_one_vs_rest('Closely Contested Shot Frequency', 6)


# %%
group8_plot = plot_one_vs_rest('Defense Rebounding Chance Adjusted', 7)

# %%
group9_plot = plot_one_vs_rest('Open Shot Frequency', 8)

# %%
group10_plot = plot_one_vs_rest('Paint Touches Frequency', 9)

# %%
def group_describe(df, group_number):
    df_return = df
    df_return = df_return.iloc[:, 5:-1].describe().loc["mean"].reset_index()
    df_return = df_return.T
    df_return = df_return.drop('index')
    df_return.columns = cols[:-1]
    df_return.index = ['group' + str(group_number)]
    return df_return


# %%
df_group0_describe = group_describe(df_data_group0, 0)
df_group1_describe = group_describe(df_data_group1, 1)
df_group2_describe = group_describe(df_data_group2, 2)
df_group3_describe = group_describe(df_data_group3, 3)
df_group4_describe = group_describe(df_data_group4, 4)
df_group5_describe = group_describe(df_data_group5, 5)
df_group6_describe = group_describe(df_data_group6, 6)
df_group7_describe = group_describe(df_data_group7, 7)
df_group8_describe = group_describe(df_data_group8, 8)
df_group9_describe = group_describe(df_data_group9, 9)

# %%
df_mean_groups = pd.concat([df_group0_describe, df_group1_describe, df_group2_describe, df_group3_describe, df_group4_describe, df_group5_describe, df_group6_describe, df_group7_describe, df_group8_describe, df_group9_describe])

# %%
df_mean_groups

# %%
rank_dict = {}
for i, col in enumerate(df_mean_groups.columns.to_list()):
    rank_dict[col] = [d for d in df_mean_groups[col].sort_values(ascending=False).index][0]

# %%
rank_dict_lst = [[v,k] for k, v in rank_dict.items()]

# %%
group0_decription = [l[1] for l in rank_dict_lst if l[0] == "group0"]
group1_decription = [l[1] for l in rank_dict_lst if l[0] == "group1"]
group2_decription = [l[1] for l in rank_dict_lst if l[0] == "group2"]
group3_decription = [l[1] for l in rank_dict_lst if l[0] == "group3"]
group4_decription = [l[1] for l in rank_dict_lst if l[0] == "group4"]
group5_decription = [l[1] for l in rank_dict_lst if l[0] == "group5"]
group6_decription = [l[1] for l in rank_dict_lst if l[0] == "group6"]
group7_decription = [l[1] for l in rank_dict_lst if l[0] == "group7"]
group8_decription = [l[1] for l in rank_dict_lst if l[0] == "group8"]
group9_decription = [l[1] for l in rank_dict_lst if l[0] == "group9"]

# %%
rank_dict_2nd = {}
for i, col in enumerate(df_mean_groups.columns.to_list()):
    rank_dict_2nd[col] = [d for d in df_mean_groups[col].sort_values(ascending=False).index][1]

# %%
rank_2nd_lst = [[v,k] for k, v in rank_dict_2nd.items()]
rank_2nd_lst.sort()

# %%
group0_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group0"]
group1_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group1"]
group2_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group2"]
group3_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group3"]
group4_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group4"]
group5_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group5"]
group6_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group6"]
group7_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group7"]
group8_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group8"]
group9_second_descr = [l[1] for l in rank_2nd_lst if l[0] == "group9"]

# %%
cluster_dictionary = {}

# %%
cluster_dictionary['group0'] = {1: group0_decription, 2: group0_second_descr}

# %%
cluster_dictionary['group1'] = {1: group1_decription, 2: group1_second_descr}

# %%
cluster_dictionary['group2'] = {1: group2_decription, 2: group2_second_descr}

# %%
cluster_dictionary['group3'] = {1: group3_decription, 2: group3_second_descr}

# %%
cluster_dictionary['group4'] = {1: group4_decription, 2: group4_second_descr}

# %%
cluster_dictionary['group5'] = {1: group5_decription, 2: group5_second_descr}

# %%
cluster_dictionary['group6'] = {1: group6_decription, 2: group6_second_descr}

# %%
cluster_dictionary['group7'] = {1: group7_decription, 2: group7_second_descr}

# %%
cluster_dictionary['group8'] = {1: group8_decription, 2: group8_second_descr}

# %%
cluster_dictionary['group9'] = {1: group9_decription, 2: group9_second_descr}

# %%
def print_results(group_num):
    group_string = 'group' + str(group_num)
    format_str1 = 'Primary Feature(s): '
    format_str2 = 'Secondary Feature(s): '
    print(', '.join(eval(group_string)))
    print(format_str1 + ', '.join([c.title() for c in cluster_dictionary[group_string][1]]))
    print(format_str2 + ', '.join([c.title() for c in cluster_dictionary[group_string][2]]))

# %%
for i in range(10):
    print_results(i)
    print()

# %%



