#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 23:55:35 2022

@author: tzework
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import numpy as np
import os
import sys
from DB.optical_data_db import ODB_class

class container():
    pass

class StoreData():
    def __init__(self):
        self.db=container();
        
        self.sDBname='Database_for_optical_data.db'
        self.root = tk.Tk()
        self.root.geometry("1000x600")
        self.root.title("App for creating or filling optical data database")
        self.init_mainframe()
        self.init_dbchoice()
        try:
            (self.seplist,self.dbdirectory,self.filedirectory)=self.check_ini()
        except:
            self.seplist=['\t',' ',',']
            self.dbdirectory='Documents'
            self.filedirectory='Documents'
            self.write_to_ini()
            
    def check_ini(self):
        with open(os.path.join(os.path.dirname(__file__),'dbconfig.ini'), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split('=')
                if tmp[0]=='seplist':            
                    seplist=tmp[-1].split("\\")
                if tmp[0]=='database_path':
                    dbdirectory=tmp[-1]
                if tmp[0]=='datafiles_path':
                    filedirectory=tmp[-1]
            return (seplist,dbdirectory,filedirectory)
            
    def write_to_ini(self):
        write=[]
        text=self.Add_items('seplist=',self.seplist,'\\')
        write.append(text)
        write.append('database_path='+self.dbdirectory)
        write.append('datafiles_path='+self.filedirectory)
        with open(os.path.join(os.path.dirname(__file__),'dbconfig.ini'),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            
    def Add_items(self,text,itemlist,sep):
        for item in itemlist:
            text=text+str(item)+sep
        return text[:-1]
    
    def init_mainframe(self):
        self.mainframe = tk.Frame(self.root)
        self.mainframe.grid(column=0,row=0)
        self.mainframe.columnconfigure(0, weight = 1)
        self.mainframe.rowconfigure(0, weight = 1)
        self.mainframe.pack(pady = 50, padx = 50)
        #self.error=tk.StringVar()
        self.errormsg=tk.StringVar()
        self.errormsg.set('\n')
        #self.elb=tk.Label(self.mainframe, textvariable=self.error, fg='#f00')
        #self.elb.grid(row = 0, column = 1)
        self.emlb=tk.Label(self.mainframe, textvariable=self.errormsg, fg='#f00')
        self.emlb.grid(row = 0, column = 1)
        
        
    def init_dbchoice(self): 
        textlbl=tk.Label(self.mainframe, text="Choose an existing data base with\noptical data or create a new one:", borderwidth=2,relief=tk.GROOVE,width=30)
        textlbl.grid(row = 1, column = 1, columnspan=3)
        
        
        oldDB=tk.Button(self.mainframe, text="Open DB", command=self.Get_DB,width=12)
        oldDB.grid(row=2,column=1)
        
        
        newDB=tk.Button(self.mainframe, text="Create new DB", command=self.Create_DB,width=12)
        newDB.grid(row=2,column=3)
        
    def Placeholder(self):
        pass
    
    def init_start(self):
        self.root.mainloop()

    def End(self):
        self.conn.close()
        self.root.destroy()
        sys.exit()
        
    def Back(self):
        self.conn.close()
        self.mainframe.destroy()
        self.init_mainframe()
        self.init_dbchoice()
        
    def Get_tables(self,cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables=[v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
        return tables
        
    def Get_DB(self):
        self.gDBname = askopenfilename(title="Select database.", initialdir=self.dbdirectory, filetypes=[("Database files","*.db *.db3 *.sqlite *.sqlite3")])
        if self.gDBname:
            self.dbdirectory=os.path.dirname(self.gDBname)
            (sep,dbdir,filedir)=self.check_ini()
            if self.dbdirectory!=dbdir:
                self.write_to_ini()
            self.conn,self.errorDB=ODB_class().make_connection(self.gDBname)
            if self.errorDB!='':
                #self.error.set('Error:')
                self.errormsg.set(self.errorDB)
            else:
                self.errorDB=ODB_class().table_test(self.conn)
                if self.errorDB!='':
                    #self.error.set('Error:')
                    self.errormsg.set(self.errorDB)
                else:
                    self.init_mat_window()
        else:
            pass
        
    def Create_DB(self):
        self.sDBname = asksaveasfilename(title="Select the folder to save database.", initialdir=self.dbdirectory,filetypes=[("Database files","*.db *.db3 *.sqlite *.sqlite3")],initialfile=self.sDBname)
        if self.sDBname:
            self.dbdirectory=os.path.dirname(self.sDBname)
            (sep,dbdir,filedir)=self.check_ini()
            if self.dbdirectory!=dbdir:
                self.write_to_ini()
            self.conn,self.errorDB=ODB_class().make_connection(self.sDBname)
            if self.errorDB!='':
                #self.error.set('Error:')
                self.errormsg.set(self.errorDB)
            else:
                ODB_class().create_DB(self.conn)
                self.init_mat_window()
        else:
            pass
    
    def add_buttons(self):
        self.back=tk.Button(self.mainframe, text="Go Back", command=self.Back, width=12)
        self.back.grid(row=5,column=3, sticky='N')
        self.finish=tk.Button(self.mainframe, text="FINISH", command=self.End, width=12)
        self.finish.grid(row=5,column=4, sticky='N')
        self.deletemat=tk.Button(self.mainframe, text="Delete\nmaterial(s)", command=self.Del_Material, width=12)
        self.deletemat.grid(row=4,column=4, sticky='S')
        self.deletemat.configure(state='disabled')
        self.datafile=tk.Button(self.mainframe, text="Add data\nfrom a file", command=self.Get_file,width=12)
        self.datafile.grid(row=4,column=3, sticky='S')
        
    def init_mat_window(self):
        #self.error.set('')
        self.errormsg.set('\n')
        self.mainframe.destroy()
        self.init_mainframe()
        self.Material_list()
        self.add_buttons()
        self.List_of_materials()
        
    def adjust_string_length(self, data):
        new_data=[[str(ele) for ele in row] for row in data]
        cmax=[[len(ele) for ele in row] for row in new_data]
        cmax=[max(ele) for ele in zip(*cmax)]
        for rows in new_data:
            for idx in range(0,len(rows)):
                rows[idx]=rows[idx].ljust(cmax[idx])
        return new_data
    
    def Material_list(self):
        #self.labeltext=tk.StringVar(self.mainframe)
        label=tk.Label(self.mainframe, text='Materials stored in database', font='Courier', borderwidth=2,relief=tk.GROOVE, width=45)
        label.grid(row=1,column=1)
        self.titlebox=tk.Listbox(self.mainframe, font='Courier',width=45,height=1)
        self.titlebox.grid(row = 3, column = 1)
        #label=tk.Label(self.mainframe, textvariable=self.labeltext, font='Courier', borderwidth=2,relief=tk.GROOVE)
        #label.grid(row = 1, column=1)
        self.listbox=tk.Listbox(self.mainframe, font='Courier', selectbackground='red', selectmode='extended',width=45)#https://stackoverflow.com/questions/51376597/how-can-i-shift-select-multiple-items-in-tkinter-listbox
        self.listbox.grid(row = 4, column = 1, rowspan=3)
        self.xscrollbar=tk.Scrollbar(self.mainframe,orient='horizontal')
        self.xscrollbar.grid(row = 2, column = 1, sticky='WE')
        self.yscrollbar=tk.Scrollbar(self.mainframe)
        self.yscrollbar.grid(row = 4, column = 2, rowspan=3, sticky='NS')
        self.listbox.config(yscrollcommand = self.yscrollbar.set)
        self.listbox.config(xscrollcommand = self.xscrollbar.set)
        self.titlebox.config(xscrollcommand = self.xscrollbar.set)
        self.yscrollbar.config(command = self.listbox.yview)
        self.xscrollbar.config(command = self.OnVsb)
# =============================================================================
#         https://stackoverflow.com/questions/4066974/scrolling-multiple-tkinter-listboxes-together
# =============================================================================
    def OnVsb(self, *args):
        self.titlebox.xview(*args)
        self.listbox.xview(*args)
        
        
        
    def List_of_materials(self):
        try:
            self.titlebox.delete(0,tk.END)
            self.listbox.delete(0,tk.END)
            self.listindex=[]
            self.deletemat.configure(state='disabled')
        except:
            pass
        data=ODB_class().get_materials(self.conn)
        if data!=[]:
            data.insert(0,('Name','Range','','Unit','Data Pts.','ID'))
            string_data=self.adjust_string_length(data)
            #self.labeltext.set('Materials stored in database.\n'+string_data[0][0]+' | '+string_data[0][1]+'   '+string_data[0][2]+' | '+string_data[0][3]+' | '+string_data[0][4])
            self.titlebox.insert(0,string_data[0][0]+' | '+string_data[0][1]+'   '+string_data[0][2]+' | '+string_data[0][3]+' | '+string_data[0][4])
            for rows in string_data[1:]:
                string=rows[0]+' | '+rows[1]+' - '+rows[2]+' | '+rows[3]+' | '+rows[4]
                self.listbox.insert(rows[-1], string)
                self.listindex.append(rows[-1])
            #self.listbox.configure(width=len(string))
            self.mainframe.update()
            self.deletemat.configure(state='normal')
        else:
            #self.labeltext.set('Materials stored in database.\n Name | Range | Units | No. Entries')
            self.titlebox.insert(0,'Name | Range | Unit | Data Pts.')
            #self.listbox.configure(width=len(' Name | Range | Units | No. Entries'))
        
        
    def Del_Material(self):
        for item in self.listbox.curselection():
            ODB_class().delete_from_materials(self.conn,self.listindex[item])
        self.List_of_materials()
            
    def Get_file(self):
        #self.error.set('')
        self.errormsg.set('\n')
        self.filename = askopenfilename(title="Select database.", initialdir=self.filedirectory, filetypes=[("Optical data file","*txt")])
        if self.filename:
            self.filedirectory=os.path.dirname(self.filename)
            (sep,dbdir,filedir)=self.check_ini()
            if self.filedirectory!=filedir:
                self.write_to_ini()
            #https://learnandlearn.com/python-programming/python-how-to/python-function-arguments-mutable-and-immutable
            #If the contents of the list are primitive data types, you can use a comprehension
            #new_list = [i for i in old_list]
            #You can nest it for multidimensional lists like:
            #new_grid = [[i for i in row] for row in grid]
            #https://stackoverflow.com/questions/17873384/how-to-deep-copy-a-list
            #deep copy of a list
            seplist=[item for item in self.seplist]
            self.find_sep(seplist)
            if self.errormsg.get()=='\n':
                if np.shape(self.data)[1]!=3:
                    #self.error.set('Error:')
                    self.errormsg.set("Data in file doesn't\nseem to be optical data.")
                else:
                    self.process_data()
                    if self.errormsg.get()=='\n':
                        matname=os.path.splitext(os.path.basename(self.filename))[0]
                        self.errorDB,self.mat_id=ODB_class().insert_into_materials(self.conn,(matname,self.data[0,0],self.data[-1,0],self.unit,np.shape(self.data)[0]))
                        if self.errorDB!='':
                            #self.error.set('Error:')
                            self.errormsg.set(self.errorDB)
                        else:
                            self.pause()
                            ODB_class().insert_into_data(self.conn,self.data,self.mat_id)
                            self.List_of_materials()
                            self.endpause()
    
    def pause(self):
        self.finish.configure(state='disabled')
        self.back.configure(state='disabled')
        self.datafile.configure(state='disabled')
        self.errormsg.set("Data is being stored!\nDon't click on the buttons.")
        try:
            self.deletemat.configure(state='disabled')
        except:
            pass
        self.mainframe.update()#to enforce an update to mainframe
        
    def endpause(self):
        self.errormsg.set('\n')
        self.finish.configure(state='normal')
        self.back.configure(state='normal')
        self.datafile.configure(state='normal')
        try:
            self.deletemat.configure(state='normal')
        except:
            pass
        self.mainframe.update()#to enforce an update to mainframe
        
    #reccursive approach to find separator
    def find_sep(self,seplist):
        if len(seplist)==0:
            self.data=np.array([])
            #self.error.set('Error:')
            self.errormsg.set("Data in file cannot\nbe properly read.")
        else:
            with open(self.filename, 'r') as f:
                tmp=[]
                for line in f:
                    a=line.strip()
                    tmp.append(a.split(seplist[-1]))
                try:
                    data=[[float(y) for y in x] for x in tmp[1:]]
                    self.data=np.array(data)
                    self.header=tmp[0]
                except:
                    seplist.pop(-1)
                    self.find_sep(seplist)
                    
    def process_data(self):
        tmp=np.empty(self.data.shape)
        if 'n' in self.header and 'k' in self.header and ('m' in self.header or 'mm' in self.header or 'nm' in self.header or '\u03BCm' in self.header):#data file should contain three columns labeled with unit of wavelength n and k unit of wavelegnth can only be m, mm, nm and \u03BCm
            for i in range(0,len(self.header)):
                if self.header[i]!='n' and self.header[i]!='k':
                    self.unit=self.header[i]
                    tmp[:,0]=self.data[:,i]
                if self.header[i]=='n':
                    tmp[:,1]=self.data[:,i]
                if self.header[i]=='k':
                    tmp[:,2]=self.data[:,i]
            self.data=tmp[tmp[:,0].argsort()]
        else:
            #self.error.set('Error:')
            self.errormsg.set("Data file should contain\n wlength, n, k columns.")
    
if __name__=='__main__':
    StoreData.init_start(StoreData())