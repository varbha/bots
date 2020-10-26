# TODO
## create issue hook for action = updated [ for label change ]
## ePMS connection and design/implementation discussion
## add list of avaliable [/command] (s) availaible for that page in greeting
## integrate shell scripts instead of dummy data 
## MR - action = opened, reopen, close
## change labels as per decided git workflow
## create issue board when MR is created
## put greetings into another file

# TODO-BUGS
## Commit update on MR causes the creation of new Issue

from gidgetlab.aiohttp import GitLabBot
import json
import urllib.parse
import os
import subprocess
import time

bot = GitLabBot("xpt-bot")

async def checkOrCreateLabels(gl, event):
    """check if project labels exist, and create new labels if they dont exist"""

    url = f"/projects/{event.project_id}/labels"
    exist_flag = 0
    labels = [i async for i in gl.getiter(url)]
    for dict_item in labels:
        for item in dict_item.items():
            if item[0] == 'name':
                if item[1] in ['MR1 :: created', 'MR1 :: completed', 'Maven Deploy :: pending', 'Maven Deploy :: completed', 'Configuration Team Confirmation :: pending', 'Configuration Team Confirmation :: completed', 'Operations team Confirmation :: pending', 'Operations team Confirmation :: completed', 'MR2 :: pending', '"MR2 :: completed'] :
                    exist_flag = 1
                    break
    if exist_flag == 0 :
        await gl.post(url, data={"name":"MR1 :: created", "color": "#428BCA", "description" : "Added when MR1 has been created"})
        await gl.post(url, data={"name":"MR1 :: completed", "color": "#AD8D43", "description" : "Added when MR1 has been completed"})
        await gl.post(url, data={"name":"Maven Deploy :: pending", "color": "#A8D695", "description" : "Added when Nexus deployment is pending"})
        await gl.post(url, data={"name":"Maven Deploy :: completed", "color": "#5CB85C", "description" : "Added when Nexus deployment has been created"})
        await gl.post(url, data={"name":"Configuration Team Confirmation :: pending", "color": "#FF0000", "description" : "Added when configuration team confirmation is pending"})
        await gl.post(url, data={"name":"Configuration Team Confirmation :: completed", "color": "#FF0000", "description" : "Added when configuration teams confirmation has been recieved"})
        await gl.post(url, data={"name":"Operations team Confirmation :: pending", "color": "#428BCA", "description" : "Added when Operations teams' confirmation is pending"})
        await gl.post(url, data={"name":"Operations team Confirmation :: completed", "color": "#428BCA", "description" : "Added when Operations teams' confirmation has been recieved"})
        await gl.post(url, data={"name":"MR2 :: pending", "color": "#D1D100", "description" : "Added when MR2 has not been performed"})
        await gl.post(url, data={"name":"MR2 :: completed", "color": "#D1D100", "description" : "Added when MR2 has been created = end of STUP"})

 
async def createIssueGreeting(gl, event):
    """create markdown greeting whenever issue is created"""
    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}/notes"
    message = f"Thanks for the report @{event.data['user']['username']}! I have created the desciption and labels for this issue, while also linking it to your merge request(MR). (I'm a bot). \n\n このIssueの説明とラベルを作成し、マージリクエスト（MR）にもリンクしました。 （私はボットです）\n\n ---\n\n  If there are any issues, please contact either @varbha or @taeho911 . \n\n If you want to contribute to this bot, please contact @varbha \n "
    
    await gl.post(url, data={"body": message})

async def createIssueGreetingForUpdate(gl, event):
    """create markdown greeting whenever issue is updated - remind to change labels if required"""
    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}/notes"
    message = f"Reminder : @{event.data['user']['username']}, please don't forget to remove redundant labels. (I'm a bot). \n\n---\n  If there are any issues, please contact either @varbha or @taeho911 . \n\n If you want to contribute to this bot, please contact @varbha \n\n  リマインダー： @{event.data['user']['username']}, 冗長なラベルを削除することを忘れないでください。 （私はボットです） \n\n  問題がある場合は、@varbha または @taeho911 に連絡してください \n\n  このボットに貢献したい場合は、@varbha に連絡してください \n "
    
    await gl.post(url, data={"body": message})

