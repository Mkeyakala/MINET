import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
def execute_dynamic_query(selected_duration, selected_companies, selected_claim, selected_quarter, selected_year):
    
    query = """
        SELECT c.company_name, d.claim_type, SUM(p.premium_value)
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
    if selected_companies:
        query += f" AND c.company_name IN ({','.join(['%s']*len(selected_companies))})"
        parameters.extend(selected_companies)
    if selected_claim:
        query += f" AND d.claim_type IN ({','.join(['%s']*len(selected_claim))})"
        parameters.extend(selected_claim)
    if selected_quarter:
        query += f" AND p.quarter_name IN ({','.join(['%s']*len(selected_quarter))})"
        parameters.extend(selected_quarter)
    if selected_year:
        query += " AND p.year = %s"
        parameters.append(selected_year)

    query += " GROUP BY c.company_name, d.claim_type"

    # Execute the SQL query with parameters
    cursor.execute(query, parameters)
    results = cursor.fetchall()

    # Convert premium values to integers
    results = [(company, claim_type, int(total_premium)) for company, claim_type, total_premium in results]

    return results

# Get user input
selected_duration = st.sidebar.selectbox("Select Duration", [""] + execute_query("Duration"))
selected_year = st.sidebar.selectbox("Select Year", [""] + execute_query("Years"))
selected_companies = st.sidebar.multiselect("Select Companies", execute_query("Companies", selected_duration=selected_duration))
selected_claim = st.sidebar.multiselect("Select Claim Type", [""] + execute_query("Claim Type", selected_duration=selected_duration))
selected_quarter = st.sidebar.multiselect("Select Quarter", [""] + execute_query("Quarters"))

# Button to trigger graph display
if st.sidebar.button("Generate Graph"):
    # Display company, claim type, and total premium value based on user input
    if selected_duration:
        results = execute_dynamic_query(selected_duration, selected_companies, selected_claim, selected_quarter, selected_year)
        data = pd.DataFrame(results, columns=['Company', 'Claim Type', 'Total Premium Value'])
        # st.write("Data:", data) 

        # Pivot the data
        pivoted_data = data.pivot(index='Claim Type', columns='Company', values='Total Premium Value')
        a = pivoted_data.dtypes
        
       
            # Display pivoted data in styled squares
        st.write("<style> .square { padding: 10px; border: 2px solid #ddd; border-radius: 5px; margin-right: 5px; margin-bottom: 5px; } </style>", unsafe_allow_html=True)
        
        for company, values in pivoted_data.items():
            st.write(f"<div class='square' style='float: left;'><h4>{company}</h4>{values.to_frame().to_html()}</div>", unsafe_allow_html=True)
           

        
        # Convert 'Total Premium Value' to numeric, coercing errors to NaN
        data['Total Premium Value'] = pd.to_numeric(data['Total Premium Value'], errors='coerce')

        # Drop rows with NaN values in 'Total Premium Value'
        data.dropna(subset=['Total Premium Value'], inplace=True)

        # Bar chart
        if not pivoted_data.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            pivoted_data.plot(kind='bar', ax=ax)
            ax.set_xlabel('Claim Type')
            ax.set_ylabel('Total Premium Value')
            ax.set_title(selected_duration)
            st.pyplot(fig)
        else:
            st.write("No data available for the selected criteria")

        
# Close the cursor and connection
cursor.close()
conn.close()
