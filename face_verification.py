import face_recognition
from deepface import DeepFace
import numpy as np
import os
import cv2
from utils import file_exists, read_yaml
import logging

logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir,"ekyc_logs.log"), level=logging.INFO, format=logging_str, filemode="a")

configPath = "config.yaml"
config = read_yaml(configPath)

artifacts = config['artifacts']
cascadePath = artifacts['HAARCASCADE_PATH']
outputPath = artifacts['INTERMEDIATE_DIR']


def detectAndExtractFace(image):

    greyImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier(cascadePath)

    faces = faceCascade.detectMultiScale(greyImage, scaleFactor=1.1, minNeighbors=5)

    maxArea = 0
    largestFace = None

    for (x, y, w, h) in faces:
        area = w*h

        if area > maxArea:
            maxArea = area
            largestFace = (x, y, w, h)

    if largestFace is not None:
        (x, y, w, h) = largestFace

        newW = int(w*1.50)
        newH = int(h*1.50)
        newX = max(0, x-int((newW - w)/2))
        newY = max(0, y-int((newH - h)/2))

        extractedFace = image[newY:newY+newH, newX:newX+newW]

        currentWD = os.getcwd()
        fileName = os.path.join(currentWD, outputPath, "extracted_face.jpg")

        if os.path.exists(fileName):
            os.remove(fileName)

        cv2.imwrite(fileName, extractedFace)
        print(f"Extracted face saved at : {fileName}")
        return fileName

    else:
        return None


def faceRecognitionAndFaceComparison(image1Path="data\\02_intermediate_data\\extracted_face.jpg", image2Path = "data\\02_intermediate_data\\face_image.jpg"):

    img1Path = file_exists(image1Path)
    img2Path = file_exists(image2Path)

    if not img1Path or not img2Path:
        print("Check the path for the images provided")
        return False

    image1 = face_recognition.load_image_file(image1Path)
    image2 = face_recognition.load_image_file(image2Path)

    if image1 is not None and image2 is not None:
        faceEncoding1 = face_recognition.face_encodings(image1)
        faceEncoding2 = face_recognition.face_encodings(image2)
    else:
        print("image is not loaded properly")
        return False

    if len(faceEncoding1) == 0 or len(faceEncoding2) == 0:

        if len(faceEncoding1) == 0 and len(faceEncoding2) == 0:
            print("No face is detected in both images.")
        elif len(faceEncoding1) == 0 and len(faceEncoding2) > 0:
            print("No face is detected in first image.")
        else:
            print("No face is detected in second image.")
        return False
    else:
        matches = face_recognition.compare_faces(np.array(faceEncoding1), np.array(faceEncoding2))

    if matches[0]:
        print("face is Verified")
        return True
    else:
        print("Face is not verified")
        return False


def deepFaceFaceComparison(image1Path="data\\02_intermediate_data\\extracted_face.jpg", image2Path = "data\\02_intermediate_data\\face_image.jpg"):

    img1Exists = file_exists(image1Path)
    img2Exists = file_exists(image2Path)

    if not(img1Exists or img2Exists):
        print("Check the path for the images provided")
        return False

    verification = DeepFace.verify(img1_path=image1Path, img2_path=image2Path)

    if len(verification) > 0 and verification['verified']:
        print("Face are Verified")
        return True
    else:
        print("Face is not verified")
        return False


def faceComparison(image1Path, image2Path, modelName='faceRecognition'):

    isVerified = False
    if modelName == 'deepface':
        isVerified = deepFaceFaceComparison(image1Path, image2Path)
    elif modelName == 'faceRecognition':
        isVerified = faceRecognitionAndFaceComparison(image1Path, image2Path)
    else:
        print("Mention proper model name for face recognition")

    return isVerified


def getFaceEmbedding(imagePath):

    imgExists = file_exists(imagePath)

    if not imgExists:
        print("Check the Path for the images provided")
        return None

    embeddingObjects = DeepFace.represent(img_path=imagePath, model_name='Facenet')
    embedding = embeddingObjects[0]['embedding']

    if len(embedding) > 0:
        return embedding
    return None


if __name__ == "__main__":
    idCardPath = "data\\01_raw_data\\pan_2.jpg"

    # Load the image
    idCardImage = cv2.imread(idCardPath)

    if idCardImage is None:
        print(f"Error: Could not load image from {idCardPath}")
    else:
        extractedFacePath = detectAndExtractFace(image=idCardImage)

        if extractedFacePath is None:
            print("No face detected in the ID card image.")
        else:
            print(f"Extracted face saved at: {extractedFacePath}")
    






