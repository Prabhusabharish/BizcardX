import pandas as pd
import easyocr
import streamlit as st
from PIL import Image
import psycopg2
import os
import cv2
import matplotlib.pyplot as plt
import re

# - - - - - - - - - - - - - - -set st addbar page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

icon = Image.open("C:/Users/prabh/Downloads/Datascience/Project/BizCardX/Bizcard/1.png")
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by *PrabhuSabharish*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# - - - - - - - - - - - - - - -set bg image - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://cutewallpaper.org/21/web-background-images/webplunder-background-image-technology-online-website-.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True) 
setting_bg()



# Connect to PostgreSQL
pk = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="Sabharish@2015",
    database="BizcardX",
    port="5432"
)
cursor = pk.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS card_data (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255),
    card_holder VARCHAR(255),
    designation VARCHAR(255),
    mobile_number VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    area VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    pin_code VARCHAR(10),
    image BYTEA -- Assuming you want to store the image data as binary (adjust the data type accordingly)
);
"""

cursor.execute(create_table_query)

pk.commit()

cursor.close()
pk.close()
# - - - - - - - - - - - - - - - - - - -Home page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Home page creation
def home_page() :
    st.title("Home Page")

    col1,col2 = st.columns(2)

    with col1 :

        with col1:
            st.markdown("""
                Technologies Used:
                - Python
                - PostgreSQL
                - Easy OCR
                - Pandas
                - Streamlit
                
                Features:
                - Upload business card images for data extraction.
                - Extract information such as company name, cardholder name, designation, mobile number, email, website, area, city, state, pin code.
                - Store extracted data in a PostgreSQL database.
                - Modify or delete existing business card data in the database.
                - User-friendly interface built with Streamlit.
                """)

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

                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] +"." + res[5]

                elif "@" in i:
                    data["email"].append(i)

                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) ==2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                elif ind == len(res)-1:
                    data["company_name"].append(i)

                elif ind == 0:
                    data["card_holder"].append(i)

                elif ind == 1:
                    data["designation"].append(i)

                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["area"].append(i)

                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                     data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                    data["state"].pop(0)

                if len(i)>=6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["pin_code"].append(i[10:])
        get_data(result)
        
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        df = create_df(data)
        st.success("### Data Extracted!")
        st.write(df)
        
        if st.button("Upload to Database"):
            for i,row in df.iterrows():
                sql = """INSERT INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(sql, tuple(row))
                pk.commit()
            st.success("#### Uploaded to database successfully!")
        



# - - - - - - - - - - - - - - - - - - -Modify page - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# modify page creation

def modify_Page():
    pk.autocommit = True  


    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## Alter or Delete the data here")
    column1, column2 = st.columns(2, gap="large")

    with column1:
        cursor.execute("SELECT * FROM card_data")
        result_all = cursor.fetchall()

        cursor.execute("SELECT card_holder FROM card_data")
        result = cursor.fetchall()
        business_cards = {}

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
            if result is not None:
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

        pk.autocommit = False

# - - - - - - - - - - - - - - - - - - -sidebar - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Connect to Postgres SQL
pk = psycopg2.connect(host="localhost",
                      user="postgres",
                      password="Sabharish@2015",
                      database="BizcardX",
                      port="5432")

cursor = pk.cursor()

def main():
    st.title("")
    cursor = pk.cursor()

    st.sidebar.title("")
    page = ["Home", "Upload and Extract",  "Modify Page"]
    selected_page = st.sidebar.radio("", page)

    if selected_page == "Home":
        home_page()
    elif selected_page == "Upload and Extract":
        upload_extract_page()
    elif selected_page == "Modify Page":
        modify_Page()
 
if __name__ == "__main__":
    main()  
