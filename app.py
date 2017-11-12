from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
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
    baseurl = "http://104.196.56.147:9090"

    if req.get("result").get("action") != "jobdetails":
        jobname = getjobname(req)
        jenkins_url = baseurl + "/job/" + jobname + "/api/json"
        result = urlopen(jenkins_url).read()
        data = json.loads(result)
        output = getJobDetails(data)
        res = makeWebhookResult(output)
        return res

    if req.get("result").get("action") != "listalljobs":
        jenkins_url = baseurl + "/api/json"
        result = urlopen(jenkins_url).read()
        data = json.loads(result)
        output = getAllJobs(data)
        res = makeWebhookResult(output)
        return res

def getjobname(req):
    result = req.get("result")
    parameters = result.get("parameters")
    jobname = parameters.get("jobs")
    return jobname


def getJobDetails(data):
    displayName = data["displayName"]
    lastStableBuild = data["lastStableBuild"]["number"]
    output = "displayName is: " + str(displayName) + "\nlastStableBuild is:" + str(lastStableBuild)
    return output


def getAllJobs(data):
    nodeDescription = data["nodeDescription"]
    output = "nodeDescription is: " + str(nodeDescription)


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
