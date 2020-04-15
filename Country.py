import csv
import random
import pickle
import datetime
import glob

# Check https://matplotlib.org/3.1.0/gallery/color/named_colors.html for Named Colors
country_colors ={"France":"cornflowerblue", "Ecuador":"cornflowerblue",
                "Miami-Dade, Florida":"turquoise","Illinois":"turquoise",
                "Germany":"dimgray", "Iran":"dimgray",
                "Massachusetts":"skyblue", "Argentina":"skyblue", "Luxembourg":"skyblue", "Israel":"skyblue",
                "Panama":"deepskyblue", "Georgia*":"deepskyblue",
                "Uruguay":"steelblue", "Iceland":"steelblue", "Singapore":"steelblue", "Pennsylvania":"steelblue",
                "Turkey":"darkorchid", "New Jersey":"darkorchid", "US":"darkorchid",
                "Delaware":"gold", "Spain":"gold", "Bolivia":"gold", "Saudi Arabia":"gold",
                "Connecticut":"limegreen", "Italy":"limegreen", "Qatar":"limegreen",
                "District of Columbia":"forestgreen", "Mexico":"forestgreen",
                "Michigan":"orange", "Netherlands":"orange", "Malaysia":"orange", "Colombia":"orange",
                "Louisiana":"orchid", "United Kingdom":"orchid", "Austria":"orchid", "Japan":"orchid",
                "New York":"grey", "Ireland": "grey",
                "Paraguay":"slategrey", "Lebanon":"slategrey",
                "Korea, South":"pink", "Florida":"pink", "Belgium":"pink",
                "California":"darkgoldenrod",
                "Los Angeles, California": "goldenrod",
                "China":"orangered", "Chile":"orangered", "Switzerland":"orangered","Rhode Island":"orangered",
                "Peru":"peru", "Maryland":"peru",
                "Venezuela":"crimson", "Hong Kong":"crimson",
                "World":"black"}

populationD ={"World":7800}

