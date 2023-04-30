import urllib.request
import zipfile
import os
import pandas as pd

DATASET_FILE_URL = 'https://iotanalytics.unsw.edu.au/iottestbed/csv/16-09-23.csv.zip'
DATASET_FILE = '16-09-23.csv'

def does_dataset_exist():
    return DATASET_FILE in os.listdir(os.path.curdir)

def download_dataset():
    urllib.request.urlretrieve(DATASET_FILE_URL, DATASET_FILE)

def unzip_dataset():
    with zipfile.ZipFile(os.path.join(os.path.curdir, DATASET_FILE), 'r') as zip_ref:
        zip_ref.extractall(os.path.curdir)


def get_dataset():
    if not does_dataset_exist():
        download_dataset()
        unzip_dataset()
    
    return pd.read_csv(os.path.join(os.path.curdir, DATASET_FILE))