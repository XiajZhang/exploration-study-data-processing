from locale import normalize
from statistics import mean
from turtle import color
import pandas as pd
import json
import os
import warnings
import matplotlib.pyplot as plt
from sklearn import preprocessing
import numpy as np
import seaborn as sns

def plot_child_session_trend(data, child_id):

    child_data = data[data['child_id'] == child_id]
    child_data.plot(x='session number', y='total_sum')

if __name__ == "__main__":

    INPUT_DIR = os.path.join(os.getcwd(), "output")
    INPUT_DATA = os.path.join(INPUT_DIR, "children_exploration_results.csv")

    # Processing data, Treatment Group/Control Group, (Pre/Post, Intervention)
    data = pd.read_csv(INPUT_DATA)
    session_num = []
    study_group = []
    pre_post_intervention = []
    
    # Column Manipulation
    for index, row in data.iterrows():
        session_num.append(int(row['session_id'].split('_')[0]))
        study_code = row['study_code']

        if 'treatment' in study_code:
            study_group.append('treatment')
        elif 'control' in study_code:
            study_group.append('control')
        else:
            warnings.warn("study code is neither treatment nor control: " + study_code)
        
        if '-' in study_code:
            pre_post = study_code.split('-')[-1]
            pre_post_intervention.append(pre_post)
        else:
            pre_post_intervention.append("intervention")
    data['session number'] = session_num
    data['group'] = study_group
    data['interaction'] = pre_post_intervention
    print(data.head(5))

    plotting_value = 'total_avg'
    # plotting_value = 'total_sum'
    # plotting_value = 'decoding_sum'
    # plotting_value = 'explanation_sum'
    columns_in_question = ['session number', 'child_id', 'interaction', plotting_value]
    for group_condition in ['treatment', 'control']:
        group_data = data[data['group'] == group_condition][columns_in_question]
        # Plot 1: Plotting trend
        legend = []
        normalized = {
            'child_id': [],
            'session number': [],
            'normalized_by_child': []
        }
        child_in_group = list(set(group_data['child_id'].values))
        child_in_group.sort()
        print("%d Children In %s"%(len(child_in_group), group_condition))
        for child in child_in_group:
            # legend.append(child)
            child_data = group_data[group_data['child_id'] == child].copy()
            # child_data = child_data[child_data['session number'] != 1]
            # child_data = child_data[child_data['session number'] != 1][child_data['session number'] != 8]
            child_data = child_data[child_data['session number'].between(0, 3)]
            child_data = child_data.sort_values('session number')
            child_vals = list(child_data[plotting_value])
            normalized_vals = list(preprocessing.normalize([child_vals])[0])
            normalized['child_id'] += list(child_data['child_id'].values)
            normalized['session number'] += list(child_data['session number'].values)
            normalized['normalized_by_child'] += list(normalized_vals)
           
            plt.plot(child_data['session number'], normalized_vals)
            child_data['normalized'] = normalized_vals
            ax = sns.regplot(x="session number", y='normalized', data=child_data).set(title=group_condition + " " + child)
            plt.ylim(-0.1, 1)
            plt.show(block=True)
        # plot_df = pd.DataFrame(normalized)
        # ax = sns.regplot(x="session number", y='normalized_by_child', data=plot_df)
        # plt.show(block=True)

        # Plot 2: Plotting box with pre and post
        # pre_rst = []
        # post_rst = []
        # mid_rst = []
        # all_child_data = []
        # for child in list(set(group_data['child_id'].values)):
        #     print(child)
        #     # Get Child's sessions
        #     child_data = group_data[group_data['child_id'] == child]
        #     child_data.sort_values('session number')
        #     normalized_child_data = child_data[plotting_value].values
        #     # print(normalized_child_data)
        #     normalized_child_data = preprocessing.normalize([normalized_child_data])[0]
        #     # print(normalized_child_data)
        #     # print('\n')
        #     all_child_data.append(normalized_child_data)

            # child_data = group_data[group_data['child_id'] == child]
            # pre_val = child_data[child_data['interaction'] == 'pre'][plotting_value].values[0]
            # post_val = child_data[child_data['interaction'] == 'post'][plotting_value].values[0]
            # mid_val = mean(child_data[child_data['interaction'] == 'intervention'][plotting_value].values)
            # # print(child, pre_val, post_val)
            # child_mean = mean([pre_val, post_val, mid_val])
            # if child_mean == 0:
            #     child_mean = 1
            # pre_rst.append(pre_val/child_mean)
            # post_rst.append(post_val/child_mean)
            # mid_rst.append(mid_val/child_mean)
        # child_array = np.array(all_child_data)
        # # plt_data = np.transpose(child_array)
        # plt_data = child_array
        # print(plt_data)
        # fig = plt.figure(figsize=(15, 10))
        # ax = fig.add_axes([0, 0, 1, 1])
        # boxplt = ax.boxplot(plt_data)
        # plt.show()
