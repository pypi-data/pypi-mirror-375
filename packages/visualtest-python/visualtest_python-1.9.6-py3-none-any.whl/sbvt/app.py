import json
import os
import logging
from .imagetools import ImageTools
from .timer import StopWatch
from .api import Api

log = logging.getLogger(f'vt.{os.path.basename(__file__)}')

# defaults - can be overridden with limits parameter
DEFAULT_MAX_IMAGE_SIZE_MB = 20  # 20MB
DEFAULT_MAX_TIME_MIN = 3.5  # minutes (really for mobiles)

class App:
    """
    Class for wrapping appium driver and controlling the remote app in order to generate screenshots.
    Used by VisualTest class and should not be instantiated directly. 

    Args:
        driver: appium driver with active session
        limits: Dictionary of values to change default limits for during creation fullpage images (not recommended)
            - MAX_IMAGE_PIXELS (int): Max fullpage image size. (default INT32 or 2^31)
            - MAX_TIME_MIN (float): Max time to create fullpage image.  Default is 3.5 minutes. Can be set to a max of 10 minutes. 
    Returns:
        Class instance
    """

    def __init__(self, driver, limits: dict = {}):

        # setup api
        self.devicePixelRatio = 1
        self.statusbarHeight = 0
        self.bottomBarHeight = 0
        self._api = Api()
        log.info(f'Capabilities from driver: {driver.capabilities}')
        self._driver = driver
        if self._driver.capabilities['platformName'] == 'Android':
            self.devicePixelRatio = float(self._driver.capabilities['pixelRatio'])
            self.statusbarHeight = self._driver.capabilities['statBarHeight']
        else:
            self._appleDevicesList = Api.getDevicesList('apple-devices')
            data = json.loads(self._appleDevicesList)
            for device in data:
                if device["name"] == self._driver.capabilities.get("deviceName"):
                    self.devicePixelRatio = device["scale"]
                    self.statusbarHeight = device["statusBar"]["portrait"]*self.devicePixelRatio
        self._userAgentInfo = {
            'appPackage': self._driver.capabilities["appPackage"] if "appPackage" in self._driver.capabilities else 
                    self._driver.capabilities["app"] if "app" in self._driver.capabilities else self._driver.capabilities["bundleId"],
            'appActivity':self._driver.capabilities["appActivity"] if "appActivity" in self._driver.capabilities else 
                    self._driver.capabilities["app"] if "app" in self._driver.capabilities else self._driver.capabilities["bundleId"],
            'appiumDriverType':self._driver.capabilities["automationName"].lower(),
            'driverType':'Appium',
            'deviceName': self._driver.capabilities.get("deviceModel") or self._driver.capabilities.get("deviceName"),
            'devicePixelRatio':self.devicePixelRatio,
            'deviceType':'mobile',
            'orientation':'portrait',
            'osName':self._driver.capabilities["platformName"],
            'osVersion':self._driver.capabilities["platformVersion"],
            'screenHeight':self._driver.get_window_size()["height"]*self.devicePixelRatio,
            'screenWidth':self._driver.get_window_size()["width"]*self.devicePixelRatio
        }
        if "deviceManufacturer" in self._driver.capabilities:
            self._userAgentInfo["deviceName"] = self._driver.capabilities["deviceManufacturer"].capitalize() + " " + self._userAgentInfo["deviceName"].capitalize()
        self._deviceInfo = self._api.getDeviceInfo(self._userAgentInfo, driver.capabilities)
        self._deviceInfo['deviceName'] = self._userAgentInfo["deviceName"]
        
        log.info(f'limits: {limits}')
        if 'MAX_IMAGE_PIXELS' in limits:
            ImageTools.setMaxImagePixels(limits['MAX_IMAGE_PIXELS'])

        if 'MAX_TIME_MIN' in limits:
            self.MAX_TIME_MIN = limits['MAX_TIME_MIN']
        else:
            self._MAX_TIME_MIN = DEFAULT_MAX_TIME_MIN
            
        log.info(f'Final Device info: {self._deviceInfo}')

        # default options
        self._scrollMethod = 'CSS_TRANSLATE'
        self._debug = False
        self._debugDir = None
        self.dom = {}

    @property
    def capabilities(self):
        return self._driver.capabilities

    @property
    def debugDir(self):
        return self._debugDir

    @debugDir.setter
    def debugDir(self, debugDir):
        
        if type(debugDir) == str or debugDir == None:
            self._debugDir = debugDir
        else:
            raise Exception(f'Argument must be a string!')

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, debug):
        if type(debug) == bool:
            self._debug = debug
        else:
            raise Exception(f'Argument must be a boolean!')

    @property
    def MAX_TIME_MIN(self):
        return self._MAX_TIME_MIN

    @MAX_TIME_MIN.setter
    def MAX_TIME_MIN(self, minutes):
        if type(minutes) != int:
            raise Exception(f'MAX_TIME_MIN must be an integer')
        if minutes not in range(0, 11):
            raise Exception(f'MAX_TIME_MIN must be between 0 and 10 minutes')
        self._MAX_TIME_MIN = minutes
 
    def _getPageDimensions(self):
        if int(self._driver.capabilities['platformVersion'].split('.')[0]) < 11 and self._driver.capabilities['platformName'] == 'Android':
            jsonDimensions = self._driver.capabilities['viewportRect']
        else:
            jsonDimensions = self._driver.get_window_size()
            if 'orientation' in self.capabilities and self.capabilities['orientation'] == 'LANDSCAPE':
                jsonDimensions['width'] = float(self.capabilities['deviceScreenSize'].split('x')[1]) 
            
        height = jsonDimensions['height']
        width = jsonDimensions['width']
        dimensions = {
                "document": {
                    "height": height,
                    "width": width
                },
                "body": {
                    "height": height,
                    "width": width
                },
                "windowInner": {
                    "height": height,
                    "width":  width
                },
                "fullpage": {
                    "height": height,
                    "width": width
                },
                "devicePixelRatio": self.devicePixelRatio,
                "initialScroll": {
                    'x': 0, 
                    'y': 0
                }
            }

        # for now, take the window.inner dimensions as viewport
        # there may be cases where we need the documentElement or body on older browsers
        self.viewportHeight = dimensions['windowInner']['height']
        self.viewportWidth = dimensions['windowInner']['width']
        self.fullpageHeight = dimensions['fullpage']['height']
        self.fullpageWidth = dimensions['fullpage']['width']
        self.devicePixelRatio = dimensions['devicePixelRatio']
        log.info(f'devicePixelRatio: {self.devicePixelRatio}')
        # validate the viewport from javascript matches 
        # what we actually get from a png
        imageBinary = self._driver.get_screenshot_as_png()
        testImageWidth, testImageHeight = ImageTools.getImageSize(imageBinary)
        log.info(f'Size Test: image dimensions: {testImageWidth}x{testImageHeight}')

        self._cropEachBottom = None
        self._cropEachTop = None
        self._cropEachLeft = None

        if 'orientation' in self.capabilities and self._driver.capabilities['orientation'] == 'LANDSCAPE':
            if int(self._driver.capabilities['platformVersion'].split('.')[0]) < 11:
                jsonDimensions = self._driver.capabilities['viewportRect']
            else:
                jsonDimensions = self._driver.get_window_size()
                
        if self._driver.capabilities['platformName'] == 'Android':
            self._cropEachBottom = testImageHeight - (jsonDimensions['height']) - self.statusbarHeight
        self._cropEachTop = self.statusbarHeight
        self._cropEachLeft = testImageWidth - (jsonDimensions['width'] )
        log.info(
            f'Size Test: Appium Android device has {self._cropEachBottom}px extra pixels to crop on each image at the bottom')

    
    def takeAppiumViewportScreenshot(self, name, options):
        """
        Will take a screenshot of the browser viewport and place the image at the path provided. \n
        Args:
            path (str): the directory for where to save the image
        """
        log.info(f'Taking screenshot of viewport')

        debugImageDir = None
        debugImageName = None
        debugImagePath = None
        if self._debug and self._debugDir:
            debugImageDir = os.path.join(self._debugDir, f'{name}')
            os.makedirs(debugImageDir)

        # measure how long it takes
        self.watch = StopWatch()
        self.watch.start()

        imageBinary = bytearray()  # New empty byte array

        # freezePage script
        freezePageResult = None

        # update the dimensions of the browser window and webpage
        self._getPageDimensions()

        imageBinary = self._driver.get_screenshot_as_png()
        
        if self._debug:
            debugImageName = f'{name}-beforecut.png'
            debugImagePath = os.path.join(debugImageDir, debugImageName)
            with open(debugImagePath, 'wb') as outfile:
                outfile.write(imageBinary)
                outfile.close()


        if self._cropEachBottom and (not 'orientation' in self.capabilities or  self.capabilities['orientation'] == 'PORTRAIT'):
            imageBinary = ImageTools.cropBottom(imageBinary, self._cropEachBottom)

        if self._cropEachLeft and 'orientation' in self.capabilities and self.capabilities['orientation'] == 'LANDSCAPE':
            imageBinary = ImageTools.cropLeft(imageBinary, self._cropEachLeft)

        if self._cropEachTop:
            imageBinary = ImageTools.cropTop(imageBinary, self._cropEachTop)
            
        # validate final fullpage image dimensions
        imageWidth, imageHeight = ImageTools.getImageSize(imageBinary)        
        
        if self._debug:
            debugImageName = f'{name}-aftercut.png'
            debugImagePath = os.path.join(debugImageDir, debugImageName)
            with open(debugImagePath, 'wb') as outfile:
                outfile.write(imageBinary)
                outfile.close()

        expectedImageWidth = self.viewportWidth 
        expectedImageHeight = self.viewportHeight - (self.bottomBarHeight/self.devicePixelRatio) - (self.statusbarHeight/self.devicePixelRatio)
        if self._driver.capabilities['platformName'] == 'Android':
            expectedImageWidth = self.viewportWidth / self.devicePixelRatio 
            expectedImageHeight = (self.viewportHeight - self.bottomBarHeight)/self.devicePixelRatio

        totalTime = self.watch.stop()
        log.info(f'Total viewport capture time duration: {totalTime} seconds')
        self.url = ""
        result = {
            'imagePath': None,
            'imageSize': {
                'width': imageWidth,
                'height': imageHeight
            },
            'expectedSize': {
                'width': expectedImageWidth,
                'height': expectedImageHeight
            },
            'devicePixelRatio': self.devicePixelRatio,
            'duration': f'{totalTime} seconds',
            'url': self.url,
            'freezePageResult': freezePageResult
        }

        log.info(f'Result: {result}')
        result['imageBinary'] = imageBinary
        return result
            