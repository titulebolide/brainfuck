from tkinter import *
from tkinter.filedialog import *
import os

class prgm():    
    def __init__(self):
        self.t = ""
        self.entrevar = []
        self.n = 30000
        self.memory = [0]*self.n #mémoire
        self.pos = 0 #position dans le code
        self.prevpos = 0
        self.pointeur = 0 #pointeur dans la mémoire
        self.listbr = [] #liste permettant de gérer les boucles
        self.out = ""
        self.stepbystepon = False
        self.reset = False
        self.filepath = ""
        self.erroroccured = False #mis à True si une erreur survient pour stopper le programme


        #général
        self.fenetre = Tk()
        self.fenetre.title("Brainfuck Interpreter 2.0 - untitled.bfk")

        self.fenetre.bind("<F1>", lambda event: self.bfall())
        self.fenetre.bind("<F2>", lambda event: self.bfstep())
        self.fenetre.bind("<F3>", lambda event: self.havereset())

        ##framecode
        framecode = LabelFrame(self.fenetre, text = "Code")
        framecode.pack(fill = BOTH)

        #framecode1
        framecode1 = Frame(framecode)
        framecode1.pack(side = TOP, fill = BOTH)

        scroller = Scrollbar(framecode1)
        scroller.pack(side = RIGHT, fill = Y)
        self.code = Text(framecode1, height = 44)
        scroller.config(command=self.code.yview)
        self.code.config(yscrollcommand=scroller.set)
        self.code.pack(fill = BOTH)
        self.code.tag_configure('big', font=('DejaVu Sans Mono', 10, 'bold'), foreground = "red", underline = True) #forme de l'élément lu

        #framecode2
        framecode2 = Frame(framecode)
        framecode2.pack(side = TOP, fill = BOTH)

        Button(framecode2, text = "RUN CODE (F1)", command = self.bfall).pack(fill = BOTH)


        ##frameIO
        frameIO = LabelFrame(self.fenetre, text = "Input/Output")
        frameIO.pack(fill = BOTH)

        #frameIO1

        frameIO1 = Frame(frameIO)
        frameIO1.pack(side = TOP, fill = BOTH)

        Label(frameIO1, text = """Input:   """).pack(side = LEFT)

        self.entrevar = StringVar()
        Entry(frameIO1, textvariable = self.entrevar).pack(fill = BOTH)

        #frameIO2

        frameIO2 = Frame(frameIO)
        frameIO2.pack(fill = BOTH)

        Label(frameIO2, text = """Output: """).pack(side = LEFT)

        self.sortievar = StringVar()
        Entry(frameIO2, textvariable = self.sortievar).pack(fill = BOTH)

        #frameIO3
        frameIO3 = Frame(frameIO)
        frameIO3.pack(side = BOTTOM, fill = BOTH)

        self.asciiinput = IntVar()
        Checkbutton(frameIO3, text = "Ascii input", variable = self.asciiinput).pack(side = LEFT)

        self.asciioutput = IntVar()
        Checkbutton(frameIO3, text = "Ascii output", variable = self.asciioutput).pack(side = LEFT)

        self.debug = IntVar()
        Checkbutton(frameIO3, text = "Debugging mode", variable = self.debug, command = self.debugmode).pack(side = LEFT)

        ##framedebug
        self.framedebug = LabelFrame(self.fenetre, text = "Debugging")
        #on ne l'affiche pas immédiatement

        #framedebug1
        framedebug1 = Frame(self.framedebug)
        framedebug1.pack(fill = BOTH)

        self.nbbox = StringVar()
        self.nbbox.set("20")
        Spinbox(framedebug1, from_ = 1, to = 100, textvariable = self.nbbox, width = 3, command = self.setdisplay).pack(side = RIGHT)

        Label(framedebug1, text = "Number of displayed memory blocs :").pack(side = RIGHT)

        self.stepbystepbutton = Button(framedebug1, text = "STEP BY STEP (F2)", command = self.bfstep)
        self.stepbystepbutton.pack(fill = BOTH, side = LEFT)

        Button(framedebug1, text = "RESET ENVIRONNEMENT (F3)", command = self.resetvariables).pack(fill = BOTH, side = LEFT)


        #framedebug2
        framedebug2 = Frame(self.framedebug)
        framedebug2.pack(fill = BOTH)

        self.debugout = StringVar()
        Entry(framedebug2, textvariable = self.debugout).pack(fill = BOTH)

        ##menu
        menubar = Menu(self.fenetre)
        
        menu1 = Menu(menubar, tearoff=0)

        menu1.add_command(label="New File", command=self.newfile)
        menu1.add_command(label="Open", command=self.openfile)
        menu1.add_command(label="Save", command=self.savefile)
        menu1.add_command(label="Save As", command=self.savefileas)
        menubar.add_cascade(label="Fichier", menu=menu1)

        self.fenetre.config(menu=menubar)

        ##launch
        self.havereset()
        self.fenetre.mainloop()

    def havereset(self): #réinitialise les variables et planifie une réinitialisation pour le prochain lancement (en cas de mise à jour du code)
        self.resetvariables()
        self.reset = True
    
    def resetvariables(self):
        self.t = self.code.get("1.0", "end-1c")
        if self.asciiinput.get() == 1:
            self.entre = list(self.entrevar.get()) #si l'entrée est une chaine de caractères, cela fait alors autant d'entrées que de lettres
        else:
            self.entre = self.entrevar.get().split(",") #si ce sont des nombres en entrée, ils sont séparés par un point virgule
        self.memory = [0]*self.n #mémoire
        self.pos = 0 #position dans le code
        self.prevpos = 0
        self.pointeur = 0 #pointeur dans la mémoire
        self.listbr = [] #liste permettant de gérer les boucles
        self.out = ""
        self.stepbystepbutton.config(state = NORMAL)
        self.stepbystepon = False
        self.reset = False
        self.filepath = ""
        self.setdisplay()
        self.erroroccured = False

    def error(self,message):
        self.sortievar.set(message)
        self.erroroccured = True

    def setdisplay(self):
        self.sortievar.set(self.out)
        if self.debug.get() == 1:
            if not 0<=self.pointeur < int(self.nbbox.get()):
                foo = str(self.memory[:int(self.nbbox.get())])[:-1] + ", ...]"
            else:
                lmark = ", |"
                rmark = "|, "
                if self.pointeur == 0:
                    lmark = "|"
                elif self.pointeur == int(self.nbbox.get())-1:
                    rmark = "|"
                foo = str(self.memory[:self.pointeur])[:-1] + lmark + str(self.memory[self.pointeur]) + rmark + str(self.memory[self.pointeur + 1:int(self.nbbox.get())])[1:-1] + ", ...]"
            self.debugout.set(foo)
        if self.stepbystepon: #affichage du code lu en gras
            if self.prevpos < len(self.t)-1:
                self.code.delete(1.0,END)
                self.code.insert(END, self.t[:self.prevpos])
                self.code.insert(END, self.t[self.prevpos], "big")
                self.code.insert(END, self.t[self.prevpos+1:])
            elif self.prevpos == len(self.t)-1:
                self.code.delete(1.0,END)
                self.code.insert(END, self.t[:self.prevpos])
                self.code.insert(END, self.t[self.prevpos], "big")
            elif self.prevpos == len(self.t):
                self.code.delete(1.0,END)
                self.code.insert(END, self.t)
        
    def step(self):
        self.prevpos = self.pos
        char = self.t[self.pos]
        if char == ">":
            self.pointeur += 1
            if self.pointeur == len(self.memory):
                self.error("Pointer to much shifted to the right")
        elif char == "<":
            self.pointeur -= 1
            if self.pointeur == -1:
                self.error("Pointer to much shifted to the left")
        elif char == "+":
            self.memory[self.pointeur] += 1
        elif char == "-":
            self.memory[self.pointeur] -= 1
        elif char == ".":
            if self.asciioutput.get() == 1:
                self.out += chr(self.memory[self.pointeur])
            else:
                self.out += str(self.memory[self.pointeur])
        elif char == ",":
            if self.entre != []:
                try:
                    if self.asciiinput.get() == 1:
                        self.memory[self.pointeur] = ord(self.entre.pop(0))
                    else:   
                        self.memory[self.pointeur] = int(self.entre.pop(0))
                except:
                    self.error("An input is required")
            else:
                self.memory[self.pointeur] = 0 #s'il n'y a pas suffisemment d'entrées, on met par défaut des 0
        elif char == "[":
            if self.memory[self.pointeur] == 0:
                try:
                    self.pos += self.t[self.pos:].index("]")
                except:
                    self.error("""There lacks loop structure ']'""")
            else:
                self.listbr.append(self.pos)
        elif char == "]":
            if self.listbr == []:
                self.error("""There lacks loop structure '['""")
            if self.memory[self.pointeur] == 0:
                del self.listbr[-1]
            else:
                self.pos = self.listbr[-1]
        
        for i in range(self.pos+1, len(self.t)+1):
            if i == len(self.t):
                break
            if self.t[i] in ("+", "-", ",", ".", ">", "<", "[", "]"):
                break
        self.pos = i

    def bfstep(self):
        if self.reset:
            self.resetvariables()
            self.reset = False
        self.stepbystepon = True
        if self.pos < len(self.t):
            self.step()
        else:
            self.stepbystepbutton.config(state = DISABLED)
            self.prevpos = self.pos
        self.setdisplay()

    def bfall(self):
        self.resetvariables()
        while self.pos < len(self.t) and not self.erroroccured:
            self.step()
        self.setdisplay()

    def debugmode(self):
        if self.debug.get() == 1:
            self.framedebug.pack(fill = BOTH)
            self.setdisplay()
        else:
            self.framedebug.pack_forget()

    def refreshtitle(self): #permet d'écrire le titre de la fenetre en fonction du nom du fichier
        foo = -(self.filepath[::-1].index("/"))
        self.fenetre.title("Brainfuck Interpreter 2.0 - " + self.filepath[foo:])

    def newfile(self):
        self.filepath = ""
        self.code.delete(1.0, END)
        self.refreshtitle("/untilted.bfk")
        self.havereset()

    def openfile(self):
        self.filepath = askopenfilename(initialfile = os.getcwd(), title="Open",filetypes=[('brainfuck files', '.bfk'),('all files','.*')])
        if self.filepath != '':
            f = open(self.filepath, 'r')
            self.code.delete(1.0, END)
            for l in f:
                self.code.insert(END, l)
            f.close()
        self.refreshtitle()

    def savefileas(self):
        self.filepath = asksaveasfilename(initialfile = os.getcwd(), title= "Save Under", filetypes=[('brainfuck files', '.bfk'),('all files','.*')])
        f = open(self.filepath, 'w')
        f.write(self.code.get("1.0", "end-1c"))
        f.close()
        self.refreshtitle(self.filepath)

    def savefile(self):
        if self.filepath == '':
            self.savefileas()
        else:
            f = open(self.filepath, 'w')
            f.write(self.code.get("1.0", "end-1c"))
            f.close()
            
app = prgm()
