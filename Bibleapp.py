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
icon_path = resource_path("Bibleicon.ico")  # make sure you have a logo.ico file
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
        
        self.add_command(label="Help", command=on_help)
        
def on_help():
    helped=tk.Toplevel()
    helped.title('Help')
    helped.iconbitmap(icon_path)
    helpframe=ttk.Frame(helped)
    helpframe.columnconfigure(0, weight=1)
    helpframe.rowconfigure(0, weight=1)
    hcanvas=tk.Canvas(helpframe, width=500)
    hcanvas.grid(column=0,row=0, sticky="n,w,e,s")
    hscrollbar = ttk.Scrollbar(helpframe, orient=tk.VERTICAL, command=hcanvas.yview)
    hscrollbar.grid(column=1,row=0, sticky='n,s')

    hcanvas.configure(yscrollcommand=hscrollbar.set)
    hcanvas.bind('<Configure>', lambda e: hcanvas.configure(scrollregion=hcanvas.bbox("all")))
    hlabel_frame = ttk.Frame(hcanvas)
    hcanvas.create_window((0, 0), window=hlabel_frame, anchor="nw")
    hcanvas.bind_all("<MouseWheel>", lambda e,c=hcanvas: on_mousewheel(e,c))
    helpframe.grid(column=0,row=0)
    helptext="""Welcome to my Bible application.
    To get started, simply input a book, chapter and verse in the respective boxes, press
    enter in the verse box, and the verse should appear below.
    You can now click "Copy", after which you will be able to paste the verse into a document
    of your choice.
    
    Input options:
        Books:
            You can either select the dropdown menu using the mouse, or start typing.
            At any point if you select the dropdown menu or use the down arrow key, a list of 
            suggestions will appear.
            If what you've typed matches the start of one or more books, these will costitute
            the list, otherwise it will show all books whose names contain what you've typed.
            Pressing enter while an option is selected will choose that option and move you to
            the Chapter box,
            pressing enter while typing will suggest the first suggested option, even if you 
            haven't got the options showing,
            this can be a useful shorthand.
            
            Input is case insensitive.
            
        Chapters:
            The chapter box will accept any input, but you will only get an output if the 
            chapter is in the book, so only use numeric characters.
            
            Pressing enter moves you to the Verse box.
            
        Verses:
            You can leave the verse box blank, in which case the whole chapter will be displayed.
            Single numbers, if found in the chapter will display the verse only.
            You can also input a range of verses, separated by a hyphen (-).
            Multiple groups of verses (or single verses) can be input, separated by commas, for 
            instance, '1,3-6' or'3,7,10'.
            When there is a break between verses (i.e. between 1 and 3 in the first example), 
            there will be a line break and a verse number in the output.
            
            Pressing enter updates the output.
    
    Options:
        The options dropdown menu allows you to adjust the format of the output.
        With the exception of Text size, these will not update an output already on the screen, 
        but pressing enter again in the verse box will refresh it.
        
        Display verse numbers:
            When on, this will place verse number before each verse unless only one verse is 
            returned.
            
        New line between verses:
            When on, this creates a line break between each verse.
            
        Reference:
            Choose whether to include the reference for the quotation at the beginning or end 
            of the output, or not at all.
            
        Text size:
            Select the size of the output text
    """
    helplabel=ttk.Label(hlabel_frame, text=helptext)
    helplabel.grid(column=0,row=0)
    helped.bind('<Destroy>',update_scrollregion)


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
        try:
            if event.keysym in ('BackSpace', 'Delete'):
                self._position = self.index(tk.END)
            elif event.keysym=='Return':
                self.event_generate('<<Entered>>')
                #make sure existent book chosen, also creates shorthand method for use
                if self.get() not in self._completion_list:
                    try:
                        self.set(self._hits[0])
                    except:
                        self.set(self._completion_list[0])
            else:
                self._position = self.index(tk.INSERT)
        except: pass
        # Get the current text in the combobox
        text = self.get()
        if text == '' or text in self._completion_list:#speeds up repeat search
            self['values'] = self._completion_list
        else:
            # Filter suggestions based on input
            self._hits = [item for item in self._completion_list if item.lower().startswith(text.lower())]
            if not self._hits:
                self._hits=[item for item in self._completion_list if text.lower() in item.lower()]
            self['values'] = self._hits

       
def findVerse(event):
    b=book.get()
    c=chap.get()
    v=verse.get()
    if b and c in bible[b].keys():
        chapter=bible[b][c]
        if v in chapter.keys():
            result=chapter[v]
        else:
            vss=v.split(',')
            verses=[]
            result={}
            for vs in vss:
                if vs in chapter.keys():
                    verses.append(vs)
                elif vs.count('-')==1:
                    bounds=vs.split('-')                    
                    if bounds[0] in chapter.keys() and bounds[1] in chapter.keys() and bounds[0]<bounds[1]:
                        verses+=[str(n) for n in range(int(bounds[0]),int(bounds[1])+1)]
                for n in verses:
                    result[n]=chapter[n]
        if not result: result=chapter
        display(result,b,c,v)

def display(inputt,b,c,v):
    if reference.get()=="Beginning":
        disp="%s %s"%(b,c)
        if v:
            disp+=":%s"%(v)
        disp+="\n"
    else: disp=""
    if isinstance(inputt,dict):
        first=True
        nex=1
        for num,ve in inputt.items():
            if nex!=int(num) and not first:
                disp+='\n'
            if vnum.get() or (nex!=int(num) and not first):
                #add number if option selected or there is a jump between verses
                disp+=num
                disp+=" "
            disp+=ve
            if newline.get():
                disp+="\n"
            else:
                disp+=" "
            nex=int(num)+1
            first=False
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
    canvas.bind_all("<MouseWheel>", lambda e,c=canvas: on_mousewheel(e,c))


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