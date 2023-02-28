import tkinter as tk
from tkinter import ttk
import os
from pkg_resources import resource_filename
import getpass
import math
import serial
import serial.tools.list_ports
import threading
import time

#pyinstaller Unit_Code_Logs.py --onefile --noconsole --icon=icon.ico

username = getpass.getuser()

class App():
    def __init__(self):        
        try:
            os.mkdir(f"{username}")
        except:
            pass

        try:
            os.mkdir(f"{username}/Blocks")
        except:
            pass
        
        self.root = tk.Tk()
        self.root.title("Block Reader")
        self.root.geometry("610x290")
        self.root.resizable(True, False)
        try:
            icon_path = resource_filename(__name__, "icon.png")
            icon = tk.PhotoImage(file=icon_path)
            self.root.wm_iconphoto(True, icon)
        except:
            pass

        self.notebook = ttk.Notebook(self.root)
        self.notebook.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

        self.mainTab = tk.Frame(self.notebook)

        self.leftFrame = tk.LabelFrame(self.mainTab, text="Blocks: ")
        self.leftFrame.place(relx = 0, rely = 0, relwidth = 0.25, relheight = 1)

        self.rightFrame = tk.LabelFrame(self.mainTab, text="Commands: ")
        self.rightFrame.place(relx = 0.26, rely = 0, relwidth = 0.74, relheight = 1)

        self.notebook.add(self.mainTab, text=" Commands ")

        #Left#

        self.folderBrowser = ttk.Combobox(self.leftFrame, postcommand=self.updateBlockList)
        self.folderBrowser.place(relx = 0.025, rely = 0.025, relwidth = 0.95, relheight = 0.1)
        self.folderBrowser.bind("<<ComboboxSelected>>", self.updateFileList)

        self.fileBrowser = tk.Listbox(self.leftFrame)
        self.fileBrowser.bind("<Double-Button-1>", self.openFile)
        self.fileBrowser.place(relx = 0.025, rely = 0.15, relwidth = 0.95, relheight = 0.7)

        self.refreshButton = tk.Button(self.leftFrame, text="Refresh", command=self.updateFileListButton)
        self.refreshButton.place(relx = 0.025, rely = 0.875, relwidth = 0.45, relheight = 0.1)

        self.deleteButton = tk.Button(self.leftFrame, text="Delete", command=self.removeFile)
        self.deleteButton.place(relx = 0.525, rely = 0.875, relwidth = 0.45, relheight = 0.1)

        #Right#

        self.titleLabel = tk.Label(self.rightFrame, text="Title: ")
        self.titleLabel.place(relx = 0, rely = 0, relwidth = 0.1, relheight = 0.1)

        self.titleEntry = tk.Entry(self.rightFrame)
        self.titleEntry.place(relx = 0.1, rely = 0, relwidth = 0.89, relheight = 0.1)

        self.textAreaFrame = tk.Frame(self.rightFrame)
        self.textAreaFrame.place(relx = 0.01, rely = 0.125, relwidth = 0.98, relheight = 0.6)
        
        self.textArea = tk.Text(self.textAreaFrame)
        self.textArea.pack(fill=tk.BOTH, expand=True)

        self.scrollbarY = tk.Scrollbar(self.textArea)
        self.scrollbarY.pack(side=tk.RIGHT, fill=tk.Y)
        self.textArea.config(yscrollcommand=self.scrollbarY.set)
        self.scrollbarY.config(command=self.textArea.yview)
        
        self.loadButton = tk.Button(self.rightFrame, text="-> Load", command=self.openFileButton)
        self.loadButton.place(relx = 0.025, rely = 0.875, relwidth = 0.3, relheight = 0.1)

        self.saveButton = tk.Button(self.rightFrame, text="<- Save", command=self.saveFile)
        self.saveButton.place(relx = 0.675, rely = 0.875, relwidth = 0.3, relheight = 0.1)

        #Mileage Tab#
        self.mileageTab = tk.Frame(self.notebook)

        self.miles = tk.StringVar()
        self.kilometers = tk.StringVar()

        self.milesLabel = tk.Label(self.mileageTab, text="Miles: ")
        self.milesLabel.grid(row=0, column=0, padx=5, pady=5)

        self.milesInput = tk.Entry(self.mileageTab, textvariable=self.miles)
        self.milesInput.grid(row=0, column=1, padx=5, pady=5)

        self.kilometersLabel = tk.Label(self.mileageTab, text="Kilometers: ")
        self.kilometersLabel.grid(row=1, column=0, padx=5, pady=5)

        self.kilometersInput = tk.Entry(self.mileageTab, textvariable=self.kilometers)
        self.kilometersInput.grid(row=1, column=1, padx=5, pady=5)

        self.miles.trace("w", lambda *args: self.updateKilos())
        self.kilometers.trace("w", lambda *args: self.updateMiles())

        self.sysMileageOutputLabel = tk.Label(self.mileageTab, text="SYS Mileage: ")
        self.sysMileageOutputLabel.grid(row=2, column=0, padx=5, pady=5)

        self.sysMileageOutput = tk.Label(self.mileageTab)
        self.sysMileageOutput.grid(row=2, column=1, padx=5, pady=5)
        
        self.sysMileageCopyButton = tk.Button(self.mileageTab, text="Copy", command=self.copy_sys_mileage)
        self.sysMileageCopyButton.grid(row=2, column=2, padx=5, pady=5)

        self.gpsMileageOutputLabel = tk.Label(self.mileageTab, text="GPS Mileage: ")
        self.gpsMileageOutputLabel.grid(row=3, column=0, padx=5, pady=5)

        self.gpsMileageOutput = tk.Label(self.mileageTab)
        self.gpsMileageOutput.grid(row=3, column=1, padx=5, pady=5)
        
        self.gpsMileageCopyButton = tk.Button(self.mileageTab, text="Copy", command=self.copy_gps_mileage)
        self.gpsMileageCopyButton.grid(row=3, column=2, padx=5, pady=5)

        self.isMilesUpdating = False
        self.isKilometersUpdating = False

        self.notebook.add(self.mileageTab, text=" Mileage ")

        ##### String Comparison #####

        self.stringTab = tk.Frame(self.notebook)

        self.stringFrame = tk.LabelFrame(self.stringTab, text="String Comparison: ")
        self.stringFrame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

        self.string1Label = tk.Label(self.stringFrame, text="Enter String: ")
        self.string1Label.grid(row=0,column=0, sticky="ew")
        self.string1Entry = tk.Entry(self.stringFrame)
        self.string1Entry.grid(row=0,column=1, columnspan=2, sticky="ew")

        self.string2Label = tk.Label(self.stringFrame, text="Enter String: ")
        self.string2Label.grid(row=1,column=0, sticky="ew")
        self.string2Entry = tk.Entry(self.stringFrame)
        self.string2Entry.grid(row=1,column=1, columnspan=2, sticky="ew")

        self.compareButton = tk.Button(self.stringFrame, text="Compare", command=self.compareStrings)
        self.compareButton.grid(row=0,column=3,rowspan=2)

        self.comparisonOutput = tk.Text(self.stringFrame)
        self.comparisonOutput.grid(row=3,column=0,columnspan=4)

        self.comparisonOutput.tag_configure('green', foreground='green')
        self.comparisonOutput.tag_configure('red', foreground='red')

        self.notebook.add(self.stringTab, text=" String Comparison ")
        
        ##### END #####
        
        ##### Automations #####
        
        self.serialTab = tk.Frame(self.notebook)

        self.serialFrame = tk.LabelFrame(self.serialTab, text="Serial: ")
        self.serialFrame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

        self.comActiveLabel = tk.Label(self.serialFrame, text="COM: ")
        self.comActiveLabel.place(x=5,y=5,width=40,height=20)
        self.comActiveIndicator = tk.Label(self.serialFrame, text="Inactive",foreground="red")
        self.comActiveIndicator.place(x=45,y=5,width=120,height=20)

        self.portIdentifier = tk.Label(self.serialFrame, text="PORT: ")
        self.portIdentifier.place(x=5,y=25,width=40,height=20)

        self.comPort = tk.StringVar(self.root)
        self.comPort.set("Select a port")
        self.comMenu = tk.OptionMenu(self.serialFrame, self.comPort, [])
        self.comMenu.place(x=45,y=20,width=120,height=30)

        self.baudIdentifier = tk.Label(self.serialFrame, text="Baud: ")
        self.baudIdentifier.place(x=5,y=55,width=40,height=20)

        self.baudRate = tk.StringVar(self.root)
        self.baudRate.set("115200")
        self.baudRateMenu = tk.Label(self.serialFrame, text="115200")
        self.baudRateMenu.place(x=45,y=50,width=120,height=30)

        self.portOpen = False
        self.openPortButton = tk.Button(self.serialFrame, text="Open Port", command=self.handlePort)
        self.openPortButton.place(x=5,y=85,width=160,height=30)
        
        self.display_text = tk.Text(self.serialFrame, width=51, height=10, state="disabled")
        self.display_text.place(x=180,y=5)

        self.display_text.tag_configure("Error", foreground="red")
        self.display_text.tag_configure("Office", foreground="blue")

        self.commandEntry = tk.Entry(self.serialFrame)
        self.commandEntry.place(x=180,y=210, width=355,height=25)
        self.commandEntry.bind("<Return>",self.sendButton)
        self.commandSend = tk.Button(self.serialFrame,text="Send",command=self.sendButton)
        self.commandSend.place(x=545,y=210, width=50,height=25)

        self.serialConnection = None
        self.serialThread = None

        self.serialFolderBrowser = ttk.Combobox(self.serialFrame, postcommand=self.updateSerialBlockList)
        self.serialFolderBrowser.place(x = 5, y=125, width = 160, height = 20)
        self.serialFolderBrowser.bind("<<ComboboxSelected>>", self.updateSerialFileList)

        self.serialFileBrowser = tk.Listbox(self.serialFrame)
        self.serialFileBrowser.place(x = 5, y = 150, width = 160, height = 70)

        self.blockSend = tk.Button(self.serialFrame,text="Send Block",command=self.sendBlock)
        self.blockSend.place(x=180,y=175, width=80,height=25)
        
        self.auto_scroll = tk.BooleanVar()
        self.auto_scroll.set(True)
        
        self.autoScrollBox = tk.Checkbutton(self.serialFrame, text="Auto Scroll", variable=self.auto_scroll)
        self.autoScrollBox.place(x=5,y=220)

        self.auto_send = tk.BooleanVar()
        self.auto_send.set(False)
        
        self.autoSendBox = tk.Checkbutton(self.serialFrame, text="Auto Send", variable=self.auto_send)
        self.autoSendBox.place(x=270,y=175)

        self.update_menu()

        thread = threading.Thread(target=self.monitor_ports)
        thread.start()
        
        self.notebook.add(self.serialTab, text=" Serial ")

        ##### End Automations #####
        self.root.mainloop()

    def compareStrings(self):
        text1 = self.string1Entry.get()
        text2 = self.string2Entry.get()

        metSpace = False
        for i, (a, b) in enumerate(zip(text1, text2)):
            if metSpace:
                self.comparisonOutput.insert(tk.END, a)
            else:
                metSpace = a == " " or b == " "
                if a == b:
                    self.comparisonOutput.insert(tk.END, a, 'green')
                else:
                    self.comparisonOutput.insert(tk.END, a, 'red')

        if len(text1) > len(text2):
            for i in range(len(text2), len(text1)):
                if metSpace:
                    self.comparisonOutput.insert(tk.END, text1[i])
                else:
                    self.comparisonOutput.insert(tk.END, text1[i], 'red')
                
        self.comparisonOutput.insert(tk.END,"\n")
        metSpace = False
        for i, (a, b) in enumerate(zip(text1, text2)):
            if metSpace:
                self.comparisonOutput.insert(tk.END, b)
            else:
                metSpace = a == " " or b == " "
                if a == b:
                    self.comparisonOutput.insert(tk.END, b, 'green')
                else:
                    self.comparisonOutput.insert(tk.END, b, 'red')
        
        if len(text1) < len(text2):
            for i in range(len(text1), len(text2)):
                if metSpace:
                    self.comparisonOutput.insert(tk.END, text2[i])
                else:
                    self.comparisonOutput.insert(tk.END, text2[i], 'red')

        self.comparisonOutput.insert(tk.END,"\n")
        
        
    def sendButton(self,e=None):
        userInput = self.commandEntry.get()
        self.send_data(userInput)

    def sendBlock(self):
        thread = threading.Thread(target=self.runBlockToUnit)
        thread.start()

    def runBlockToUnit(self):
        try:
            selected_file = self.serialFileBrowser.get(self.serialFileBrowser.curselection())
            folder = self.serialFolderBrowser.get()
            path = f"{username}/Blocks/{folder}/{selected_file}.block"
        
            with open(path,'r') as f_:
                lines = f_.read().split("\n")
                for line in lines:
                    self.send_data(line)
                    time.sleep(1)
        except:
            self.updateSerialText("Auto Not Selected","Error")
                
    def readSerialData(self):
        while self.serialConnection:
            try:
                data = self.serialConnection.readline().decode().strip()
                if data:
                    self.updateSerialText(data)
            except Exception as E:
                self.handlePort()
                self.updateSerialText(E,"Error")
                
    def handlePort(self):
        try:
            if self.portOpen:
                self.openPortButton.config(text="Open Port")
                self.serialConnection.close()
                self.serialConnection = None
                self.comActiveIndicator.config(text="Inactive",foreground="red")
            else:
                self.openPortButton.config(text="Close Port")
                self.serialConnection = serial.Serial(self.comPort.get(),int(self.baudRate.get()),timeout=1)
                self.serialThread = threading.Thread(target=self.readSerialData)
                self.serialThread.start()
                self.comActiveIndicator.config(text="Active",foreground="green")
                
            self.portOpen = not(self.portOpen)
        except Exception as E:
            self.updateSerialText(E,"Error")
            
    def update_menu(self):
        current_ports = set(serial.tools.list_ports.comports())
        current_selection = self.comPort.get()

        self.comMenu["menu"].delete(0, "end")
        for port in current_ports:
            self.comMenu["menu"].add_command(label=port.device, command=lambda port=port: self.comPort.set(port.device))
            if port.device == current_selection or len(current_ports) == 1:
                self.comPort.set(port.device)

                if self.auto_send.get():
                    self.openPortButton.config(text="Close Port")
                    self.serialConnection = serial.Serial(self.comPort.get(),int(self.baudRate.get()),timeout=1)
                    self.serialThread = threading.Thread(target=self.readSerialData)
                    self.serialThread.start()
                    self.comActiveIndicator.config(text="Active",foreground="green")
                    self.portOpen = True

                    self.sendBlock()
        
    def monitor_ports(self):
        previous_ports = set(serial.tools.list_ports.comports())
        while True:
            current_ports = set(serial.tools.list_ports.comports())
            newly_connected_ports = current_ports - previous_ports
            disconnected_ports = previous_ports - current_ports

            if disconnected_ports:
                for port in disconnected_ports:
                    print(f"A device has been disconnected from {port.device}")
                    self.update_menu()
            
            if newly_connected_ports:
                for port in newly_connected_ports:
                    print(f"A device has been connected to {port.device}")
                    self.update_menu()

            previous_ports = current_ports
            time.sleep(1)
        
    def updateSerialText(self,data,tags=""):
        self.display_text.config(state="normal")
        self.display_text.insert("end", str(data) + "\n", tags)
        self.display_text.config(state="disabled")
        if self.auto_scroll.get():
            self.display_text.see(tk.END)

    def readSerial(self):
        while True:
            data = self.serialConnection.readline().decode('utf-8').strip()
            if data:
                updateSerialText(data)

    def send_data(self, user_input):
        try:
            self.serialConnection.write(user_input.encode('utf-8'))
            self.updateSerialText(user_input, "Office")
        except Exception as E:
            self.updateSerialText(E, "Error")
            
    def copy_sys_mileage(self):
        sys_mileage = self.sysMileageOutput.cget("text")
        self.root.clipboard_clear()
        self.root.clipboard_append(sys_mileage)
        self.root.update()

    def copy_gps_mileage(self):
        sys_mileage = self.gpsMileageOutput.cget("text")
        self.root.clipboard_clear()
        self.root.clipboard_append(sys_mileage)
        self.root.update()

    def updateKilos(self, *args):
        if not self.isMilesUpdating:
            self.isKilometersUpdating = True
            miles = self.miles.get()
            if miles:
                if '.' in miles:
                    fmiles = float(miles)
                else:
                    fmiles = int(miles)
                kilometers = fmiles * 1.60934
                self.kilometers.set(kilometers)
                self.updateSYSMileage()
                self.updateGPSMileage()
            self.isKilometersUpdating = False
        
    def updateMiles(self, *args):
        if not self.isKilometersUpdating:
            self.isMilesUpdating = True
            kilometers = self.kilometers.get()
            if kilometers:
                if '.' in kilometers:
                    fkilometers = float(kilometers)
                else:
                    fkilometers = int(kilometers)
                miles = fkilometers / 1.60934
                self.miles.set(miles)
                self.updateSYSMileage()
                self.updateGPSMileage()
            self.isMilesUpdating = False
    
    def updateSYSMileage(self):
        numeric_value = float(self.kilometers.get())
        sys_mileage = 'o2w,14,840500' + format(int(math.floor(1000*numeric_value)), '08x')
        self.sysMileageOutput.config(text=sys_mileage)

    def updateGPSMileage(self):
        numeric_value = float(self.kilometers.get())
        gps_mileage = 'o2w,16,B806' + format(int(math.floor(1000*numeric_value)), '08x') + '0400'
        self.gpsMileageOutput.config(text=gps_mileage)

    def updateFileListButton(self):
        self.updateFileList(None)
        
    def openFileButton(self):
        self.openFile(None)
        
    def saveFile(self):
        title = self.titleEntry.get()
        folder = self.folderBrowser.get()
        content = self.textArea.get("1.0", tk.END)
        path = f"{username}/Blocks/{folder}/{title}.block"

        try:
            with open(path, "w") as file:
                file.write(content)
            self.fileBrowser.insert(tk.END, title)
            print("File saved!")
        except:
            print("Error: File could not be saved")        

    def removeFile(self):
        selected_file = self.fileBrowser.get(self.fileBrowser.curselection())
        folder = self.folderBrowser.get()
        path = f"{username}/Blocks/{folder}/{selected_file}.block"
        try:
            os.remove(path)
            self.fileBrowser.delete(self.fileBrowser.curselection())
            print("File deleted!")
        except:
            print("File not found")
        
    def openFile(self, event):
        try:
            selected_file = self.fileBrowser.get(self.fileBrowser.curselection())
            folder = self.folderBrowser.get()
            path = f"{username}/Blocks/{folder}/{selected_file}.block"
            try:
                with open(path, 'r') as file:
                    data = file.read()
            except:
                data = "File not found"

            self.titleEntry.delete(0, tk.END)
            self.titleEntry.insert(tk.END, selected_file)
            self.textArea.delete("1.0", tk.END)
            self.textArea.insert(tk.END, data)
        except:
            pass
    
    def updateFileList(self,e):
        folder = self.folderBrowser.get()
        fileList = os.listdir(f"{username}/Blocks/{folder}")

        self.fileBrowser.delete(0,tk.END)

        for i,item in enumerate(fileList):
            if item.endswith(".block"):
                self.fileBrowser.insert(i,item.replace(".block",""))
        
    def updateBlockList(self):
        values = ["."]
        for file in os.scandir(f"{username}/Blocks"):
            if file.is_dir():
                values.append(file.name)
    
        self.folderBrowser.configure(values=values)

    def updateSerialFileList(self,e):
        folder = self.serialFolderBrowser.get()
        fileList = os.listdir(f"{username}/Blocks/{folder}")

        self.serialFileBrowser.delete(0,tk.END)

        for i,item in enumerate(fileList):
            if item.endswith(".block"):
                self.serialFileBrowser.insert(i,item.replace(".block",""))
                
    def updateSerialBlockList(self):
        values = ["."]
        for file in os.scandir(f"{username}/Blocks"):
            if file.is_dir():
                values.append(file.name)
    
        self.serialFolderBrowser.configure(values=values)

if __name__ == "__main__":
    App()
