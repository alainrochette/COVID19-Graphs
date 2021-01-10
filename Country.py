import csv
import random
import pickle
import datetime
import glob
from matplotlib import colors

# Check https://matplotlib.org/3.1.0/gallery/color/named_colors.html for Named Colors
country_colors ={"France":"cornflowerblue", "Ecuador":"cornflowerblue","Honduras":"cornflowerblue","Morocco":"cornflowerblue",
                "Murray, Georgia":"darkkhaki",
                "Miami-Dade, Florida":"turquoise","Illinois":"turquoise","Costa Rica":"turquoise","Australia":"turquoise",
                "Germany":"dimgray", "Iran":"dimgray","Algeria":"dimgray","New Zealand":"dimgray",
                "Massachusetts":"skyblue", "Argentina":"skyblue", "Luxembourg":"skyblue", "Israel":"skyblue","Madagascar":"skyblue",
                "Panama":"deepskyblue", "Georgia*":"deepskyblue",
                "Uruguay":"steelblue", "Iceland":"steelblue", "Singapore":"steelblue", "Pennsylvania":"steelblue",
                "Turkey":"darkorchid", "New Jersey":"darkorchid", "US":"darkorchid","Paraguay":"darkorchid","Andorra":"darkorchid",
                "Delaware":"gold", "Spain":"gold", "Bolivia":"gold", "Saudi Arabia":"gold","Haiti":"gold","Egypt":"gold",
                "Connecticut":"limegreen", "Italy":"limegreen", "Qatar":"limegreen", "Brazil":"limegreen", "Cameroon":"limegreen",
                "District of Columbia":"forestgreen", "Mexico":"forestgreen","Nigeria":"forestgreen",
                "Michigan":"orange", "Netherlands":"orange", "Malaysia":"orange", "Colombia":"orange","Dominican Republic":"orange","Cote d'Ivoire":"orange",
                "Louisiana":"orchid", "United Kingdom":"orchid", "Austria":"orchid", "Japan":"orchid","Guatemala":"orchid",
                "New York, New York":"grey", "Ireland": "grey",
                "Lebanon":"slategrey",
                "Korea, South":"hotpink", "Belgium":"hotpink","Florida":"hotpink","Guam":"hotpink",
                "California":"darkgoldenrod","Kenya":"darkgoldenrod",
                "Los Angeles, California": "goldenrod", "Russia":"goldenrod",
                "China":"orangered", "Chile":"orangered", "Switzerland":"orangered","Rhode Island":"orangered","South Africa":"orangered",
                "Peru":"peru", "Maryland":"peru","Cuba":"peru",
                "Venezuela":"crimson", "Hong Kong":"crimson",
                "World":"black"}
country_colors  = {k:colors.to_rgba(country_colors[k]) for k in country_colors.keys()}
populationD ={"World":7800}

