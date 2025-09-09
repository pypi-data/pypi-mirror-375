import os
import logging
import json
import time
import requests
import sbvt
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(f'vt.{os.path.basename(__file__)}')

api = requests.Session()
s3 = requests.Session()


# from https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = 10  # seconds
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


# define retry strategy and timeout
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = TimeoutHTTPAdapter(timeout=30, max_retries=retries)

# Mount it for both http and https usage
api.mount("https://", adapter)
api.mount("http://", adapter)
s3.mount("https://", adapter)

s3.headers.update({"Content-Type": "application/octet-stream"})

class Api:

    baseUrl = None
    webUrl = None
    cdnUrl = None

    @staticmethod
    def setEnv(env):
        if env != "prod":
            print(f'overwritten env is: {env}')
            Api.baseUrl = f'https://api.{env}.visualtest.io/api/v1'
            Api.webUrl = f"https://app.{env}.visualtest.io"
            Api.cdnUrl = f"https://cdn.{env}.visualtest.io/browser-toolkit"
        else:
            Api.baseUrl = 'https://api.visualtest.io/api/v1'
            Api.webUrl = 'https://app.visualtest.io'
            Api.cdnUrl = 'https://cdn.visualtest.io/browser-toolkit'

    def __init__(self, projectToken=None):
        self.projectToken = None
        self.projectId = None
        if projectToken:
            self.projectToken = projectToken
            self.projectId = projectToken.split("/")[0]
            api.headers.update({
                'Authorization': f'Bearer {projectToken}',
                'sbvt-client': 'sdk',
                'sbvt-sdk': 'python',
                'sbvt-sdk-version': sbvt.__version__
            })
        self.testRun = None
        self.scmCommitId = None
        self.scmBranch = None

    def getDeviceInfo(self, userAgentInfo, driverCapabilities):

        url = f'{Api.baseUrl}/device-info/'
        log.info(f'calling API to get device info at: {url}')
        response = api.post(url, json={'userAgentInfo': userAgentInfo, 'driverCapabilities': driverCapabilities})
        if response.status_code in range(200, 300):

            return response.json()
        else:
            raise Exception(f'Failed to save image. HTTP Response: {response}')

    def findTestRunByName(self, name):
        query = {'testRunName': {'eq': name}}
        url = f'{Api.baseUrl}/projects/{self.projectId}/testruns?q={requests.utils.quote(json.dumps(query))}'
        log.info(f'calling API to get testRun by name: {url}')
        response = api.get(url)
        log.info(f'findTestRunByName response: {response}')
        if response.status_code in range(200, 300):
            result = response.json()
            if type(result['items']) == list and len(result['items']) == 1:
                log.info(f'Found existing testRunName: {str(result)}')
                return result['testruns'][0]
            else:
                log.info(f"type of items: {type(result['items'])}")
                log.info(f"length of items: {len(result['items'])}")
                log.info(f'Did NOT find existing testRunName')
                return None
        else:
            raise Exception(f'Failed to get test run by name: {name}. HTTP Response: {str(response)}')

    def createTestRun(self, testRunName, testGroupId):

        url = f'{Api.baseUrl}/projects/{self.projectId}/testruns'
        log.info(f'calling API to create testRun by name: {url}')
        if testGroupId == None:      
            jsonObject = {
                'testRunName': testRunName,
                'sdk': 'python',
                'sdkVersion': sbvt.__version__,
            }
        else:
            jsonObject = {
                'testRunName': testRunName,
                'testGroupId': testGroupId,
                'sdk': 'python',
                'sdkVersion': sbvt.__version__,
            }
            
        if self.scmCommitId:
            jsonObject['scmCommitId'] = self.scmCommitId
            
        if self.scmBranch:
            jsonObject['scmBranch'] = self.scmBranch
        
        response = api.post(url, json=jsonObject)
        if response.status_code in range(200, 300):
            return response.json()
        else:
            log.error(f'Failed to create testRun. HTTP Response: {response.json()}')
            raise Exception(f'Failed to create testRun. HTTP Response: {response.json()}')

    def createTestGroup(self, testGroupName):
        url = f'{Api.baseUrl}/projects/{self.projectId}/testgroups'
        log.info(f'calling API to create testGroup by name: {url}')
        response = api.post(url, json={
            'testGroupName': testGroupName,
        })
        if response.status_code in range(200, 300):
            return response.json()
        else:
            log.error(f'Failed to create testGroup. HTTP Response: {response.json()}')
            raise Exception(f'Failed to create testGroup. HTTP Response: {response.json()}')

    def saveImage(self, testRunName, testGroupName, imageData, imageBinary, domString):
        log.info(f'Saving image for testRunName: {testRunName}')

        testGroupId = None

        if testGroupName:
            testGroup = self.createTestGroup(testGroupName)
            testGroupId = testGroup['testGroupId']

        # check if testRun already exists, if not create one
        if not self.testRun:
            self.testRun = self.createTestRun(testRunName, testGroupId)

        # create image on backend via API
        url = f'{Api.baseUrl}/projects/{self.projectId}/testruns/{self.testRun["testRunId"]}/images'
        log.info(f'calling API to save image: {url}')
        log.debug(f'imageData: {imageData}')

        response = api.post(url, json=imageData)
        log.info(f'create image response: {response}')

        if response.status_code in range(200, 300):
            result = response.json()
        else:
            log.error(f'Failed to create image. HTTP Response: {response.json()}')
            raise Exception(f'Failed to create image. HTTP Response: {response.json()}')

        domCaptured = False
        # Upload DOM file to S3
        log.info(f'uploading DOM to S3: {result["domUploadUrl"]}')
        try:
            if 'domUploadUrl' not in result:
                raise Exception(f'No domUploadUrl received from POST to /images API')
            else:
                response = s3.put(result['domUploadUrl'], data=domString.encode())
                log.info(f'upload DOM to S3 response: {response.status_code}')
                if not response.status_code in range(200, 300):
                    log.error(f'Failed to upload DOM to S3.')
                    raise Exception(f'{response.text}')
                domCaptured = True

        except Exception as e:
            log.debug(f'error: {e.__str__()}')
            errorMessage = {"errorMessage": e.__str__()}
            url = f'{Api.baseUrl}/projects/{self.projectId}/testruns/{self.testRun["testRunId"]}/images/{result["imageId"]}'

            response = api.patch(url, json=errorMessage)
            log.info(f'calling API to add error: {url}')
            log.debug(f'errorMessage: {errorMessage}')

            if response.status_code in range(200, 300):
                log.debug(f'errorResult: {response.json()}')
            else:
                log.error(
                    f'Failed to send error. HTTP Response: {response.text}')
                raise Exception(
                    f'Failed to send error. HTTP Response: {response.text}')
        
        if domCaptured:
            # Call API to set domCaptured=captured
            url = f'{Api.baseUrl}/projects/{self.projectId}/testruns/{self.testRun["testRunId"]}/images/{result["imageId"]}'
            log.info(f'calling API to PATCH image with domCaptured=true: {url}')

            response = api.patch(url, json={'domCaptured': True})
            log.info(f'patch image response: {response}')

        
        # Upload image to S3
        log.info(f'uploading image to S3: {result["uploadUrl"]}')
        try:
            response = s3.put(result['uploadUrl'], data=imageBinary)
            log.info(f'upload image to S3 response: {response.status_code}')

            if response.status_code in range(200, 300):
                return result
            else:
                log.error(f'Failed to upload image to S3.')
                raise Exception(f'{response.text}')

        except Exception as e:
            log.debug(f'error: {e.__str__()}')
            errorMessage = {"errorMessage": e.__str__()}
            url = f'{Api.baseUrl}/projects/{self.projectId}/testruns/{self.testRun["testRunId"]}/images/{result["imageId"]}'

            response = api.patch(url, json=errorMessage)
            log.info(f'calling API to add error: {url}')
            log.debug(f'errorMessage: {errorMessage}')

            if response.status_code in range(200, 300):
                log.debug(f'errorResult: {response.json()}')
                return result
            else:
                log.error(
                    f'Failed to send error. HTTP Response: {response.text}')
                raise Exception(
                    f'Failed to send error. HTTP Response: {response.text}')

    @staticmethod
    def getToolkit(scriptName=None):
        if scriptName in ['user-agent','dom-capture','freeze-page','chrome-os-version','detect-chrome-headless']:
            url = f'{Api.cdnUrl}/{scriptName}.min.js'
            response = api.get(url)
            return response.text
        else:
            log.error(f'Invalid scriptName for getToolkit from cdn: {scriptName}')
            raise Exception(f'Invalid scriptName for getToolkit from cdn: {scriptName}')

    @staticmethod
    def getDevicesList(scriptName=None):
        if scriptName in ['apple-devices']:
            url = f'{Api.cdnUrl}/{scriptName}.json'
            response = api.get(url)
            return response.text
        else:
            log.error(f'Invalid scriptName for getToolkit from cdn: {scriptName}')
            raise Exception(f'Invalid scriptName for getToolkit from cdn: {scriptName}')

    def getTestRunResult(self, timeout=3):
        if not self.testRun:
            raise Exception("Cannot run get testrun result without first taking a capture()")
        i = 0
        comparisons = { 'pending': 1 }
        while comparisons['pending'] > 0 and i < timeout * 4 * 60:
            url = f'{Api.baseUrl}/projects/{self.projectId}/testruns/{self.testRun["testRunId"]}?expand=comparison-totals'
            response = api.get(url).json()
            comparisons = response['comparisons']
            i = i + 1
            time.sleep(0.25)
        return comparisons

    def canConnectToApiServer(self):
        url = f'{Api.webUrl}'
        log.info(f'Check API connection to backend')

        try:
            response = api.get(url)
            if response.status_code in range(200, 300):
                log.info(f'Connection to API is working')
            elif response.json():
                raise Exception(response.json()['message'])
            else:
                raise Exception("Error checking connection:" + str(response.text))
        except Exception as e:
            raise Exception(f'The VisualTest SDK is unable to communicate with our server. This is usually due to one of the following reasons:\n\
                1) Firewall is blocking the domain: Solution is to whitelist the domain: "*.visualtest.io"\n\
                2) Internet access requires a proxy server: Talk to your network admin\n\
                \n\
                Error:\n\
                {e}')
    

    def isValidProjectToken(self):
        url = f'{Api.baseUrl}/projects/{self.projectId}'
        log.info(f'Check ProjectToken connection to backend')
        try:
            response = api.get(url)
            if response.status_code in range(200, 300):
                log.info(f'ProjectToken is correct.')
            elif response.json():
                raise Exception(response.json()['message'])
            else:
                raise Exception(str(response.text))
        except Exception as e:
            raise Exception("Error checking projectToken:" + str(e))

