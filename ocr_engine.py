import easyocr


def extractText(imagePath, confidenceThreshold=0.6, languages=None):
    if languages is None:
        languages = ['en']

    reader = easyocr.Reader(languages)

    try:
        result = reader.readtext(imagePath)
        outputText = ""

        for text in result:
            boundingBox, recognizedText, confidence = text

            if confidence > confidenceThreshold:
                outputText += recognizedText + "|"

        return outputText

    except Exception as e:
        print("An error occurred during text extraction", e)
        return ""

