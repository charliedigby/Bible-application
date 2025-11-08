# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 09:55:33 2025

@author: charl
"""
#run this to package: !pyinstaller --onefile --windowed --add-data "ESVUK_bible.json;." --add-data "Bibleicon.ico;." --icon=Bibleicon.ico Bibleapp.py
import tkinter as tk
from tkinter import ttk
import json

import sys
import os

# Helper to get the correct resource path, works with PyInstaller
def resource_path(relative_path):
    try:
        # PyInstaller stores temp folder path here
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

json_path=resource_path("ESVUK_bible.json")
with open(json_path,'r',encoding='utf-8') as b:
    bi=b.read()
bible=json.loads(bi)

books=[book for book in bible.keys()]

def updatesize():

    result.configure(font=("Arial",int(size.get())))
    
class Menubar(tk.Menu):
    def __init__(self,parent,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.options=tk.Menu(self)
        self.add_cascade(menu=self.options,label="Options")
        self.options.add_checkbutton(label="Display verse numbers",variable=vnum)
        self.options.add_checkbutton(label="New line between verses",variable=newline)
        
        self.reference=tk.Menu(self.options)
        self.reference.add_radiobutton(label="Beginning",variable=reference,value="Beginning")
        self.reference.add_radiobutton(label="None",variable=reference,value="None")
        self.reference.add_radiobutton(label="End",variable=reference,value="End")
        self.options.add_cascade(menu=self.reference,label="Reference")
       
        self.textsize=tk.Menu(self.options)
        for i in range(6,15):
            self.textsize.add_radiobutton(label=str(i),value=str(i),variable=size,command=updatesize)
        self.options.add_cascade(menu=self.textsize,label="Text size")
        



class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []  # List of suggestions
        self._hits = []
        self._position = 0
        self.bind('<KeyRelease>', self._on_keyrelease)

    def set_completion_list(self, completion_list):
        """Set the list of possible suggestions."""
        self._completion_list = completion_list
        self['values'] = self._completion_list

    def _on_keyrelease(self, event):
        """Handle key release events to filter suggestions."""
        if event.keysym in ('BackSpace', 'Delete'):
            self._position = self.index(tk.END)
        elif event.keysym=='Return':
            self.event_generate('<<Entered>>')
        else:
            self._position = self.index(tk.INSERT)

        # Get the current text in the combobox
        text = self.get()
        if text == '':
            self['values'] = self._completion_list
        else:
            # Filter suggestions based on input
            self._hits = [item for item in self._completion_list if item.lower().startswith(text.lower())]
            self['values'] = self._hits

       
def findVerse(event):
    b=book.get()
    c=chap.get()
    v=verse.get()
    if b and c in bible[b].keys():
        chapter=bible[b][c]
        if v in chapter.keys():
            result=chapter[v]
        elif v.count('-')==1:
            bounds=v.split('-')
            if bounds[0] in chapter.keys() and bounds[1] in chapter.keys() and bounds[0]<bounds[1]:
                verses=[str(n) for n in range(int(bounds[0]),int(bounds[1])+1)]
                result={n:chapter[n] for n in verses}
            else:result=chapter    
        else:
            result=chapter
        display(result,b,c,v)

def display(inputt,b,c,v):
    if reference.get()=="Beginning":
        disp="%s %s"%(b,c)
        if v:
            disp+=":%s"%(v)
        disp+="\n"
    else: disp=""
    if isinstance(inputt,dict):
        for num,ve in inputt.items():
            if vnum.get():
                disp+=num
                disp+=" "
            disp+=ve
            if newline.get():
                disp+="\n"
            else:
                disp+=" "
    else: 
        disp+=inputt
    if reference.get()=="End":
        if isinstance(inputt,str) or not newline.get():
            disp+="\n"
        disp+="%s %s"%(b,c)
        if v:
            disp+=":%s"%(v)
    result.configure(text=disp)
    
            
def coppy():
    root.clipboard_clear()
    copied=result.cget("text")
    root.clipboard_append(copied)
    # Ensure the clipboard content is saved after the script ends
    root.update()


root=tk.Tk()
root.title("ESV Bible")
root.geometry("300x300")
root.option_add('*tearOff', tk.FALSE)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

vnum=tk.BooleanVar(value=False)
newline=tk.BooleanVar(value=False)
reference=tk.StringVar(value="End")
size=tk.StringVar(value="8")


icon_path = resource_path("Bibleicon.ico")  # make sure you have a logo.ico file
root.iconbitmap(icon_path)

root['menu'] = Menubar(root)
fr=ttk.Frame(root)
fr.grid(column=0,row=0, sticky='n,w,e,s')
fr.rowconfigure(3, weight=1)
#fr.columnconfigure(0, weight=1)
fr.columnconfigure(1, weight=1)



canvas=tk.Canvas(fr)
canvas.grid(column=0,row=3, columnspan=2, sticky="n,w,e,s")
scrollbar = ttk.Scrollbar(fr, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.grid(column=2,row=3, sticky='n,s')

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
label_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=label_frame, anchor="nw")
canvas.bind_all("<MouseWheel>", lambda e,c=canvas: on_mousewheel(e,c))
def on_mousewheel(event,canvas):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


result=ttk.Label(label_frame,wraplength=250,  # Set wrap length in pixels
    justify="left",  # Align text to the left
    font=("Arial", 8))  # Optional: Set font)
result.grid(column=0,row=0,sticky='n,w')
result.bind('<Configure>',update_scrollregion)



ttk.Label(fr,text="Verse:").grid(column=0,row=2)
verse=ttk.Entry(fr)
verse.grid(column=1,row=2,sticky='e,w')
verse.bind("<Return>",findVerse)

ttk.Label(fr,text="Chapter:").grid(column=0,row=1)
chap=ttk.Entry(fr)
chap.grid(column=1,row=1,sticky='e,w')
chap.bind("<Return>",lambda e:verse.focus_set())

ttk.Label(fr,text="Book:").grid(column=0,row=0)
book=AutocompleteCombobox(fr)
book.set_completion_list(books)
book.grid(column=1,row=0,sticky='e,w')
book.bind('<<Entered>>',lambda e: chap.focus_set())
book.focus_set()



buttons=ttk.Frame(fr)
buttons.grid(column=0,row=4)

copy=ttk.Button(buttons, text="Copy",command=coppy)
copy.grid()

root.mainloop()