import pandas as pd
import numpy as np
import psycopg2
import easyocr
import streamlit as st
import re
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_option_menu import option_menu
from io import BytesIO
import os
import io
import cv2
import pytesseract as reader
import pytesseract
import base64
import logging
import tempfile
from PIL import Image, UnidentifiedImageError
import streamlit as st
from PIL import Image
import pytesseract
# Connect to Postgres SQL
pk = psycopg2.connect(host = "localhost",
                        user = "postgres",
                        password = "Sabharish@2015",
                        database = "BizcardX",
                        port = "5432")


cursor = pk.cursor()


# - - - - - - - - - - - - - - -set st addbar page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

icon = Image.open("C:/Users/prabh/Downloads/Datascience/Project/BizCardX/Bizcard/1.png")
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by *Jafar Hussain*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# - - - - - - - - - - - - - - -set bg image - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://cutewallpaper.org/21/web-background-images/webplunder-background-image-technology-online-website-.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True) 
setting_bg()

# - - - - - - - - - - - - - - - - - - -Home page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Home page creation
def home_page() :
    st.title("Home Page")

    col1,col2 = st.columns(2)

    with col1 :

        st.markdown("Technologies Used : Python, PostgreSQL, Easy OCR, Pandas and Streamlit")

    with col2 :
        image_path = "home.png"
        st.image(image_path, use_column_width=True)

# - - - - - - - - - - - - - - - - - - -Upload and Extract page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Connect to Postgres SQL
pk = psycopg2.connect(host = "localhost",
                        user = "postgres",
                        password = "Sabharish@2015",
                        database = "BizcardX",
                        port = "5432")


cursor = pk.cursor()


reader = easyocr.Reader(['en'])


def upload_extract_page() :      
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
        
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards",uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())   
        save_card(uploaded_card)
       
        def image_preview(image,res): 
            for (bbox, text, prob) in res: 
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(image)
        
        col1,col2 = st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)
        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(image_preview(image,res))  
                
            
        saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)
        

        def img_to_binary(file):
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        data = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "mobile_number" :[],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : [],
                "image" : img_to_binary(saved_img)
               }

        def get_data(res):
            for ind,i in enumerate(res):

                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] +"." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) ==2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # To get COMPANY NAME  
                elif ind == len(res)-1:
                    data["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                     data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                    data["state"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["pin_code"].append(i[10:])
        get_data(result)
        
        #FUNCTION TO CREATE DATAFRAME
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        df = create_df(data)
        st.success("### Data Extracted!")
        st.write(df)
        
        if st.button("Upload to Database"):
            for i,row in df.iterrows():
                #here %S means string values 
                sql = """INSERT INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                pk.commit()
            st.success("#### Uploaded to database successfully!")
        



# - - - - - - - - - - - - - - - - - - -Modify page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# modify page creation

def modify_Page():
    pk.autocommit = True  # Set autocommit to True


    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## Alter or Delete the data here")
    column1, column2 = st.columns(2, gap="large")

    with column1:
        # Print the contents of card_data table
        cursor.execute("SELECT * FROM card_data")
        result_all = cursor.fetchall()
        print("Contents of card_data table:", result_all)

        cursor.execute("SELECT card_holder FROM card_data")
        result = cursor.fetchall()
        business_cards = {}

        # Check if result is empty
        if not result:
            st.warning("No card holders found.")
        else:
            for row in result:
                business_cards[row[0]] = row[0]

            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))

            st.markdown("#### Update or modify any data below")
            cursor.execute(
                "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",
                (selected_card,))
            result = cursor.fetchone()
            # Check if result is not None before accessing its elements
            if result is not None:
                # DISPLAYING ALL THE INFORMATIONS
                company_name = st.text_input("Company_Name", result[0] if result[0] is not None else "")
                card_holder = st.text_input("Card_Holder", result[1] if result[1] is not None else "")
                designation = st.text_input("Designation", result[2] if result[2] is not None else "")
                mobile_number = st.text_input("Mobile_Number", result[3] if result[3] is not None else "")
                email = st.text_input("Email", result[4] if result[4] is not None else "")
                website = st.text_input("Website", result[5] if result[5] is not None else "")
                area = st.text_input("Area", result[6] if result[6] is not None else "")
                city = st.text_input("City", result[7] if result[7] is not None else "")
                state = st.text_input("State", result[8] if result[8] is not None else "")
                pin_code = st.text_input("Pin_Code", result[9] if result[9] is not None else "")

                if st.button("Commit changes to DB"):
                    # Update the information for the selected business card in the database
                    cursor.execute(
                        """UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                            WHERE card_holder=%s""",
                        (company_name, card_holder, designation, mobile_number, email, website, area, city, state,
                         pin_code, selected_card))
                    pk.commit()
                    st.success("Information updated in database successfully.")
            else:
                st.warning("No data found for the selected card holder.")

    with column2:
        cursor.execute("SELECT card_holder FROM card_data")
        result = cursor.fetchall()
        business_cards = {}

        # Check if result is empty
        if not result:
            st.warning("No card holders found.")
        else:
            for row in result:
                business_cards[row[0]] = row[0]

            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                cursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                pk.commit()
                st.success("Business card information deleted from database.")

    if st.button("View updated data"):
        cursor.execute(
            "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
        updated_df = pd.DataFrame(cursor.fetchall(),
                                  columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number", "Email",
                                           "Website", "Area", "City", "State", "Pin_Code"])
        st.write(updated_df)
        pk.commit()

        # Reset autocommit to False
        pk.autocommit = False








# - - - - - - - - - - - - - - - - - - -sidebar - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Connect to Postgres SQL
pk = psycopg2.connect(host="localhost",
                      user="postgres",
                      password="Sabharish@2015",
                      database="BizcardX",
                      port="5432")

# Create a cursor
cursor = pk.cursor()


# Main Page
def main():
    st.title("")

    st.sidebar.title("Navigation")
    page = ["Home", "Upload and Extract", "Modify Page"]
    selected_page = st.sidebar.radio("Navigation", page)

    if selected_page == "Home":
        home_page()
    elif selected_page == "Upload and Extract":
        upload_extract_page()
    elif selected_page == "Modify Page":
        modify_Page()

# Sidebar option with a tooltip using markdown
st.sidebar.markdown("")
st.sidebar.write("")

if __name__ == "__main__":
    main()