class Countries:
    def __init__(self,region,days_since=0,colors=None):
        self.days_since = days_since
        self.countries = []
        self.dates = []
        self.countries_list = []
        self.regions = {}
        self.region = region
        if colors:
            self.country_colors = colors
        else:
            self.country_colors = country_colors
        self.loadRegion()

    def show(self, c):
        for country in self.countries:
            if country.name == c:
                 country.vis = 1
                 return True
        self.addOther(c)

    def get(self, c):
        for country in self.countries:
            if country.name == c: return country
        return 0

    def hide(self, c):
        for country in self.countries:
            if country.name == c:
                 country.vis = 0
                 self.countries_list = list(set(self.countries_list))
                 self.countries_list.remove(country.name)
                 if self.region == "My List":
                     with open('My_List.txt', 'wb') as fp:
                         pickle.dump(self.countries_list, fp)
                 return True
        return False

    def addOther(self,name):
        if "*" in name:
            self.addState(name)
            return 0
        pop = 0
        found = False
        if name in populationD: pop =populationD[name]
        if pop==0:
            with open('population_data/Pop2020.csv',encoding='mac_roman') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count > 0 and row[0].lower()==name.lower():
                        pop =int(row[4])/1000
                        break
                    line_count += 1
        if pop == 0: pop = 1
        with open('csse_covid_19_time_series/time_series_covid19_confirmed_global.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                c = None
                for row in csv_reader:
                    if line_count == 0:
                        self.dates = [d for d in row[4:] if d != ""]
                    elif row[1].lower().replace("*","")==name.lower() or row[0].lower().replace("*","")==name.lower()or name=="World":
                        if row[1].lower().replace("*","")==name.lower(): name = row[1].replace("*","")
                        if row[0].lower().replace("*","")==name.lower(): name = row[0].replace("*","")
                        found = True
                        if c:
                            c.allcases =  [x + y for x, y in zip(c.allcases, [int(x) for x in row[4:][0:len(self.dates)] if x != ""])]
                        else:
                            newcolor =[random.random(),random.random(),random.random()]
                            if name in self.country_colors: newcolor = self.country_colors[name]
                            c = self.get(name)
                            if not c: c = Country(self,name,pop,newcolor)
                            c.allcases = [int(x) for x in row[4:][0:len(self.dates)] if x != ""]
                    line_count += 1

                if found:
                    c.day = 0
                    for cc in range(0,len(c.allcases)):
                        if c.allcases[cc]  > self.days_since - 1 and c.day==0:
                            c.day = cc
                            break

                    c.cases =  [c.allcases[0]]
                    max = c.allcases[0]
                    for x in range(1,len(c.allcases)):
                        if c.allcases[x] >=  max:
                            c.cases.append(c.allcases[x])
                            max = c.allcases[x]
                        else:
                            c.cases.append(max)

                    c.newcases = [0] + [c.cases[x] - c.cases[x-1] for x in range(1,len(c.cases))]
                    c.days = len(self.dates)-c.day

                    c.x =[i for i in range(0,c.days)]
                    c.cases = c.cases[c.day:]
                    c.newcases = c.newcases[c.day:]
        if found:
            if self.region == "My List":
                with open('My_List.txt', 'wb') as fp:
                    pickle.dump(list(set(self.countries_list)), fp)
            with open('csse_covid_19_time_series/time_series_covid19_deaths_global.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                deathCount = 0
                for row in csv_reader:
                    if line_count == 0:
                        self.dates = [d for d in row[4:] if d != ""]
                    elif row[1].lower().replace("*","")==name.lower() or row[0].lower().replace("*","")==name.lower() or name=="World":
                        if deathCount > 0:
                            c.alldeaths =  [x + y for x, y in zip(c.alldeaths , [int(x) for x in row[4:][0:len(self.dates)] if x != ""])]
                        else:
                            c.alldeaths = [int(x) for x in row[4:][0:len(self.dates)] if x != ""]
                        deathCount += 1
                    line_count += 1


                c.deaths =  [c.alldeaths[0]]
                max = c.alldeaths[0]
                for x in range(1,len(c.alldeaths)):
                    if c.alldeaths[x] >=  max:
                        c.deaths.append(c.alldeaths[x])
                        max = c.alldeaths[x]
                    else:
                        c.deaths.append(max)
                c.deaths = c.deaths[c.day:]
                c.newdeaths = [0] + [c.deaths[x] - c.deaths[x-1] for x in range(1,len(c.deaths))]
                c.vis = 1
            with open('testing/covid-testing-all-observations.csv') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for row in reversed(list(csv_reader)):
                        n =  row[0].lower().split(" - ")[0].replace("south korea", "korea, south")
                        if ("CDC" not in row[0]) and ((name.lower() ==n) or (name=="US" and n =="united states")) :
                            dt = datetime.datetime.strptime(row[1], '%Y-%m-%d').strftime('%m/%d')
                            c.testing = dt +"|{:,.0f}".format(int(row[5])) + " " + row[0].split(" - ")[1].replace("(COVID Tracking Project)","") + " ("+ "{:,.2f}".format(float(row[7])) + "/K)"
                            break
        else:
            self.addState(name)


    def addState(self,place):
        pop = 0
        found = False
        ast = ""
        if "*" in place:
            place= place.replace("*","")
            ast = "*"

        if place in populationD: pop =populationD[place]
        with open('csse_covid_19_time_series/time_series_covid19_confirmed_US.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                c = None
                for row in csv_reader:
                    if line_count == 0:
                        self.dates = [d for d in row[11:] if d != ""]
                    elif (place.lower().replace(" ","")  ==  row[10].replace(", US","").lower().replace(" ","") or
                        place.lower()  ==  row[6].lower()):
                        found = True
                        if place.lower().replace(" ","")  ==  row[10].replace(", US","").lower().replace(" ",""): place = row[10].replace(", US","")
                        if place.lower()  ==  row[6].lower(): place = row[6]
                        if c:
                            c.allcases =  [x + y for x, y in zip(c.allcases, [int(x) for x in row[11:][0:len(self.dates)] if x != ""])]
                        else:
                            newcolor =[random.random(),random.random(),random.random()]
                            if place +ast in self.country_colors: newcolor = self.country_colors[place+ast]
                            c = self.get(place+ast)
                            if not c: c = Country(self,place +ast,pop,newcolor)
                            c.allcases = [int(x) for x in row[11:][0:len(self.dates)] if x != ""]
                    line_count += 1

                if found:
                    c.day = 0
                    for cc in range(0,len(c.allcases)):
                        if c.allcases[cc]  > self.days_since - 1 and c.day==0:
                            c.day = cc
                            break

                    c.cases =  [c.allcases[0]]
                    max = c.allcases[0]
                    for x in range(1,len(c.allcases)):
                        if c.allcases[x] >=  max:
                            c.cases.append(c.allcases[x])
                            max = c.allcases[x]
                        else:
                            c.cases.append(max)

                    c.newcases = [0] + [c.cases[x] - c.cases[x-1] for x in range(1,len(c.cases))]
                    c.days = len(self.dates)-c.day

                    c.x =[i for i in range(0,c.days)]
                    c.cases = c.cases[c.day:]
                    c.newcases = c.newcases[c.day:]
        if found:
            if self.region == "My List":
                with open('My_List.txt', 'wb') as fp:
                    pickle.dump(list(set(self.countries_list)), fp)
            with open('csse_covid_19_time_series/time_series_covid19_deaths_US.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                deathCount = 0
                totalpop = 0
                for row in csv_reader:
                    if line_count == 0:
                        self.dates = [d for d in row[12:] if d != ""]
                    elif (place.lower().replace(" ","")  ==  row[10].replace(", US","").lower().replace(" ","") or
                        place.lower()  ==  row[6].lower()):
                        totalpop = totalpop + int(row[11])
                        if deathCount > 0:
                            c.alldeaths =  [x + y for x, y in zip(c.alldeaths , [int(x) for x in row[12:][0:len(self.dates)] if x != ""])]
                        else:
                            c.alldeaths = [int(x) for x in row[12:][0:len(self.dates)] if x != ""]
                        deathCount += 1
                    line_count += 1

                if pop == 0: c.pop = totalpop/1000000

                c.deaths =  [c.alldeaths[0]]
                max = c.alldeaths[0]
                for x in range(1,len(c.alldeaths)):
                    if c.alldeaths[x] >=  max:
                        c.deaths.append(c.alldeaths[x])
                        max = c.alldeaths[x]
                    else:
                        c.deaths.append(max)
                c.deaths = c.deaths[c.day:]
                c.newdeaths = [0] + [c.deaths[x] - c.deaths[x-1] for x in range(1,len(c.deaths))]

                c.vis = 1
            newest = sorted(glob.glob('csse_covid_19_daily_reports_us/*.csv'))[-1]
            with open(newest) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for row in csv_reader:
                        if place.lower() == row[0].lower() and row[11] != "" :
                            dt = datetime.datetime.strptime(newest.split("/")[1].split(".")[0],'%m-%d-%Y').strftime('%m/%d')
                            c.testing = dt +"|{:,.0f}".format(int(row[11])) + " people tested  ("+ "{:,.2f}".format(int(row[11])/(c.pop*1000)) + "/K)"
                            break

    def loadRegion(self):
        self.regions  = {"South America": [ "Chile", "Argentina", "Colombia",
                                        "Uruguay", "Paraguay", "Venezuela",
                                        "Peru", "Bolivia", "Ecuador", "Brazil", "Panama"],
                        "Europe":["Germany", "Italy", "Spain", "United Kingdom",
                                "France", "Switzerland", "Poland", "Sweden",
                                "Austria", "Belgium", "Portugal", "Greece", "Luxembourg",
                                "Netherlands", "Denmark", "Ireland","Romania","Serbia","Iceland"],
                        "States":["Alabama", "Alaska", "American Samoa",
                                "Arizona", "Arkansas", "California", "Colorado",
                                "Connecticut", "Delaware", "District of Columbia",
                                "Florida", "Georgia*", "Guam", "Hawaii", "Idaho", "Illinois",
                                "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
                                "Maryland", "Massachusetts", "Michigan", "Minnesota",
                                "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
                                "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
                                "North Dakota","Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico",
                                "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
                                "Virgin Islands", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"],
                        "Asia": [ "Japan", "Indonesia", "China", "India", "Turkey",
                                "Thailand", "Korea, South","Singapore", "Vietnam",
                                "Phillippines", "Hong Kong", "Malaysia", "Iran", "Pakistan",
                                "Israel", "Cambodia", "Taiwan", "Iraq","Qatar","Syria","Lebanon","Jordan","Saudi Arabia"],
                        "Other": [ "Russia","Canada", "Mexico", "Honduras",
                                    "South Africa", "Egypt", "New Zealand",
                                    "Cuba", "Cote d'Ivoire", "Reunion", "Costa Rica", "Haiti"],
                        }
        try:
            with open('My_List.txt', 'rb') as fp:
                mycountries = list(set(pickle.load(fp)))
        except FileNotFoundError:
            mycountries = [ "Chile","Argentina","Miami-Dade, Florida", "US",
                            "Spain", "Italy", "United Kingdom", "Netherlands",
                            "New York"]
            with open('My_List.txt', 'wb') as fp:
                pickle.dump(mycountries, fp)
        self.regions["My List"] = mycountries
        for c in self.regions[self.region]:
            self.show(c)


class Country:
    def __init__(self,All,name,pop,color):
        self.name = name
        self.pop = pop
        self.vis = 0
        self.color= color
        self.newcases = []
        self.newcasesPerM = []
        self.cases  = []
        self.deaths  = []
        self.allcases = 0
        self.alldeaths = 0
        self.newdeaths= []
        self.newdeathsPerM= []
        self.casesPerM = []
        self.deathsPerM =[]
        self.day = 0
        self.days = 0
        self.x =[]
        self.GF=[]
        self.testing = ""
        All.countries = list(All.countries)
        All.country_colors[name] = color
        All.countries_list.append(name)
        All.countries.append(self)
