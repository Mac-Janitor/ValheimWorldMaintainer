import json
import base64
import requests

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

def determine_host(filename, repo, branch, token):
    url="https://api.github.com/repos/"+repo+"/contents/"+filename

    data = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})

    textLines = data.text.splitlines()
    if textLines[-1].startswith("Checked In"):
        return True
    return False  

def download_world_files(worldName, repo, branch, token, gamePath):
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
    files = response.json()["tree"]

    # Copy each world file
    for file in files:
        fileName = str(file["path"])
        if fileName.startswith(worldName):
            sha = file["sha"]
            print("Success!")
            bytes = requests.get(url+'git/blobs/'+sha, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"}).content
            f = open(gamePath+"/"+fileName, "wb")
            f.write(bytes)
            f.close()

def push_to_github(filename, repo, branch, token):
    url="https://api.github.com/repos/"+repo+"/contents/"+filename

    base64content=base64.b64encode(open(filename,"rb").read())

    data = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token}).json()
    sha = data['sha']

    if base64content.decode('utf-8')+"\n" != data['content']:
        message = json.dumps({"message":"update",
                            "branch": branch,
                            "content": base64content.decode("utf-8") ,
                            "sha": sha
                            })

        resp=requests.put(url, data = message, headers = {"Content-Type": "application/json", "Authorization": "token "+token})

        print(resp)
    else:
        print("nothing to update")

token = config["git"]["token"]
logFileName= config["git"]["logFileName"]
repo = config["git"]["repo"]
branch = config["git"]["branch"]
worldName = config["valheim"]["worldName"]
gamePath = config["valheim"]["path"]

push_to_github(logFileName, repo, branch, token)

host = determine_host(logFileName, repo, branch, token)
if host == True:
    print("You da host")
    download_world_files(worldName, repo, branch, token, gamePath)
else:
    print("You NOT da host")

