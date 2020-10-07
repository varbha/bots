from gidgetlab.aiohttp import GitLabBot
import json
import urllib.parse

bot = GitLabBot("xpt-bot", access_token="")

async def createIssueGreeting(gl, event):
    """create marksdown whenever MR is created"""
    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}/notes"
    message = f"Thanks for the report @{event.data['user']['username']}! I will look into it ASAP! (I'm a bot). \n\n If there are any issues, please contact @taeho911 . \n\n If you want to contribute to this bot, please contact @varbha \n "
    await gl.post(url, data={"body": message})

async def createMarkdown(gl, event):
    """create marksdown whenever MR is created"""
    with open("markdown.txt", 'r') as file:
        line = file.read()
#        message += line;
#    print(line);
    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}/notes"
    # message = f"Thanks for the report @{event.data['user']['username']}! I will look into it ASAP! (I'm a bot). \n\n If there are any issues, please contact @taeho911 . \n\n If you want to contribute to this bot, please contact @varbha \n "
    message = line;
    await gl.post(url, data={"body": message})

async def createMarkdownDescription(gl, event):
    """create marksdown whenever MR is created"""
    with open("desc.txt", 'r') as file:
        line = file.read()
#        message += line;
#    print(line);
    query = urllib.parse.quote(line, safe='');
#    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}?description=ABBAAA%0A%0AABBA"
    url = f"/projects/{event.project_id}/issues/{event.object_attributes['iid']}?description={query}"
    print(url)
    message = f"Thanks for the report @{event.data['user']['username']}! I will look into it ASAP! (I'm a bot). \n\n If there are any issues, please contact @taeho911 . \n\n If you want to contribute to this bot, please contact @varbha \n "
    #message = line;
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

    return [project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace ]


async def createNewIssue(gl, event, jsonStr, project_id, namespace, merge_iid, source_branch, path_with_namespace ):
    """create new issue for corresponding MR"""
    url = f"/projects/{project_id}/issues"
    print(url)
    description = f"Default Issue [{source_branch}] for MR !{merge_iid}"
    labels = "default-issue, MR-created"
    milestone_id = path_with_namespace.split('/')[2]
    due_date = f"{path_with_namespace.split('/')[2][:4]}-{path_with_namespace.split('/')[2][4:6]}-{path_with_namespace.split('/')[2][6:]}"
    print(due_date)
    await gl.post(url, params={"title": description, "description": description, "labels": labels, "milestone_id" : milestone_id, "due_date":due_date}, data={})


@bot.router.register("Issue Hook", action="open")
async def issue_opened_event(event, gl, *args, **kwargs):
    """Whenever an issue is opened"""
    jsonStr = json.dumps(event.__dict__)
#    print(jsonStr)

    await createIssueGreeting(gl, event);
    title = (json.loads(jsonStr))['data']['object_attributes']['title']
    print(title)

    if(not "!" in ((json.loads(jsonStr))['data']['object_attributes']['title'])):
        await createMarkdown(gl, event);
    await createMarkdownDescription(gl, event);

@bot.router.register("Merge Request Hook", state="opened")
async def merge_request_created_event(event, gl, *args, **kwargs):
    """Whenever a merge request is created"""
    jsonStr = json.dumps(event.__dict__)
    print('---------Merge Request Created-------')
    print(jsonStr)
    project_id, gitlab_clone_url, namespace, source_branch, target_branch, merge_iid, merge_error, path_with_namespace = await generate_metadata(gl, event, jsonStr)
    print(source_branch)
    await createNewIssue(gl, event, jsonStr, project_id, namespace, merge_iid, source_branch, path_with_namespace )

#    await createMarkdownMR(gl, event, jsonStr)
#    await createMarkdownDescriptionMR(gl,event,jsonStr)
#    await createLabels(gl, event, jsonStr)


# @bot.router.register("Note Hook")
# async def comment_created_event(event, gl, *args, **kwargs):
#    """Whenever a new comment is created"""
#    jsonStr = json.dumps(event.__dict__)
#
#    if(jsonStr.object_attributes.noteable_type == "MergeRequest"):
#        generate_metadata_merge_request(gl, event, jsonStr)
#    
#    if(jsonStr.object_attributes.noteable_type == "Issue"):
#        generate_metadat_issue(gl, event, jsonStr)

#    await generate_metadata(gl, event, jsonStr)
#    await createNewIssue(gl, event, jsonStr)
#    await createMarkdownMR(gl, event, jsonStr)
#    await createMarkdownDescriptionMR(gl,event,jsonStr)
#    await createLabels(gl, event, jsonStr)
    


if __name__ == "__main__":
    bot.run()