async def createMergeRequestGreeting(gl,event, jsonStr):
    """create markdown greeting whenever MR is created"""
    webhook_payload = json.loads(jsonStr)
    merge_iid = webhook_payload['data']['object_attributes']['iid']

    url = f"/projects/{event.project_id}/merge_requests/{merge_iid}/notes"
    message = f"Merge Request created succesfully.\n\n  The default project issue has also been created - use it to track your project across different stages!\n\n  (I'm a bot). \n\n このIssueの説明とラベルを作成し、マージリクエスト（MR）にもリンクしました。 （私はボットです）\n\n ---\n\n  If there are any issues, please contact either @varbha or @taeho911 . \n\n If you want to contribute to this bot, please contact @varbha \n "
    
    await gl.post(url, data={"body": message})

async def createMarkdown(gl, event):
    """create markdown whenever MR is created"""
    with open("markdown.txt", 'r') as file:
        line = file.read()

    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}/notes"
    message = line

    await gl.post(url, data={"body": message})

async def createMarkdownForMergeRequest(gl, event, project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace):
    """create markdown whenever MR is created"""

    if os.name != 'nt' :
        await createMarkdownForMergeRequest_linux(gl, event, project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace)
    else:
        # fileToShellFile = os.chdir(os.getcwd() + '\/helpers')
        with open("markdown.txt", 'r') as file:
            line = file.read()

        url = f"/projects/{event.project_id}/merge_requests/{merge_iid}/notes"
        message = line

        await gl.post(url, data={"body": message})

async def createMarkdownForMergeRequest_linux(gl, event, project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace):
    """create markdown whenever MR is created (if application is running in an linux environment)"""
    
    # add git credentials to clone url
    replacementString =  'https://' + os.environ.get('GIT_USER') + ':' + os.environ.get('GIT_PASS') + '@'
    gitlab_clone_url = gitlab_clone_url.replace("https://", replacementString)
    # add namespace folder name
    namespace = path_with_namespace[path_with_namespace.rindex('/') + 1:]
    print("Namespace : " + namespace)
    print(gitlab_clone_url)

    ts = time.gmtime()
    now = time.strftime("%Y%m%d%H%M%S", ts)
    # commandString = f"./create_markdown.sh {gitlab_clone_url} {namespace} {target_branch} {source_branch} {now}"
    subprocess.call(['bash', './mr_maker.sh', gitlab_clone_url, namespace, target_branch, source_branch, now])
    
    # file at /usr/src/app
    with open("markdown-linux.txt", 'r') as file:
        line = file.read()
    
    url = f"/projects/{event.project_id}/merge_requests/{merge_iid}/notes"
    message = line

    await gl.post(url, data={"body": message})



async def createMarkdownDescription(gl, event):
    """create marksdown whenever MR is created"""
    with open("desc.txt", 'r') as file:
        line = file.read()

    '''encode line to URI compatible strings'''
    query = urllib.parse.quote(line, safe='')

    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}?description={query}"
    
    await gl.put(url)

async def generate_metadata(gl, event, jsonStr):
    """extract metadata from JSON payload"""
    webhook_payload = json.loads(jsonStr)

    project_id = event.project_id
    gitlab_clone_url = webhook_payload['data']['object_attributes']['source']['git_http_url']
    namespace = webhook_payload['data']['object_attributes']['source']['namespace']
    source_branch = webhook_payload['data']['object_attributes']['source_branch']
    target_branch = webhook_payload['data']['object_attributes']['target_branch']
    merge_iid = webhook_payload['data']['object_attributes']['iid']
    merge_error  = webhook_payload['data']['object_attributes']['merge_error']
    path_with_namespace = webhook_payload['data']['object_attributes']['source']['path_with_namespace']

    return [project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace]


