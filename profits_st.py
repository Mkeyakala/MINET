import pandas as pd
import MySQLdb

# Function to get company ID
def get_company_id(cursor, company_name):
    cursor.execute("SELECT company_id FROM companies WHERE company_name = %s", (company_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Function to get claim type ID by name
def get_claim_type_id(cursor, claim_type_name):
    cursor.execute("SELECT claim_type_id FROM claim_type WHERE claim_type = %s", (claim_type_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

conn = MySQLdb.connect(user='root', passwd='admin', host='localhost', database='LULUPOP')
cursor = conn.cursor()

# Read short-term profits from Excel
xls_st = pd.ExcelFile("shortterm/profits/2023.xlsx")

# Iterate over each sheet (quarter) in short-term profits
for sheet_name in xls_st.sheet_names:
    print("Processing short-term profits for quarter:", sheet_name)

    # Read the current sheet into a DataFrame
    df_st = pd.read_excel(xls_st, sheet_name=sheet_name)

    # Replace NaN values with 0
    df_st.fillna(0, inplace=True)

    # Iterate over each row (company) in short-term profits
    for index, row in df_st.iterrows():
        company_name = row.iloc[0]  # Assuming company name is in the first column
        company_id = get_company_id(cursor, company_name)

        if company_id is not None:
            # Insert short-term profits into the database
            for claim_type, profit_value in row.iloc[1:].items():
                if profit_value != '-':
                    # Get claim type ID by name
                    claim_type_id = get_claim_type_id(cursor, claim_type)
                    if claim_type_id is not None:
                        print("Company:", company_name, "| Claim Type:", claim_type, "| Short-Term Profit Value:", profit_value)
                        cursor.execute("INSERT INTO profits (company_id, claim_type_id, profit_value, year, quarter_name, duration) VALUES (%s, %s, %s, %s, %s, 'ST')",
                                       (company_id, claim_type_id, profit_value, 2023, sheet_name))
                        print("Short-term profit inserted successfully for company:", company_name, "in quarter:", sheet_name)

# Commit changes after processing short-term profits
conn.commit()

# Read long-term profits from Excel
xls_lt = pd.ExcelFile("shortterm/profits/2023plt.xlsx")

# Iterate over each sheet (quarter) in long-term profits
for sheet_name in xls_lt.sheet_names:
    print("Processing long-term profits for quarter:", sheet_name)

    # Read the current sheet into a DataFrame
    df_lt = pd.read_excel(xls_lt, sheet_name=sheet_name)

    # Replace NaN values with 0
    df_lt.fillna(0, inplace=True)

    # Iterate over each row (company) in long-term profits
    for index, row in df_lt.iterrows():
        company_name = row.iloc[0]  # Assuming company name is in the first column
        company_id = get_company_id(cursor, company_name)

        if company_id is not None:
            # Insert long-term profits into the database
            long_term_profit = row.iloc[3]  # Assuming the long-term profit is in the fourth column
            if long_term_profit != '-':
                print("Company:", company_name, "| Long-Term Profit Value:", long_term_profit)
                cursor.execute("INSERT INTO profits (company_id, profit_value, year, quarter_name, duration) VALUES (%s, %s, %s, %s, %s)",
                               (company_id, long_term_profit, 2023, sheet_name, 'LT'))
                print("Long-term profit inserted successfully for company:", company_name, "in quarter:", sheet_name)

# Commit changes after processing long-term profits
conn.commit()

# Close cursor and connection
cursor.close()
conn.close()
