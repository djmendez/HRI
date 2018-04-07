import tkinter as Tk
from PIL import Image, ImageTk
from os import listdir
import time
import csv

# Perform subtask
class HRISubtask(Tk.Frame):
    def __init__(self, parent, output_file, script_reader, task, time):
        Tk.Frame.__init__(self, parent)
        self.parent = parent
        self.currentTask = task
        self.subtaskTime = time
        self.outputFile = output_file
        self.scriptReader = script_reader
        self.initialize()

    def bcolorchange(self,x):
        answer = self.but[x].config('bg')[-1]
        if answer == "blue":
            self.but[x].configure(bg="red")
        else:
            self.but[x].configure(bg="blue")

    def do_buttons(self, files):
        self.but = [0 for x in range(1,10)]
        self.photo = [0 for x in range (1,10)]

        for button in range(0,9):
            self.imgName = files[button]

            self.photo[button] = ImageTk.PhotoImage(Image.open(self.imgName))

            self.but[button] = Tk.Button(self.frame, height=150, width=150, image=self.photo[button], bg="blue", command=lambda x=button: self.bcolorchange(x))
            row, col = divmod(button,3)
            self.but[button].grid(row=row+1, column=col+1)

    def stopProg(self,e):
        elapsedTime = time.time() - self.startTime
        print ("Elapsed time " + str(elapsedTime) + " ")

        #compute and write to file the percentage accuracy for this screen
        correct = 0
        for x in range(0, 9):
            answer = self.but[x].config('bg')[-1]
            # number of correct answers minus a penalty for incorrect choices
            if answer == "red":
                if (x + 1) in self.correctAnswers:
                    correct += 1
                else:
                    correct -= .5
        perCorrect = max(0,correct / self.correctAnswers.__len__()) * 100
        print("Percent Correct " + str(perCorrect))

        self.outputFile.write("%d, %d, %.1f\n" % (self.currentTask,self.screen, perCorrect))

        if elapsedTime < self.subtaskTime:
            self.screen += 1
            self.typeselect()
        else:
            self.parent.destroy()

    def choosefiles(self):
        row = next(self.scriptReader)
        self.currType = row[0]

        chosenFiles = []
        correctAnswers = []

        for i in range(2,20,2):
            type = row[i]
            x = row[i+1]
            if type == self.currType:
                correctAnswers.append(int(i/2))
            imgfiles = listdir("images/"+type)
            chosenfile = imgfiles[int(x)]

            #print ("choosing "+chosenfile)
            chosenFiles.append("images/"+type+"/"+chosenfile)
        print (correctAnswers)
        return chosenFiles,correctAnswers

    def typeselect(self):

        self.chosenFiles, self.correctAnswers = self.choosefiles()
        self.do_buttons(self.chosenFiles)

        vartext = "Select "+self.currType.upper()+" Images"
        self.label = Tk.Label(self.frame,text=vartext,width=20,font='Helvetica 8 bold')
        self.label.grid(row=4,column=2)

        self.label2 = Tk.Label(self.frame,text="then click NEXT")
        self.label2.grid(row=5,column=2)

        self.nextbut = Tk.Button(self.frame,text="NEXT")
        self.nextbut.grid(row=6, column=2)
        self.nextbut.bind('<Button-1>', self.stopProg)

    def initialize(self):
        self.parent.title("SUBTASK %d" % self.currentTask)
        self.parent.grid_rowconfigure(1, pad=20, weight=1)
        self.parent.grid_columnconfigure(1, pad=20, weight=1)

        self.parent.geometry('480x600+700+250')
        self.parent.resizable(False,False)

        self.frame = Tk.Frame(self.parent)
        self.frame.pack(fill=Tk.X, padx=5, pady=5)

        #start sub-task time
        self.startTime = time.time()

        #start first screen
        self.screen = 1
        self.typeselect()

# Behavior between subtasks: currently just waits
class HRIWait(Tk.Frame):

    def __init__(self, parent,waitTime):
        Tk.Frame.__init__(self, parent)
        self.parent = parent
        self.subtaskTime = waitTime
        self.initialize()

    def stopProg(self,e):
        elapsedTime = time.time() - self.startTime
        print ("Elapsed time " + str(elapsedTime) + " ")

        if elapsedTime > self.subtaskTime:
            self.parent.destroy()

    def typeselect(self):
        vartext = "Performing Evaluation. Please wait."
        self.label = Tk.Label(self.frame, text=vartext, font='Helvetica 8 bold')
        self.label.grid(row=1,column=0)
        self.label2 = Tk.Label(self.frame, text="Click NEXT when ready to continue")
        self.label2.grid(row=2, column=0)

        self.nextbut = Tk.Button(self.frame,text="NEXT")
        self.nextbut.grid(row=3, column=0)
        self.nextbut.bind('<Button-1>', self.stopProg)

    def initialize(self):
        self.parent.title("EVALUATION: WAIT")
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        self.parent.geometry('250x100+800+450')
        self.parent.resizable(False,False)

        self.frame = Tk.Frame(self.parent)
        self.frame.pack(fill=Tk.X, padx=5, pady=5)

        #start sub-task time
        self.startTime = time.time()

        #start first screen
        self.typeselect()

# Start the main program here               
if __name__ == "__main__":
    ##### CONTROL APP HERE ###########################
    # number of subtasks and time for each
    # all times are in seconds
    totalSubtasks = 2
    subtaskTime = 5
    waitTime = 5        # wait time between subtasks

    ###################################################
    # open scriptfile
    scriptFile = open("script.csv")
    scriptReader = csv.reader(scriptFile)

    # open results file
    outputFile = open("subjectOutput.txt", "w")

    for task in range(1,totalSubtasks+1):
        #do subtask
        root = Tk.Tk()
        app = HRISubtask(root, outputFile, scriptReader, task, subtaskTime)
        root.mainloop()

        #wait between subtasks
        if task < totalSubtasks:    # No need to wait after last subtask
            root = Tk.Tk()
            app = HRIWait(root,waitTime)
            root.mainloop()

    outputFile.close()
    scriptFile.close()