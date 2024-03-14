import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="LULUPOP"
)

cursor = conn.cursor()

# Function to execute queries based on selected section
def execute_query(section, selected_duration=None):
    if section == "Companies":
        if selected_duration:
            cursor.execute("SELECT DISTINCT company_name FROM premiums INNER JOIN companies ON premiums.company_id = companies.company_id WHERE duration = %s", (selected_duration,))
        else:
            cursor.execute("SELECT DISTINCT company_name FROM companies")
    elif section == "Quarters":
        cursor.execute("SELECT DISTINCT quarter_name FROM premiums")
    elif section == "Years":
        cursor.execute("SELECT DISTINCT year FROM premiums")
    elif section == "Duration":
        cursor.execute("SELECT DISTINCT duration FROM premiums")
    elif section == "Claim Type":
        if selected_duration:
            cursor.execute("SELECT DISTINCT claim_type FROM premiums INNER JOIN claim_type ON premiums.claim_type_id = claim_type.claim_type_id WHERE duration = %s", (selected_duration,))
        else:
            cursor.execute("SELECT DISTINCT claim_type FROM claim_type")
    return [result[0] for result in cursor.fetchall()]

# Function to execute dynamic query
def execute_dynamic_query(selected_duration, selected_quarters, selected_company, selected_claim):
    
    query = """
        SELECT c.company_name, d.claim_type, p.quarter_name, SUM(p.premium_value)
        FROM premiums p 
        JOIN companies c ON p.company_id = c.company_id 
        JOIN claim_type d ON p.claim_type_id = d.claim_type_id
        WHERE 1=1
    """
    parameters = []

    # Add conditions based on user-selected filters
    if selected_duration:
        query += " AND p.duration = %s"
        parameters.append(selected_duration)
    if selected_company:
        query += " AND c.company_name = %s"
        parameters.append(selected_company)
    if selected_claim:
        query += f" AND d.claim_type IN ({','.join(['%s']*len(selected_claim))})"
        parameters.extend(selected_claim)
    if selected_quarters:
        query += f" AND p.quarter_name IN ({','.join(['%s']*len(selected_quarters))})"
        parameters.extend(selected_quarters)

    query += " GROUP BY c.company_name, d.claim_type, p.quarter_name"

    # Execute the SQL query with parameters
    cursor.execute(query, parameters)
    results = cursor.fetchall()

    # Convert premium values to integers
    results = [(company, claim_type, quarter, int(total_premium)) for company, claim_type, quarter, total_premium in results]

    return results

# Get user input
selected_duration = st.sidebar.selectbox("Select Duration", [""] + execute_query("Duration"))
selected_company = st.sidebar.selectbox("Select Company", [""] + execute_query("Companies", selected_duration=selected_duration))
selected_claim = st.sidebar.multiselect("Select Claim Type", [""] + execute_query("Claim Type", selected_duration=selected_duration))
selected_quarters = st.sidebar.multiselect("Select Quarters", execute_query("Quarters"))

# Display company, claim type, and total premium value based on user input
if selected_duration and len(selected_quarters) == 2:
    results = execute_dynamic_query(selected_duration, selected_quarters, selected_company, selected_claim)
    data = pd.DataFrame(results, columns=['Company', 'Claim Type', 'Quarter', 'Total Premium Value'])
    
    if not data.empty:
        # Calculate percentage change between the two quarters for each claim type
        data_pivot = data.pivot_table(index=['Company', 'Claim Type'], columns='Quarter', values='Total Premium Value', fill_value=0)
        data_pivot['Change (%)'] = ((data_pivot[selected_quarters[1]] - data_pivot[selected_quarters[0]]) / data_pivot[selected_quarters[0]]) * 100

        st.write("Quarterly Premium Change (%)")
        st.write(data_pivot)

        # Create a joined bar chart
        data_bar = data.pivot_table(index=['Company', 'Claim Type'], columns='Quarter', values='Total Premium Value', fill_value=0)
        ax = data_bar.plot(kind='bar', figsize=(10, 6))
        ax.set_xlabel('Company, Claim Type')
        ax.set_ylabel('Total Premium Value')
        ax.set_title('Comparison of Premium Values for Selected Companies and Quarters')
        st.pyplot()
        st.set_option('deprecation.showPyplotGlobalUse', False)
else:
    st.write("Please select two quarters to compare premium collection and see change in percentage ")
    
# Close the cursor and connection
cursor.close()
conn.close()
