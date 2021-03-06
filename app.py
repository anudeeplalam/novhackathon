from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import requests
import jenkins
import json
import time
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    baseurl = "http://35.185.49.228:9090"
    username = "hackadmin"
    token = "b3e2a79dfc1d7186e35744c2016fd899"

    if req.get("result").get("action") == "startbuild":
        jobname = getjobname(req)
        server = jenkins.Jenkins(baseurl, username=username, password=token)
        try:
            result = server.build_job(jobname)
            time.sleep(2)
            if not result:
                jenkins_url = baseurl + "/job/" + jobname + "/api/json"
                result = urlopen(jenkins_url).read()
                data = json.loads(result)
                lastBuild = data["lastBuild"]["number"]
                output = "Successfully started the build " + str(lastBuild) + " for " + jobname + " project"
        except Exception as e:
            output = "Failed to start the build of " + jobname + \
                     " becasue of " + str(e)
        res = makeWebhookResult(output)
        return res

    if req.get("result").get("action") == "jobdetails":
        jobname = getjobname(req)
        jenkins_url = baseurl + "/job/" + jobname + "/api/json"
        result = urlopen(jenkins_url).read()
        data = json.loads(result)
        output = getJobDetails(data)
        res = makeWebhookResult(output)
        return res

    if req.get("result").get("action") == "listalljobs":
        jenkins_url = baseurl + "/api/json"
        result = urlopen(jenkins_url).read()
        data = json.loads(result)
        output = getAllJobs(data)
        res = makeWebhookResult(output)
        return res

    if req.get("result").get("action") == "getjobinfo":
        jenkins_url = baseurl + "/api/json"
        result = urlopen(jenkins_url).read()
        data = json.loads(result)
        output = getJobInfo(data)
        res = makeWebhookResult(output)
        return res


def getjobname(req):
    result = req.get("result")
    parameters = result.get("parameters")
    jobname = parameters.get("jobs")
    return jobname


def getJobDetails(data):
    lastBuild = data["lastBuild"]["number"]
    lastStableBuild = data["lastStableBuild"]["number"]
    output = "Total Number of Builds are: " + str(lastBuild) + \
             "\nLast Stable Build is: " + str(lastStableBuild)
    return output


def getJobInfo(data):
    allJobs = []

    for job in data['jobs']:
        allJobs.append(job['name'])

    output = "Your Jenkins instance has " + str(len(allJobs)) + " jobs.\n" + \
             "Would you like me to list all jobs?"
    return(output)


def getAllJobs(data):
    allJobs = []
    #jsonbody = ""

    for job in data['jobs']:
        allJobs.append(job['name'])
    
    #for job in allJobs:
        #jsonbody = jsonbody + "{\"value\":\"" + str(job) + "\"},"

    output = "\n".join(allJobs)
    #url = "https://api.dialogflow.com/v1/entities/"
    #headers = {"Content-Type":"application/json","Authorization":"Bearer d9bd5f4be39d43bd80b24099151305db"}
    #body = {"entries": "[" + jsonbody + "]","name": "jobs"}
    #pprint(body)
    #r = requests.put(url, data=json.dumps(body), headers=headers)
    return(output)


def makeWebhookResult(output):
    print("Response:")
    print(output)

    return {
        "speech": output,
        "displayText": output,
        "source": "jenkins-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
