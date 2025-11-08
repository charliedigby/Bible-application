An application to speed up scripture quotations.
Using the ESVUK bible json from jadenzaleski's bible-translations
repository, this tkinter application displays a quotation from a
reference input, which can be coppied to the clipboard to be
pasted into other windows.
The book is input in a combobox, and by typing the start of the
book name followed by the down arrow, suggestions will appear.
Pressing enter changes focus to the chapter, which only takes
integers. Pressing enter again moves to verses, and one more 
enter generates the result.
Leaving verses blank returns the whole chapter, typing an int
which occurs in the chapter will return the single verse. Typing
2 such integers separated by a hyphen returns verses in that 
range.
There is an options menu to choose whether the reference is
included in the coppiabe text and where; whether the verse 
numbers are displayed; whether a new line occurs with each
verse; and what size the text displays.
