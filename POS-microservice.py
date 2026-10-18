import streamlit as st
import pandas as pd
import smtplib
from datetime import datetime
from fpdf import FPDF
from email.mime.text import MIMEText

st.title("Market Organizer!")

if "page" not in st.session_state:
    st.session_state.page = "Home"

#validations
# Initialize session state safely
if "inventory" not in st.session_state:
    st.session_state.inventory = None

if "receipt" not in st.session_state:
    st.session_state.receipt = []

#basic information
if "details_saved" in st.session_state and st.session_state.details_saved:
    st.success("Details saved!")
    st.write("Now you can continue:")
else:
    # Show inputs
    brand_name = st.text_input("Please enter your organization's name:")
    email = st.text_input("Please enter your business email:")

    if st.button("Save Details"):
        if brand_name.strip() == "" or email.strip() == "":
            st.error("Please fill all fields")
        else:
            st.session_state.details_saved = True
            st.session_state.brand_name = brand_name
            st.session_state.email = email
            st.rerun()

#functions
def check_stock():
    no_rows=st.session_state.inventory[
        st.session_state.inventory["quantity"]<=2
    ]
    return no_rows


#---DEVELOPMENTAL FEATURE TO BE DEBUGGED SOON---

#def send_alert(item_name, email):
    #msg=MIMEText(f"Alert: {item_name} out of stock")
    #msg["Subject"]="Item in inventory out of stock"
    #msg["From"]="hooria4911@gmail.com"
    #msg["To"]=email
    #with smtplib.SMTP("smtp.gmail.com", 587) as mail:
        #mail.starttls()
        #mail.login("hooria4911@gmail.com")
        #mail.send_message(msg)


#file uploading Stuff
upload_file=st.file_uploader("Upload your current inventory status in CSV form:", type=["csv"])
st.write("Please ensure that your csv file has clear columns named 'Item name', 'quantity', and 'price'")
required_columns=['Item name', 'quantity', 'price']
if upload_file is not None:
    df = pd.read_csv(upload_file)
    if not all(col in df.columns for col in required_columns):
        st.error("CSV file must contain 'Item name', 'quantity', and 'price' columns")
    else:
        st.session_state.inventory=df
        no_items=check_stock()
        if not no_items.empty:
            for i, row in no_items.iterrows():
                item_name=row["Item name"]
                #send_alert(item_name, st.session_state.email)
elif upload_file is None and st.session_state.inventory is None:
    st.info("Upload a CSV to begin.")

  
#country and tax
countries={
    "United Arab Emirates": 5,
    "Saudi Arabia": 15,
    "India": 18,
    "United Kingdom": 20,
    "Unites States of America": 7,
    "Canada": 5,
    "Australia": 10,
    "Singapore": 9,
    "Germany":19,
    "France":20
}
country_list=list(countries.keys())+["Other"]
region=st.selectbox("Please choose your country", country_list)
if region!="Other":
    tax_rate=countries[region]/100
    st.write(f"Tax rate for {region}: {tax_rate}")
else:
    act_tax=st.text_input("Please enter the tax rate of your country/region (e.g '5')")
    try:
        act_tax = float(act_tax)
        tax_rate=act_tax/100
        if act_tax<0:
            st.error("Tax must be 0 or higher")
    except:
        st.error("Value must be a valid number")
            
#pages now
if st.session_state.page=="Track Inventory":
    if st.session_state.inventory is not None:
        st.write(st.session_state.inventory)
    else:
        st.info("Upload a CSV first.")



elif st.session_state.page=="Make Receipt":
    items=st.selectbox("Select items ordered:", st.session_state.inventory["Item name"])
    qty = st.number_input("Quantity:", min_value=1)
    price = st.session_state.inventory.loc[
        st.session_state.inventory["Item name"] == items,
        "price"
    ].iloc[0]
    subtotal=price*qty
    if st.button("Add Item"):
        st.session_state.receipt.append({
            "Items": items,
            "Quantity": qty,
            "Individual Price": price,
            "Subtotal": subtotal
        })
        st.session_state.inventory.loc[
            st.session_state.inventory["Item name"] == items,
            "quantity"
        ] -= qty
    st.write(pd.DataFrame(st.session_state.receipt))
    
    
    df_receipt = pd.DataFrame(st.session_state.receipt)
    grand_subtotal = df_receipt["Subtotal"].sum()
    tax_added= grand_subtotal*tax_rate
    grand_total=grand_subtotal+tax_added
    if st.button("Export PDF"):
        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Times", size=48)
        pdf.cell(800,60, txt=st.session_state.brand_name, ln=True)
        pdf.cell(800,10, txt="", ln=True)
        pdf.set_font("Arial", size=22)
        pdf.cell(800,10, txt=f"Date: {datetime.now()}", ln=True)
        pdf.cell(200,15, txt="", ln=True)
        for item in st.session_state.receipt:
            pdf.cell(800,10, txt=f"{item['Items']} x {item['Quantity']} = {item['Subtotal']}", ln=True)
        pdf.cell(800,10, txt=f" Tax rate: {tax_rate}", ln=True)
        pdf.cell(800,10, txt=f"Tax amount added: {tax_added}", ln=True)
        pdf.cell(800,12, txt=f"Grand Total: {grand_total}", ln=True)
        pdf.cell(800,30, txt="", ln=True)
        pdf.add_font("Festive", "", "Festive-Regular.ttf", uni=True)
        pdf.set_font("Festive", size=48)
        pdf.cell(800, 15, txt="Thank you for shopping!", ln=True)
        pdf.cell(800,20, txt="", ln=True)
        pdf.output("receipt.pdf")
        with open("receipt.pdf", "rb") as f:
            st.download_button("Download", f)


elif st.session_state.page == "Z receipt":
    if st.session_state.receipt == []:
        st.error("No orders have been made yet!")
    else:
        df = pd.DataFrame(st.session_state.receipt)
        daily_total = df["Subtotal"].sum()
        st.subheader("Z-Receipt (Daily Summary)")
        st.table(df)
        st.write("Daily Total:", daily_total)
        st.write(st.write("Tax Added:", f"{daily_total * tax_rate:.2f}"))
        st.write("Grand Total:", f"{daily_total + (daily_total * tax_rate):.2f}")
        st.write("Date:", datetime.now().strftime("%Y-%m-%d"))

#buttons last bruh
        
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Track Inventory"):
        st.session_state.page = "Track Inventory"

with col2:
    if st.button("Make Receipt"):
        st.session_state.page = "Make Receipt"

with col3:
    if st.button("Daily Summary"):
        st.session_state.page = "Z receipt"

    

            
        
