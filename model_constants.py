INPUT_SIZE = 7 # Number of features in each input record
HIDDEN_SIZE = 256 # Number of LSTM cells in the hidden layer
OUTPUT_SIZE = 21 # Number of possible IP.dst values

BATCH_SIZE = 32 # Number of sequences to train on in each batch
SEQUENCE_LENGTH = 50 # Length of each sequence
NUM_FEATURES = INPUT_SIZE + 1 # Total number of features in each sample

EPOCHS_PER_ROUND = 25
LOCAL_FACTOR = 0.7
NUM_EPOCHS = 200