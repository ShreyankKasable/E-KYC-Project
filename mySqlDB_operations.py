import mysql.connector
import pandas as pd


mydb = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd='Shreyank@sk5',
    database='ekyc'
)

cursor = mydb.cursor()
print("Connection Established")


def insertRecords(textInfo):

    sql = "INSERT INTO person_details(id, name, father_name, dob, id_type, embedding) VALUES (%s, %s, %s, %s, %s, %s)"
    value = (textInfo['ID'],
             textInfo['Name'],
             textInfo["Father's Name"],
             textInfo['DOB'],  # Make sure this is formatted as a string 'YYYY-MM-DD'
             textInfo['ID Type'],
             str(textInfo['Embedding']))
    cursor.execute(sql, value)
    mydb.commit()


def fetchRecords(textInfo):
    sql = "SELECT * FROM person_details WHERE id =%s"
    value = (textInfo['ID'],)
    cursor.execute(sql, value)
    result = cursor.fetchall()

    if result:
        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
        return df
    else:
        return pd.DataFrame()


def checkDuplicates(textInfo):

    isDuplicate = False
    df = fetchRecords(textInfo)

    if df.shape[0] > 0:
        isDuplicate = True
    return isDuplicate


def getData():
    pass


