# Using Federated Learning for network traffic flow prediction & pre-installation of flows at the switch level

## Running simulations:
Most of the code provided (other than custom_pox_controller.py and fl_topo.py) is code related to simulations. POX controller implementation is still pending and requires needing to be merged with the ML model.

The simulation requires installation of the following python libraries:
1. torch
2. numpy
3. pandas
4. scikit-learn
5. matplotlib

Here's the command to install them:
```
python3 -m pip install torch numpy pandas scikit-learn matplotlib
```

After the installation of these librarires, only the main.py python file needs to be run. From the root project directory, run:
```
python3 main.py
```

## Simulation code explained:
The code is setup such that part of the dataset is downloaded (code in download_data.py) automatically if it doesn't exist already. The model.py file contains the main LSTM model used for training purposes. This file includes the architecture of the LSTM model, which for now contains 1 hidden layer with a size of 256. It also has a Linear Layer of 21 (the number of distinct IP addresses we are considering) followed by a softmax layer. Arguably, this needs to be better formulated such that this is not a classification task since using classifiaction may not be scalable for larger and more dynamic systems. The file model_constants.py contains all the constants such as the number of parameters in the hidden LSTM laye (256), batch size (32), number of epochs (32), sequence length (50 - this is the number of timesteps/packets we consider before making the prediction for IPs that would be likely hit in the upcoming 50 timesteps - i.e: predicting destination IP addresses for the next outgoing IP packets). The file train_model.py contains the code to trian the lstm, with train_federated_lstm being the main function that gets called in main.py. Finally, the file test_performance.py 

## Simulation output:
Running the simulation outputs three training summary graphs (s1_epochs.png, s2_epochs.png, and s3_epochs.png). These graphs show the difference between the correct v/s incorrect predictions for each of the switch. These graphs are slightly different from the ones shown in the original report. The simulation also displays logs throughout the trianing process.

After finishing training, the main.py split uses test_performance.py to simulate switches as "caches" with a flow table size of 5. The test basically goes through the testing dataset to measure the number of cache "misses" (i.e: PacketIn requests sent to the server) for two approaches - the Federated Learning approch and the approach where no Machine Learning is used. Currently, the Federated Learning performs worse than the standard approach. Here are the results (updated and different from the report due to a bug in the code):
1. Switch: S1. Federated Learning (FL):  654 hits/2 misses, Standard: 651 hits / 5 misses
2. Switch: S2. FL: 529/167, Standard: 654/42
3. Switch: S3. FL: 95/5; Standard: 5

As can be seen, for switch S1 the FL model slightly outperforms the normal approach. For S3, their peformances are about equal. However, for switch s2 the standard model totally outperforms FL with a major difference in hit/miss ratio. These results require reasoning and further investigation.

## Mininet setup:
Currently, the setup is incomplete and not fully implemented. We decided to use POX as our choice for remote controller due to it's simplicity and available online documentation, as well as avaialbility of official examples provided by POX. POX can be installed by cloning the official POX git repository using:
```
git clone http://github.com/noxrepo/pox
cd pox
```
After cloning pox repo, place the custom_pox_controller.py file inside the root directory of pox. Then start the POX controller (need to be in pox root directory):
```
./pox.py log.level --DEBUG my_controller
```
This starts my_controller_pox.py. However, this controller is incomplete.

The fl_topy.py sets the topology for the mininet and should be provided to the mininet's mn command when starting mininet.
