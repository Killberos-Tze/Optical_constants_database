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
        self.error=tk.StringVar()
        self.errormsg=tk.StringVar()
        self.elb=tk.Label(self.mainframe, textvariable=self.error, fg='#f00')
        self.elb.grid(row = 0, column = 1)
        self.emlb=tk.Label(self.mainframe, textvariable=self.errormsg, fg='#f00')
        self.emlb.grid(row = 0, column = 3)
        
        
    def init_dbchoice(self): 
        textlbl=tk.Label(self.mainframe, text="Choose an existing data base with\noptical data or create a new one:", borderwidth=2,relief=tk.GROOVE)
        textlbl.grid(row = 1, column = 1, columnspan=3)
        
        
        oldDB=tk.Button(self.mainframe, text="Open DB", command=self.Get_DB)
        oldDB.grid(row=2,column=1)
        
        
        newDB=tk.Button(self.mainframe, text="Create new DB", command=self.Create_DB)
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
                self.error.set('Error:')
                self.errormsg.set(self.errorDB)
            else:
                self.errorDB=ODB_class().table_test(self.conn)
                if self.errorDB!='':
                    self.error.set('Error:')
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
                self.error.set('Error:')
                self.errormsg.set(self.errorDB)
            else:
                ODB_class().create_DB(self.conn)
                self.init_mat_window()
        else:
            pass
    
    def add_buttons(self):
        self.back=tk.Button(self.mainframe, text="Go Back", command=self.Back)
        self.back.grid(row=5,column=1, sticky='E')
        self.finish=tk.Button(self.mainframe, text="FINISH", command=self.End)
        self.finish.grid(row=5,column=3, sticky='W')
        
    def init_mat_window(self):
        self.error.set('')
        self.errormsg.set('')
        self.mainframe.destroy()
        self.init_mainframe()
        self.Material_list()
        self.List_of_materials()
        self.Add_material()
        self.add_buttons()
    
    def adjust_string_length(self, data):
        new_data=[[str(ele) for ele in row] for row in data]
        cmax=[[len(ele) for ele in row] for row in new_data]
        cmax=[max(ele) for ele in zip(*cmax)]
        for rows in new_data:
            for idx in range(0,len(rows)):
                rows[idx]=rows[idx].ljust(cmax[idx])
        return new_data
    
    def Material_list(self):
        self.labeltext=tk.StringVar(self.mainframe)
        label=tk.Label(self.mainframe, textvariable=self.labeltext, font='Courier', borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=1)
        self.listbox=tk.Listbox(self.mainframe, font='Courier', selectbackground='red', selectmode='multiple')
        self.listbox.grid(row = 2, column = 1, rowspan=3)
        self.scrollbar=tk.Scrollbar(self.mainframe)
        self.scrollbar.grid(row = 2, column = 2, rowspan=3, sticky='NS')
        self.listbox.config(yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.listbox.yview)
        
    def Add_material(self):
        textlbl=tk.Label(self.mainframe, text="Choose a file with data\nto store in database:", borderwidth=2,relief=tk.GROOVE)
        textlbl.grid(row = 1, column = 3)
        self.datafile=tk.Button(self.mainframe, text="Open File", command=self.Get_file)
        self.datafile.grid(row=2,column=3, sticky='N')
        
    def List_of_materials(self):
        try:
            self.listbox.delete(0,tk.END)
            self.listindex=[]
            self.deletemat.destroy()
            self.textldel.destroy()
        except:
            pass
        data=ODB_class().get_materials(self.conn)
        if data!=[]:
            data.insert(0,('Name','Range','','Units','No. Entries','ID'))
            string_data=self.adjust_string_length(data)
            self.labeltext.set('Materials stored in database.\n'+string_data[0][0]+' | '+string_data[0][1]+'   '+string_data[0][2]+' | '+string_data[0][3]+' | '+string_data[0][4])
            for rows in string_data[1:]:
                string=rows[0]+' | '+rows[1]+' - '+rows[2]+' | '+rows[3]+' | '+rows[4]
                self.listbox.insert(rows[-1], string)
                self.listindex.append(rows[-1])
            self.listbox.configure(width=len(string))
            self.mainframe.update()
            self.add_delete()
        else:
            self.labeltext.set('Materials stored in database.\n Name | Range | Units | No. Entries')
            self.listbox.configure(width=len(' Name | Range | Units | No. Entries'))
            
    def add_delete(self):
        self.textldel=tk.Label(self.mainframe, text="Delete selected\n material(s):", borderwidth=2,relief=tk.GROOVE)
        self.textldel.grid(row = 3, column = 3,sticky='S')
        self.deletemat=tk.Button(self.mainframe, text="Delete material(s)", command=self.Del_Material)
        self.deletemat.grid(row=4,column=3, sticky='N')
        
    def Del_Material(self):
        for item in self.listbox.curselection():
            ODB_class().delete_from_materials(self.conn,self.listindex[item])
        self.List_of_materials()
            
    def Get_file(self):
        self.filename = askopenfilename(title="Select database.", initialdir=self.filedirectory, filetypes=[("Optical data file","*txt")])
        if self.filename:
            self.filedirectory=os.path.dirname(self.filename)
            (sep,dbdir,filedir)=self.check_ini()
            if self.filedirectory!=filedir:
                self.write_to_ini()
            seplist=[item for item in self.seplist]
            self.find_sep(seplist)
            if np.shape(self.data)[1]!=3:
                self.error.set('Error:')
                self.errormsg.set("Data in file doesn't\nseem to be optical data.")
            else:
                self.error.set('')
                self.errormsg.set('')
                self.process_data()
                if self.error.get()=='':
                    matname=os.path.splitext(os.path.basename(self.filename))[0]
                    self.errorDB,self.mat_id=ODB_class().insert_into_materials(self.conn,(matname,self.data[0,0],self.data[-1,0],self.unit,np.shape(self.data)[0]))
                    if self.errorDB!='':
                        self.error.set('Error:')
                        self.errormsg.set(self.errorDB)
                    else:
                        self.pause()
                        ODB_class().insert_into_data(self.conn,self.data,self.mat_id)
                        self.List_of_materials()
                        self.endpause()
    
    def pause(self):
        self.finish.configure(state='disabled')
        self.back.configure(state='disabled')
        self.datafile.configure(state='disabled', text="Data is being stored!\nDon't click on the buttons.")
        try:
            self.deletemat.configure(state='disabled')
        except:
            pass
        self.mainframe.update()#to enforce an update to mainframe
        
    def endpause(self):
        self.finish.configure(state='normal')
        self.back.configure(state='normal')
        self.datafile.configure(text="Open File", state='normal')
        try:
            self.deletemat.configure(state='normal')
        except:
            pass
        self.mainframe.update()#to enforce an update to mainframe
        
    #reccursive approach to find separator
    def find_sep(self,seplist):
        if len(seplist)==0:
            self.data=np.array([])
            self.error.set('Error:')
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
        if 'n' in self.header and 'k' in self.header and ('m' in self.header or 'mm' in self.header or 'nm' in self.header or 'μm' in self.header):#data file should contain three columns labeled with unit of wavelength n and k unit of wavelegnth can only be m, mm, nm and μm
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
            self.error.set('Error:')
            self.errormsg.set("Data file should contain\n wlength, n, k columns.")
    
if __name__=='__main__':
    StoreData.init_start(StoreData())
