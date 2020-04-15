from Covid import *
import pickle
import os
import sys

# svn export https://github.com/CSSEGISandData/COVID-19.git/trunk/csse_covid_19_data/csse_covid_19_time_series --force
# svn export https://github.com/owid/covid-19-data.git/trunk/public/data/testing --force



#[--------- Pick days since Xth case ---------]

DAYS_SINCE = 0

#[--------- Pick which countries to show ---------]
#[------------------------------------------------]
#[--------- If not valid, check spelling ---------]
#[--------- in time_series_covid19 files ---------]
#[------------------------------------------------]
#[-------- You can choose states as well ---------]
#[----- Enter state population in Country.py -----]

countries_i = [           #[------ Choose color in Country.py -----]
"Chile",
"Argentina",
"Miami-Dade, Florida",
"Florida",
"US",
"Spain",
"Italy",
"United Kingdom",
"Netherlands",
# "Sweden",
# "China",
"New York",
# "London",
# "World",
]


try:
    with open('My_List.txt', 'rb') as fp:
        countries = list(set(pickle.load(fp)))
except FileNotFoundError:
    countries = countries_i
    with open('My_List.txt', 'wb') as fp:
        pickle.dump(countries, fp)

if "--install" in sys.argv:
    os.system("python3 -m pip install --user scipy matplotlib")
if "--update" in sys.argv:
    os.system("clear")
    print("---- Updating World Data ----\n")
    os.system("svn export https://github.com/CSSEGISandData/COVID-19.git/trunk/csse_covid_19_data/csse_covid_19_time_series --force")
    print("\n---- Updating US Data ----\n")
    os.system("svn export https://github.com/CSSEGISandData/COVID-19.git/trunk/csse_covid_19_data/csse_covid_19_daily_reports_us --force")
    print("\n---- Updating Testing Data ----\n")
    os.system("svn export https://github.com/owid/covid-19-data.git/trunk/public/data/testing --force")
    os.system("clear")

graph = Graph()
graph.load("My List")