class Countries:
    def __init__(self,region,days_since=0):
        self.world_countries = []
        self.countries_cache = []
        self.country_colors = country_colors
        self.countries = list()
        self.dates = []
        self.regions  = {"World":[],
                        "South America": [ "Chile", "Argentina", "Colombia",
                                        "Uruguay", "Paraguay", "Venezuela",
                                        "Peru", "Bolivia", "Ecuador", "Brazil", "Panama"],
                        "Europe":["Germany", "Italy", "Spain", "United Kingdom",
                                "France", "Switzerland", "Poland", "Sweden",
                                "Austria", "Belgium", "Portugal", "Greece", "Luxembourg",
                                "Netherlands", "Denmark", "Ireland","Romania","Serbia","Iceland", "Finland","Andorra"],
                        "States":["Alabama", "Alaska", "American Samoa",
                                "Arizona", "Arkansas", "California", "Colorado",
                                "Connecticut", "Delaware", "District of Columbia",
                                "Florida", "Georgia*", "Hawaii", "Idaho", "Illinois",
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
                        "Africa":[ "Kenya","Nigeria", "Morocco", "Madagascar",
                                    "South Africa", "Egypt", "Algeria",
                                    "Cameroon", "Cote d'Ivoire", "Congo (Kinshasa)", "Congo (Brazzaville)", "Ethiopia", "Ghana",
                                    "Tanzania", "Mali", "Senegal", "Uganda", "Zambia", "Sudan", "Angola", "Somalia", "Zimbabwe",
                                    "Rwanda", "Algeria", "Niger", "Tunisia", "Libya", "Mozambique", "Namibia", "Liberia", "Burma Faso",
                                    "Guinea", "Malawi", "Togo", "Botswana", "Cabo Verde", "Chad", "Gabon", "Sierra Leone", "Mauritania"],
                        "Americas":[ "Mexico","Honduras", "Cuba", "Costa Rica",
                                    "Haiti", "Dominican Republic","Guatemala","Canada","Jamaica","US"],
                        "Other": ["Australia", "New Zealand", "Antarctica", "Russia", "Japan", "South Korea"]
                        }
        with open('csse_covid_19_time_series/time_series_covid19_confirmed_global.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                self.world_countries = list(set([row[1] for row in csv_reader if "Country" not in row[1]]))
                csv_file.close()
        self.regions["World"] = self.world_countries
        # for c in self.world_countries:
        #     found = False
        #     for r in ["South America","Europe","Asia","Africa","Americas"]:
        #         if c in self.regions[r]:
        #             found = True
        #             break
        #     if not found: self.regions["Other"].append(c)
        try:
            with open('myCache/My_List.txt',  'rb') as fp:
                mycountries = list(set(pickle.load(fp)))
        except FileNotFoundError:
            mycountries = [ "Chile","Argentina","Miami-Dade, Florida", "US",
                            "Spain", "Italy", "United Kingdom", "Netherlands", "Florida", "World", "California", "New York, New York"]
            with open('myCache/My_List.txt',  'wb') as fp:
                pickle.dump(mycountries, fp)
        self.regions["My List"] = mycountries
        self.loadRegion(region, days_since)

    def make_vis(self, c):
        c.vis = 1
        if c not in self.countries_list: self.countries_list.append(c)
        if self.region == "My List":
            self.regions[self.region] = self.countries_list
            with open('myCache/My_List.txt', 'wb') as fp:
                pickle.dump([cc.name for cc in self.countries_list], fp)
            fp.close()
            self.save()

    def make_invis(self, c):
        c.vis = 0
        if c in self.countries_list: self.countries_list.remove(c)
        if self.region == "My List":
            self.regions[self.region] = self.countries_list
            with open('myCache/My_List.txt',  'wb') as fp:
                pickle.dump([cc.name for cc in self.countries_list], fp)
            self.save()

    def show(self, c):
        if isinstance(c, Country):
            self.make_vis(c)
            return c
        for country in self.countries:
            if country.name.replace(" ","").lower() == c.replace(" ","").lower():
                self.make_vis(country)
                return country
        show_c = self.addOther(c)
        return show_c


    def get(self, c):
        self.countries = list(self.countries)
        for country in self.countries:
            if country.name.replace(" ","").lower() == c.replace(" ","").lower(): return country
        return 0

    def hide(self, c):
        if isinstance(c, Country):
            self.make_invis(c)
            return True
        for country in self.countries:
            if country.name == c:
                self.make_invis(country)
                return True
        return False

    def addOther(self,name):
        if "*" in name:
            return self.addState(name)
        found = False
        pop = populationD[name] if name in populationD else 0
        if pop==0:
            with open('population_data/Pop2020.csv',encoding='mac_roman') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count > 0 and row[0].lower()==name.lower():
                        pop =int(float(row[4]))/1000
                        break
                    line_count += 1
        if pop == 0: pop = 1
        with open('csse_covid_19_time_series/time_series_covid19_confirmed_global.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                c = None
                for row in csv_reader:
                    if line_count == 0:
                        cdates = [d.split("/")[0] + "/"+ d.split("/")[1] for d in row[4:] if d != ""]

                        if not self.dates: self.dates = cdates
                    elif row[1].lower().replace("*","")==name.lower() or row[0].lower().replace("*","")==name.lower()or name=="World":
                        if row[1].lower().replace("*","")==name.lower(): name = row[1].replace("*","")
                        if row[0].lower().replace("*","")==name.lower(): name = row[0].replace("*","")
                        found = True
                        if c:
                            c.allcases =  [x + y for x, y in zip(c.allcases, [int(float(x)) for x in row[4:][0:len(c.dates)] if x != ""])]
                        else:
                            newcolor =[random.random(),random.random(),random.random()]
                            if name in self.country_colors: newcolor = self.country_colors[name]
                            c = Country(self,name,pop,newcolor) if not c else self.get(name)
                            c.dates = cdates
                            c.allcases = [int(float(x)) for x in row[4:][0:len(c.dates)] if x != ""]
                    line_count += 1

                if found:
                    self.clean(c,"cases")
        if found:
            self.countries.append(c)
            if self.region == "My List":
                with open('myCache/My_List.txt',  'wb') as fp:
                    # pickle.dump(list(set(self.countries_list)), fp)
                    pickle.dump([c.name for c in self.countries_list], fp)
            with open('csse_covid_19_time_series/time_series_covid19_deaths_global.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                deathCount = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                    elif row[1].lower().replace("*","")==name.lower() or row[0].lower().replace("*","")==name.lower() or name=="World":
                        if deathCount > 0:
                            c.alldeaths =  [x + y for x, y in zip(c.alldeaths , [int(float(x)) for x in row[4:][0:len(c.dates)] if x != ""])]
                        else:
                            c.alldeaths = [int(float(x)) for x in row[4:][0:len(c.dates)] if x != ""]
                        deathCount += 1
                    line_count += 1

                self.clean(c,"deaths")
                c.vis = 1
            with open('csse_covid_19_time_series/time_series_covid19_recovered_global.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                recoveredCount = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                    elif row[1].lower().replace("*","")==name.lower() or row[0].lower().replace("*","")==name.lower() or name=="World":
                        if recoveredCount > 0:
                            c.allrecovered += [x + y for x, y in zip(c.allrecovered , [int(float(x)) for x in row[4:][0:len(c.dates)] if x != ""])]
                        else:
                            c.allrecovered = [int(float(x)) for x in row[4:][0:len(c.dates)] if x != ""]
                        recoveredCount += 1
                    line_count += 1
            with open('testing/covid-testing-all-observations.csv') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for row in reversed(list(csv_reader)):
                        n =  row[0].lower().split(" - ")[0].replace("south korea", "korea, south")
                        try:
                            a = int(row[6])
                        except ValueError:
                            pass
                        else:
                            if ("CDC" not in row[0]) and ((name.lower() ==n) or (name=="US" and n =="united states")):
                                dt = datetime.datetime.strptime(row[2], '%Y-%m-%d').strftime('%m/%d')
                                try:
                                    c.testing = dt +"|{:,.0f}".format(int(row[6])) + " " + row[0].split(" - ")[1].replace("(COVID Tracking Project)","") + " ("+ "{:,.1f}".format(int(float(row[8]))/10) + "%)"
                                except ValueError:
                                    pass
                                break
            return c
        else:
            return self.addState(name)

    def addState(self,place):
        found = False
        ast = "*" if "*" in place else ""
        place = place.replace(ast,"")
        pop = populationD[place] if place in populationD else 0
        with open('csse_covid_19_time_series/time_series_covid19_confirmed_US.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                c = None
                for row in csv_reader:
                    if line_count == 0:
                        cdates = [d.split("/")[0] + "/"+ d.split("/")[1] for d in row[11:] if d != ""]
                    elif (place.lower().replace(" ","")  ==  row[10].replace(", US","").lower().replace(" ","") or
                        place.lower()  ==  row[6].lower()):
                        found = True
                        if place.lower().replace(" ","")  ==  row[10].replace(", US","").lower().replace(" ",""): place = row[10].replace(", US","")
                        if place.lower()  ==  row[6].lower(): place = row[6]
                        if c:
                            c.allcases =  [x + y for x, y in zip(c.allcases, [int(float(x)) for x in row[11:][0:len(c.dates)] if x != ""])]
                        else:
                            newcolor =[random.random(),random.random(),random.random()]
                            if place +ast in self.country_colors: newcolor = self.country_colors[place+ast]
                            c = self.get(place+ast)
                            if not c: c = Country(self,place +ast,pop,newcolor)
                            c.dates = cdates
                            c.allcases = [int(float(x)) for x in row[11:][0:len(c.dates)] if x != ""]
                    line_count += 1

                if found:
                    self.clean(c,"cases")
        if found:
            self.countries.append(c)
            if self.region == "My List":
                with open('myCache/My_List.txt',  'wb') as fp:
                    pickle.dump([c.name for c in self.countries_list], fp)
                    # pickle.dump(list(set(self.countries_list)), fp)
            with open('csse_covid_19_time_series/time_series_covid19_deaths_US.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                deathCount = 0
                totalpop = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                    elif (place.lower().replace(" ","")  ==  row[10].replace(", US","").lower().replace(" ","") or
                        place.lower()  ==  row[6].lower()):
                        totalpop = totalpop + int(float(row[11]))
                        if deathCount > 0:
                                c.alldeaths =  [x + y for x, y in zip(c.alldeaths , [int(float(x)) for x in row[12:][0:len(c.dates)] if x != ""])]
                        else:
                            c.alldeaths = [int(float(x)) for x in row[12:][0:len(c.dates)] if x != ""]
                        deathCount += 1
                    line_count += 1

                if pop == 0: c.pop = totalpop/1000000

                self.clean(c, "deaths")
                c.vis = 1
            newest = sorted(glob.glob('csse_covid_19_daily_reports_us/*.csv'))[-1]
            with open(newest) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for row in csv_reader:
                        if place.lower() == row[0].lower() and row[11] != "" :
                            dt = datetime.datetime.strptime(newest.split("/")[1].split(".")[0],'%m-%d-%Y').strftime('%m/%d')
                            c.testing = dt +"|{:,.0f}".format(int(float(row[11]))) + " people tested ("+ "{:,.1f}".format(int(float(row[11]))/(c.pop*10000)) + "%)"
                            c.allrecovered = [int(row[7])] if row[7].isdigit() else ["?"]
                            break
            return c
        return 0

    def clean(self,c,type):
        days_since = 0 if "/" in str(self.days_since) else self.days_since
        if type == "cases":
            c.day = 0
            for cc in range(0,len(c.allcases)):
                if c.allcases[cc]  > days_since - 1 and c.day==0:
                    c.day = cc
                    break
            c.days = len(c.dates)-c.day
            c.x =[i for i in range(0,c.days)]
        all = getattr(c,"all"+type)
        norm =  [all[0]]
        max = all[0]
        for x in range(1,len(all)):
            if all[x] >=  max:
                norm.append(all[x])
                max = all[x]
            else:
                norm.append(max)
        new = [0] + [norm[x] - norm[x-1] for x in range(1,len(norm))]
        norm= norm[c.day:]
        new = new[c.day:]
        setattr(c,type,norm)
        setattr(c,"new"+type,new)

    def loadRegion(self, region, days_since):
        self.days_since = days_since
        self.countries_list = []
        self.region = region
        before = len(self.countries)
        for c in self.regions[self.region]:
            self.show(c)
        if len(self.countries) != before:
            self.save()

    def save(self):
        with open('myCache/Countries.txt', 'wb') as fp:
            pickle.dump(self, fp)
        fp.close()




class Country:
    def __init__(self,All,name,pop,color):
        self.name = name
        self.pop = pop
        self.vis = 0
        self.color= color
        self.defcolor= color
        # self.lightcolor = [x + (1 - x) * 0.35 for x in light_colors[color]] if isinstance(color, str) else [x + (1 - x) * 0.9 for x in color]
        self.lightcolor = [x + (1 - x) * 0.9 for x in color]
        self.dates = []
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
        self.allrecovered  = ["?"]
        All.country_colors[name] = color
        # All.countries_list.append(name)
        All.countries_list.append(self)
