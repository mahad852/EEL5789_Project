import numpy as np
from train_model import getSequenceData
from model_constants import SEQUENCE_LENGTH, OUTPUT_SIZE   
import torch 

cache_capacity = 5
def test_ml_approach(server_test_df, model):
    X, _ = getSequenceData(server_test_df, SEQUENCE_LENGTH, OUTPUT_SIZE)
    cache = []
    hits = 0
    misses = 0
    actualFlows = X[:,:, 3]
    with torch.no_grad():
        preds = model.forward(torch.tensor(X).float())
        predFlows = preds.argmax(axis=2)
    
    for i in range(actualFlows.shape[0]):
        af = actualFlows[i]
        flows, counts = np.unique(af, return_counts=True)
        flowAndCounts = [(flows[i], counts[i])  for i in range(len(flows))]
        topFlows = sorted(flowAndCounts, key=lambda k: k[1], reverse=True)
        topFlows = topFlows[:cache_capacity] if len(topFlows) > cache_capacity else topFlows
        for (flow, _) in topFlows:
            if flow not in cache:
                cache.append(flow)
                misses += 1
            else:
                hits += 1
        if len(cache) > cache_capacity:
            cache = cache[len(cache) - cache_capacity:]
        
        flows, counts = np.unique(predFlows[i], return_counts=True)
        flowAndCounts = [(flows[i], counts[i])  for i in range(len(flows))]
        topFlows = sorted(flowAndCounts, key=lambda k: k[1], reverse=True)
        topFlows = topFlows[:cache_capacity] if len(topFlows) > cache_capacity else topFlows
        for (flow, _) in topFlows:
            if flow not in cache:
                cache.append(flow)
        if len(cache) > cache_capacity:
            cache = cache[len(cache) - cache_capacity:]
    return hits, misses

def test_without_ml(server_test_df):
    X, y = getSequenceData(server_test_df, SEQUENCE_LENGTH, OUTPUT_SIZE)
    cache = []
    hits = 0
    misses = 0
    actualFlows = X[:,:, 3]
    
    for i in range(actualFlows.shape[0]):
        af = actualFlows[i]
        flows, counts = np.unique(af, return_counts=True)
        flowAndCounts = [(flows[i], counts[i])  for i in range(len(flows))]
        topFlows = sorted(flowAndCounts, key=lambda k: k[1], reverse=True)
        topFlows = topFlows[:cache_capacity] if len(topFlows) > cache_capacity else topFlows
        for (flow, _) in topFlows:
            if flow not in cache:
                cache.append(flow)
                misses += 1
            else:
                hits += 1
        if len(cache) > cache_capacity:
            cache = cache[len(cache) - cache_capacity:]
        
    return hits, misses