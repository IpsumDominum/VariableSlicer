import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.simpledialog import askstring
from PIL import Image, ImageTk
from tkinter import END
from netCDF4 import Dataset
import os
import numpy as np
import sys
import re
import threading
import time
sys.setrecursionlimit(5000)



LARGE_FONT = ("Helvatica",15)
SMALL_FONT = ("VerdaNA",10)
MEDIUM_FONT = ("VerdaNA",12)
w_height = "750"
w_width = "500"

class Data_interface(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args,**kwargs)
        self.geometry(w_height+"x"+w_width)
        self.directory = ""
        self.saving_directory = ""
        self.current_dir = os.getcwd()
        self.not_saved = True
        self.errorlog = StringVar()
        self.errorlog.set("error log: ")


        tk.Tk.wm_title(self, "Data_interface 2018")
        container = tk.Frame(self)
        container.pack(side="top",fill="both",expand = True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        #all the frames pages
        self.frames = {}
        for F in (StartPage, MainPage,HelpPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0, column = 0, sticky="nsew")

        #menu
        menu = Menu(self)
        files = Menu(menu)
        help_menu = Menu(menu)
        help_menu.add_command(label="help",command=lambda:self.show_frame(HelpPage))
        files.add_command(label="configure", command=lambda:self.show_frame(StartPage))
        files.add_command(label="set saving directory", command=lambda: self.set_save_directory())
        menu.add_cascade(label="files", menu=files)
        menu.add_cascade(label="help", menu=help_menu)
        self.config(menu=menu)
        self.show_frame(StartPage)

    def show_frame(self,cont):

        frame = self.frames[cont]
        frame.tkraise()
    def set_save_directory(self):
        # Allow user to select a directory and store it in global
        os.chdir(self.current_dir)
        saving_directory = filedialog.askdirectory()
        file = open("saving_directory.txt", 'w')
        file.write(saving_directory)
        file.close()
        self.saving_directory = saving_directory
        self.frames[StartPage].saving_directory.set("saving output file to: "+saving_directory)
    def popup(self,title,message):
        pop = tk.Tk()
        pop.wm_title(title)
        label = Text(pop,font=SMALL_FONT)
        label.insert(INSERT,message)
        label.pack(side="top",fill="x",pady=10)
        pop.mainloop()

class StartPage(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.value = StringVar()
        self.parent = parent
        self.controller = controller
        self.saving_directory = StringVar()
        self.saving_directory.set("saving output file to: ")
        self.selected_directory = StringVar()
        self.selected_directory.set("dataset directory: ")
        #Configuring grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=3)

        #read from file whether or not needing to configure the saving directory

        self.check_saving_directory()

        #creating frames
        frame1 = tk.Frame(self)
        frame1.grid(row=0,column=0)
        frame2 = tk.Frame(self)
        frame2.grid(row=1,column=0)
        frame2_1 = tk.Frame(frame2)
        frame2_1.grid(row=0,column=0)
        frame2_2 = tk.Frame(frame2)
        frame2_2.grid(row=0,column=1)
        frame2_1_1 = tk.Frame(frame2_1)
        frame2_1_1.grid(row=0, column=0)
        frame2_1_2 = tk.Frame(frame2_1)
        frame2_1_2.grid(row=1, column=0)
        frame2_2_1 =tk.Frame(frame2_2)
        frame2_2_1.grid(row=0,column=0)
        frame2_2_2 = tk.Frame(frame2_2)
        frame2_2_2.grid(row=1,column=0)
        frame3 = tk.Frame(self)
        frame3.grid(row=2,column=0)

        #configuring frame layout
        frame2.grid_columnconfigure(0,weight=1)
        frame2.grid_columnconfigure(1,weight=1)

        frame2_1.grid_rowconfigure(0,weight=1)
        frame2_1.grid_rowconfigure(1, weight=1)
        frame2_1.grid_rowconfigure(2,weight=3)
        frame2_2.grid_rowconfigure(0,weight=1)
        frame2_2.grid_rowconfigure(1,weight=3)

        #Browse for a directory
        browse = ttk.Button(frame2_2_1, text="Browse",command=self.browse_button)
        browse.pack(side=RIGHT)

        #show the browsed directory
        self.directory_show = Entry(frame2_2_1, width = 70,textvariable=self.selected_directory).pack(side=LEFT)


        #adding labels and buttons and other widgets
        label = ttk.Label(frame1,text="Welcome to Variable Slicer Software for NetCDF files", font=LARGE_FONT)
        label.pack(side="top",anchor="n")
        label = ttk.Label(frame1, text="For specific usage ", font=MEDIUM_FONT)
        label.pack(side="top", anchor="n")
        label2= ttk.Label(frame1,text="please configure directory",font=SMALL_FONT)
        label2.pack(side="left",anchor="sw")


        #adding a logo
        load = Image.open('tomato.jpg')
        render = ImageTk.PhotoImage(load.resize((50,50),Image.ANTIALIAS))
        img = Label(frame1, image=render)
        img.image = render
        img.pack(side="right")


        #warning

        self.show_saving_dir = Entry(frame2_2_2, width=70,textvariable = self.saving_directory).grid(row=1,column=0)

        #ready button
        self.ready = ttk.Button(frame2_2_2,text="ready", command= self.ready).grid(row=1,column=1)

        #errorlog

        self.errorlog_bar = Entry(frame3,width=100,textvariable=self.controller.errorlog)
        self.errorlog_bar.pack(side=BOTTOM)


    def browse_button(self):
        # Allow user to select a directory and store it in global
        directory = filedialog.askdirectory()
        self.controller.directory = directory
        self.selected_directory.set("dataset directory: "+ directory)
        os.chdir(directory)
    def ready(self):
        try:
            self.controller.frames[MainPage].update_variable_list("h2")
            self.controller.show_frame(MainPage)
        except FileNotFoundError:
            self.errorlog_bar.config({"background":"PINK"})
            self.controller.errorlog.set("error log: please set a valid directory containing\n h0, h1, and h2 \n files")
            self.controller.show_frame(MainPage)
    def check_saving_directory(self):
        try:
            with open("saving_directory.txt", "r") as file:
                line = file.readline()
                if line is not "not_saved":
                    self.controller.saving_directory = line
                    self.saving_directory.set("saving output file to: " + line)
                    self.controller.not_saved = False
                else:
                    self.controller.saving_directory = ""
                    self.controller.not_saved = True
        except FileNotFoundError:
            with open("saving_directory.txt","w") as file:
                file.write("not_saved")



class MainPage(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.directory_selection = StringVar()
        self.file_selection = StringVar()
        self.dir_selection = StringVar()
        self.start = StringVar()
        self.end = StringVar()
        self.warning = StringVar()
        self.interval = StringVar()
        self.saved_file_name = StringVar()
        self.selecting_from_selected = StringVar()
        self.days_c = IntVar()
        self.month_c = IntVar()
        self.ten_days_c = IntVar()
        self.years_c = IntVar()
        self.days_c.set(1)
        self.selecting_from_selected.set("selected(click delete to delete): empty")
        self.time_interval = ["year","month","day"]
        self.controller = controller
        self.path_name = ""
        self.selected_variables_list = []
        self.start_month_temp = "m"
        self.end_month_temp = "m"
        self.start_day_temp = "d"
        self.end_day_temp = "d"
        self.start_year = "y"
        self.end_year = "y"
        self.start_month = "NA"
        self.end_month = "NA"
        self.start_day = "d"
        self.end_day = "d"
        self.selecting_num = 0
        self.additional_variables = ['lev','hyam','hybm','ilev','hyai','hybi','P0','lat','lon','slat','slon','w_stag','ntrm','ntrn','ntrk','ndbase','nsbase','nbdate','nbsec','mdt','nlon','wnummax','gw']


        #making frames
        self.top_frame = ttk.Frame(self)
        self.top_frame.grid(row=0,column=0,pady=10)
        self.frame1 = ttk.Frame(self.top_frame)
        self.frame1.grid(row=0,column=0)
        self.frame2 = ttk.Frame(self.top_frame)
        self.frame2.grid(row=0,column=1)
        self.frame3 = ttk.Frame(self.top_frame)
        self.frame3.grid(row=0,column=2)
        self.frame3_1 = ttk.Frame(self.frame3)
        self.frame3_1.grid(row=0,column=0)
        self.frame3_2 = ttk.Frame(self.frame3)
        self.frame3_2.grid(row=1,column=0)
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.grid(row=2,column=0)

        ################################
        #Show the variables in the file#
        ################################
        self.variable_list = Listbox(self.frame1,width='50',selectmode=BROWSE,exportselection=0)
        self.variable_list.grid(row=0,column=0,sticky="nsew")
        self.variable_list.bind("<Double-Button-1>", self.OnVarSelect)
        scroll1y = tk.Scrollbar(self.frame1, orient=tk.VERTICAL, command=self.variable_list.yview)
        scroll1y.grid(row=0, column=1, sticky='nsw')
        self.variable_list['yscrollcommand'] = scroll1y.set

        self.all_the_selected_variables = Listbox(self.frame1, width='50',height='9', selectmode=BROWSE, exportselection=0)
        self.all_the_selected_variables.grid(row=4, column=0,sticky="nsew")
        self.all_the_selected_variables.bind("<Double-Button-1>", self.SelectedVarSelect)
        scrollvy = tk.Scrollbar(self.frame1, orient=tk.VERTICAL, command=self.all_the_selected_variables.yview)
        scrollvy.grid(row=4, column=1, sticky='nsw')
        self.all_the_selected_variables['yscrollcommand'] = scrollvy.set

        self.variable_desc = Listbox(self.frame1, width='50',height='6', selectmode=BROWSE, exportselection=0)
        self.variable_desc.grid(row=2, column=0,sticky="nsew")
        scrolldy = tk.Scrollbar(self.frame1, orient=tk.VERTICAL, command=self.variable_desc.yview)
        scrolldy.grid(row=2, column=1, sticky='nsw')
        self.variable_desc['yscrollcommand'] = scrolldy.set

        self.variable_label = Label(self.frame1, text="Variable Description")
        self.variable_label.grid(row=1, column=0)
        self.variable_label = Label(self.frame1, text="Selected Variables")
        self.variable_label.grid(row=3, column=0)
        self.selecting_selected = Entry(self.frame1,width=40,textvariable=self.selecting_from_selected)
        self.selecting_selected.grid(row=4,sticky="sw")
        self.delete_button_for_selected = Button(self.frame1,text="delete",command=self.delete_selected).grid(row=4,sticky="se")

        #making the selection option boxes

        ####################
        #select time period#
        ####################
        self.interval.set("interval")
        self.interval_selection = OptionMenu(self.frame2,self.interval,*self.time_interval,command=self.fill_times).grid(row=0,column=0)

        #start selection
        self.start_selection = Listbox(self.frame2,selectmode=BROWSE,height='13',exportselection=0)
        self.start_selection.grid(row=1,column=0)
        self.start_selection.bind("<Double-Button-1>", self.select_start)
        scrollsy = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.start_selection.yview)
        scrollsy.grid(row=1, column=1, sticky='nsw')
        self.start_selection['yscrollcommand'] = scrollsy.set

        #end selection
        self.end_selection = Listbox(self.frame2,selectmode=BROWSE,height='13',exportselection=0)
        self.end_selection.grid(row=2,column= 0)
        self.end_selection.bind("<Double-Button-1>", self.select_end)
        scrolley = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.end_selection.yview)
        scrolley.grid(row=2, column=1, sticky='nsw')
        self.end_selection['yscrollcommand'] = scrolley.set



        # various options:
        self.days_check = Checkbutton(self.frame3_1, text="days",variable=self.days_c,command=self.days).grid(row=2,column=0)
        self.month_check = Checkbutton(self.frame3_1, text="months",variable=self.month_c,command=self.months).grid(row=4,column=0)
        self.ten_days_check = Checkbutton(self.frame3_1, text="10 days",variable=self.ten_days_c,command=self.ten_days).grid(row=3,column=0)
        self.years_check = Checkbutton(self.frame3_1,text="years",variable=self.years_c,command=self.years).grid(row=1,column=0)
        self.select_label = Label(self.frame3_1,text="select a period base:").grid(row=0,column=0)

        #showing the selected dates
        self.start_show = Entry(self.frame3_2,textvariable=self.start).grid(row=3,column=0)
        self.end_show = Entry(self.frame3_2, textvariable=self.end).grid(row=4,column=0)
        self.update_date_display()

        ####################
        #select time period#
        ####################
        #save button
        self.save = Button(self.frame3_2, text="save",command = self.generate_file).grid(row=7,column=0)
        self.file_name = Entry(self.frame3_2,textvariable = self.saved_file_name).grid(row=6,column=0)
        self.set_save_name = Button(self.frame3_2, text="set file name",command=self.setFilename).grid(row=5,column=0)

        #errorlog
        self.errorlog_bar = Entry(self.bottom_frame,width=100,textvariable=self.controller.errorlog)
        self.errorlog_bar.grid(sticky="s")


    def OnVarSelect(self,event):
        #clear all variable description
        self.variable_desc.delete(0,END)
        counter = self.all_the_selected_variables.size()
        widget = event.widget
        var_name = widget.get(widget.curselection()[0])
        repeat = False
        for item in self.all_the_selected_variables.get(0,END):
            if item[2:] == var_name:
                repeat = True
        if repeat == False:
            self.all_the_selected_variables.insert(END,str(counter)+"|"+str(var_name))
            self.selected_variables_list.append(var_name)

        #populate variable description
        variable = self.nc_file.variables[var_name]
        for attr in variable.ncattrs():
            self.variable_desc.insert(END,attr+": "+str(variable.getncattr(attr)))
    def SelectedVarSelect(self,event):
        widget = event.widget
        widget_selection = widget.get(widget.curselection()[0])
        self.selecting_from_selected.set("selected(click delete to delete):"+widget_selection[2:])
        self.selecting_num = int(widget_selection[0])

    def delete_selected(self):
        refresh_list = []
        counter = 0
        if self.selecting_num < self.all_the_selected_variables.size():
            self.all_the_selected_variables.delete(self.selecting_num)
            self.selected_variables_list.remove(self.all_the_selected_variables.get(self.selecting_num)[2:])
            self.selecting_num -= 1
            if self.selecting_num < self.all_the_selected_variables.size():
                if self.selecting_num >=0:
                    self.selecting_from_selected.set("selected(click delete to delete): "+self.all_the_selected_variables.get(self.selecting_num))
                elif self.selecting_num <0:
                    self.selecting_num = 0
                    self.selecting_from_selected.set("selected(click delete to delete): empty")
            #refreshing the selecting list
            for item in self.all_the_selected_variables.get(0,END):
                refresh_list.append(item[2:])
            self.all_the_selected_variables.delete(0,END)
            for item in refresh_list:
                self.all_the_selected_variables.insert(END,str(counter)+"|"+item)
                counter +=1
        else:
            self.errorlog_bar.config({"background":"PINK"})
            self.controller.errorlog.set("errorlog : there is no more variable to be deleted from selections...")

    def select_start(self,event):
        widget = event.widget
        curselection = widget.get(widget.curselection()[0])
        if self.interval.get() == "year":
            if re.match("Select",curselection):
                pass
            else:
                self.start_year = curselection
        elif self.interval.get() == "month":
            if re.match("Select",curselection):
                pass
            elif self.month_c.get()==0:
                self.errorlog_bar.config({"background": "PINK"})
                self.controller.errorlog.set("error log: currently not in Month mode")
                pass
            else:
                self.start_month_temp = curselection
                self.start_month = self.start_month_temp
        elif self.interval.get() == "day":
            if re.match("Select",curselection):
                pass
            elif self.days_c.get() ==0 and self.ten_days_c.get() ==0:
                self.errorlog_bar.config({"background": "PINK"})
                self.controller.errorlog.set("error log: currently not in day or 10 day selecting mode")
                pass
            else:
                self.start_day_temp = curselection
                self.start_day = self.start_day_temp
        self.update_date_display()

    def select_end(self,event):
        widget = event.widget
        curselection = widget.get(widget.curselection()[0])
        if self.interval.get() == "year":
            if re.match("Select",curselection):
                pass
            else:
                self.end_year = curselection
        elif self.interval.get() == "month":
            if re.match("Select",curselection):
                pass
            elif self.month_c.get()==0:
                self.errorlog_bar.config({"background": "PINK"})
                self.controller.errorlog.set("error log: currently not in Month mode")
                pass
            else:
                self.end_month_temp = curselection
                self.end_month = self.end_month_temp
        elif self.interval.get() == "day":
            if re.match("Select",curselection):
                pass
            elif self.days_c.get() ==0 and self.ten_days_c.get() ==0:
                self.errorlog_bar.config({"background": "PINK"})
                self.controller.errorlog.set("error log: currently not in day or 10 day selecting mode")
                pass
            else:
                self.end_day_temp = curselection
                self.end_day = self.end_day_temp
        self.update_date_display()

    def days(self):
        self.month_c.set(0)
        self.ten_days_c.set(0)
        self.years_c.set(0)
        check = self.month_c.get() + self.days_c.get() + self.ten_days_c.get()+self.years_c.get()
        if check  == 0:
            self.days_c.set(1)
        else:
            self.start_month = "NA"
            self.end_month = "NA"
            self.start_day = self.start_day_temp
            self.end_day = self.end_day_temp
            self.update_variable_list("h2")
            self.update_date_display()
            self.fill_times("day")
    def months(self):
        self.days_c.set(0)
        self.ten_days_c.set(0)
        self.years_c.set(0)
        check = self.month_c.get() + self.days_c.get() + self.ten_days_c.get()+self.years_c.get()
        if check ==0:
            self.month_c.set(1)
        else:
            self.start_month = self.start_month_temp
            self.end_month = self.end_month_temp
            self.start_day = "NA"
            self.end_day = "NA"
            self.update_variable_list("h0")
            self.update_date_display()
            self.fill_times("month")

    def ten_days(self):
        self.days_c.set(0)
        self.month_c.set(0)
        self.years_c.set(0)
        check = self.month_c.get() + self.days_c.get() + self.ten_days_c.get()+self.years_c.get()
        if check==0:
           self.ten_days_c.set(1)
        else:
            self.start_month = "NA"
            self.end_month = "NA"
            self.start_day = self.start_day_temp
            self.end_day = self.end_day_temp
            self.update_variable_list("h1")
            self.update_date_display()
            self.fill_times("day")
    def years(self):
        self.days_c.set(0)
        self.ten_days_c.set(0)
        self.month_c.set(0)
        check = self.month_c.get() + self.days_c.get() + self.ten_days_c.get()+self.years_c.get()
        if check==0:
           self.years_c.set(1)
        else:
            if self.years_c.get() ==1:
                self.start_month = "NA"
                self.end_month = "NA"
                self.start_day = "NA"
                self.end_day = "NA"
                self.update_variable_list("h2")
                self.update_date_display()
                self.fill_times("year")

    def fill_times(self,selection):
        self.start_selection.delete(0, END)
        self.end_selection.delete(0, END)
        self.interval.set(selection)

        if self.interval.get() == "day":
            if self.ten_days_c.get() ==1:
                self.start_selection.insert(END, "Select start day")
                self.end_selection.insert(END, "Select end day")
                for i in range(1,36):
                    self.start_selection.insert(END,str(i*10))
                    self.end_selection.insert(END,str(i*10))
            else:
                self.start_selection.insert(END, "Select start day")
                self.end_selection.insert(END, "Select end day")
                for i in range(1,366):
                    self.start_selection.insert(END, str(i))
                    self.end_selection.insert(END, str(i))

        elif self.interval.get() == "month":
            self.start_selection.insert(END, "Select start month")
            self.end_selection.insert(END, "Select end month")
            for i in range(1,13):
                self.start_selection.insert(END, str(i))
                self.end_selection.insert(END, str(i))
        elif self.interval.get() == "year":
            self.start_selection.insert(END, "Select start year")
            self.end_selection.insert(END, "Select end year")
            for file in os.listdir(self.controller.directory+"/h2"):
                date = file[-19:]
                date = date[:4]
                self.start_selection.insert(END, date)
                self.end_selection.insert(END, date)
    def update_date_display(self):
        self.start.set("start: {}/{}/{}".format(self.start_year,self.start_month,self.start_day))
        self.end.set("end: {}/{}/{}".format(self.end_year,self.end_month,self.end_day))

    def get_ncfile(self,interval):
        file_selected = False
        # select the first file in the directory
        for file_name in os.listdir(self.controller.directory + "/"+interval):
            if not file_selected and file_name.endswith('.nc'):
                file = file_name
                file_selected = True
        self.nc_file = Dataset(self.controller.directory+"/"+interval+"/" + file, mode='r')
    def update_variable_list(self,interval):
        self.get_ncfile(interval)
        self.variable_list.delete(0,END)
        self.all_the_selected_variables.delete(0,END)
        self.selected_variables_list = []
        for variable in self.nc_file.variables.keys():
            if variable not in (self.additional_variables+['time_written','date_written','nsteph','datesec','time_bnds','ndcur','date','time']):
                self.variable_list.insert(END, variable)
    def setFilename(self):
        file_name = askstring("set file name","enter a name for the file to be saved")
        self.saved_file_name.set(file_name)

    def generate_file(self):
        #checking for errors
        if len(self.selected_variables_list)==0:
            self.errorlog_bar.config({"background": "PINK"})
            self.controller.errorlog.set("error log: please first select some variables!!!")

        elif self.saved_file_name.get() == "":
            self.errorlog_bar.config({"background": "PINK"})
            self.controller.errorlog.set("error log: please first configure the name for the file intended to be saved")
        else:
            ###############################################################################
            saving_directory = self.controller.saving_directory    ###                  ###
            try:                                                   ###                  ###
                os.chdir(saving_directory)                         ### checks           ###
            except OSError:                                        ### saving directory ###
                os.chdir(self.controller.current_dir)              ### keeping file     ###
                saving_directory = filedialog.askdirectory()       ### for the          ###
                file = open("saving_directory.txt", 'w')           ### saving directory ###
                file.write(saving_directory)                       ### if not found     ###
                file.close()                                       ### ask for one and  ###
                self.controller.saving_directory = saving_directory### save it          ###
                os.chdir(saving_directory)                         ###                  ###
            ###############################################################################

            #Initiating data manuvuring
            with Dataset(self.saved_file_name.get()+".nc", mode='w', format='NETCDF3_64BIT_OFFSET') as write_data:

                print("initiating dimensions...")

                #inheriting various dimensions from standard file
                write_data.createDimension('lat',96)
                write_data.createDimension('lon', 144)
                write_data.createDimension('slat', 95)
                write_data.createDimension('slon', 144)
                write_data.createDimension('nbnd', 2)
                write_data.createDimension('chars', 8)
                write_data.createDimension('lev', 66)
                write_data.createDimension('ilev', 67)
                write_data.createDimension('time', None)

                ########################
                #adding unit variables #
                ########################
                print("creating unit variables...")
                for var in self.additional_variables:
                    write_data.createVariable(var,np.float64,self.nc_file.variables[var].dimensions)
                #############################

                #assigning value to unit variables created
                for var in self.additional_variables:
                    write_data.variables[var][:] = self.nc_file.variables[var][:]

                #appending their corresponding attributes
                for var in self.additional_variables:
                    for attr in self.nc_file.variables[var].ncattrs():
                        write_data.variables[var].setncattr(attr,self.nc_file.variables[var].getncattr(attr))
            """
            |
            |  doing seperate calculations for separate configurations of intervals:
            |  procedure:
            |
            |  1.iterate through required files,
            |    do concatNAtion
            |  2.append concatNAted variable to new saved file
            |  3.Adding various attributes and dimensions
            |
            """
            #append all the selected variables, piled, to the new file.
            print("appending these variables:",self.selected_variables_list)
            for var_name in self.selected_variables_list:
                    #############################################################################################
                if (self.ten_days_c.get() ==1):#by 10 days
                    #############################################################################################
                    #iterating through required files
                    print("="*40)
                    print(var_name)
                    print("="*40)
                    print("by 10 days...")
                    print("interval: year" + self.start_year+"| day"+self.end_year)
                    print("interval: day" + self.start_day+"| day"+self.end_day)
                    print("iterating through required files")
                    count = 1
                    temp_progress = 0
                    initiated = False
                    years_started= False
                    years_to_end = False
                    day_started = False
                    day_to_end = False
                    day_file_count = 0
                    year_temp = ""
                    startDay = int(self.start_day)/10
                    endDay = int(self.end_day)/10
                    startYear = int(self.start_year)
                    endYear = int(self.end_year)
                    years = endYear - startYear+1
                    days_period = endDay - startDay +1

                    days_dir = self.controller.directory + "/h1/"
                    for file in os.listdir(days_dir):
                        date = file[-19:]
                        year = date[:4]
                        if year != year_temp:
                            day_file_count = 0
                            day_to_end = False
                            day_started = False
                        year_temp = year
                        day_file_count +=1
                        if int(year) == startYear:
                            years_started = True
                        if int(year) == endYear:
                            years_to_end = True
                        if int(day_file_count) == startDay:
                            day_started = True
                        if int(day_file_count) == endDay:
                            day_to_end = True
                        if years_started and day_started :
                            with Dataset(days_dir+file,mode='r') as data:
                                if (initiated):
                                    sum = np.concatenate((sum,data.variables[var_name][:]),axis=0)
                                else:
                                    sum = data.variables[var_name][:]
                                    initiated = True 
                            progress = round(count/(days_period*years),2)*100
                            print(count)
                            print(years*days_period)
                            if progress != temp_progress:
                                print("progress: "+"||"*int(progress/10) + str(progress)+"%")
                            temp_progress = progress
                            count += 1
                        if day_to_end:
                            day_started = False
                        if years_to_end and day_to_end:
                            break
                    #setting the time dimension to be equal to a fixed frame.
                    with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                    ######
                        print("appending concatNAted variable to new data file...")
                        #appending concatNAted variable to new data file/adding datavariables
                        self.get_ncfile("h1")
                        singled_out_variable = self.nc_file.variables[var_name]
                        write_data.createVariable(var_name, np.float32,self.nc_file.variables[var_name].dimensions)
                        
                        ###############################################

                        print("assinging value to variable created...")
                        #assigning value to variable created
                        write_data.variables[var_name][:] = sum

                        print("adding various attributes...")
                        #adding various attributes
                        attrdict = {"Type":"Piled data by 10 days",
                                    "From|To(years)":self.start_year+"|"+self.end_year,
                                    "From|To(days)":self.start_day+"|"+self.end_day,
                                    "period(years)": years,
                                    "period(days)": days_period}
                        for attr in singled_out_variable.ncattrs():
                            attrdict[attr] = singled_out_variable.getncattr(attr)
                        write_data.variables[var_name].setncatts(attrdict)
                    #############################################################################################
                elif (self.days_c.get() ==1):#by days
                    #############################################################################################
                    #iterating through required files
                    print("="*40)
                    print(var_name)
                    print("="*40)
                    print("by days...")
                    print("interval: year" + self.start_year+"| year"+self.end_year)
                    print("interval: day" + self.start_day+"| day"+self.end_day)
                    print("iterating through required files")
                    count = 0
                    temp_progress = 0
                    initiated = False
                    started= False
                    to_end = False
                    startDay = int(self.start_day)
                    endDay = int(self.end_day)+1
                    startYear = int(self.start_year)
                    endYear = int(self.end_year)
                    years = endYear - startYear
                    days_period = endDay - startDay

                    days_dir = self.controller.directory + "/h2/"
                    for file in os.listdir(days_dir):
                        date = file[-19:]
                        date = date[:4]
                        if int(date) == startYear:
                            started = True
                        if int(date) == endYear:
                            to_end = True
                        if started :
                            with Dataset(days_dir+file,mode='r') as data:
                                if (initiated):
                                    sum = np.concatenate((sum,data.variables[var_name][startDay:endDay]),axis=0)
                                else:
                                    sum = data.variables[var_name][startDay:endDay]
                                    initiated = True 
                            progress = round(count/years,2)*100
                            if progress != temp_progress:
                                print("progress: "+"||"*int(progress/10) + str(progress)+"%")
                            temp_progress = progress
                            count += 1
                            if to_end == True:
                                break
                    #setting the time dimension to be equal to a fixed frame.
                    with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                    ######
                        print("appending concatnated variable to new data file...")
                        #appending concatNAted variable to new data file/adding datavariables
                        self.get_ncfile("h2")
                        singled_out_variable = self.nc_file.variables[var_name]
                        write_data.createVariable(var_name, np.float32,self.nc_file.variables[var_name].dimensions)
                        
                        ###############################################

                        print("assinging value to variable created...")
                        #assigning value to variable created
                        print(sum.shape)
                        write_data.variables[var_name][:] = sum

                        print("adding various attributes...")
                        #adding various attributes
                        attrdict = {"Type":"Piled data by days",
                                    "From|To(years)":self.start_year+"|"+self.end_year,
                                    "From|To(days)":self.start_day+"|"+self.end_day,
                                    "period(years)": years,
                                    "period(days)": days_period}
                        for attr in singled_out_variable.ncattrs():
                            attrdict[attr] = singled_out_variable.getncattr(attr)
                        write_data.variables[var_name].setncatts(attrdict)
                    #############################################################################################
                elif self.month_c.get() ==1: #by months
                    #############################################################################################
                    #iterating through required files
                    print("="*40)
                    print(var_name)
                    print("="*40)
                    print("months...")
                    print("interval: year" + self.start_year+"| year"+self.end_year)
                    print("interval: month" + self.start_month+"| month"+self.end_month)
                    print("iterating through required files")
                    count = 1
                    temp_progress = 0
                    initiated = False
                    year_started= False
                    month_started = False
                    year_to_end = False
                    month_to_end = False
                    startYear = int(self.start_year)
                    endYear = int(self.end_year)
                    startMonth = int(self.start_month)
                    endMonth = int(self.end_month)
                    years = endYear - startYear +1
                    months = endMonth - startMonth + 1
                    total_months = years * months

                    months_dir = self.controller.directory + "/h0/"
                    for file in os.listdir(months_dir):
                        date = file[-10:]
                        year = date[:4]
                        month = date[5:7]
                        if int(year) == startYear:
                            year_started = True
                        if int(month) == startMonth:
                            month_started = True
                            month_to_end = False
                        if int(month) == 1:
                            month_to_end = False
                        if int(month) == endMonth:
                            month_to_end = True
                        if int(year) == endYear and month_to_end:
                            year_to_end = True
                        if year_started and month_started:
                            if (initiated):
                                with Dataset(months_dir+file,mode='r') as data:
                                    sum = np.concatenate((sum,data.variables[var_name][:]),axis=0)
                            else:
                                with Dataset(months_dir+file,mode='r') as data:
                                    sum = data.variables[var_name][:]
                                    initiated = True
                            progress = round(count/total_months,2)*100
                            if progress != temp_progress:
                                print("progress: "+"||"*int(progress/10) + str(progress)+"%")
                            temp_progress = progress
                            count +=1
                        if month_to_end == True:
                            month_started = False
                        if year_to_end :
                            break

                    #setting the time dimension to be equal to a fixed frame.
                    with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                    ######
                        print("appending concatNAted variable to new data file...")            
                        #appending concatNAted variable to new data file/adding datavariables            
                        self.get_ncfile("h0")
                        singled_out_variable = self.nc_file.variables[var_name]
                        write_data.createVariable(var_name, np.float32,self.nc_file.variables[var_name].dimensions)
                        ###############################################

                        print("assinging value to variable created...")
                        #assigning value to variable created
                        write_data.variables[var_name][:] = sum                

                        print("adding various attributes...")
                        #adding various attributes
                        attrdict = {"Type":"Piled monthly data",
                                    "From|To(year)":self.start_year+"|"+self.end_year,
                                    "From|To(month)":self.start_month+"|"+self.end_month,
                                    "period(years)": years,
                                    "period(months)":months}
                        for attr in singled_out_variable.ncattrs():
                            attrdict[attr] = singled_out_variable.getncattr(attr)
                        write_data.variables[var_name].setncatts(attrdict)
                    #############################################################################################
                elif self.years_c.get() ==1:
                    #############################################################################################
                    #iterating through required files
                    print("="*40)
                    print(var_name)
                    print("="*40)
                    print("years...")
                    print("interval: year" + self.start_year+"| year"+self.end_year)
                    print("this will take a long time...")
                    print("iterating through required files")
                    count = 1
                    temp_progress = 0
                    initiated = False
                    started= False
                    to_end = False
                    startYear = int(self.start_year)
                    endYear = int(self.end_year)
                    years = endYear - startYear
                    years_dir = self.controller.directory + "/h2/"
                    for file in os.listdir(years_dir):
                        date = file[-19:]
                        year = date[:4]
                        if int(year) == startYear:
                            started = True
                        if int(year) == endYear:
                            to_end = True
                        if started:
                            with Dataset(years_dir+file,mode='r') as data:
                                if (initiated):
                                    sum = np.concatenate((sum,data.variables[var_name][:]),axis=0)
                                else:
                                    sum = data.variables[var_name][:]
                                    initiated = True
                            progress = round(count/years,2)*100
                            if progress != temp_progress:
                                print("progress: "+"||"*int(progress/10) + str(progress)+"%")
                            temp_progress = progress
                            count +=1
                        if to_end == True:
                            break
                    #setting the time dimension to be equal to a fixed frame.
                    with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                    ######
                        print("appending concatNAted variable to new data file...")                     
                        #appending concatNAted variable to new data file/adding datavariables            
                        self.get_ncfile("h2")
                        singled_out_variable = self.nc_file.variables[var_name]
                        dimension =  singled_out_variable.dimensions
                        write_data.createVariable(var_name, np.float32,dimension)
                        ###############################################

                        print("assigning value to variable created...")
                        #assigning value to variable created
                        write_data.variables[var_name][:] = sum

                        print("adding various attributes...")
                        #adding various attributes
                        attrdict = {"Type":"Piled yearly data",
                                    "From|To":self.start_year+"|"+self.end_year,
                                    "period(years)":years}
                        for attr in singled_out_variable.ncattrs():
                            attrdict[attr] = singled_out_variable.getncattr(attr)
                        write_data.variables[var_name].setncatts(attrdict)

                    #############################################################################################
            print("done!")
            self.controller.popup("Success!", "file :'"+self.saved_file_name.get()+"' successfully saved at: " + saving_directory)
            self.errorlog_bar.config({"background": "WHITE"})
            self.controller.errorlog.set("errorlog :")
            self.variable_desc.delete(0,END)
            os.chdir(self.controller.directory)

    # def saveFilename(self):
    #     if(self.save_file_name != ""):
    #         self.window.destroy()
    #         self.name_not_set = False
    #         print("saving...")
    #     else:
    #         print("notsaving...entry empty")
    #         pass
    # def cancel(self):
    #     self.name_not_set = False
    #     self.exit = True
    #     self.window.destroy()
    #     print("exiting...")
    # def askForFilename(self):
    #     self.window = tk.Tk()
    #     self.window.wm_title("enter a file name")
    #     label = Label(self.window,text="please enter a file name:").pack(side="top")
    #     entry = Entry(self.window,textvariable=self.save_file_name).pack()
    #     save = Button(self.window,text="save",command=self.saveFilename).pack()
    #     cancel = Button(self.window,text="cancel",command=self.cancel).pack()
    #     self.window.mainloop()
class HelpPage(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        message = Label(self,text="this feature is currently in development :P")
if __name__ == "__main__":
    data = Data_interface()
    data.mainloop()