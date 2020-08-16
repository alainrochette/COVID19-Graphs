from Country import Country, Countries
from Prediction import Prediction
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, RadioButtons, Button
import matplotlib.patches as mpatches
import csv
import math
import os
from scipy.ndimage.filters import gaussian_filter1d
import textwrap
from datetime import datetime
import pickle
import scipy
from scipy.integrate import odeint
from scipy import optimize, stats
import numpy as np
import random

# plt.rc('text', usetex=True)

#[]   +    =     {}



caseWord = {0: "Jan 22", 1:"first case", 2:"second case", 3:"third case"}
SMALL_SIZE = 7
MEDIUM_SIZE = 8
BIGGER_SIZE = 10



class Graph():
    def __init__(self, lastUpdated):
        self.All  = None
        self.fig = None
        self.big = "newcasesPerM"
        self.params = False
        self.scale = 1
        self.limit = 12
        self.ylim = None
        self.xlim = None
        self.showAll= False
        self.selectedC  = None
        self.clickedG = None
        self.infoWidget = None
        self.infoBox = None
        self.inputWidget = None
        self.removeWidget = None
        self.predictWidget = None
        self.colorWidget = None
        self.removeBox = None
        self.predictBox = None
        self.colorBox = None
        self.addToListBox = None
        self.addToListWidget = None
        self.startBox = None
        self.startWidget = None
        self.LUtext = None
        self.settingsBox = None
        self.updateBox = None
        self.refreshBox = None
        self.confirmText= None
        self.inInput = False
        self.graphs = None
        self.region = None
        # self.derivFunc = self.deriv
        self.sortBy = "newcasesPerM"
        self.countries = []
        self.firstAdd ={}
        self.graphLines ={}
        self.axGraphs ={}
        self.graphsAx ={}
        self.graphsLabels={}
        self.graphsHandles={}
        self.graphsNameheight={}
        self.y0Line = {}
        self.lastUpdated = lastUpdated
        self.dayBefore = -1
        self.graphDateLine = {}
        self.predictLine= None
        self.S0 = None
        self.I0 = None
        self.R0 = None
        self.setParams()

    def load(self,region, days_since=0):
        self.region = region
        self.limit  = 120 if region == "My List" else 12
        country_colors =  self.All.country_colors if self.All else None
        self.All = Countries(region,days_since,colors=country_colors)
        self.countries = self.All.countries
        if self.lastUpdated == "???": self.lastUpdated = datetime.strptime(self.All.dates[-1], '%m/%d/%y')
        self.graph()

    def setParams(self):
        mpl.rcParams['legend.fontsize'] = SMALL_SIZE - 1
        if self.params: return 0
        self.params = { 'text.color': "0.3",
                        'font.size': 9,
                        # 'font.sans-serif' : "Consolas",
                        'lines.linewidth' : 1.7,
                        "axes.labelsize": MEDIUM_SIZE, "axes.edgecolor": "white",
                        "axes.labelcolor" :"0.5",
                        'xtick.color' : "0.5", 'xtick.labelsize' : SMALL_SIZE,
                        'ytick.color' : "0.5", 'ytick.labelsize' : SMALL_SIZE,
                        'axes.grid' : True, 'axes.grid.axis' : "y", 'grid.color' : "0.95",
                        }
        mpl.rcParams.update(self.params)

    def changeColor(self,event):
        if event and self.selectedC:
            selected = self.selectedC.name
            found = False
            for graph in self.graphs:
                labels = self.graphsLabels[graph]
                for lname in labels:
                    c =  self.All.get(lname)
                    if c and lname == selected:
                        line = self.graphLines[graph][lname][0]
                        if not found: c.color = [random.random(),random.random(),random.random()]
                        if not found: c.lightcolor = [x + (1 - x) * 0.9 for x in c.color ]
                        line.set_color(c.color)
                        found = True
                        break
            self.country_info(self.selectedC)
            self.draw()

    def predict(self,event):
        c = self.selectedC
        pred = Prediction(c, self.clickedG)
        y_train_pred=pred.fitted

        # fig = plt.figure("New",figsize=(15,7))
        # ax = fig.add_subplot(111)
        ax = self.graphsAx[self.clickedG]
        newy = y_train_pred
        if "death" in self.clickedG:
            newy = [y * sum(c.deaths) for y in newy]
        else:
            newy = [y * sum(c.cases) for y in newy]
        # ax.plot(pred.xdata, pred.ydata, color="black", linewidth=1, label='train')
        if self.predictLine:
            self.predictLine[0].remove()
            del self.predictLine[0]
        self.predictLine = ax.plot(pred.newxdata, newy[:len(pred.newxdata)], color="black", linewidth=1, label='model')
        ax.set_xlim(right=len(c.x)+len(pred.newxdata))
        ax.relim()
        plt.show()

    def sir_model(self, y, x, beta, gamma):
        S = -beta * y[0] * y[1] / (self.selectedC.pop*1000000)
        R = gamma * y[1]
        I = -(S + R)
        return S, I, R

    def fit_odeint(self,x, beta, gamma):
        return odeint(self.sir_model, (self.S0, self.I0, self.R0), x, args=(beta, gamma))[:,1]

    def skewnorm(self,x, sigmag, mu, alpha, c,a):

        normpdf = (1/(sigmag*np.sqrt(2*math.pi)))*np.exp(-(np.power((x-mu),2)/(2*np.power(sigmag,2))))

        normcdf = (0.5*(1+sp.erf((alpha*((x-mu)/sigmag))/(np.sqrt(2)))))
        return 2*a*normpdf*normcdf + c

    def growthFactor(self,c,type):
        L = getattr(c, type)
        gf = [1,1]+ [(L[i]-L[i-1])/(L[i-1]-L[i-2]) if (L[i-1]-L[i-2])!=0 else 1 for i in range(2,len(L))]
        return gf

    def averageGrowthFactor(self,c, type):
        # gf = c.casesGF if type == "cases" else c.deathsGF
        gf = c.newcasesPerM if type == "cases" else c.newdeathsPerM
        a = gf[-7 + self.dayBefore + 1]
        b = gf[len(gf) + self.dayBefore]

        if a == 0: a = 0.5
        if b == 0: b = 0.5
        return (b/a)**(1/float(7))

    def showL(self,c,data):
    	return [i*c.vis for i in data]

    def order(self,type):
        d ={}
        for c in self.countries:
            d[c.name]=getattr(c,type)[-1]
        self.countries = list({self.All.get(k): getattr(self.All.get(k),type) for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}.keys())

    def labelOrder(self,handles,labels,type):
        d ={}

        for lab in labels:
            c = self.All.get(lab)
            d[c.name]=getattr(c,type)[-1]
        labelsOrder = list({k: getattr(self.All.get(k),type) for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}.keys())
        return [handles[labels.index(label)] for label in labelsOrder], labelsOrder

    def prep(self, c=None):
        if not c:
            for c in self.countries:
                if not c.newcasesPerM:
                    c.newcasesPerM = [x/c.pop for x in c.newcases]
                    c.casesPerM = [x/c.pop for x in c.cases]
                    c.deathsPerM = [x/c.pop for x in c.deaths]
                    c.newdeathsPerM = [x/c.pop for x in c.newdeaths]
                    c.casesGF = self.growthFactor(c,"cases")
                    c.deathsGF = self.growthFactor(c,"deaths")
                    c.avgcasesGF = [self.averageGrowthFactor(c,"cases")]
                    c.avgdeathsGF = [self.averageGrowthFactor(c,"deaths")]
                    c.active = [x - y for x,y in zip(c.cases, c.deaths)]
                    if len(c.allrecovered) != 1: c.active = [x - y for x,y in zip(c.active, c.allrecovered)]
                    c.activePerM = [x/c.pop for x in c.active]
                    c.newactive = [c.active[i+1]-c.active[i] for i in range(len(c.active)-1)]
                    c.newactivePerM = [x/c.pop for x in c.newactive]
        elif not c.newcasesPerM:
            c.newcasesPerM = [x/c.pop for x in c.newcases]
            c.casesPerM = [x/c.pop for x in c.cases]
            c.deathsPerM = [x/c.pop for x in c.deaths]
            c.newdeathsPerM = [x/c.pop for x in c.newdeaths]
            c.casesGF = self.growthFactor(c,"cases")
            c.deathsGF = self.growthFactor(c,"deaths")
            c.avgcasesGF = [self.averageGrowthFactor(c,"cases")]
            c.avgdeathsGF = [self.averageGrowthFactor(c,"deaths")]
            c.active = [x - y for x,y in zip(c.cases, c.deaths)]
            if len(c.allrecovered) != 1: c.active = [x - y for x,y in zip(c.active, c.allrecovered)]
            c.activePerM = [x/c.pop for x in c.active]
            c.newactive = [c.active[i+1]-c.active[i] for i in range(len(c.active)-1)]
            c.newactivePerM = [x/c.pop for x in c.newactive]

    def addToList(self,event):
        selected = self.selectedC
        with open('myCache/My_List.txt',  'rb') as fp:
            mycountries = list(set(pickle.load(fp)))
        mynewcountries = list(set(mycountries +  [self.selectedC.name]))
        if mynewcountries != mycountries:
            with open('myCache/My_List.txt', 'wb') as fp:
                pickle.dump(mynewcountries, fp)
            self.selectedC = selected
            self.change_regions("My List",selected)

    def add(self,text, loading=False):
        if not loading: self.limit = 120
        if text != "":
            if self.All.get(text):
                self.selectedC = self.All.show(text)
            else:
                self.selectedC = self.All.addOther(text)
            if self.selectedC:
                c = self.selectedC
                if not loading:self.countries.append(c)
                self.prep(c)
                for g in self.graphs:

                    added = False
                    if "active" in g and len(c.allrecovered) < 2:
                        pass
                    else:
                        ax = self.graphsAx[g]
                        gx = c.dates if self.All.days_since == 0 or "/" in str(self.All.days_since) else c.x
                        gy =getattr(c,g.replace("Big",""))[0:len(gx)]
                        if len(gy) < len(gx): gx = gx[0:len(gy)]
                        ysigma = 1.1
                        # ysigma = 0.5
                        if "newactive" in g: ysigma = 2.5
                        if "death" in g: ysigma = 2
                        ysmoothed = gaussian_filter1d(gy, sigma=ysigma)
                        lw =1.7
                        self.graphLines[g][c.name]= ax.plot(gx, ysmoothed[0:len(gx)],color=c.color,label= c.name,linewidth=lw)
                        if not self.y0Line[g] and "newactive" in g: self.y0Line[g] = ax.axhline(0, color='black', linestyle='--', linewidth=1)

                        ax.relim()
                        ax.autoscale_view()

                        handles, labels = ax.get_legend_handles_labels()
                        newhandles, newlabels = self.labelOrder(handles,labels, g.replace("Big",""))
                        self.graphsHandles[g] = newhandles
                        self.graphsLabels[g] = newlabels

                        minx = 35 if self.All.days_since==0 or "/" in str(self.All.days_since) else 0
                        minx = self.All.dates.index(self.All.days_since) if "/" in str(self.All.days_since) else minx
                        ax.set_xlim(left=minx)
                        self.xlim = minx, len(c.x)
                        added = True


                    if added and self.firstAdd[g]:
                        if self.All.days_since==0 or "/" in str(self.All.days_since):
                            interval = int(len(self.All.dates)/45)
                            if "Big" in g: ax.set_xticks(self.All.dates[::interval])
                            if not "Big" in g: ax.set_xticks(self.All.dates[::interval*2])

                    if added: self.firstAdd[g] = False
                if self.removeBox: self.removeBox.set_visible(False)
                if self.predictBox: self.predictBox.set_visible(False)
                if self.colorBox: self.colorBox.set_visible(False)
                if self.addToListBox: self.addToListBox.set_visible(False)
                if self.infoBox: self.infoBox.set_visible(False)


                self.infoWidget = None
                self.removeWidget = None
                self.predictWidget = None
                self.colorWidget = None
                self.addToListWidget = None
                self.inputWidget.set_val("")
                if not loading: self.select(self.selectedC.name)
            if loading: self.selectedC = None
            # self.inInput = False
            self.draw()


    def remove(self,event):
        if not self.selectedC: return
        self.All.hide(self.selectedC.name)
        self.countries.remove(self.selectedC)
        for graph in self.graphs:
            if self.selectedC.name in self.graphLines[graph]:
                line = self.graphLines[graph][self.selectedC.name][0]
                line.remove()
                del line
                ax = self.graphsAx[graph]
                ax.relim()
                ax.autoscale_view()
                minx = 35 if self.All.days_since==0 or "/" in str(self.All.days_since) else 0
                minx = self.All.dates.index(self.All.days_since) if "/" in str(self.All.days_since) else minx
                ax.set_xlim(left=minx)
                ind = self.graphsLabels[graph].index(self.selectedC.name)
                self.graphsHandles[graph].remove(self.graphsHandles[graph][ind])
                self.graphsLabels[graph].remove(self.selectedC.name)
        self.select(None)
        self.infoWidget = None
        self.removeWidget = None
        self.predictWidget = None
        self.colorWidget = None
        self.addToListWidget = None

    def draw(self):
        for graph in self.graphs:
            legFontSize = SMALL_SIZE - 1 if "Big" not in graph else BIGGER_SIZE-0.5
            try:
                self.graphsAx[graph].legend(self.graphsHandles[graph],self.graphsLabels[graph],fontsize = legFontSize,fancybox=True,loc="upper left", ncol=1)
            except KeyError:
                pass
        if self.graphs[-1] in self.graphDateLine and self.graphDateLine[self.graphs[-1]]:
            self.graphDateLine[self.graphs[-1]].remove()
            del self.graphDateLine[self.graphs[-1]]
        if self.selectedC and self.dayBefore < -1:
            self.graphDateLine[self.graphs[-1]] = self.graphsAx[self.graphs[-1]].axvline(self.All.dates[self.dayBefore],ymin=0,ymax=10000,color="lightgray" )
        if self.startWidget: self.startWidget.set_val("")
        plt.figure("Main")
        plt.draw()
        plt.figure("All Graphs")
        plt.draw()

    def change_start(self,text):
        try:
            if (text.isdigit() and int(text) != self.All.days_since):
                if int(text)==0 and "/" in str(self.All.days_since):
                    for g in self.graphs:
                        ax = self.graphsAx[g]
                        ax.set_xlim(left=int(text))
                        minx = 35 if self.All.days_since==0 or "/" in str(self.All.days_since) else 0
                        ax.set_xlim(left=minx)
                    self.draw()
                else:
                    self.load(self.All.region,int(text))
            elif "/" in text and text in self.All.dates:
                for g in self.graphs:
                    ax = self.graphsAx[g]
                    self.All.days_since = text
                    ax.set_xlim(left=self.All.dates.index(text))
                self.draw()
        except ValueError:
            pass

    def change_regions(self,region,selected=False):

        if not selected: self.selectedC  = None
        plt.figure("Main")
        plt.close('all')
        self.load(region)

    def change_sortby(self,sortBy,selected=False):
        if not selected: self.selectedC  = None
        sortDict = {'Cases':"casesPerM", 'New Cases':"newcasesPerM",'Deaths':"deathsPerM",
                    'New Deaths':"newdeathsPerM", 'Cases Growth':"avgcasesGF", 'Deaths Growth':"avgdeathsGF", "Active":"activePerM"}
        self.big = sortDict[sortBy]
        if "Growth" in sortBy:
            self.big = "newcasesPerM" if "Cases" in sortBy else "newdeathsPerM"
        self.sortBy = sortDict[sortBy]
        plt.figure("Main")
        plt.close('all')
        self.load(self.region)

    def country_info(self,c):
        plt.figure("Main")
        plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor="None")
        self.selectedC = c

        name = c.name.split(",")[0] if "," in c.name else c.name.replace(" ","\ ")
        place = r"$\bf{}$".format(name.upper())
        dateBef = "{date}".format(date=c.dates[self.dayBefore])
        pop = "pop {:,.1f}K".format(round(c.pop*1000,2)) if c.pop < 0.1 else "pop {:,.1f}M".format(round(c.pop,2))
        txt = "{} {}\n".format(place,pop.rjust(50-2*(len(place)), " "))
        if dateBef != "": txt += "――――――― {} ――――――".format(dateBef)

        cases = "{:,.0f}".format(c.cases[self.dayBefore])
        casesPerM = "({:,.0f}/M)".format(c.casesPerM[self.dayBefore])
        oneincases =   "-" if c.cases[self.dayBefore] == 0 else  "(1 in {:,.0f})".format(int(1000000*c.pop/c.cases[self.dayBefore]))
        newcases = "{:,.0f}".format(c.newcases[self.dayBefore])
        casesGF = "({:3.2f} GF)".format(self.averageGrowthFactor(c, "cases"))

        deaths = "{:,.0f}".format(c.deaths[self.dayBefore])
        deathsPerM = "({:,.0f}/M)".format(c.deathsPerM[self.dayBefore])
        oneindeaths = "no deaths :)" if c.deaths[self.dayBefore] == 0 else "(1 in {:,.0f})".format(int(1000000*c.pop/c.deaths[self.dayBefore]))
        newdeaths  = "{:,.0f}".format(c.newdeaths[self.dayBefore])
        deathsGF = "({:3.2f} GF)".format(self.averageGrowthFactor(c, "deaths"))

        MR =" {:,.1f}%".format(100*c.alldeaths[self.dayBefore]/c.cases[self.dayBefore])
        txt +='\n  ' + r"$\bf{}$:  {:<10}{:>10}".format("Cases", cases,oneincases)
        txt +='\n' + "{}:  {:<11}{:>10}".format("      New", newcases,casesGF)
        txt +='\n' + r"$\bf{}$:  {:<12}{:>10}".format("Deaths", deaths, oneindeaths)
        txt +='\n' + "{}:  {:<12}{:>10}".format("      New", newdeaths,deathsGF)
        txt +='\n' + "{}: {:<10}".format("        MR", MR)

        if c.allrecovered !=  ["?"]:
            if len(c.allrecovered) > 1:
                allRec = "{:,.0f}".format(c.allrecovered[self.dayBefore])

                recoveredRate = "({:,.1f}%)".format(100*c.allrecovered[self.dayBefore]/(c.cases[self.dayBefore]))
                lastDate = ""
            else:
                allRec = "{:,.0f}".format(c.allrecovered[-1])
                recoveredRate = "({:,.1f}%)".format(100*c.allrecovered[-1]/(c.cases[-1]))
                lastDate = "[" + c.dates[-1] + "] "
            txt +='\n  ' + r"$\bf{}$:  {:<10}{:^9}{:>7}".format("  Recov", allRec,recoveredRate,lastDate)
        else:
            txt +='\n  ' + r"$\bf{}$:  {}".format("  Recov", "?")

        active = "{:,.0f}".format(c.active[self.dayBefore])
        activePerM = "({:,.0f}/M)".format(c.activePerM[self.dayBefore])

        oneinactive =  "-" if c.active[self.dayBefore] == 0 else "(1 in {:,.0f})".format(int(1000000*c.pop/c.active[self.dayBefore]))
        newactive = "{:,.0f}".format(c.newactive[self.dayBefore])
        txt +='\n  ' + r"$\bf{}$:  {:<10}{:>10}".format("Active", active,oneinactive)
        txt +='\n' + "{}:  {:<11}".format("      New", newactive)
        if c.testing == "" or (c.testing != "" and len(c.testing.split("|")[1]) < 33): txt +="\n"
        if c.testing != "":
            dt = c.testing.split("|")[0]
            if dt[0] == "0": dt = dt[1:]
            txt += "\n――――――― " + dt + " ――――――\n"
            txt += textwrap.fill(c.testing.split("|")[1],width=32)
        else:
            txt += "\n―――― No Testing Info ――――\n"

        height = 0.27
        startheight = min(0.62 - (max(7,len(self.graphsLabels[self.clickedG]))/32),0.5)

        if self.infoBox: self.infoBox.remove()
        self.infoBox = plt.axes([0.065, startheight, 0.165, height])
        self.infoBox.axis('off')
        self.infoBox.text(0.03,0.05,txt, color=[0.3,0.3,0.3], size = 8.2)



        self.infoBox.set_frame_on(False)

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,edgecolor=c.color,
                                   facecolor="white", boxstyle="round,pad=0",
                                   mutation_aspect=0.001,
                                   transform=self.infoBox.transAxes, clip_on=False)
        self.infoBox.add_patch(fancybox)

        if not self.removeWidget and not self.predictWidget and not self.colorWidget:
            if self.removeBox: self.removeBox.remove()
            if self.predictBox: self.predictBox.remove()
            if self.colorBox: self.colorBox.remove()
            self.removeBox = plt.axes([0.235, startheight+height-0.055, 0.04, 0.055])
            self.removeWidget = Button(self.removeBox, 'Remove',color="whitesmoke" ,hovercolor="lightgray")
            self.removeWidget.label.set_fontsize(7)
            self.removeWidget.on_clicked(self.remove)

            self.colorBox = plt.axes([0.235, startheight+height-3*0.055 - 0.02, 0.04, 0.055])
            self.colorWidget = Button(self.colorBox, 'Change\nColor',color="whitesmoke" ,hovercolor="lightgray")
            self.colorWidget.label.set_fontsize(7)
            self.colorWidget.on_clicked(self.changeColor)

            # self.predictBox = plt.axes([0.235, startheight+height-3*0.055 - 0.02, 0.04, 0.055])
            # self.predictWidget = Button(self.predictBox, 'Predict',color="whitesmoke" ,hovercolor="lightgray")
            # self.predictWidget.label.set_fontsize(7)
            # self.predictWidget.on_clicked(self.predict)

            if self.All.region != "My List":
                if self.addToListBox: self.addToListBox.remove()
                self.addToListBox = plt.axes([0.235, startheight+height-0.12, 0.04, 0.055])
                self.addToListWidget = Button(self.addToListBox, 'Add To\nMy List',color="whitesmoke" ,hovercolor="lightgray")
                self.addToListWidget.label.set_fontsize(6.5)
                self.addToListWidget.on_clicked(self.addToList)
        if self.addToListBox: self.addToListBox.set_visible(True)
        self.removeBox.set_visible(True)
        self.colorBox.set_visible(True)
        # self.predictBox.set_visible(True)
        self.infoBox.set_visible(True)
        if self.clickedG and not "Big" in self.clickedG: plt.figure("All Graphs")

    def press(self,event):
        if event.key == "escape": self.toggleSettings(False)
        if not self.inInput and event.key.isdigit():
            labels = self.graphsLabels[self.clickedG]
            if int(event.key) <= len(labels):
                self.select(labels[int(event.key)-1])
            return
        if self.selectedC:
            if event.key == "escape": self.onclick(event=None)
            if not self.inInput and (event.key == "down" or event.key == "s" or event.key == "up" or event.key == "w") :
                labels = self.graphsLabels[self.clickedG]
                dir = 1 if event.key == "down" or event.key == "s" else -1
                curr_index = labels.index(self.selectedC.name)
                new_index = (curr_index + dir) % len(labels)
                self.select(labels[new_index])
            if not self.inInput and (event.key == "a" or event.key == "left" or event.key == "d" or event.key == "right"):

                dir = -1 if  event.key == "a" or event.key == "left"  else 1
                self.dayBefore = min(self.dayBefore + dir, -1)
                self.select(self.selectedC.name)

    def select(self,selected):
        if not selected:
            self.selectedC = None
            self.dayBefore = -1
            self.toggleSettings(False)
        if self.removeBox: self.removeBox.set_visible(False)
        if self.predictBox: self.predictBox.set_visible(False)
        if self.colorBox: self.colorBox.set_visible(False)
        if self.addToListBox: self.addToListBox.set_visible(False)
        if self.predictLine:
            self.predictLine[0].remove()
            del self.predictLine[0]
            self.predictLine = None
        # if self.infoBox and self.infoWidget:
        if self.infoBox:
            self.infoBox.set_visible(False)
            self.infoBox.text(0,0,"")
            # self.infoWidget.set_val("")
        if "Big" in self.clickedG: self.graphsAx[self.clickedG].set_xlim(self.xlim)
        for graph in self.graphs:
            labels = self.graphsLabels[graph]
            for lname in labels:
                c =  self.All.get(lname)
                if c:
                    line =self.graphLines[graph][lname][0]

                    if lname == selected or not selected:
                        line.set_color(c.color)
                        if selected: line.set_linewidth(2.6)

                        if selected: self.selectedC = c
                        if not selected: line.set_linewidth(1.7)
                    else:
                        line.set_linewidth(1.7)
                        line.set_color(c.lightcolor)

        if self.selectedC: self.country_info(self.selectedC)
        self.draw()

    def onclick(self, event):
        if not event:
            self.select(None)
            return 0
        x = event.xdata
        y = event.ydata
        try:
            self.clickedG = self.axGraphs[event.inaxes]
        except KeyError:
            for g in self.graphs:
                if "Big" in g: self.clickedG = g
        bottom, top = self.graphsAx[self.clickedG].get_ylim()
        nameheight = (top-bottom) / 28  if "Big" in self.clickedG  else (top-bottom)/12     # Consol
        maxy =  top
        self.inInput = False
        self.showAll= False
        labels = self.graphsLabels[self.clickedG]

        try:
            if x > 2 and x < self.graphsAx[self.clickedG].get_xlim()[0] + 10 and  y < maxy and y > maxy - (nameheight*len(labels)):
                count = len(labels)
                index = math.floor((maxy-y)/nameheight)
                i = 0
                self.select(labels[index])
            elif x > 2:
                self.dayBefore = -1
                if self.selectedC:
                    self.showAll  = False
                if "Big" not in self.clickedG:
                    self.big = self.clickedG
                    self.graph()
                else:
                    self.select(None)
            else:
                self.inInput = True
        except TypeError:
            pass

    def refreshData(self, event):
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
        self.lastUpdated = lastUpdated
        self.load("My List")

    def toggleSettings(self, event):
        if not event:
            self.refreshBox.set_visible(False)
            self.confirmText.set_visible(False)
            self.helpBox.set_visible(False)
            self.helpText.set_visible(False)
        else:
            self.refreshBox.set_visible(not self.refreshBox.get_visible())
            self.confirmText.set_visible(not self.confirmText.get_visible())
            self.helpBox.set_visible(not self.helpBox.get_visible())
            if self.helpText.get_visible(): self.helpText.set_visible(False)
        plt.draw()

    def toggleHelp(self,event):
        self.helpText.set_visible(not self.helpText.get_visible())

    def toggleSort(self,event,turn=None):
        if turn==False or turn==True:
            self.raxSort.set_visible(turn)
        else:
            self.raxSort.set_visible(not self.raxSort.get_visible())

    def graph(self):
        plt.ion()
        self.prep()
        self.graphs =  ["casesPerM","newcasesPerM","deathsPerM","newdeathsPerM","activePerM","newactivePerM"] + ["Big" + self.big]
        if (self.All.days_since ==0 or "/" in str(self.All.days_since)):
            self.All.dates = [d.split("/")[0] + "/"+ d.split("/")[1] for d in self.All.dates]
        sp = 1
        if self.fig: plt.close('all')
        self.infoWidget = None
        self.removeWidget = None
        self.predictWidget = None
        self.colorBox = None
        self.addToListWidget = None

        for g in self.graphs:
            self.firstAdd[g] = True

            if "Big" in g:
                plt.rc('legend', fontsize=BIGGER_SIZE-0.5)
                plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor='white',labelcolor='dimgray')
                fig = plt.figure("Main",figsize=(15,7))
                ax = fig.add_subplot(111)
            else:
                plt.rc('legend', fontsize=SMALL_SIZE-1)
                self.fig = plt.figure("All Graphs",figsize=(15,7))
                fig  = self.fig
            plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor="None")
            if "deaths" in g:
                plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor='salmon')
            else:
                plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor="None")
            if not "Big" in g:
                ax = fig.add_subplot(3,2,sp)
                sp +=1
            self.axGraphs[ax] = g
            self.graphsAx[g] = ax
            self.graphLines[g] = {}
            self.graphsHandles[g] = {}
            self.graphsLabels[g] = {}
            self.y0Line[g] = {}

            g2 = g.replace("PerM"," (per 1M people)").replace("Big","")
            plt.title("" + g2.replace("new","New ").title(),color="0.25",fontsize=11,fontname="DejaVu Sans")
            if "Big" in g: plt.title("" + g2.replace("new","New ").title(),color="0.25",fontsize=14)
            if sp > 5:
                word = caseWord[self.All.days_since] if self.All.days_since in caseWord else str(self.All.days_since)+ "th case"
                plt.xlabel("Days since " + word,color='dimgray')
                if self.All.days_since ==0 or "/" in str(self.All.days_since): plt.xlabel("Date")

            # plt.subplots_adjust(wspace=0.07, hspace=0.3, left=0.06,bottom=0.06,right=0.96, top=0.9)
            plt.subplots_adjust(wspace=0.15, hspace=0.45, left=0.06,bottom=0.06,right=0.96, top=0.9)

            fig.canvas.mpl_connect('key_press_event', self.press)
            fig.canvas.mpl_connect('button_press_event', self.onclick)
            if "Big" in g:
                plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor="None")
                inputBox = plt.axes([0.066, 0.9, 0.14, 0.055])
                self.inputWidget = TextBox(inputBox, 'Add\nPlace:', initial="", hovercolor="lightgray")
                self.inputWidget.on_submit(self.add)
                self.inputWidget.label.set_size(9)
                self.inputWidget.label.set_color("0.4")

                self.startBox = plt.axes([0.85, 0.91, 0.03, 0.035])
                self.startWidget = TextBox(self.startBox, 'Start from  \ncase/date: ', initial='', hovercolor="lightgray")
                self.startWidget.label.set_color("0.6")
                self.startWidget.label.set_size(7)
                self.startWidget.on_submit(self.change_start)

                self.settingsBox = plt.axes([0.92, 0.91, 0.06, 0.035])
                settingsWidgets = Button(self.settingsBox, 'Settings',color="whitesmoke" ,hovercolor="lightgray")
                settingsWidgets.label.set_fontsize(7)
                settingsWidgets.on_clicked(self.toggleSettings)

                self.refreshBox = plt.axes([0.92, 0.8, 0.06, 0.035])
                refreshWidget = Button(self.refreshBox , 'Update Data',color="whitesmoke" ,hovercolor="lightgray")
                refreshWidget.label.set_fontsize(7)
                refreshWidget.on_clicked(self.refreshData)
                self.refreshBox.set_visible(False)

                props = dict( facecolor='white', edgecolor='white')
                self.confirmText= ax.text(0.958, 0.87, "Refresh takes\n up to 20 secs.", transform=ax.transAxes, fontsize=7,
                        verticalalignment='top', color ="darkgray", bbox=props)
                self.confirmText.set_visible(False)

                self.helpBox = plt.axes([0.92, 0.69, 0.06, 0.035])
                helpWidget = Button(self.helpBox , 'Help',color="whitesmoke" ,hovercolor="lightgray")
                helpWidget.label.set_fontsize(7)
                helpWidget.on_clicked(self.toggleHelp)
                self.helpBox.set_visible(False)

                self.helpText= ax.text(0.938, 0.73, ("\n".join(["•Type any Place: (Country,\n  US City, US State) \n",
                                                    "     Examples:\n          -Lithuania\n          -Houston, Texas\n          -California\n",
                                                    "•Choose starting date/\n  days since Xth case\n",
                                                    "•Click Place in Legend for\n  More Info / to Remove.\n",
                                                    "•With place selected, use\n  arrow keys to navigate\n",
                                                    "•GF: Growth Factor: Rate of\n  growth over past week\n       <1 slowing down\n       >1 speeding up\n",
                                                    "•MR: Mortality Rate",])), transform=ax.transAxes, fontsize=6,
                                                        verticalalignment='top', color ="darkgray",bbox=props)
                self.helpText.set_visible(False)
                self.LUtext= ax.text(0.958, 1, "Last Updated:\n "+self.lastUpdated.strftime("%m/%d %H:%M"), transform=ax.transAxes, fontsize=7,
                        verticalalignment='top', color ="darkgray")




                active_region ={"My List":0, "World":1,"States":2,"Europe":3,"Asia":4, "Africa":5,"South America":6, "Americas":7 ,"Other":8}
                rax = plt.axes([0.222, 0.68, 0.12, 0.22], facecolor='None')
                radio = RadioButtons(rax, ('My List', 'World','States', 'Europe', 'Asia', 'Africa','South America', 'Americas','Other'),active=active_region[self.All.region],activecolor='lightgray')
                radio.on_clicked(self.change_regions)

                regBox = plt.axes([0.222, 0.9, 0.12, 0.22], facecolor='None')
                regBox.axis('off')
                regBox.text(0,0,"Region:",color=[0.5,0.5,0.5],size=6)
                regBox.set_frame_on(False)



                if len(self.countries) > 12:
                    self.raxSort = plt.axes([0.2275, 0.49, 0.085, 0.16], facecolor='None')
                    sortOptions={"casesPerM":0, "newcasesPerM":1,"deathsPerM":2,"newdeathsPerM":3,"avgcasesGF":4, "avgdeathsGF":5, "activePerM":6}
                    radioSort = RadioButtons(self.raxSort, ('Cases', 'New Cases','Deaths', 'New Deaths', 'Cases Growth', 'Deaths Growth', 'Active'),active=sortOptions[self.sortBy],activecolor='lightgray')
                    # sortBox.text(0,0,"Sort By:",color=[0.5,0.5,0.5],size=6)
                    self.sortButton = Button(plt.axes([0.222, 0.65, 0.04, 0.025]), "Sort By:",color="whitesmoke" ,hovercolor="lightgray")
                    self.sortButton.label.set_fontsize(7)
                else:
                    self.raxSort = plt.axes([0.229, 0.52, 0.07, 0.13], facecolor='None')
                    sortOptions={"casesPerM":0, "newcasesPerM":1,"deathsPerM":2,"newdeathsPerM":3, "activePerM":4}
                    if self.sortBy not in sortOptions:
                        self.sortBy = "newcasesPerM"
                    radioSort = RadioButtons(self.raxSort, ('Cases', 'New Cases','Deaths', 'New Deaths','Active'),active=sortOptions[self.sortBy],activecolor='lightgray')
                    # sortBox.text(0,0,"Show:",color=[0.5,0.5,0.5],size=6)
                    self.sortButton = Button(plt.axes([0.222, 0.65, 0.04, 0.025]), "Show:",color="whitesmoke" ,hovercolor="lightgray")
                    self.sortButton.label.set_fontsize(7)
                radioSort.on_clicked(self.change_sortby)
                self.sortButton.on_clicked(self.toggleSort)
                self.raxSort.set_visible(False)
                # if self.region != "All" and self.region != "Europe" and self.region != "Asia" and self.region!="States":
                #     raxSort.set_visible(False)
                #     sortBox.set_visible(False)

        self.order(self.sortBy)
        selected = self.selectedC
        for c in list(reversed(self.countries[:self.limit])): self.add(c.name, loading=True)
        for c in self.countries[self.limit:]: self.countries.remove(c)
        if selected: self.select(selected.name)
        plt.ioff()
        plt.show()
