import pickle
import os
import sys

if "--install" in sys.argv:
    os.system("clear")
    print("---- Installing scipy, matplotlib ----\n")
    os.system("python3 -m pip install --user scipy matplotlib")
    if sys.platform == "darwin":
        print("\n---- Installing XCode Command Line Tools ----\n")
        os.system("xcode-select --install")

try:
    with open('myCache/lastUpdated.txt',  'rb') as fp:
        lastUpdated = pickle.load(fp)
except FileNotFoundError:
    lastUpdated = "???"
    with open('myCache/lastUpdated.txt',  'wb') as fp:
        pickle.dump(lastUpdated, fp)

from Graph import *

graph = Graph(lastUpdated)
graph.load("My List")
