import cv2
import os
import logging
import streamlit as st
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from preprocessing import readImage, extractIdCard, saveImage
from ocr_engine import extractText
from postProcess import extractInformation
from face_verification import detectAndExtractFace, faceComparison, getFaceEmbedding
from mySqlDB_operations import insertRecords, fetchRecords, checkDuplicates

# Logging Configuration
logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, "ekyc_logs.log"),
                    level=logging.INFO, format=logging_str, filemode="a")


def widerPage():
    """Set Streamlit page layout to wider view."""
    maxWidthStr = "max-width: 1200px;"
    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{ {maxWidthStr} }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    logging.info("Page layout set to wider configuration.")


def setCustomTheme():
    """Apply custom styling to Streamlit app."""
    st.markdown(
        """
        <style>
            body {
                background-color: #f0f2f6;
                color: #333333;
            }
            .sidebar .sidebar-content {
                background-color: #ffffff;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    logging.info("Custom theme applied to Streamlit app.")


def sideBarSection():
    """Sidebar selection for ID card type."""
    st.sidebar.title("SELECT ID-CARD TYPE")
    option = st.sidebar.selectbox("Select ID Type", ("PAN", "Aadhar"))  # Fixed empty label issue
    logging.info(f"ID card type selected: {option}")
    return option


def headerSection(option):
    """Display header based on selected ID card type."""
    if option == "Aadhar":
        st.title("Registration using Aadhar Card")
        logging.info("Header set for Aadhar card registration.")
    elif option == "PAN":
        st.title("Registration using PAN Card")
        logging.info("Header set for PAN card registration.")


def mainContent(imageFile, faceImageFile, conn):
    """Main processing logic for ID verification."""
    if imageFile is not None:
        faceImage = readImage(faceImageFile, isUploaded=True)
        if faceImage is None:
            st.error("Face image not uploaded. Please upload a face image.")
            logging.error("No face image uploaded")
            return

        logging.info("Face image loaded.")
        image = readImage(imageFile, isUploaded=True)
        if image is None:
            st.error("Error reading ID card image.")
            logging.error("Failed to load ID card image.")
            return

        logging.info("ID card image loaded.")
        image_ROI, _ = extractIdCard(image)
        logging.info("ID Card ROI Extracted.")

        faceImagePath1 = saveImage(faceImage, "face_image.jpg", path="data\\02_intermediate_data")
        faceImagePath2 = detectAndExtractFace(image=image_ROI)
        logging.info("Faces extracted and saved.")

        isFaceVerified = faceComparison(image1Path=faceImagePath1, image2Path=faceImagePath2)
        logging.info(f"Face Verification status: {'Successful' if isFaceVerified else 'Failed'}")

        if isFaceVerified:
            extractedText = extractText(image_ROI)
            textInfo = extractInformation(extractedText)
            logging.info("Text extracted and information parsed from ID card.")

            records = fetchRecords(textInfo)
            if not records.empty:  # Fix: Ensure records are not empty before displaying
                st.write(records.shape)
                st.write(records)
            else:
                logging.info("No existing records found for the user.")

            isDuplicate = checkDuplicates(textInfo)
            if isDuplicate:
                st.warning(f"User already present with ID {textInfo['ID']}")
            else:
                st.write(textInfo)
                try:
                    textInfo['DOB'] = textInfo['DOB'].strptime('%Y-%m-%d')  # Ensure correct format
                except Exception as e:
                    logging.error(f"Date format error: {e}")
                    # st.error("Error in date format. Please check the input.")

                textInfo['Embedding'] = getFaceEmbedding(faceImagePath1)
                insertRecords(textInfo)
                logging.info(f"New record inserted: {textInfo['ID']}")
                st.success(f"Registration successful for ID: {textInfo['ID']}")

        else:
            st.error("Face Verification Failed. Please try again.")

    else:
        st.warning("Please upload an ID Card Image.")
        logging.warning("No ID card image uploaded.")


def main():
    """Main function to run the Streamlit app."""
    db_config = st.secrets["mysql"]

    try:
        # Create the SQLAlchemy engine
        engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        Session = sessionmaker(bind=engine)
        conn = Session()
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        st.error("Database connection failed. Please check your credentials.")
        return

    widerPage()
    setCustomTheme()
    option = sideBarSection()
    headerSection(option)

    imageFile = st.file_uploader("Upload ID Card", type=["jpg", "png", "jpeg"])
    faceImageFile = st.file_uploader("Upload Face Image")

    if imageFile is not None:
        mainContent(imageFile, faceImageFile, conn)


if __name__ == "__main__":
    main()
# streamlit run "C:\Users\shrey\Desktop\DEEP LEARNING PROJECTS\2. eKYC\app.py"

# |siear|COVT, OF INDIA|INCOME TaX DEPARTMENT|SEJAL SANJAY KASABALE|MAHADEV SATAM|12/08/1980|Permanent Account Number|CUTPK7863E|Signature|Szabake|
# |fTJT|MRT|INCOME TAX DEPARTMENT|GOVT OF INDIA|Permanent Account Number Card|GJXPM96186|Name|ATHARVA MISHRA|Father $ Name|DWIJENDRA NATH MISHRA|21112020|15/01/1998|