# -*- coding: utf-8 -*-
"""
Created on Sat Nov  8 09:55:33 2025

@author: charl
"""
#run this to package: !pyinstaller --onefile --windowed --add-data "ESVUK_bible.json;." --add-data "NIVUK_bible.json;." --add-data "KJV_bible.json;." --add-data "NLT_bible.json;." --add-data "NKJV_bible.json;." --add-data "NRSV_bible.json;." --add-data "Bibleicon.ico;." --icon=Bibleicon.ico Bibleapp.py
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



    
class Menubar(tk.Menu):
    def __init__(self,parent,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.options=tk.Menu(self)
        self.add_cascade(menu=self.options,label="Options")
        self.options.add_checkbutton(label="Display verse numbers",variable=parent.vnum)
        self.options.add_checkbutton(label="New line between verses",variable=parent.newline)
        
        self.reference=tk.Menu(self.options)
        self.reference.add_radiobutton(label="Beginning",variable=parent.reference,value="Beginning")
        self.reference.add_radiobutton(label="None",variable=parent.reference,value="None")
        self.reference.add_radiobutton(label="End",variable=parent.reference,value="End")
        self.options.add_cascade(menu=self.reference,label="Reference")
       
        self.textsize=tk.Menu(self.options)
        for i in range(6,15):
            self.textsize.add_radiobutton(label=str(i),value=str(i),variable=parent.size,command=parent.updatesize)
        self.options.add_cascade(menu=self.textsize,label="Text size")
        
        self.add_command(label="Help", command=parent.on_help)


    



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

       



    
            


""" """
class BibleWindow(tk.Toplevel):
    def updatesize(self):
        self.result.configure(font=("Arial",int(self.size.get())))
    def on_help(self):
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
        hcanvas.bind_all("<MouseWheel>", lambda e,c=hcanvas: self.on_mousewheel(e,c))
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
        helped.bind('<Destroy>',self.update_scrollregion)
    def findVerse(self,event):
        b=self.book.get()
        c=self.chap.get()
        v=self.verse.get()
        if b and c in self.bible[b].keys():
            chapter=self.bible[b][c]
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
            self.display(result,b,c,v)
    def display(self,inputt,b,c,v):
        if self.reference.get()=="Beginning":
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
                if self.vnum.get() or (nex!=int(num) and not first):
                    #add number if option selected or there is a jump between verses
                    disp+=num
                    disp+=" "
                disp+=ve
                if self.newline.get():
                    disp+="\n"
                else:
                    disp+=" "
                nex=int(num)+1
                first=False
        else: 
            disp+=inputt
        if self.reference.get()=="End":
            if isinstance(inputt,str) or not self.newline.get():
                disp+="\n"
            disp+="%s %s"%(b,c)
            if v:
                disp+=":%s"%(v)
        self.result.configure(text=disp)
    def coppy(self):
        root.clipboard_clear()
        copied=self.result.cget("text")
        root.clipboard_append(copied)
        # Ensure the clipboard content is saved after the script ends
        root.update()
    def on_mousewheel(self,event,canvas):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def update_scrollregion(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)



    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", lambda e,c=self.canvas: self.on_mousewheel(e,c))

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
    def __init__(self,translation):#translation as a dictionary containing json path and name
        super().__init__()
        self.json_path=resource_path(translation['path'])
        with open(self.json_path,'r',encoding='utf-8') as b:
            bi=b.read()
        self.bible=json.loads(bi)

        self.books=[book for book in self.bible.keys()]
        
        self.title(translation['name'])
        self.geometry("300x300")
        self.option_add('*tearOff', tk.FALSE)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)    
        
        self.geometry("300x300")
        self.option_add('*tearOff', tk.FALSE)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.vnum=tk.BooleanVar(value=False)
        self.newline=tk.BooleanVar(value=False)
        self.reference=tk.StringVar(value="End")
        self.size=tk.StringVar(value="8")

        self.iconbitmap(icon_path)
        
        self['menu'] = Menubar(self)
        self.fr=ttk.Frame(self)
        self.fr.grid(column=0,row=0, sticky='n,w,e,s')
        self.fr.rowconfigure(3, weight=1)
        #self.fr.columnconfigure(0, weight=1)
        self.fr.columnconfigure(1, weight=1)



        self.canvas=tk.Canvas(self.fr)
        self.canvas.grid(column=0,row=3, columnspan=2, sticky="n,w,e,s")
        self.scrollbar = ttk.Scrollbar(self.fr, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(column=2,row=3, sticky='n,s')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.label_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.label_frame, anchor="nw")
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)
        
        


        self.result=ttk.Label(self.label_frame,wraplength=250,  # Set wrap length in pixels
            justify="left",  # Align text to the left
            font=("Arial", 8))  # Optional: Set font)
        self.result.grid(column=0,row=0,sticky='n,w')
        self.result.bind('<Configure>',self.update_scrollregion)



        ttk.Label(self.fr,text="Verse:").grid(column=0,row=2)
        self.verse=ttk.Entry(self.fr)
        self.verse.grid(column=1,row=2,sticky='e,w')
        self.verse.bind("<Return>",self.findVerse)

        ttk.Label(self.fr,text="Chapter:").grid(column=0,row=1)
        self.chap=ttk.Entry(self.fr)
        self.chap.grid(column=1,row=1,sticky='e,w')
        self.chap.bind("<Return>",lambda e:self.verse.focus_set())

        ttk.Label(self.fr,text="Book:").grid(column=0,row=0)
        self.book=AutocompleteCombobox(self.fr)
        self.book.set_completion_list(self.books)
        self.book.grid(column=1,row=0,sticky='e,w')
        self.book.bind('<<Entered>>',lambda e: self.chap.focus_set())
        self.book.focus_set()



        self.buttons=ttk.Frame(self.fr)
        self.buttons.grid(column=0,row=4)

        self.copy=ttk.Button(self.buttons, text="Copy",command=self.coppy)
        self.copy.grid()

root=tk.Tk()
root.title("Bible app")
root.geometry("300x300")
root.option_add('*tearOff', tk.FALSE)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

root.iconbitmap(icon_path)

fr=ttk.Frame(root)
fr.grid(column=0, row=0)

translations={'ESV':{'name':'ESV','path':"ESVUK_bible.json"},'KJV':{'name':'KJV','path':'KJV_bible.json'},
              'NLT':{'name':'NLT','path':'NLT_bible.json'},'NIV':{'name':'NIV','path':'NIVUK_bible.json'},
              'NRSV':{'name':'NRSV','path':'NRSV_bible.json'},'NKJV':{'name':'NKJV','path':'NKJV_bible.json'}}
tbuttons=[]
for i,translation in enumerate(translations.values()):
    tbuttons.append(ttk.Button(fr,text=translation['name'],command=lambda t=translation:BibleWindow(t)))
    tbuttons[i].grid(column=0,row=i)
    



root.mainloop()