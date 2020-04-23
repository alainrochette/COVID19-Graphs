from Country import Country, Countries
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
        self.showAll= False
        self.selectedC  = None
        self.clickedG = None
        self.infoWidget = None
        self.infoBox = None
        self.inputWidget = None
        self.removeWidget = None
        self.removeBox = None
        self.startWidget = None
        self.LUtext = None
        self.refreshBox = None
        self.updateBox = None
        self.confirmBox = None
        self.confirmText= None
        self.inInput = False
        self.graphs = None
        self.places = []
        self.graphLines ={}
        self.axGraphs ={}
        self.graphsAx ={}
        self.graphsLabels={}
        self.graphsHandles={}
        self.graphsNameheight={}
        self.lastUpdated = lastUpdated
        self.dayBefore = - 1
        self.graphDateLine = {}
        self.setParams()

    def load(self,region, days_since=0):
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


    def growthFactor(self,c):
        L = c.cases
        gf = [1,1]+ [(L[i]-L[i-1])/(L[i-1]-L[i-2]) if (L[i-1]-L[i-2])!=0 else 1 for i in range(2,len(L))]
        return gf

    def averageGrowthFactor(self,c):
        return sum(c.GF[-6:])/6

    def showL(self,c,data):
    	return [i*c.vis for i in data]

    def order(self,type):
        d ={}
        for c in self.places:
            d[c.name]=getattr(c,type)[-1]
        self.places = {self.All.get(k): getattr(self.All.get(k),type) for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}.keys()

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
                    c.GF = self.growthFactor(c)
        elif not c.newcasesPerM:
            c.newcasesPerM = [x/c.pop for x in c.newcases]
            c.casesPerM = [x/c.pop for x in c.cases]
            c.deathsPerM = [x/c.pop for x in c.deaths]
            c.newdeathsPerM = [x/c.pop for x in c.newdeaths]
            c.GF = self.growthFactor(c)

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
                    ax = self.graphsAx[g]
                    gx = c.dates if self.All.days_since == 0 or "/" in str(self.All.days_since) else c.x
                    gy =getattr(c,g.replace("Big",""))[0:len(gx)]
                    if len(gy) < len(gx): gx = gx[0:len(gy)]
                    ysmoothed = gaussian_filter1d(gy, sigma=1)
                    if c.name== "World":
                        if "PerM" in g: ax.plot(gx, ysmoothed[0:len(gx)],'k--',label= c.name)
                    else:
                        self.graphLines[g][c.name]= ax.plot(gx, ysmoothed[0:len(gx)],color=c.color,label= c.name)

                    ax.relim()
                    ax.autoscale_view()


                    handles, labels = ax.get_legend_handles_labels()
                    # sort both labels and handles by labels
                    # self.order(g.replace("Big",""))
                    newhandles, newlabels = self.labelOrder(handles,labels, g.replace("Big",""))
                    self.graphsHandles[g] = newhandles
                    self.graphsLabels[g] = newlabels

                    # maxx = ax.get_xlim()[1]*1.04
                    minx = 35 if self.All.days_since==0 or "/" in str(self.All.days_since) else 0
                    minx = self.All.dates.index(self.All.days_since) if "/" in str(self.All.days_since) else minx
                    ax.set_xlim(left=minx)

                    if self.firstAdd:
                        if self.All.days_since==0 or "/" in str(self.All.days_since):
                            if "Big" in g: ax.set_xticks(self.All.dates[::2])
                            if not "Big" in g: ax.set_xticks(self.All.dates[::4])

                if self.removeBox: self.removeBox.set_visible(False)
                if self.infoBox: self.infoBox.set_visible(False)
                self.firstAdd = False
                self.infoWidget = None
                self.infoBox = None
                self.removeWidget = None
                self.removeBox = None
                self.inputWidget.set_val("")
                if not loading: self.select(self.selectedC.name)
            if loading: self.selectedC = None
            self.draw()


    def remove(self,event):
        if not self.selectedC: return
        self.All.hide(self.selectedC.name)
        self.countries.remove(self.selectedC)
        for graph in self.graphs:
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
        self.infoBox = None
        self.removeWidget = None
        self.removeBox = None

    def draw(self):
        for graph in self.graphs:
            legFontSize = SMALL_SIZE - 1 if "Big" not in graph else BIGGER_SIZE-0.5
            self.graphsAx[graph].legend(self.graphsHandles[graph],self.graphsLabels[graph],fontsize = legFontSize,fancybox=True,loc="upper left", ncol=1)
            if self.selectedC and self.dayBefore< -1:
                if graph in self.graphDateLine and self.graphDateLine[graph]:
                    self.graphDateLine[graph].remove()
                    del self.graphDateLine[graph]
                self.graphDateLine[graph] = self.graphsAx[graph].axvline(self.All.dates[self.dayBefore],ymin=0,ymax=10000,color="lightgray" )
            elif graph in self.graphDateLine:
                self.graphDateLine[graph].remove()
                del self.graphDateLine[graph]

        # print(self.startWidget)
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
                # self.load(self.All.region,text)
        except ValueError:
            pass

    def change_regions(self,region):
        self.selectedC  = None
        plt.figure("Main")
        plt.close('all')
        self.load(region)

    def country_info(self,c):
        plt.figure("Main")
        plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor="None")
        self.selectedC = c
        name = c.name.split(",")[0] if "," in c.name else c.name

        txt ='{:18.18}  ({:3.2f} GF) {date}'.format(name, self.averageGrowthFactor(c),date="[" + c.dates[self.dayBefore] + "]" if self.dayBefore < -1 else "")
        if c.pop < 0.1: txt +='\n{}  {:,.1f}K'.format("Population:", round(c.pop*1000,2))
        if c.pop >= 0.1: txt +='\n{}  {:,.1f}M'.format("Population:", round(c.pop,2)) #{:15s}

        if c.testing != "" and len(c.testing.split("|")[1]) < 33: txt +="\n"

        txt +='\n{}   {:,.0f} {} ({:,.0f}/M)'.format("Cases:", c.cases[self.dayBefore], " "*(20-len(str(c.casesPerM[self.dayBefore]))),c.casesPerM[self.dayBefore])
        txt +='\n{} {:,.0f} {} ({:,.0f}/M)\n'.format("Deaths:", c.deaths[self.dayBefore], " "*(25-len(str(c.deathsPerM[self.dayBefore]))),c.deathsPerM[self.dayBefore])

        if c.testing != "":
            dt = c.testing.split("|")[0]
            txt += "------------ " + dt + " -----------\n"
            txt += textwrap.fill(c.testing.split("|")[1],width=32)
        else:
            txt +="\n"
            txt += "------- No Testing Info ------\n"

        height = 0.15
        startheight = min(0.74 - (max(5,len(self.graphsLabels[self.clickedG]))/32),0.6)

        if self.infoWidget:
            self.infoWidget.set_val(txt)
        else:
            self.infoBox = plt.axes([0.065, startheight, 0.16, height])
            self.infoBox.set_frame_on(False)
            self.infoWidget = TextBox(self.infoBox, '', txt)
        self.infoWidget.text_disp.set_color([0.3, 0.3, 0.3])
        self.infoWidget.text_disp.set_size(8.2)

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1, edgecolor=c.color,
                                   facecolor="white", boxstyle="round,pad=0",
                                   mutation_aspect=0.001,
                                   transform=self.infoBox.transAxes, clip_on=False)
        self.infoBox.add_patch(fancybox)

        if not self.removeWidget:
            self.removeBox = None
            self.removeBox = plt.axes([0.23, startheight+height-0.055, 0.04, 0.055])
            self.removeWidget = Button(self.removeBox, 'Remove',color="whitesmoke" ,hovercolor="lightgray")
            self.removeWidget.label.set_fontsize(7)
            self.removeWidget.on_clicked(self.remove)

        self.removeBox.set_visible(True)
        self.infoBox.set_visible(True)
        if self.clickedG and not "Big" in self.clickedG: plt.figure("All Graphs")

    def press(self,event):
        if event.key == "escape": self.toggleConfirm(False)
        if not self.inInput and event.key.isdigit():
            labels = self.graphsLabels[self.clickedG]
            if int(event.key) <= len(labels):
                self.select(labels[int(event.key)-1])
            return
        if self.selectedC:
            if event.key == "escape": self.onclick(event=None)
            if not self.inInput and event.key == "down" or event.key == "s" or event.key == "up" or event.key == "w" :
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
            self.toggleConfirm(False)
        if self.removeBox:
            self.removeBox.set_visible(False)
        if self.infoBox:
            self.infoBox.set_visible(False)
            self.infoWidget.set_val("")

        for graph in self.graphs:
            labels = self.graphsLabels[graph]
            for lname in labels:
                c =  self.All.get(lname)
                if c:
                    line =self.graphLines[graph][lname][0]
                    if lname == selected or not selected:
                        line.set_color(c.defcolor)
                        if selected: self.selectedC = c
                    else:
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
        nameheight = top / 27  if "Big" in self.clickedG  else top/18     # Consol
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
                self.select(None)
                if "Big" not in self.clickedG:
                    self.big = self.clickedG
                    self.graph()
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

    def toggleConfirm(self, event):
        if not event:
            self.confirmBox.set_visible(False)
            self.confirmText.set_visible(False)
        else:
            self.confirmBox.set_visible(not self.confirmBox.get_visible())
            self.confirmText.set_visible(not self.confirmText.get_visible())
        plt.draw()

    def graph(self):
        plt.ion()
        self.prep()
        self.graphs =  ["casesPerM","newcasesPerM","deathsPerM","newdeathsPerM"] + ["Big" + self.big]

        if (self.All.days_since ==0 or "/" in str(self.All.days_since)): self.All.dates = [d.split("/")[0] + "/"+ d.split("/")[1] for d in self.All.dates]
        sp = 1
        if self.fig: plt.close('all')
        self.infoWidget = None
        self.removeWidget = None
        self.firstAdd  = True
        for g in self.graphs:
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
                ax = fig.add_subplot(2,2,sp)
                sp +=1
            self.axGraphs[ax] = g
            self.graphsAx[g] = ax
            self.graphLines[g] = {}

            g2 = g.replace("PerM"," (per 1M people)").replace("Big","")
            plt.title("" + g2.replace("new","New ").title(),color="0.25",fontsize=11,fontname="DejaVu Sans")
            if "Big" in g: plt.title("" + g2.replace("new","New ").title(),color="0.25",fontsize=14)
            word = caseWord[self.All.days_since] if self.All.days_since in caseWord else str(self.All.days_since)+ "th case"
            plt.xlabel("Days since " + word,color='dimgray')
            if self.All.days_since ==0 or "/" in str(self.All.days_since): plt.xlabel("Date")

            plt.subplots_adjust(wspace=0.07, hspace=0.3, left=0.06,bottom=0.06,right=0.96, top=0.9)

            fig.canvas.mpl_connect('key_press_event', self.press)
            fig.canvas.mpl_connect('button_press_event', self.onclick)
            if "Big" in g:
                plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor="None")
                # inputBox = plt.axes([0.24, 0.675, 0.1, 0.055])
                inputBox = plt.axes([0.066, 0.9, 0.14, 0.055])
                self.inputWidget = TextBox(inputBox, 'Add\nPlace:', initial="", hovercolor="lightgray")
                self.inputWidget.on_submit(self.add)
                self.inputWidget.label.set_size(8)
                self.inputWidget.label.set_color("0.4")

                startBox = plt.axes([0.85, 0.91, 0.03, 0.035])
                self.startWidget = TextBox(startBox, 'Start from\ncase/date: ', initial='', hovercolor="lightgray")
                self.startWidget.label.set_color("0.5")
                self.startWidget.label.set_size(8)
                self.startWidget.on_submit(self.change_start)

                self.confirmBox = plt.axes([0.92, 0.8, 0.06, 0.035])
                confirmWidget = Button(self.confirmBox , 'Confirm',color="whitesmoke" ,hovercolor="lightgray")
                confirmWidget.label.set_fontsize(7)
                confirmWidget.on_clicked(self.refreshData)
                self.confirmBox.set_visible(False)

                self.confirmText= ax.text(0.958, 0.87, "Refresh takes\n up to 20 secs.", transform=ax.transAxes, fontsize=7,
                        verticalalignment='top', color ="darkgray")
                self.confirmText.set_visible(False)

                self.refreshBox = plt.axes([0.92, 0.91, 0.06, 0.035])
                refreshWidget = Button(self.refreshBox, 'Refresh Data',color="whitesmoke" ,hovercolor="lightgray")
                refreshWidget.label.set_fontsize(7)
                refreshWidget.on_clicked(self.toggleConfirm)

                self.LUtext= ax.text(0.958, 1, "Last Updated:\n "+self.lastUpdated.strftime("%m/%d %H:%M"), transform=ax.transAxes, fontsize=7,
                        verticalalignment='top', color ="darkgray")


                active_region ={"My List":0, "Europe":1,"Asia":2, "South America":3,"States":4,"Other":5}
                rax = plt.axes([0.23, 0.729, 0.1, 0.18], facecolor='white')
                radio = RadioButtons(rax, ('My List', 'Europe', 'Asia', 'South America','States', 'Other'),active=active_region[self.All.region],activecolor='lightgray')
                radio.on_clicked(self.change_regions)

        self.order("casesPerM")
        count=0
        for c in self.countries:
            if count < self.limit: self.add(c.name, loading=True)
            if count >= self.limit: self.countries.remove(c)
            count += 1
        plt.ioff()
        plt.show()
