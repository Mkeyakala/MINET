import streamlit as st
import pandas as pd
import MySQLdb
import matplotlib.pyplot as plt


# Function to connect to the database and retrieve data for companies
def get_company_data_from_database(duration):
    conn = MySQLdb.connect(user='root', passwd='admin', host='localhost', database='LULUPOP')
    cursor = conn.cursor()

    # Query to retrieve total profits for each company based on duration
    cursor.execute("""
        SELECT 
            c.company_name,
            SUM(p.profit_value) AS total_profit
        FROM 
            profits AS p
        JOIN 
            companies AS c ON p.company_id = c.company_id
        WHERE 
            p.year = 2023 AND p.duration = %s
        GROUP BY 
            p.company_id
        ORDER BY 
            total_profit DESC
    """, (duration,))
    data = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    # Convert data into a DataFrame
    df = pd.DataFrame(data, columns=['Company Name', 'Total Profit'])

    return df


# Function to connect to the database and retrieve data for claim types
def get_claim_type_data_from_database(duration):
    conn = MySQLdb.connect(user='root', passwd='admin', host='localhost', database='LULUPOP')
    cursor = conn.cursor()

    # Query to retrieve total profits for each claim type based on duration
    cursor.execute("""
        SELECT 
            ct.claim_type,
            SUM(p.profit_value) AS total_profit
        FROM 
            profits AS p
        JOIN 
            claim_type AS ct ON p.claim_type_id = ct.claim_type_id
        WHERE 
            p.year = 2023 AND p.duration = %s
        GROUP BY 
            p.claim_type_id
        ORDER BY 
            total_profit DESC
    """, (duration,))
    data = cursor.fetchall()

    # Close cursor and connection
    cursor.close()
    conn.close()

    # Convert data into a DataFrame
    df = pd.DataFrame(data, columns=['Claim Type', 'Total Profit'])

    return df


# Main function to run the Streamlit app
def main():
    st.title("Ranking of Companies and Claim Types based on Profitability in 2023 in '000's ")

    # Sidebar for selecting duration
    duration = st.sidebar.radio("Select Duration", ['Short Term', 'Long Term'])

    # Load data for companies and claim types from database based on duration
    if duration == 'Short Term':
        company_data = get_company_data_from_database('ST')
        claim_type_data = get_claim_type_data_from_database('ST')
    else:
        company_data = get_company_data_from_database('LT')
        claim_type_data = get_claim_type_data_from_database('LT')

    # Display ranked companies based on profitability
    st.write('Ranked Companies based on Profitability in 2023:')
    st.write(company_data)

    # Display ranked claim types based on profitability
    st.write('Ranked Claim Types based on Profitability in 2023:')
    st.write(claim_type_data)

    # Plot bar chart for companies
    plt.figure(figsize=(10, 6))
    plt.barh(company_data['Company Name'], company_data['Total Profit'], color='skyblue')
    plt.xlabel('Total Profit')
    plt.ylabel('Company Name')
    plt.title('Top Companies based on Profit in 2023')
    st.pyplot(plt)

    # Plot bar chart for claim types
    plt.figure(figsize=(10, 6))
    plt.barh(claim_type_data['Claim Type'], claim_type_data['Total Profit'], color='lightgreen')
    plt.xlabel('Total Profit')
    plt.ylabel('Claim Type')
    plt.title('Top Claim Types based on Profit in 2023')
    st.pyplot(plt)


if __name__ == '__main__':
    main()
