import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

st.markdown("<h1 style='display: inline;'>AKP Devices</h1><br/>", unsafe_allow_html=True)

# Load the Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'pak-devices-credentials.json', 
    scope)

# Connect to the Google Sheet
gc = gspread.authorize(credentials)

# Replace with your Google Sheet name
sheet_name = 'pak-devices'  
sheet = gc.open(sheet_name).sheet1

def create_data(fullname, device, barcode):
    last_row_value = sheet.acell('A1').value
    row_number = int(last_row_value) + 1 if last_row_value else 1
    sheet.append_row([row_number, fullname, device, barcode])

def read_data():
    data = sheet.get_all_values()
    if len(data) > 3:
        header = data[2]  # Use the first row as column names
        data = data[3:]  # Remove the header row
        df = pd.DataFrame(data, columns=header)  # Create DataFrame with header as column names
        df = df.iloc[:, 1:]  # Exclude the first column (column A)
    else:
        df = pd.DataFrame(columns=['Fullname', 'Device', 'Barcode'])
    return df
    
def update_data(index, fullname, device, barcode):
    data = sheet.get_all_values()
    if index > 0 and index <= len(data) - 3:
        row_data = [fullname, device, barcode]
        row_range = f"B{index + 3}:D{index + 3}"  # Adjust index by 1 since row indices start from 1 in Google Sheets
        sheet.update(row_range, [row_data])
    else:
        st.warning("Invalid row index.")

def delete_data(index):
    if index > 0:
        df = read_data()
        if index <= len(df):
            row_index = df.index[index - 1]
            sheet.delete_rows(row_index + 4)  # Adjust for header row and 0-based index
        else:
            st.warning("Invalid row index.")
    else:
        st.warning("Invalid row index.")



with st.sidebar:
    image_url = "akp-logo.png"
    st.image(image_url, caption='', use_column_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    index_row = st.text_input('Number of row: ', "", placeholder="used only for update and delete...")
    fullname = st.selectbox(
                            'In the name of: ',
                            ('Vegim Çeku', 'Petrit Preteni', 'Meriton Bunjaku')
                            )
    device = st.text_input('Device: ', "", placeholder="name of device...")
    barcode = st.text_input('Barcode: ', "", placeholder="barcode of device...")

    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        create = st.button('Add')
        if create:
            create_data(fullname, device, barcode)
    
    with col2:
        update = st.button("Update")
        if update:
            if index_row:
                update_data(int(index_row), fullname, device, barcode)
            else:
                st.warning("Please enter the row index.")

    with col3:
        delete = st.button("Delete")
        if delete:
            if index_row and int(index_row) > 0:  # Check for valid row index
                delete_data(int(index_row))
            else:
                st.warning("Invalid row index.")

# Search Engine For Specific Column
def search_data(df, column, query):
    if column in df.columns:
        results = df[df[column].str.contains(query, case=False, na=False)]
        return results
    else:
        st.warning(f"Column '{column}' not found in the data.")

col4, col5 = st.columns(2)
with col4:
    search_column = st.selectbox('Column Name:', ('Fullname', 'Device', 'Barcode'))
with col5:
    search_query = st.text_input('Search by:', "", placeholder=f"{search_column}...")

# Style thead for table in web app
table_style = """
    <style>
        thead {background-color: #454545;}
        thead th {color: #EFF5F5 !important;}
        tbody tr:nth-child(even) th,
        tbody tr:nth-child(even) td {background-color: #E3E3E3;}
        tbody tr:nth-child(odd) th,
        tbody tr:nth-child(odd) td {background-color: #FAFAFA;}
        .row_heading {background-color: #F7F9F9;}

        @media (prefers-color-scheme: dark) {
            tbody tr:nth-child(even) th,
            tbody tr:nth-child(even) td {color: black;}
            tbody tr:nth-child(odd) th,
            tbody tr:nth-child(odd) td {color: black;}
        }
    </style>
"""

df = read_data()
if not df.empty:
    df.index = df.index + 1  # Adjust row index to start from 1
    if search_query:
        search_results = search_data(df, search_column, search_query)

        # Display the table with the custom background color and text color
        st.markdown(table_style, unsafe_allow_html=True)
        st.table(search_results)
    else:
        # Display the table with the custom background color and text color
        st.markdown(table_style, unsafe_allow_html=True)
        st.table(df)
else:
    st.info(f"No devices for {fullname}.")


# Style for buttons, section for responsive buttons
button_width_desktop = "118px"

# Adjust this value based on your preference for mobile devices
button_width_mobile = "100%"  

st.markdown(
    f"""
    <style>
        @media only screen and (min-width: 768px) {{
            div.stButton > button:first-child {{
                width: {button_width_desktop};
                height: auto;
            }}
        }}
        @media only screen and (max-width: 767px) {{
            div.stButton > button:first-child {{
                width: {button_width_mobile};
                height: auto;
            }}
        }}
    </style>
    """, unsafe_allow_html=True,
)





