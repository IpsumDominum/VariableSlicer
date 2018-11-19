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
sys.setrecursionlimit(5000)



LARGE_FONT = ("Helvatica",15)
SMALL_FONT = ("Verdana",10)
MEDIUM_FONT = ("Verdana",12)


class Data_interface(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args,**kwargs)
        self.geometry("600x400")
        self.directory = ""
        self.saving_directory = ""
        self.current_dir = os.getcwd()
        self.not_saved = True

        tk.Tk.wm_title(self, "Data_interface 2018")
        container = tk.Frame(self)
        container.pack(side="top",fill="both",expand = True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        #all the frames pages
        self.frames = {}
        for F in (StartPage, MainPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0, column = 0, sticky="nsew")

        #menu
        menu = Menu(self)
        files = Menu(menu)
        files.add_command(label="configure", command=lambda:self.show_frame(StartPage))
        files.add_command(label="set saving directory", command=lambda: self.set_save_directory())
        menu.add_cascade(label="files", menu=files)
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
        label = ttk.Label(pop,text=message,font=SMALL_FONT)
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
        self.directory_show = Entry(frame2_2_1, width = 80,textvariable=self.selected_directory).pack(side=LEFT)


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

        self.show_saving_dir = Entry(frame2_2_2, width=80,textvariable = self.saving_directory).grid(row=1,column=0)

        #ready button
        self.ready = ttk.Button(frame2_2_2,text="ready", command= self.ready).grid(row=1,column=1)

    def browse_button(self):
        # Allow user to select a directory and store it in global
        directory = filedialog.askdirectory()
        self.controller.directory = directory
        self.selected_directory.set("dataset directory: "+ directory)
        os.chdir(directory)
    def ready(self):
        try:
            file_selected = False
            #select the first file in the directory
            for file_name in os.listdir(self.controller.directory+"\\h0"):
                if not file_selected and file_name.endswith('.nc'):
                    file = file_name
                    file_selected = True
            self.nc_file = Dataset("h0\\"+file,mode='r')
            self.controller.show_frame(MainPage)
            self.nc_file.close()
        except FileNotFoundError:
            self.controller.popup("Error","please set a valid directory containing\n h0, h1, and h2 \n files")
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
        self.time_interval = ["10 days","months","years"]
        self.controller = controller
        self.path_name = ""
        self.var_shape = ()
        self.var_name = ""
        self.start_date = ""
        self.end_date = ""


        #making frames
        frame1 = ttk.Frame(self)
        frame1.grid(row=0,column=0)
        self.frame2 = ttk.Frame(self)
        self.frame2.grid(row=0,column=1)
        self.frame3 = ttk.Frame(self)
        self.frame3.grid(row=0,column=2)

        ################################
        #Show the variables in the file#
        ################################
        self.variable_list = Listbox(frame1,width='50',selectmode=BROWSE,exportselection=0)
        self.variable_list.grid(row=0,column=0,sticky="nsew")
        self.variable_list.bind("<Double-Button-1>", self.OnVarSelect)
        scroll1y = tk.Scrollbar(frame1, orient=tk.VERTICAL, command=self.variable_list.yview)
        scroll1y.grid(row=0, column=1, sticky='nsw')
        self.variable_list['yscrollcommand'] = scroll1y.set
        self.variable_desc = Listbox(frame1, width='50', selectmode=BROWSE, exportselection=0)
        self.variable_desc.grid(row=2, column=0,sticky="nsew")
        scrollvy = tk.Scrollbar(frame1, orient=tk.VERTICAL, command=self.variable_desc.yview)
        scrollvy.grid(row=2, column=1, sticky='nsw')
        self.variable_label = Label(frame1, text="Variables")
        self.variable_label.grid(row=1, column=0)

        ####################
        #select time period#
        ####################
        self.interval.set("Select a time interval")
        self.interval_selection = OptionMenu(self.frame2,self.interval,*self.time_interval,command=self.fill_times).grid(row=0,column=0)

        #making the selection option boxes

        #start selection
        self.start_selection = Listbox(self.frame2,selectmode=BROWSE,exportselection=0)
        self.start_selection.grid(row=1,column=0)
        self.start_selection.insert(END, "Start time Selection")
        self.start_selection.bind("<Double-Button-1>", self.select_start)
        scrollsy = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.start_selection.yview)
        scrollsy.grid(row=1, column=1, sticky='nsw')
        self.start_selection['yscrollcommand'] = scrollsy.set

        #end selection
        self.end_selection = Listbox(self.frame2,selectmode=BROWSE,exportselection=0)
        self.end_selection.grid(row=2,column= 0)
        self.end_selection.insert(END, "End time Selection")
        self.end_selection.bind("<Double-Button-1>", self.select_end)
        scrolley = tk.Scrollbar(self.frame2, orient=tk.VERTICAL, command=self.end_selection.yview)
        scrolley.grid(row=2, column=1, sticky='nsw')
        self.end_selection['yscrollcommand'] = scrolley.set

        #showing the selected dates
        self.start_show = Entry(self.frame3,textvariable=self.start).grid(row=0,column=0)
        self.end_show = Entry(self.frame3, textvariable=self.end).grid(row=1,column=0)
        self.start.set("start: ")
        self.end.set("end: ")

        #save button
        self.save = Button(self.frame3, text="save",command = self.generate_file).grid(row=4,column=0)
        self.file_name_label = Label(self.frame3, text="file name:").grid(row=3,column=0)
        self.file_name = Entry(self.frame3,textvariable = self.saved_file_name).grid(row=3,column=0)
        self.set_save_name = Button(self.frame3, text="set file name",command=self.setFileName).grid(row=2,column=0)

    def OnVarSelect(self,event):
        self.variable_desc.delete(0,END)
        widget = event.widget
        self.var_name = widget.get(widget.curselection()[0])
        variable = self.nc_file.variables[self.var_name]
        self.var_shape = variable[0].shape
        attributes = variable.ncattrs()
        self.variable_desc.insert(END,str(variable.name))
        for attr in attributes:
            self.variable_desc.insert(END,str(attr)+": "+str(variable.getncattr(attr)))
    def select_start(self,event):
        widget = event.widget
        curselection = widget.get(widget.curselection()[0])
        self.start.set("start: "+curselection)
        self.start_date = curselection

    def select_end(self,event):
        widget = event.widget
        curselection = widget.get(widget.curselection()[0])
        self.end.set("end: "+curselection)
        self.end_date = curselection

    def fill_times(self,selection):
        self.start_selection.delete(0, END)
        self.end_selection.delete(0, END)
        self.start_selection.insert(END, "Start time Selection")
        self.end_selection.insert(END, "End time Selection")
        self.interval.set(selection)
        if self.interval.get() == "10 days":
            self.get_ncfile("h1")
            for file in os.listdir(self.controller.directory+"/h1"):
                date = file[-19:]
                date = date[:10]
                self.start_selection.insert(END,date)
                self.end_selection.insert(END,date)

        elif self.interval.get() == "months":
            self.get_ncfile("h0")
            for file in os.listdir(self.controller.directory+"/h0"):
                date = file[-10:]
                date = date[:7]
                self.start_selection.insert(END, date)
                self.end_selection.insert(END, date)
        elif self.interval.get() == "years":
            self.get_ncfile("h2")
            for file in os.listdir(self.controller.directory+"/h2"):
                date = file[-19:]
                date = date[:10]
                self.start_selection.insert(END, date)
                self.end_selection.insert(END, date)

    def generate_file(self):
        if self.var_name =="":
            self.controller.popup("error","please first select a variable!!!")
        elif self.start_date == "" or self.start_date == "Start time Selection" or  self.end_date == "" or self.end_date == "End time Selection" or (len(self.start_date) != len(self.end_date)):
            self.controller.popup("error", "please select valid both start and end times")
        elif self.saved_file_name.get() == "":
            self.controller.popup("error","please first configure the name for the file intended to be saved")
        else:
            saving_directory = self.controller.saving_directory
            try:
                os.chdir(saving_directory)
            except OSError:
                os.chdir(self.controller.current_dir)
                saving_directory = filedialog.askdirectory()
                file = open("saving_directory.txt", 'w')
                file.write(saving_directory)
                file.close()
                self.controller.saving_directory = saving_directory
                os.chdir(saving_directory)  

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

                ########################
                #adding unit variables #
                ########################
                print("creating unit variables...")
                write_data.createVariable('lat',np.float64,self.nc_file.variables['lat'].dimensions)
                write_data.createVariable('lon',np.float64,self.nc_file.variables['lon'].dimensions)
                write_data.createVariable('lev',np.float64,self.nc_file.variables['lev'].dimensions)
                #############################

                #assigning value to unit variables created
                variables = ['lat','lon','lev']
                for var in variables:
                    write_data.variables[var][:] = self.nc_file.variables[var][:]

                #appending their corresponding attributes
                for var in variables:
                    for attr in self.nc_file.variables[var].ncattrs():
                        write_data.variables[var].setncattr(attr,self.nc_file.variables[var].getncattr(attr))


            """
            |
            |  doing seperate calculations for separate configurations of intervals:
            |  procedure:
            |
            |  1.iterate through required files,
            |    do concatnation
            |  2.append concatnated variable to new saved file
            |  3.Adding various attributes and dimensions
            |
            """
                #############################################################################################
            if self.interval.get() == "10 days":
                #############################################################################################
                #iterating through required files
                print("10 days...")
                print("iterating through required files")
                count = 0
                temp_progress = 0
                initiated = False
                started= False
                to_end = False
                years = int(self.end_date[:4]) - int(self.start_date[:4])
                months = int(self.end_date[5:7])- int(self.start_date[5:7])
                days = int(self.end_date[8:10])
                total_days = years*365 + months *30 + days
                days_dir = self.controller.directory + "/h1/"
                for file in os.listdir(days_dir):
                    date = file[-19:]
                    date = date[:10]
                    if date == self.start_date:
                        started = True
                    if date == self.end_date:
                        to_end = True
                    if started :
                        with Dataset(days_dir+file,mode='r') as data:
                            if (initiated):
                                sum = np.concatenate((sum,data.variables[self.var_name][:]),axis=0)
                            else:
                                sum = data.variables[self.var_name][:]
                                initiated = True 
                        count += 1
                        progress = round(count/total_days,2)*1000
                        if progress != temp_progress:
                            print("progress: "+"||"*int(progress/10) + str(progress)+"0%")
                        temp_progress = progress
                        if to_end == True:
                            break
                #setting the time dimension to be equal to a fixed frame.
                with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                ######
                    write_data.createDimension('time', count)

                    print("appending concatnated variable to new data file...")
                    #appending concatnated variable to new data file/adding datavariables
                    self.get_ncfile("h0")
                    singled_out_variable = self.nc_file.variables[self.var_name]
                    write_data.createVariable(self.var_name, np.float32,self.nc_file.variables[self.var_name].dimensions)
                    
                    ###############################################

                    print("assinging value to variable created...")
                    #assigning value to variable created
                    write_data.variables[self.var_name][:] = sum

                    print("adding various attributes...")
                    #adding various attributes
                    attrdict = {"Type":"Piled data by 10 days",
                                "From|To":self.start_date+"|"+self.end_date,
                                "Total_days":total_days}
                    for attr in singled_out_variable.ncattrs():
                        attrdict[attr] = singled_out_variable.getncattr(attr)
                    write_data.variables[self.var_name].setncatts(attrdict)
                #############################################################################################
            elif self.interval.get() == "months":
                #############################################################################################
                #iterating through required files
                print("months...")
                print("iterating through required files")
                count = 0
                initiated = False
                started= False
                to_end = False
                years = int(self.end_date[:4]) - int(self.start_date[:4])
                months = int(self.end_date[5:7])- int(self.start_date[5:7])
                total_months = years*12 + months
                months_dir = self.controller.directory + "/h0"
                for file in os.listdir(months_dir):
                    date = file[-10:]
                    date = date[:7]
                    if date == self.start_date:
                        started = True
                    if date == self.end_date:
                        to_end = True
                    if started:
                        with Dataset(months_dir+file,mode='r') as data:
                            if (initiated):
                                sum = np.concatenate((sum,data.variables[self.var_name][:]),axis=0)
                            else:
                                sum = data.variables[self.var_name][:]
                                initiated = True 
                        count +=1
                        progress = round(count/total_days,2)*100
                        if progress != temp_progress:
                            print("progress: "+"||"*int(progress) + str(progress)+"0%")
                        temp_progress = progress
                        if to_end == True:
                            break
                #setting the time dimension to be equal to a fixed frame.
                with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                ######
                    write_data.createDimension('time', count)

                    print("appending concatnated variable to new data file...")            
                    #appending concatnated variable to new data file/adding datavariables            
                    self.get_ncfile("h1")
                    singled_out_variable = self.nc_file.variables[self.var_name]
                    write_data.createVariable(self.var_name, np.float32,self.nc_file.variables[self.var_name].dimensions)
                    ###############################################

                    print("assinging value to variable created...")
                    #assigning value to variable created
                    write_data.variables[self.var_name][:] = sum

                    print("adding various attributes...")
                    #adding various attributes
                    attrdict = {"Type":"Piled monthly data",
                                "From|To":self.start_date+"|"+self.end_date,
                                "Total_months":total_months}
                    for attr in singled_out_variable.ncattrs():
                        attrdict[attr] = singled_out_variable.getncattr(attr)
                    write_data.variables[self.var_name].setncatts(attrdict)
                #############################################################################################
            elif self.interval.get() == "years":
                #############################################################################################
                #iterating through required files
                print("years...")
                print("iterating through required files")
                count = 0
                initiated = False
                started= False
                to_end = False
                years = int(self.end_date[:4]) - int(self.start_date[:4])
                years_dir = self.controller.directory + "/h2/"
                for file in os.listdir(years_dir):
                    date = file[-19:]
                    date = date[:10]
                    if date == self.start_date:
                        started = True
                    if date == self.end_date:
                        to_end = True
                    if started:
                        with Dataset(years_dir+file,mode='r') as data:
                            if (initiated):
                                sum = np.concatenate((sum,data.variables[self.var_name][:]),axis=0)
                            else:
                                sum = data.variables[self.var_name][:]
                                initiated = True 
                        data.close()
                        count +=1
                        progress = round(count/total_days,2)*100
                        if progress != temp_progress:
                            print("progress: "+"||"*int(progress) + str(progress)+"%")
                        temp_progress = progress
                        if to_end == True:
                            break
                #setting the time dimension to be equal to a fixed frame.
                with Dataset(self.saved_file_name.get()+".nc", mode='r+') as write_data:
                ######
                    write_data.createDimension('time', count)

                    print("appending concatnated variable to new data file...")                     
                    #appending concatnated variable to new data file/adding datavariables            
                    self.get_ncfile("h2")
                    singled_out_variable = self.nc_file.variables[self.var_name]
                    dimension =  singled_out_variable.dimensions
                    write_data.createVariable(self.var_name, np.float32,dimension)
                    ###############################################

                    print("assinging value to variable created...")
                    #assigning value to variable created
                    write_data.variables[self.var_name][:] = sum

                    print("adding various attributes...")
                    #adding various attributes
                    attrdict = {"Type":"Piled yearly data",
                                "From|To":self.start_date+"|"+self.end_date,
                                "Total_years":years}
                    for attr in singled_out_variable.ncattrs():
                        attrdict[attr] = singled_out_variable.getncattr(attr)
                    write_data.variables[self.var_name].setncatts(attrdict)

                #############################################################################################
            print("done!")
            self.controller.popup("Success!", "file :'"+self.saved_file_name.get()+"' successfully saved at: " + saving_directory)
            os.chdir(self.controller.directory)

    def get_ncfile(self,interval):
        file_selected = False
        self.variable_list.delete(0,END)
        # select the first file in the directory
        for file_name in os.listdir(self.controller.directory + "/"+interval):
            if not file_selected and file_name.endswith('.nc'):
                file = file_name
                file_selected = True
        self.nc_file = Dataset(self.controller.directory+"/"+interval+"/" + file, mode='r')
        for variable in self.nc_file.variables.keys():
            self.variable_list.insert(END, variable)
    def setFileName(self):
        file_name = askstring("set file name","enter a name for the file to be saved")
        self.saved_file_name.set(file_name)
    # def saveFileName(self):
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
    #     save = Button(self.window,text="save",command=self.saveFileName).pack()
    #     cancel = Button(self.window,text="cancel",command=self.cancel).pack()
    #     self.window.mainloop()
if __name__ == "__main__":
    data = Data_interface()
    data.mainloop()