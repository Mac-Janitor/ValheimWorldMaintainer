import json
import base64
import requests

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

host = False

def pull_from_github(filename, repo, branch, token):
    global host
    url="https://api.github.com/repos/"+repo+"/contents/"+filename

    data = requests.get(url+'?ref='+branch, headers = {"Authorization": "token "+token, "Accept": "application/vnd.github.v3.raw"})

    textLines = data.text.splitlines()
    if textLines[-1].startswith("Checked In"):
        host = True
    print(textLines[-1])
    if host == True:
        print("You da host")
        # download_file(filename, repo, branch, token)

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
filename= config["git"]["filename"]
repo = config["git"]["repo"]
branch = config["git"]["branch"]

pull_from_github(filename, repo, branch, token)
# push_to_github(filename, repo, branch, token)