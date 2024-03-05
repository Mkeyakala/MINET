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

# Function to get claim type ID
def get_claim_type_id(cursor, claim_type_name):
    cursor.execute("SELECT claim_type_id FROM claim_type WHERE claim_type = %s", (claim_type_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

conn = MySQLdb.connect(user='root', passwd='admin', host='localhost', database='LULUPOP')
cursor = conn.cursor()

# Read the Excel file into a DataFrame
xls = pd.ExcelFile("profits/2018.xlsx")

# Iterate over each sheet (quarter)
for sheet_name in xls.sheet_names:
    print("Processing quarter:", sheet_name)
    
    # Read the current sheet into a DataFrame
    df1 = pd.read_excel(xls, sheet_name=sheet_name)
    
    print("DataFrame contents:")
    print(df1)  # Check DataFrame content
    
    # Iterate over each row (company)
    for index, row in df1.iterrows():
        company_name = row.iloc[0]  # Assuming company name is in the first column
        company_id = get_company_id(cursor, company_name)
        
        if company_id is not None:
            # Iterate over each column (claim type) starting from the second column
            for claim_type, premium_value in row.iloc[1:].items():
                claim_type_id = get_claim_type_id(cursor, claim_type)
                
                if claim_type_id is not None:
                    print("Company:", company_name, "| Claim Type:", claim_type, "| Premium Value:", premium_value)
                    
                    # Insert data into the database
                    cursor.execute("INSERT INTO premiums (company_id, claim_type_id, premium_value, year, quarter_name) VALUES (%s, %s, %s, %s, %s)",
                                   (company_id, claim_type_id, premium_value, 2018, sheet_name))
                    print("Data inserted successfully for company:", company_name, "in quarter:", sheet_name)

# Commit changes after processing all rows
conn.commit()

# Close cursor and connection
cursor.close()
conn.close()

