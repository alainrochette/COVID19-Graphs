
from Graph import *
import pickle
import os
import sys
from datetime import datetime

now = datetime.now()




if "--install" in sys.argv:
    os.system("clear")
    print("---- Installing scipy, matplotlib ----\n")
    os.system("python3 -m pip install --user scipy matplotlib")
    if sys.platform == "darwin":
        print("\n---- Installing XCode Command Line Tools ----\n")
        os.system("xcode-select --install")
if "--update" in sys.argv:
    os.system("clear")
    print("---- Updating World Data ----\n")
    os.system("svn export https://github.com/CSSEGISandData/COVID-19.git/trunk/csse_covid_19_data/csse_covid_19_time_series --force")
    print("\n---- Updating US Data ----\n")
    os.system("svn export https://github.com/CSSEGISandData/COVID-19.git/trunk/csse_covid_19_data/csse_covid_19_daily_reports_us --force")
    print("\n---- Updating Testing Data ----\n")
    os.system("svn export https://github.com/owid/covid-19-data.git/trunk/public/data/testing --force")
    os.system("clear")
    lastUpdated = datetime.now()
    with open('myCache/lastUpdated.txt',  'wb') as fp:
        pickle.dump(lastUpdated, fp)
else:
    try:
        with open('myCache/lastUpdated.txt',  'rb') as fp:
            lastUpdated = pickle.load(fp)
    except FileNotFoundError:
        lastUpdated = "???"
        with open('myCache/lastUpdated.txt',  'wb') as fp:
            pickle.dump(lastUpdated, fp)

graph = Graph(lastUpdated)
graph.load("My List")