async def createNewIssue(gl, event, jsonStr, project_id, namespace, merge_iid, source_branch, path_with_namespace ):
    """create new issue for corresponding MR"""

    url = f"/projects/{project_id}/issues"
    description = f"Default Issue [{source_branch}] for MR !{merge_iid}"

    '''check for existing labels'''
    await checkOrCreateLabels(gl,event)

    labels = "MR1 :: created, Maven Deploy :: pending, Configuration Team Confirmation :: pending, Operations team Confirmation :: pending, MR2 :: pending"
    milestone_id = path_with_namespace.split('/')[2]
    due_date = f"{path_with_namespace.split('/')[2][:4]}-{path_with_namespace.split('/')[2][4:6]}-{path_with_namespace.split('/')[2][6:]}"
    
    await gl.post(url, params={"title": description, "description": description, "labels": labels, "milestone_id" : milestone_id, "due_date":due_date}, data={})


async def executeCommandForMergeRequest(gl, event, jsonStr, note):
    if '/createDiff' in note:
        webhook_payload = json.loads(jsonStr)

        project_id = event.project_id
        gitlab_clone_url = webhook_payload['data']['merge_request']['source']['git_http_url']
        namespace = webhook_payload['data']['merge_request']['source']['namespace']
        source_branch = webhook_payload['data']['merge_request']['source_branch']
        target_branch = webhook_payload['data']['merge_request']['target_branch']
        merge_iid = webhook_payload['data']['merge_request']['iid']
        merge_error  = webhook_payload['data']['merge_request']['merge_error']
        path_with_namespace = webhook_payload['data']['merge_request']['source']['path_with_namespace']

        await createMarkdownForMergeRequest(gl, event, project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace)


@bot.router.register("Issue Hook", action="open")
async def issue_opened_event(event, gl, *args, **kwargs):
    """Whenever an issue is opened"""
    jsonStr = json.dumps(event.__dict__)
    await createIssueGreeting(gl, event);

    title = (json.loads(jsonStr))['data']['object_attributes']['title']
    if(not "!" in ((json.loads(jsonStr))['data']['object_attributes']['title'])):
        await createMarkdown(gl, event);

    await createMarkdownDescription(gl, event);

@bot.router.register("Issue Hook", action="update")
async def issue_updated_event(event, gl, *args, **kwargs):
    """Whenever an issue is updated, add a reminder to remove unecessary labels"""
    jsonStr = json.dumps(event.__dict__)
    await createIssueGreetingForUpdate(gl, event);


@bot.router.register("Merge Request Hook", state="opened")
async def merge_request_created_event(event, gl, *args, **kwargs):
    """Whenever a merge request is created, update the MR and create a new default issue"""
    jsonStr = json.dumps(event.__dict__)
    
    '''create new default issue for newly created MR'''
    project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace = await generate_metadata(gl, event, jsonStr)
    await createNewIssue(gl, event, jsonStr, project_id, namespace, merge_iid, source_branch, path_with_namespace )
    
    '''create greeting for MR'''
    await createMergeRequestGreeting(gl,event, jsonStr) 

    await createMarkdownForMergeRequest(gl, event, project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace )

#    await createMarkdownMR(gl, event, jsonStr)
#    await createMarkdownDescriptionMR(gl,event,jsonStr)
#    await createLabels(gl, event, jsonStr)


@bot.router.register("Note Hook")
async def note_created_event(event, gl, *args, **kwargs):
    """Whenever a note is created, define the type of note and follow up"""
    jsonStr = json.dumps(event.__dict__)
    noteable_type = json.loads(jsonStr)['data']['object_attributes']['noteable_type']
    print(noteable_type)
    if noteable_type == 'MergeRequest':
        if ((json.loads(jsonStr)['data']['object_attributes']['note']) in ['/listSTickets', '/createDiff']) or ('/createRTicket' in (json.loads(jsonStr)['data']['object_attributes']['note'])):
            print((json.loads(jsonStr)['data']['object_attributes']['note']))
            await executeCommandForMergeRequest(gl, event, jsonStr, (json.loads(jsonStr)['data']['object_attributes']['note']))
    


if __name__ == "__main__":
    bot.run()
