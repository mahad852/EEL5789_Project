import pandas as pd
import numpy as np
from download_data import get_dataset
from ip_node_division import ALL_IPS, SWITCH_TO_GROUPS
import matplotlib.pyplot as plt
from test_performance import test_ml_approach, test_without_ml

from train_model import train_federated_lstm

def get_df():
    main_df = get_dataset() 
    return main_df.loc[main_df['IP.src'].isin(ALL_IPS)].loc[main_df['IP.dst'].isin(ALL_IPS)]

def drop_irrelevant_columns(df):
    return df.drop(columns=['eth.src', 'eth.dst', 'Packet ID'])

def convert_ips_to_categorical(df, IPToInt):
    return df.replace({'IP.src' : IPToInt, 'IP.dst' : IPToInt})

def divide_ips_among_switches(df, IPToInt):
    switch1_df = df[df['IP.src'].isin(list(map(lambda IP: IPToInt[IP], SWITCH_TO_GROUPS['switch1'])))]
    switch2_df = df[df['IP.src'].isin(list(map(lambda IP: IPToInt[IP], SWITCH_TO_GROUPS['switch2'])))]
    switch3_df = df[df['IP.src'].isin(list(map(lambda IP: IPToInt[IP], SWITCH_TO_GROUPS['switch3'])))]

    return switch1_df, switch2_df, switch3_df

def get_ip_mappings():
    IPToInt = {}
    intToIP = {}
    for i, ip in enumerate(ALL_IPS):
        if ip not in IPToInt:
            IPToInt[ip] = i
            intToIP[i] = ip
    return IPToInt, intToIP


def plot_results(results, switch_name):
    results = np.array(results)
    correct = results[:, 0]
    incorrect = results[:, 2]

    plt.plot([i + 1 for i in range(len(correct))], correct, label='Correct predictions')
    plt.plot([i + 1 for i in range(len(incorrect))], incorrect, label='Incorrect predictions')
    # plt.xlabel('Longitude')
    plt.ylabel('Number of predictions')
    plt.title('Number of predictions v/s epochs - Switch s1')
    plt.legend()
    plt.savefig(switch_name + '_epochs.png')

        

def main():
    IPToInt, intToIP = get_ip_mappings()
    df = get_df()
    df = drop_irrelevant_columns(df)
    df = convert_ips_to_categorical(df, IPToInt)
    switch1_df, switch2_df, switch3_df = divide_ips_among_switches(df, IPToInt)
    
    switch1_df_train, switch1_df_test = switch1_df[:int(len(switch1_df) * 0.7)], switch1_df[int(len(switch1_df) * 0.7):]
    switch2_df_train, switch2_df_test = switch2_df[:int(len(switch2_df) * 0.7)], switch2_df[int(len(switch2_df) * 0.7):]
    switch3_df_train, switch3_df_test = switch3_df[:int(len(switch3_df) * 0.7)], switch3_df[int(len(switch3_df) * 0.7):]

    results1 = []
    results2 = []
    results3 = []
    model1, model2, model3 = train_federated_lstm(switch1_df_train, switch2_df_train, switch3_df_train, results1, results2, results3)
    print('----------------------------------------------------')

    hits_switch1, misses_switch1 = test_ml_approach(switch1_df_test, model1)
    hits_switch2, misses_switch2 = test_ml_approach(switch2_df_test, model2)
    hits_switch3, misses_switch3 = test_ml_approach(switch3_df_test, model3)
    print('Switch1 had', hits_switch1, 'hits and', misses_switch1, ' misses using the FL approach')
    print('Switch2 had', hits_switch2, 'hits and', misses_switch2, ' misses using the FL approach')
    print('Switch3 had', hits_switch3, 'hits and', misses_switch3, ' misses using the FL approach')
    print()


    hits_switch1, misses_switch1 = test_without_ml(switch1_df_test)
    hits_switch2, misses_switch2 = test_without_ml(switch2_df_test)
    hits_switch3, misses_switch3 = test_without_ml(switch3_df_test)
    print('Switch1 had', hits_switch1, 'hits and', misses_switch1, ' misses using normal approach')
    print('Switch2 had', hits_switch2, 'hits and', misses_switch2, ' misses using the normal approach')
    print('Switch3 had', hits_switch3, 'hits and', misses_switch3, ' misses using the normal approach')
    print()

    plot_results(results1, 's1')
    plot_results(results1, 's2')
    plot_results(results1, 's3')

if __name__ == '__main__':
    main()
