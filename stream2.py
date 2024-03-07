import streamlit as st
import mysql.connector


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="LULUPOP"
)

cursor = conn.cursor()

# Function to execute queries based on selected section
def execute_query(section):
    if section == "Companies":
        cursor.execute("SELECT DISTINCT company_name FROM companies")
    elif section == "Quarters":
        cursor.execute("SELECT DISTINCT quarter_name FROM premiums")
    elif section == "Years":
        cursor.execute("SELECT DISTINCT year FROM premiums")
    elif section =='Claim Type':
        cursor.execute('SELECT DISTINCT claim_type FROM claim_type') 
    return [result[0] for result in cursor.fetchall()]


def execute_dynamic_query(selected_company, selected_claim, selected_quarter, selected_year):
    # Build the SQL query dynamically based on user input
    query = """
        SELECT SUM(p.premium_value)
        FROM premiums p 
        JOIN companies c ON p.company_id = c.company_id 
        JOIN claim_type d ON p.claim_type_id = d.claim_type_id
        WHERE 1=1
    """
    parameters = []

    # Add conditions based on user-selected filters
    if selected_company:
        query += " AND c.company_name = %s"
        parameters.append(selected_company)
    if selected_claim:
        query += f" AND d.claim_type IN ({','.join(['%s']*len(selected_claim))})"
        parameters.extend(selected_claim)
    if selected_quarter:
        query += f" AND p.quarter_name IN ({','.join(['%s']*len(selected_quarter))})"
        parameters.extend(selected_quarter)
    if selected_year:
        query += " AND p.year = %s"
        parameters.append(selected_year)

    print("Query:", query)
    print("Parameters:", parameters)

    # Execute the SQL query with parameters
    cursor.execute(query, parameters)
    result = cursor.fetchone()
    print("Result:", result)

    return result[0]

# Get user input
selected_year = st.sidebar.selectbox("Select Year", [""] + execute_query("Years"))
selected_company = st.sidebar.selectbox("Select Company", [""] + execute_query("Companies"))
selected_claim = st.sidebar.multiselect("Select Claim Type", [""] + execute_query("Claim Type"))
selected_quarter = st.sidebar.multiselect("Select Quarter", [""] + execute_query("Quarters"))

# Display total premium value based on user input
total_premium = execute_dynamic_query(selected_company, selected_claim, selected_quarter, selected_year)

st.write(f"Total Premium Value: {total_premium}")

# Close the cursor and connection
cursor.close()
conn.close()

