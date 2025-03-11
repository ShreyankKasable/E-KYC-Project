import cv2
import os

import numpy as np
from utils import file_exists, read_yaml

configPath = "config.yaml"
config = read_yaml(configPath)

artifacts = config['artifacts']
intermediateDirPath = artifacts['INTERMEDIATE_DIR']
contourFilePath = artifacts['CONTOUR_FILE']


def readImage(imagePath, isUploaded=False):

    if isUploaded:
        try:
            imageBytes = imagePath.read()
            img = cv2.imdecode(np.frombuffer(imageBytes, np.uint8), cv2.IMREAD_COLOR)

            if img is None:
                raise Exception("Failed to read Image : {}".format(imagePath))
            return img
        except Exception as e:
            print("Error reading Images :", e)
            return None

    else:
        try:
            img = cv2.imread(imagePath)
            if img is None:
                raise Exception("Failed to read Image : {}".format(imagePath))
            return img
        except Exception as e:
            print("Error Reading image:", e)
            return None


def extractIdCard(img):

    greyImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bluredImg = cv2.GaussianBlur(greyImg, (5, 5), 0)
    thresholdImg = cv2.adaptiveThreshold(bluredImg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    contours, _ = cv2.findContours(thresholdImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largestContour = None
    largestArea = 0

    for contour in contours:

        area = cv2.contourArea(contour)
        if area > largestArea:
            largestContour = contour
            largestArea = area

    if largestContour is None:
        return None

    x, y, w, h = cv2.boundingRect(largestContour)

    currentWD = os.getcwd()
    fileName = os.path.join(currentWD, intermediateDirPath, contourFilePath)
    contourId = img[y:y+h, x:x+h]
    isExists = file_exists(fileName)

    if isExists:
        os.remove(fileName)

    cv2.imwrite(fileName, contourId)

    return contourId, fileName


def saveImage(image, fileName, path="."):

    fullPath = os.path.join(path, fileName)
    isExists = file_exists(fullPath)

    if isExists:
        os.remove(fullPath)

    cv2.imwrite(fullPath, image)

    return fullPath
