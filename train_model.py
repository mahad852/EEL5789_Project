import torch
import torch.nn as nn
import model_constants
from model import LSTMClassifier
import numpy as np

def one_hot(a, num_classes):
    return np.squeeze(np.eye(num_classes)[a.reshape(-1)])    
    
def getSequenceData(df, sequence_size, num_classes):
    y = one_hot(df['IP.dst'].to_numpy(), num_classes)
    y.resize((int(df.shape[0]/sequence_size), sequence_size, num_classes))
    X = df.to_numpy().copy()
    X.resize((int(df.shape[0]/sequence_size), sequence_size, df.shape[1]))
    
    return X[:-1], y[1:]
             
def train_epoch(X, y, model, optimizer, criterion, results, name='model'):
    correctPredictions = 0
    missedPredictions = 0
    incorrectPredictions = 0
    
    for i in range(0, X.shape[0], model_constants.BATCH_SIZE):
        # Get a batch of input and target sequences
        inputs = torch.tensor(X[i:i+model_constants.BATCH_SIZE]).float()
        targets = torch.tensor(y[i:i+model_constants.BATCH_SIZE]).argmax(axis=2)        

        # Zero the gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(inputs)


        # Compute the loss
        loss = criterion(outputs.view(-1, model_constants.OUTPUT_SIZE), targets.view(-1))

        # Backward pass
        loss.backward()

        # Update the weights
        optimizer.step()

        # Compute the accuracy
        predicted = outputs.argmax(axis=2)

        for b in range(predicted.shape[0]):
            nextFlows = set(list(targets[b].flatten().numpy()))
            predictedFlows = set(list(predicted[b].flatten().numpy()))            
            intersectCount = len(nextFlows.intersection(predictedFlows))
            correctPredictions += intersectCount
            missedPredictions += (len(nextFlows) - intersectCount)
            incorrectPredictions += (len(predictedFlows) - intersectCount)
    
    results.append((correctPredictions, missedPredictions, incorrectPredictions))
    print(name, '; correctPredicts:', correctPredictions, '; missedPredictions:', missedPredictions, 'incorrectPredictions:', incorrectPredictions)
    return model
    
def train_federated_lstm(df1, df2, df3, results1, results2, results3):    
    model1 = LSTMClassifier(model_constants.INPUT_SIZE, model_constants.HIDDEN_SIZE, model_constants.OUTPUT_SIZE)
    X1, y1 = getSequenceData(df1, model_constants.SEQUENCE_LENGTH, model_constants.OUTPUT_SIZE)
    optimizer1 = torch.optim.Adam(model1.parameters())
    
    # Define the loss function and optimizer
    criterion = nn.CrossEntropyLoss()

    model2 = LSTMClassifier(model_constants.INPUT_SIZE, model_constants.HIDDEN_SIZE, model_constants.OUTPUT_SIZE)
    X2, y2 = getSequenceData(df2, model_constants.SEQUENCE_LENGTH, model_constants.OUTPUT_SIZE)
    optimizer2 = torch.optim.Adam(model2.parameters(), lr=0.001)
        
    model3 = LSTMClassifier(model_constants.INPUT_SIZE, model_constants.HIDDEN_SIZE, model_constants.OUTPUT_SIZE)
    X3, y3 = getSequenceData(df3, model_constants.SEQUENCE_LENGTH, model_constants.OUTPUT_SIZE)
    optimizer3 = torch.optim.Adam(model3.parameters(), lr=0.001)
    
    # Train the model
    for epoch in range(model_constants.NUM_EPOCHS):
        print('Training Epoch:', epoch)
        model1 = train_epoch(X1, y1, model1, optimizer1, criterion, results1, name='switch1')
        model2 = train_epoch(X2, y2, model2, optimizer2, criterion, results2, name='switch2')
        model3 = train_epoch(X3, y3, model3, optimizer3, criterion, results3, name='switch3')
            
        if epoch % model_constants.EPOCHS_PER_ROUND == 0 and epoch > 0:
            averaged_params = []
            total_size = df2.shape[0] + df3.shape[0] + df1.shape[0]
            params2 = [param for param in model2.parameters()]
            params3 = [param for param in model3.parameters()]
            with torch.no_grad():
                for i, param1 in enumerate(model1.parameters()):
                    averaged = ((params2[i] * df2.shape[0])  + (param1  * df1.shape[0]) + (params3[i] * df3.shape[0]))/total_size
                    averaged_params.append(averaged)
                    param1.copy_((averaged * (1 - model_constants.LOCAL_FACTOR)) + (param1 * model_constants.LOCAL_FACTOR))

                for i, param in enumerate(model2.parameters()):
                    param.copy_((averaged_params[i] * (1 - model_constants.LOCAL_FACTOR)) + (param * model_constants.LOCAL_FACTOR))

                for i, param in enumerate(model3.parameters()):
                    param.copy_((averaged_params[i] * (1 - model_constants.LOCAL_FACTOR)) + (param * model_constants.LOCAL_FACTOR))
            
    return model1, model2, model3