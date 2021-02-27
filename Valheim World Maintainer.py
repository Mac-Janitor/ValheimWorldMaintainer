import tkinter as tk
import shutil 
import glob
import os
import git

root= tk.Tk()

canvas = tk.Canvas(root, width = 800, height = 600,  relief = 'raised')
canvas.pack()

headerLabel = tk.Label(root, text='Transfer Valheim World With Git Repo')
headerLabel.config(font=('helvetica', 14))
canvas.create_window(400, 25, window=headerLabel)

worldNameLabel = tk.Label(root, text='Enter The Name of Your World:')
worldNameLabel.config(font=('helvetica', 10))
canvas.create_window(400, 100, window=worldNameLabel)

worldNameEntry = tk.Entry (root) 
canvas.create_window(400, 140, window=worldNameEntry)

windowsPathLabel = tk.Label(root, text='Enter The Path To Your Valheim World Directory:')
windowsPathLabel.config(font=('helvetica', 10))
canvas.create_window(400, 180, window=windowsPathLabel)

windowsEntry = tk.Entry (root) 
canvas.create_window(400, 220, window=windowsEntry)

gitRepoLabel = tk.Label(root, text='Enter The URL To Your Git Repository:')
gitRepoLabel.config(font=('helvetica', 10))
canvas.create_window(400, 260, window=gitRepoLabel)

gitEntry = tk.Entry (root) 
canvas.create_window(400, 300, window=gitEntry)

def getDirectories():
    valheimDirectory = windowsEntry.get()

    gitRepoURL = gitEntry.get()

    # repo = Repo("https://github.com/Mac-Janitor/ValheimHelloWorld.git", odbt=GitDB)

    os.chdir(valheimDirectory)
    filenamesList = glob.glob(worldNameEntry.get() + '*')
    for filename in filenamesList:
        print("Copying " + filename)
        shutil.copyfile(valheimDirectory + "\\" + filename, gitRepoURL + "\\" + filename)
    
startGameButton = tk.Button(text='Decide Server Owner and Start Valheim', command=getDirectories, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas.create_window(400, 340, window=startGameButton)

root.mainloop()