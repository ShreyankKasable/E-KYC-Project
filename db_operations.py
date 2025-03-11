from sqlalchemy import text, select
import streamlit as st
import pandas as pd

conn = st.connection('mysql', type='sql')


def insertRecords(textInfo):

    with conn.session as s:
        s.execute(
            text(
                'INSERT INTO users (id, name, father_name, dob, id_type, embedding) VALUES (:id, :name, :father_name, '
                ':dob, :id_type, :embedding);'),
            {
                'id': textInfo['ID'],
                'name': textInfo['Name'],
                'father_name': textInfo["Father's Name"],
                'dob': textInfo['DOB'],  # Ensure it's in 'YYYY-MM-DD' format
                'id_type': textInfo['ID Type'],
                'embedding': str(textInfo['Embedding'])
            }
        )
        s.commit()


def fetchRecord(textInfo):

    df = pd.DataFrame(conn.query('SELECT * FROM users;', ttl=600))
    return df


def checkDuplicate(textInfo):

    isDuplicate = False
    df = fetchRecord(textInfo)
    df = df[df['id'] == textInfo['ID']]

    if df.shape[0] > 0:
        isDuplicate = True

    return isDuplicate
