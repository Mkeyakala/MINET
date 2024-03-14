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
def execute_dynamic_query(selected_duration, selected_company, selected_category):
    query = """
        SELECT c.company_name, d.claim_type, p.year, p.quarter_name, SUM(p.premium_value), SUM(pr.profit_value)
        FROM premiums p 
        JOIN companies c ON p.company_id = c.company_id 
        JOIN claim_type d ON p.claim_type_id = d.claim_type_id
        JOIN profits pr ON p.company_id = pr.company_id
        WHERE 1=1
    """
    parameters = []

    # Add conditions based on user-selected filters
    if selected_company:
        query += " AND c.company_name = %s"
        parameters.append(selected_company)
    if selected_duration:
        query += " AND p.duration = %s"
        parameters.append(selected_duration)
    if selected_category == "Profits":
        query += " AND pr.profit_value IS NOT NULL"
    else:
        query += " AND p.premium_value IS NOT NULL"

    query += " GROUP BY c.company_name, d.claim_type, p.year, p.quarter_name"
    
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    return results

# Get user input
selected_duration = st.sidebar.selectbox("Select Duration", [""] + execute_query("Duration"))
selected_company = st.sidebar.selectbox("Select Company", [""] + execute_query("Companies", selected_duration=selected_duration))
selected_category = st.sidebar.radio("Select Category", ["Profits", "Premiums"])

# Button to trigger graph display
if st.sidebar.button("Generate Graph"):
    if selected_duration and selected_company:
        results = execute_dynamic_query(selected_duration, selected_company, selected_category)
        if results:
            data = pd.DataFrame(results, columns=['Company', 'Claim Type', 'Year', 'Quarter', 'Total Premium', 'Total Profit'])
            st.write(data)

            # Plot profit and premium growth over the years, segmented by claims and quarters
            for claim_type in data['Claim Type'].unique():
                plt.figure(figsize=(10, 6))

                for quarter in data['Quarter'].unique():
                    subset = data[(data['Claim Type'] == claim_type) & (data['Quarter'] == quarter)]
                    if selected_category == "Profits":
                        plt.plot(subset['Year'], subset['Total Profit'], label=quarter)
                    else:
                        plt.plot(subset['Year'], subset['Total Premium'], label=quarter)

                plt.xlabel('Year')
                if selected_category == "Profits":
                    plt.ylabel('Total Profit')
                    plt.title(f'Profit Growth over Years for {selected_company}, {claim_type}')
                else:
                    plt.ylabel('Total Premium')
                    plt.title(f'Premium Growth over Years for {selected_company}, {claim_type}')
                plt.legend()
                st.pyplot(plt)
        else:
            st.write("No data available for the selected company and duration")

# Close the cursor and connection
cursor.close()
conn.close()

