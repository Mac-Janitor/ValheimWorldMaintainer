import json
import base64
import requests
import tempfile
import getpass
import datetime
import subprocess
import time
import psutil

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

global fileNames
fileNames = []

def determine_host(filename, repo, branch, token):
    url="https://api.github.com/repos/"+repo+"/contents/"+filename

    data = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})

    textLines = data.text.splitlines()
    if textLines[-1].startswith("Checked In"):
        return True
    return False 

def get_git_files(worldName, repo, branch, token):
    url="https://api.github.com/repos/"+repo+"/"

    # Get the sha of the latest commit
    response = requests.get(url+'git/refs/heads/'+branch, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})
    sha = response.json()["object"]["sha"]
    print(sha)

    # Get the commit info to get the sha of the tree
    response = requests.get(url+'git/commits/'+sha, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})
    sha = response.json()["tree"]["sha"]
    print (sha)

    # Get the contents of the tree
    response = requests.get(url+'git/trees/'+sha, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})
    return response.json()["tree"]

def download_world_files(worldName, repo, branch, token, worldPath):
    url="https://api.github.com/repos/"+repo+"/"
    global fileNames
    files = get_git_files(worldName, repo, branch, token)

    # Copy each world file
    for file in files:
        fileName = str(file["path"])
        if fileName.startswith(worldName):
            fileNames.append(fileName)
            sha = file["sha"]
            print("Success!")
            bytes = requests.get(url+'git/blobs/'+sha, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"}).content
            f = open(worldPath+"/"+fileName, "wb")
            f.write(bytes)
            f.close()

def upload_world_files(worldPath, repo, branch, token):
    files = get_git_files(worldName, repo, branch, token)
    global fileNames

    for file in files:
        fileName = str(file["path"])
        if fileName.startswith(worldName):  
            sha = file["sha"]
            push_to_github(worldPath, fileName, repo, branch, token, sha)

def push_to_github(pathToFile, filename, repo, branch, token, sha):
    url="https://api.github.com/repos/"+repo+"/contents/"+filename

    filePath = filename
    if pathToFile != "":
        filePath = pathToFile+"\\"+filename

    base64content=base64.b64encode(open(filePath,"rb").read())

    # if base64content.decode('utf-8')+"\n" != data['content']:
    message = json.dumps({"message":"update",
                        "branch": branch,
                        "content": base64content.decode("utf-8") ,
                        "sha": sha
                        })

    resp=requests.put(url, data = message, headers = {"Content-Type": "application/json", "Authorization": "token "+token})

    print(resp)

def update_log_file(action, filename, repo, branch, token):
    url="https://api.github.com/repos/"+repo+"/contents/"+filename

    response = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})

    f = open(tempfile.gettempdir()+"/"+filename, "wb")
    f.write(response.content)
    f.close()

    f = open(tempfile.gettempdir()+"/"+filename, "a")
    f.write("\n" + action + " By "+getpass.getuser()+" "+str(datetime.datetime.now()))
    f.close()    

    response = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token})

    push_to_github(tempfile.gettempdir(), filename, repo, branch, token, response.json()["sha"])

def wait_for_process(name):
    time.sleep(5)
    run = True
    while run:
        run = False
        for proc in psutil.process_iter():
            if name in proc.name():
                run = True
                time.sleep(1.0)

token = config["git"]["token"]
logFileName= config["git"]["logFileName"]
repo = config["git"]["repo"]
branch = config["git"]["branch"]
worldName = config["valheim"]["worldName"]
worldPath = config["valheim"]["worldPath"]
steamPath = config["valheim"]["steamPath"]
appID = config["valheim"]["appID"]
gamePath = config["valheim"]["gamePath"]

host = determine_host(logFileName, repo, branch, token)
if host == True:
    print("You da host")
    update_log_file("Checked Out", logFileName, repo, branch, token)
    download_world_files(worldName, repo, branch, token, worldPath)

    process = subprocess.Popen(steamPath + "\steam.exe -applaunch " + appID)
    wait_for_process("valheim")

    print("Game has ended")
    upload_world_files(worldPath, repo, branch, token)
    update_log_file("Checked In", logFileName, repo, branch, token)
else:
    print("You NOT da host")

    process = subprocess.Popen(steamPath + "\steam.exe -applaunch " + appID)
    wait_for_process("valheim")