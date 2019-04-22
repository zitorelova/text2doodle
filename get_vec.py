import os 
import numpy as np
import pickle
import subprocess
from sklearn.metrics.pairwise import cosine_similarity
from shutil import move

bucket = "https://console.cloud.google.com/storage/browser/quickdraw_dataset/sketchrnn/"

def load_matrices():
    outs = []
    for filename in ['embed_ix', 'embed_matrix', 'categories']:
        with open(f'data/{filename}.pkl', 'rb') as f:
           temp = pickle.load(f)
           outs.append(temp)
           
    return outs

embed_ix, embed_matrix, cats = load_matrices()

def get_closest(inputs, stochastic=False):
    """
    Function for finding the closest vector among the categories

    Arguments:

    inputs (str): Input string to be embedded
    stochastic (boolean): If True, randomly samples from top 5 closest vectors else use the closest vector 
    """
    inputs = inputs.lower().split(" ")
    feat_vec = np.tile(embed_matrix.mean(axis=0), (len(inputs), 1))
    for ix, word in enumerate(inputs):
        try: feat_vec[ix] = embed_ix[word]
        except KeyError: pass
    feat_vec = feat_vec.mean(axis=0).reshape(1, -1)
    sims = cosine_similarity(feat_vec, embed_matrix)
    if stochastic:
        return cats[np.random.choice(sims.argsort()[0, -5:][::-1].tolist())]
    else: 
        return cats[np.argmax(sims)]

input_str = input("Enter your text: ")
chosen_class = get_closest(str(input_str)) 
chosen_class = chosen_class.replace(' ', '%20')
file_download = bucket + chosen_class + '.npz'
print("Downloading closest class...")
subprocess.run(["wget", file_download])
f = [i for i in os.listdir() if i.endswith('.npz')][0]
move(f, 'data')
