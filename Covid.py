from Country import Country, Countries
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, RadioButtons, Button
import matplotlib.patches as mpatches
import csv
import math
import os
from scipy.ndimage.filters import gaussian_filter1d
import textwrap


caseWord = {0: "Jan 22", 1:"first case", 2:"second case", 3:"third case"}


class Graph():
    def __init__(self):
        self.All  = None
        self.fig = None
        self.limit = 12
        self.legend = None
        self.ylim = None
        self.selected_place  = None
        self.infoWidget = None
        self.infoBox = None
        self.removeWidget = None
        self.removeBox = None

    def load(self,region, days_since=0):
        self.limit = 12
        if region == "My List": self.limit = 120
        country_colors = None
        if  self.All: country_colors = self.All.country_colors
        self.All = Countries(region,days_since,colors=country_colors)
        self.clean()
        self.graph()

    def growthFactor(self,c):
        L = c.allcases
        gf = [1,1]+ [(L[i]-L[i-1])/(L[i-1]-L[i-2]) if (L[i-1]-L[i-2])!=0 else 1 for i in range(2,len(L))]
        return gf[c.day:len(gf)]

    def averageGrowthFactor(self,c):
        gf = self.growthFactor(c)
        return sum(gf[-3:])/3

    def showL(self,c,data):
    	return [i*c.vis for i in data]

    def getMaxY(self,type):
        sum = []
        for c in self.All.countries:
            if c.name != "World": sum += self.showL(c,getattr(c,type))
        return max(sum)*(1.05)

    def getMaxX(self,type):
        sum = []
        for c in self.All.countries:
            if c.name != "World": sum += self.showL(c,c.x)
        return max(sum)*(1.05)

    def order(self,type):
        d ={}
        for c in self.All.countries:
            if c.vis: d[c.name]=getattr(c,type)[-1]
        self.All.countries = {self.All.get(k): getattr(self.All.get(k),type) for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}.keys()

    def clean(self,):
        for c in self.All.countries:
            if c.vis:
                c.newcasesPerM = [x/c.pop for x in c.newcases]
                c.casesPerM = [x/c.pop for x in c.cases]
                c.deathsPerM = [x/c.pop for x in c.deaths]
                c.newdeathsPerM = [x/c.pop for x in c.newdeaths]
                c.GF = self.growthFactor(c)
        self.order("casesPerM")
        count=0
        for c in self.All.countries:
            c.vis = False
            if count < self.limit: c.vis = True
            count += 1

    def submit(self,text):
        self.limit = 120
        if text != "":
            if self.All.get(text):
                self.All.show(text)
            else:
                self.All.addOther(text)
            self.clean()
            self.graph()

    def remove(self,text):
        if self.selected_place:
            if self.All.hide(self.selected_place):
                self.clean()
                self.graph()

    def change_start(self,text):
        try:
            if int(text) != self.All.days_since:
                plt.close('all')
                self.load(self.All.region,int(text))
        except ValueError:
            pass

    def change_regions(self,region):
        plt.close('all')
        self.load(region)

    def country_info(self,c):
        self.selected_place = c.name
        txt = str(c.name)  + " " * (25-len(c.name)) + "GF: " +  "{:,.2f}".format(self.averageGrowthFactor(c))
        txt +="\nPopulation:         " + str(round(c.pop,2)) + "M"
        if c.testing != "" and len(c.testing.split("|")[1]) < 33: txt +="\n"
        txt +="\nCurrent Cases:   {:,.0f} ".format(c.cases[-1])
        txt +="\nCurrent Deaths: {:,.0f} ".format(c.deaths[-1])
        txt +="\n"
        if c.testing != "":
            dt = c.testing.split("|")[0]

            txt += "---------------- " + dt + " ----------------\n"
            txt += textwrap.fill(c.testing.split("|")[1],width=32)
        else:
            txt +="\n"
            txt += "----------- No Testing Info -----------\n"

        height = 0.15
        startheight = min(0.74 - (len([c for c in self.All.countries if c.vis])/31),0.6)

        if self.infoWidget:
            self.infoWidget.set_val(txt)
        else:
            self.infoBox = plt.axes([0.065, startheight, 0.16, height])
            self.infoBox.set_frame_on(False)
            self.infoWidget = TextBox(self.infoBox, '', txt)


        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor=c.color,
                                   facecolor="white",
                                   boxstyle="round,pad=0",
                                   mutation_aspect=0.001,
                                   transform=self.infoBox.transAxes,
                                   clip_on=False)
        self.infoBox.add_patch(fancybox)

        if not self.removeWidget:
            self.removeBox = plt.axes([0.23, startheight+height-0.055, 0.04, 0.055])
            self.removeWidget = Button(self.removeBox, 'Remove',color="whitesmoke" ,hovercolor="lightgray")
            self.removeWidget.label.set_fontsize(7)
            self.removeWidget.on_clicked(self.remove)

        self.removeBox.set_visible(True)
        self.infoBox.set_visible(True)
        self.infoWidget.text_disp.set_color([0.3, 0.3, 0.3])
        self.infoWidget.text_disp.set_size(8.2)

    def onclick(self, event):
        x = event.xdata
        y = event.ydata
        bottom, top = self.ylim
        nameheight = top / 26
        maxy =  top
        if self.removeBox: self.removeBox.set_visible(False)
        if self.infoBox: self.infoBox.set_visible(False)
        try:
            if x < 42.5 and  y < maxy and y > maxy - (nameheight*len([c for c in self.All.countries if c.vis])):
                count = len([c for c in self.All.countries if c.vis])
                index = math.floor((maxy-y)/nameheight)
                i = 0
                for x in self.All.countries:
                    if x.vis:
                        if i == index:
                            self.country_info(x)
                            break
                        i += 1
        except TypeError:
            pass

    def graph(self):
        graphs= ["casesPerM","newcasesPerM","deathsPerM","newdeathsPerM","newdeathsPerM","newcasesPerM"]
        sp = 1
        plt.close()
        if self.fig: plt.close('all')
        self.fig = plt.figure(figsize=(15,7))
        fig  = self.fig

        SMALL_SIZE = 6
        MEDIUM_SIZE = 8
        BIGGER_SIZE = 10
        self.infoWidget = None
        self.removeWidget = None
        if self.All.days_since ==0: self.All.dates = [d.split("/")[0] + "/"+ d.split("/")[1] for d in self.All.dates]

        for g in graphs:

            plt.rc('xtick', labelsize=SMALL_SIZE,color='dimgray')
            plt.rc('ytick', labelsize=SMALL_SIZE,color='dimgray')
            plt.rc('legend', fontsize=SMALL_SIZE)
            if sp > 4: plt.rc('legend', fontsize=BIGGER_SIZE)
            plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor='white',labelcolor='dimgray')
            if sp == 3 or sp == 4 :plt.rc('axes', labelsize=MEDIUM_SIZE,edgecolor='salmon')
            plt.rc('figure', titlesize=BIGGER_SIZE)

            if sp <= 4: fig =plt.subplot(2,2, sp)
            if sp > 4:
                fig= plt.figure(figsize=(15,7))


            g2 = g.replace("PerM"," (per 1M people)")
            plt.title("" + g2.replace("new","New ").title(),color="0.25")
            word = caseWord[self.All.days_since] if self.All.days_since in caseWord else str(self.All.days_since)+ "th case"
            plt.xlabel("Days since " + word,color='dimgray')

            if self.All.days_since ==0: plt.xlabel("Date")

            self.order(g)
            for c in self.All.countries:
                if c.vis:
                    gx =c.x
                    if self.All.days_since == 0: gx = self.All.dates
                    gy =getattr(c,g)[0:len(gx)]
                    if len(gy) < len(gx): gx = gx[0:len(gy)]
                    ysmoothed = gaussian_filter1d(gy, sigma=1.1)
                    if c.name== "World":
                        if "PerM" in g: plt.plot(gx, ysmoothed[0:len(gx)],'k--',label= c.name)
                    elif not (c.name == "London" and "death" in g):
                        plt.plot(gx, ysmoothed[0:len(gx)],color=c.color,label= c.name)

            self.legend = plt.legend(fancybox=True,loc="upper left", ncol=1)
            plt.grid(axis="y",color = "whitesmoke")
            plt.xticks(rotation=-0)

            if self.All.days_since==0:
                if sp > 4: plt.xticks(self.All.dates[::2])
                if sp <= 4: plt.xticks(self.All.dates[::4])

            maxx = self.getMaxX(g)
            minx=0
            if self.All.days_since==0: minx = 35

            plt.xlim(minx,maxx)
            # plt.ylim(0,maxy)
            plt.subplots_adjust(wspace=0.07, hspace=0.3, left=0.06,bottom=0.06,right=0.96, top=0.9)
            self.ylim = plt.ylim()
            if sp==len(graphs):
                fig.canvas.mpl_connect('button_press_event', self.onclick)
                inputBox = plt.axes([0.24, 0.675, 0.1, 0.055])
                inputWidget = TextBox(inputBox, '+', initial="", hovercolor="lightgray")
                inputWidget.on_submit(self.submit)

                startBox = plt.axes([0.85, 0.92, 0.03, 0.035])
                startWidget = TextBox(startBox, 'Start from case: ', initial='', hovercolor="lightgray")
                startWidget.label.set_color("0.5")
                startWidget.label.set_size(8)
                startWidget.on_submit(self.change_start)

                active_region ={"My List":0, "Europe":1,"Asia":2, "South America":3,"States":4,"Other":5}
                rax = plt.axes([0.23, 0.729, 0.1, 0.18], facecolor='white')
                radio = RadioButtons(rax, ('My List', 'Europe', 'Asia', 'South America','States', 'Other'),active=active_region[self.All.region],activecolor='lightgray')
                # radio.label.set_color("0.2")
                radio.on_clicked(self.change_regions)
            sp +=1

        plt.show()
