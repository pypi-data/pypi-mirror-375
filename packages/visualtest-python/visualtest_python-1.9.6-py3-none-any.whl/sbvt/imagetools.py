import io
import os
import logging
from io import BytesIO
from PIL import Image, ImageChops
import numpy

log = logging.getLogger(f'vt.{os.path.basename(__file__)}')

class ImageTools:

    @staticmethod
    def getMaxImagePixels():
        return Image.MAX_IMAGE_PIXELS

    @staticmethod
    def setMaxImagePixels(pixels):
        if type(pixels) != int:
            raise Exception(f'MAX_IMAGE_PIXELS must be an integer')
        if pixels < 0:
            raise Exception(f'MAX_IMAGE_PIXELS must be greater than 0')
            
        Image.MAX_IMAGE_PIXELS = pixels
            

    @staticmethod
    def mergeImages(image1, image2):
        """Merge two images into one, displayed on top of one another
        :param image1: first buffered Image (top image)
        :param image2: second buffered Image (bottom image)
        :return: the merged Image object
        """

        (width1, height1) = image1.size
        (width2, height2) = image2.size

        result_width = max(width1, width2)
        result_height = height1 +  height2

        result = Image.new('RGB', (result_width, result_height))
        result.paste(im=image1, box=(0, 0))
        result.paste(im=image2, box=(0, height1))
        return result

    @staticmethod
    def stitchImages(images):

        if len(images) == 0:
            log.error('Could not stitch files as none were found.')
            return

        bigImage = Image.open(BytesIO(images[0]))

        for i in range(1,len(images)):
            nextImage = Image.open(BytesIO(images[i]))
            bigImage = ImageTools.mergeImages(bigImage, nextImage)
            nextImage.close()

        imageBuffer = io.BytesIO()
        bigImage.save(imageBuffer, format='png')
        bigImage.close()
        return imageBuffer.getvalue()

    @staticmethod
    def getImageSize(imagePath):
        image = Image.open(BytesIO(imagePath))
        size = image.size
        image.close()
        return size

    @staticmethod
    def cropLeft(imageBinary, numPixels, debugImagePath=None):
        if numPixels == 0:
            return imageBinary

        image = Image.open(BytesIO(imageBinary))
        width, height = image.size
        if width-numPixels < 0 or numPixels< 0:
            raise Exception(f'Invalid cropBottom parameters: height={height}, numPixels={numPixels}')
        imageBuffer = io.BytesIO()
        image.crop((numPixels, 0, width, height)).save(imageBuffer, format='png')
        if debugImagePath: 
            image.crop((numPixels, 0, width, height)).save(debugImagePath.replace('.png', '_cropped_left.png'))
        image.close()
        return imageBuffer.getvalue()

    @staticmethod
    def cropTop(imageBinary, numPixels, debugImagePath=None):
        if numPixels == 0:
            return imageBinary

        image = Image.open(BytesIO(imageBinary))
        width, height = image.size
        imageBuffer = io.BytesIO()
        if width-numPixels < 0 or numPixels< 0:
            raise Exception(f'Invalid cropBottom parameters: height={height}, numPixels={numPixels}')
        image.crop((0, numPixels, width, height)).save(imageBuffer, format='png')
        if debugImagePath: 
            image.crop((0, numPixels, width, height)).save(debugImagePath.replace('.png', '_cropped_top.png'))
        image.close()
        return imageBuffer.getvalue()

    @staticmethod
    def cropBottom(imageBinary, numPixels, debugImagePath=None):
        if numPixels == 0:
            return imageBinary

        image = Image.open(BytesIO(imageBinary))
        width, height = image.size
        if height-numPixels < 0 or numPixels< 0:
            raise Exception(f'Invalid cropBottom parameters: height={height}, numPixels={numPixels}')
        imageBuffer = io.BytesIO()
        image.crop((0, 0, width, height-numPixels)).save(imageBuffer, format='png')
        if debugImagePath: 
            image.crop((0, 0, width, height-numPixels)).save(debugImagePath.replace('.png', '_cropped_bottom.png'))
        image.close()
        return imageBuffer.getvalue()

    @staticmethod
    def imagesMatch(pathOne, pathTwo):
        imageOne = Image.open(BytesIO(pathOne))
        imageTwo = Image.open(BytesIO(pathTwo))

        diff = ImageChops.difference(imageOne, imageTwo)
        imageOne.close()
        imageTwo.close()

        if diff.getbbox():
            return False
        else:
            return True

    @staticmethod
    def imageDiff(pathOne, pathTwo):
        imageOne = Image.open(BytesIO(pathOne))
        imageTwo = Image.open(BytesIO(pathTwo))

        diff = ImageChops.difference(imageOne, imageTwo)
        imageOne.close()
        imageTwo.close()

        return diff

    @staticmethod
    def resizeImageByDpr(imagePath, dpr):
        # Open the image
        originalImage = Image.open(BytesIO(imagePath))

        # Get the original width and height
        originalWidth, originalHeight = originalImage.size

        # Calculate the new width and height based on the DPR
        new_width = int(originalWidth / dpr)
        new_height = int(originalHeight / dpr)
        imageBuffer = io.BytesIO()
        # Resize the image
        originalImage.resize((new_width, new_height), Image.LANCZOS).save(imageBuffer, format='png')
        originalImage.close()
        return imageBuffer.getvalue(), new_width, new_height

    """
    Given an browser screenshot image with toolbars and
    a viewport set to a single color throughout the image.
    Find the beginning and ending Y coordinates (or offsets)
    of the toolbars.
    """
    @staticmethod
    def getToolbarHeights(imagePath):

        toolbarHeights = {
            'top': 0,
            'bottom': 0
        }

        log.debug(f'Finding center RGB color in image: {imagePath}')
        # Load image, ensure not palettised, and make into Numpy array
        image = Image.open(imagePath)
        imageWidth, imageHeight = image.size
        log.debug(f'Image Dimensions: {imageWidth}x{imageHeight}')

        pim = image.convert('RGB')
        im  = numpy.array(pim)

        #get actual pixel value as some screenshots don't keep RGB of exact red
        color = pim.getpixel((imageWidth/2,imageHeight/2))
        log.debug(f'RGB value at center is {color}')

        # Define the colour we want to find - PIL uses RGB ordering
        # color = rgb

        # Get X and Y coordinates of all matching pixels
        Y,X = numpy.where(numpy.all(im==color,axis=2))
        coords = numpy.column_stack((X,Y))
        image.close()

        # log.debug(f'Finding RGB color in image.. results:')
        log.debug(coords)
        if len(coords) == 0:
            return toolbarHeights

        firstX, firstY = coords[0]
        lastX, lastY = coords[-1]

        hasTopToolbar = firstY > 0 # has top toolbar if first Y coordinate > 0
        hasBottomToolbar = lastY != imageHeight-1 # has bottom toolbar if last Y coordinate is not at the bottom of the image

        log.debug(f'hasTopToolbar={hasTopToolbar}, hasBottomToolbar={hasBottomToolbar}')
        log.debug(f'color starts at {firstY} and ends at {lastY} for total height of {lastY-firstY}')

        #ensure matches across full width
        firstRow = [pos for pos in coords if pos[1] == firstY]
        lastRow =  [pos for pos in coords if pos[1] == lastY]
        log.debug(f'firstRow length: {len(firstRow)}')
        log.debug(f'lastRow length: {len(lastRow)}')
        

        if len(firstRow) == imageWidth and len(lastRow) == imageWidth:
            log.debug(f'color pixel found across full width t first and last row')
        else:
            log.debug(f'color pixel IS NOT full width at first and last row')

        toolbarHeights['top'] = int(firstY) if hasTopToolbar else 0
        toolbarHeights['bottom'] = int(imageHeight - lastY - 1) if hasBottomToolbar else 0

        log.debug(f'Final toolbarHeights returned: {toolbarHeights}')

        return toolbarHeights


