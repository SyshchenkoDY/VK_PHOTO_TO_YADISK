import pickle
from pprint import pprint

with open('json_file', 'rb') as file:
    json_file = pickle.load(file)
    pprint(json_file)
