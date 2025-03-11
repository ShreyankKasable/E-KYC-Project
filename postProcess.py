import pandas as pd
from datetime import datetime
import json
import re


def filterLines(lines):
    startIndex = None
    endIndex = None

    for i, line in enumerate(lines):
        if "INCOME TAX DEPARTMENT" in line:
            startIndex = i
        if "Signature" in line:
            endIndex = i
            break

    filteredLines = []
    if startIndex is not None and endIndex is not None:
        for line in lines[startIndex : endIndex + 1]:
            if len(line.strip()) > 2:
                filteredLines.append(line.strip())

    return filteredLines


def createDataFrame(texts):
    lines = filterLines(texts)
    print("=" * 20)
    print(lines)
    print("=" * 20)

    data = []
    name = lines[2].strip() if len(lines) > 2 else ""
    fatherName = lines[3].strip() if len(lines) > 3 else ""
    dob = lines[4].strip() if len(lines) > 4 else ""

    # Extract PAN number safely
    pan = ""
    for i in range(len(lines)):
        if "Permanent Account Number" in lines[i]:
            pan = lines[i + 1].strip() if i + 1 < len(lines) else ""
            break  # Stop searching after finding the PAN

    data.append({"ID": pan, "Name": name, "Father's Name": fatherName, "DOB": dob, "ID Type": "PAN"})
    df = pd.DataFrame(data)
    return df


def extractInformation(dataString):
    updatedDataString = re.sub(r"[,.]", "", dataString)
    words = [word.strip() for word in updatedDataString.split("|") if len(word.strip()) > 2]
    print(words)
    panID = ""
    DOB = ""
    panHonderName = ""
    fatherName = ""

    for word in words:
        if re.match(r"^[A-Z]{5}[0-9]{4}", word):
            panID = word
            break

    for word in words:
        if re.match(r"^\d{2}/\d{2}/\d{4}$", word):
            DOB = word
            break
    words = [word.lower() for word in words]
    exclude_terms = ["name", "permanent account number", "permanent account number card", "nncome tax depariment",
                     "signature", "govt of india", "income tax department", "nncome tax department", "covt of india",
                     'father $ name', "father's name", 'date of birth']
    potential_names = [word for word in words if word not in exclude_terms]

    potential_names = [word for word in potential_names if not bool(re.search(r'\d', word))]

    if len(potential_names) >= 2:
        panHonderName = potential_names[-2]
        fatherName = potential_names[-1]
    else:
        print("Error: Names not found or are insufficient!")

    dobValue = ""
    if DOB:
        try:
            dobValue = datetime.strptime(DOB, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            print("Error: Invalid DOB format")

    extractedInfo = {
        "ID": panID,
        "Name": panHonderName,
        "Father's Name": fatherName,
        "DOB": dobValue,
        "ID Type": "PAN"
    }

    return extractedInfo