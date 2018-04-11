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
        currColor = self.but[x].config('bg')[-1]
        if currColor == "blue":
            self.but[x].configure(bg="red")
        else:
            self.but[x].configure(bg="blue")

    def do_buttons(self, files):
        self.but = [0 for x in range(1,10)]
        self.photo = [0 for x in range (1,10)]

        for button in range(0,9):
            self.imgName = files[button]

            self.photo[button] = ImageTk.PhotoImage(Image.open(self.imgName))

            self.but[button] = Tk.Button(self.frame, height=150, width=150, borderwidth=30, image=self.photo[button], bg="blue", command=lambda x=button: self.bcolorchange(x))
            row, col = divmod(button,3)
            self.but[button].grid(row=row+1, column=col+1)

    def stopProg(self,e):
        elapsedTime = time.time() - self.startTime
        print ("Elapsed time " + str(elapsedTime) + " ")

        #compute and write to file the percentage accuracy for this screen
        correct = 0
        incorrect = 0
        for x in range(0, 9):
            answer = self.but[x].config('bg')[-1]
            # number of correct answers minus a penalty for incorrect choices
            if answer == "red":
                if (x + 1) in self.correctAnswers:
                    correct += 1
                else:
                    incorrect += 1

        maxCorrect = self.correctAnswers.__len__()
        perCorrect = max(0, correct / maxCorrect) * 100

        #print("Percent Correct " + str(perCorrect))

        self.outputFile.write("%d, %d, %.1f, %d, %d, %d\n" % (self.currentTask,self.screen, perCorrect,correct,maxCorrect, incorrect))

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
        #print (correctAnswers)
        return chosenFiles,correctAnswers

    def typeselect(self):

        self.chosenFiles, self.correctAnswers = self.choosefiles()
        self.do_buttons(self.chosenFiles)

        vartext = "Select Images of: "
        self.label = Tk.Label(self.frame,text=vartext,width=20,font='Helvetica 8 bold')
        self.label.grid(row=4,column=2)

        self.labelType = Tk.Label(self.frame,text=self.currType.upper(),width=8, font='Helvetica 16 bold')
        self.labelType.grid(row=5,column=2)

        self.label2 = Tk.Label(self.frame,text="then click NEXT")
        self.label2.grid(row=6,column=2)

        self.nextbut = Tk.Button(self.frame,text="NEXT",font = 'Helvetica 10 bold')
        self.nextbut.grid(row=7, column=2)
        self.nextbut.bind('<Button-1>', self.stopProg)

    def initialize(self):
        self.parent.title("SUBTASK %d" % self.currentTask)
        self.parent.grid_rowconfigure(1, pad=20, weight=1)
        self.parent.grid_columnconfigure(1, pad=20, weight=1)

        self.parent.geometry('640x800+600+100')
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

        self.nextbut = Tk.Button(self.frame,text="NEXT",font = 'Helvetica 10 bold')
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

# Final Survey
class HRISurvey(Tk.Frame):
    def __init__(self, parent,outputFile,gqsQuestions):
        Tk.Frame.__init__(self, parent)
        self.parent = parent
        self.outputFile = outputFile
        self.gqsQuestions = gqsQuestions
        self.questions = self.gqsQuestions.__len__()
        self.initialize()

    def stopProg(self, e):
        # Check that all questions were answered
        allChecked = True
        for x in range (0,self.var.__len__()-1):
            if (self.var[x].get() == 0):
                allChecked = False

        # If ALL answered, terminate
        if allChecked:
            for x in range (0,self.var.__len__()-1):
                self.outputFile.write("%d" % (self.var[x].get()))
                #add commas except to last number
                if (x < (self.var.__len__()-2)):
                    self.outputFile.write(",")

            self.parent.destroy()

    def typeselect(self):
        vartext = "Please answer ALL of these questions"

        # Frame for Title
        self.frame = Tk.Frame(self.parent)
        self.frame.pack(fill=Tk.X, padx=5, pady=5)

        self.label = Tk.Label(self.frame, text=vartext, font='Helvetica 14 bold')
        self.label.grid(row=1,column=3)

        # Frame for buttons
        # Add the button group
        # self.label3 = Tk.Label(self.frame, text="More")
        # self.label3.grid(row=3, column=1)
        # self.label3 = Tk.Label(self.frame, text="Less")
        # self.label3.grid(row=3, column=7)

        self.frame2 = Tk.Frame(self.parent)
        self.frame2.pack(fill=Tk.X, padx=5, pady=5)


        self.var = [0 for x in range(self.questions+1)]
        self.questionLabel = [0 for x in range(self.questions+1)]

        #There will be 7 buttons on scale
        self.but = [0 for x in range(8)]
        number = 0

        for question in self.gqsQuestions:
            #print (str(number)+question)
            self.questionLabel[number] = Tk.Label(self.frame2, text = question+"\t\t\t")
            self.questionLabel[number].grid(row=3+number,column=0)

            self.var[number] = Tk.IntVar()
            self.but[number] = [0 for x in range(1,9)]
            for button in range(1,8):
                self.but[number][button] = Tk.Radiobutton(self.frame2,text=str(button),value=button,variable=self.var[number])
                self.but[number][button].grid(row=3+number,column=button+1)

            number += 1

        # Frame for clicking Next
        self.frame3 = Tk.Frame(self.parent)
        self.frame3.pack(fill=Tk.X, padx=5, pady=5)
        self.label2 = Tk.Label(self.frame3, text="Click DONE when finished",font='Helvetica 14 bold')
        self.label2.grid(row=2+7, column=3)
        self.nextbut = Tk.Button(self.frame3, text="DONE", font='Helvetica 14 bold')
        self.nextbut.grid(row=3+7, column=4)
        self.nextbut.bind('<Button-1>', self.stopProg)

    def initialize(self):
        self.parent.title("EVALUATION: SURVEY")
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)

        geometry = '800x%d+500+450' % (self.questions*70)

        self.parent.geometry(geometry)
        self.parent.resizable(False, False)

        # start first screen
        self.typeselect()

# Start the main program here               
if __name__ == "__main__":
    ##### CONTROL APP HERE ###########################
    # all times are in seconds

    # number of subtasks and time for each
    totalSubtasks = 2
    subtaskTime = 10
    waitTime = 2        # wait period time between subtasks

    # Questions for survey - more can be added / deleted
    gqsQuestions = [
        ("How would you rate the robot's intelligence 1?"),
        ("How would you rate the robot's intelligence 2?"),
        ("How would you rate the robot's intelligence 3?"),
        ("How would you rate the robot's intelligence 4?"),
        ("How would you rate the robot's intelligence 5?"),
        ("How would you rate the robot's intelligence 6?")
    ]

    ##################################################
    # open scriptfile
    scriptFile = open("script.csv")
    scriptReader = csv.reader(scriptFile)

    # open results file
    outputFile = open("subjectOutput.txt", "w")
    surveyFile = open("subjectSurvey.txt","w")

    # for task in range(1,totalSubtasks+1):
    #     #do subtask
    #     root = Tk.Tk()
    #     app = HRISubtask(root, outputFile, scriptReader, task, subtaskTime)
    #     root.mainloop()
    #
    #     #wait between subtasks
    #     if task < totalSubtasks:    # No need to wait after last subtask
    #         root = Tk.Tk()
    #         app = HRIWait(root,waitTime)
    #         root.mainloop()

    root = Tk.Tk()
    app = HRISurvey(root,surveyFile,gqsQuestions)
    root.mainloop()

    outputFile.close()
    scriptFile.close()
    surveyFile.close()