import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import mysql.connector
import seaborn as sns
#import plotly.express as px

# DataBase Connection
import mysql.connector

conn = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '12345'
)
# MySQL connection Setup
cursor = conn.cursor()

# Use Database
cursor.execute("use food_data")

r = st.sidebar.radio('NAVIGATION',['Home', 'View Tables', 'CRUD Operation', 'SQL Queries and Visualizations', 'SQL Play Field', 'Contact', 'About'])

if r == 'Home':
    st.subheader("Welcome To Food Waste Management System")
    st.image("food_waste_management_picture.png")
    #st.balloons()
    st.markdown("""
    ## Problem Statement
    Food wastage is a significant issue, with many households and restaurants discarding surplus food while numerous people struggle with food insecurity. This project aims to develop a Local Food Wastage Management System, where:
    - Restaurants and individuals can list surplus food.
    - NGOs or individuals in need can claim the food.
    - SQL stores available food details and locations.
    - A Streamlit app enables interaction, filtering, CRUD operations, and visualization. 
    """)

if r == 'View Tables':
    st.title("DataBase Tabels")
    dataset = st.selectbox("Choose Table", ['food_listings_data.csv', 'providers_data.csv', 'receivers_data.csv', 'claims_data.csv'])
    
    if dataset == 'food_listings_data.csv':
        df = pd.read_csv("food_listings_data.csv")
        st.write(df)
    
    if dataset == 'providers_data.csv':
        df = pd.read_csv("providers_data.csv")
        st.write(df)

    if dataset == 'receivers_data.csv':
        df = pd.read_csv("receivers_data.csv")
        st.write(df)
    
    if dataset == 'claims_data.csv':
        df = pd.read_csv("claims_data.csv")
        st.write(df)

if r == 'CRUD Operation':
    st.title("Manage Food Data")
    table_selection = st.selectbox("Select Table",['food_listings', 'providers', 'receivers', 'claims'])
    operation = st.selectbox("Select Your Operation",['Insert','Update','Delete'])
    
    cursor.execute(f"SELECT * FROM {table_selection};")
    rows = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    if table_selection:
        if operation == 'Insert':
            with st.form("Insert Data"):
                    new_values = [st.text_input(f'Enter {col}') for col in cols]
                    submit = st.form_submit_button("Insert")      
                    if submit:
                        placeholder = ','.join(["%s"] * len(new_values))
                        sql = f"INSERT INTO {table_selection} ({', '.join(cols)}) VALUES ({placeholder})"
                        cursor.execute(sql,new_values)
                        conn.commit()
                        st.success('Row Inserted Successfully')
                        cursor.close()
                        conn.close()   
    
        
        elif operation == 'Update':
            condition_col = st.selectbox('Condition Column', cols)
            condition_val = st.text_input('Condition Value')
            update_col = st.selectbox('Column to Update', cols)
            new_value = st.text_input("New Value")
            if st.button("Update"):
                sql = f"UPDATE {table_selection} SET {condition_col}=%s WHERE {condition_val}=%s"
                cursor.execute(sql,(new_value,condition_val))
                conn.commit()
                st.success('Row Updated Successfully')
                cursor.close()
                conn.close()                
                     
        elif operation == 'Delete':
            condition_col = st.selectbox('Condition Column', cols)
            condition_val = st.text_input('Condition Value')
            if st.button("Delete"):
                sql = f"DELETE FROM {table_selection} WHERE {condition_col}=%s"
                cursor.execute(sql,(condition_val,))
                conn.commit()
                st.success('Row Deleted Successfully')
                cursor.close()
                conn.close()               
    
        else:
            print("Please Select one of the Above Choice.")


if r == 'SQL Queries and Visualizations':
    st.title("SQL Queries and Visualizations")
    query_selection = st.selectbox("Select Query Section of your choice",
                                   ['Food Providers & Receivers',
                                    'Food Listings & Availability',
                                    'Claims & Distribution',
                                    'Analysis & Insights'
                                   ])
    if query_selection == 'Food Providers & Receivers':
        q1 = st.selectbox("Select Relevant Sub-Query",
                         ['Total Food Providers and Receivers in Each City',
                         'Top Most Food Contributor',
                         'Contact Information of Food Provider Specific to City',
                         'Most Claimed Food by Receiver'])


        # Query1
        if q1 == "Total Food Providers and Receivers in Each City":
            query1 = """
            SELECT City, COUNT(*) AS Provider_Count 
            FROM providers
            GROUP BY City
            ORDER BY Provider_Count DESC;
            """

            cursor.execute(query1)
            result = cursor.fetchall()

            # convert result into a dataframe
            df1 = pd.DataFrame(result,columns =['City','Provider_Count'])
            st.write(df1)

            query2 = """
            SELECT City, COUNT(*) AS Receivers_Count
            FROM receivers
            GROUP BY City
            ORDER BY Receivers_Count DESC;
            """

            cursor.execute(query2)
            result = cursor.fetchall()

            # convert result into a dataframe
            df2 = pd.DataFrame(result,columns =['City','Receiver_Count'])
            st.write(df2)

        # Query2
        if q1 == "Top Most Food Contributor":
            query = """
            SELECT Provider_Type as Food_Provider_Type, SUM(Quantity) AS 'Total_food_Contribution(in Quantity)'
            FROM food_data.food_listings 
            GROUP BY 1
            ORDER BY 2 DESC;
            """

            cursor.execute(query)
            result = cursor.fetchall()

            # convert result into dataframe
            df = pd.DataFrame(result,columns =['Provider Type','Total_food_Contribution(in Quantity)'])
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    x=alt.X('Provider Type', sort='-y'),
                    y='Total_food_Contribution(in Quantity)',
                    color='Provider Type',   # different color per bar
                    tooltip=['Provider Type', 'Total_food_Contribution(in Quantity)']
                )
                .properties(
                    title="Most Frequent Food Providers",
                    width=600,
                    height=400
                )
            )
            st.altair_chart(chart, use_container_width=True)

        # Query 3
        if q1 == "Contact Information of Food Provider Specific to City":
            query = """
            SELECT f.Location as City, p.Name AS Provider_Name, p.Contact AS Contact_No
            FROM food_data.food_listings f
            JOIN food_data.providers p
            ON f.Provider_ID = p.Provider_ID
            ORDER BY 1;
            """

            cursor.execute(query)
            result = cursor.fetchall()

            # convert result into dataframe
            df = pd.DataFrame(result,columns =['City','Provier Name','Contact No.'])
            st.write(df)

            
        # Query 4
        if q1 == "Most Claimed Food by Receiver":
            query = """
            SELECT  DISTINCT r.Type AS Receivers_Type, SUM(f.Quantity) AS Total_Claimed
            FROM receivers r
            JOIN claims c
            ON r.Receivers_ID = c.Receiver_ID
            JOIN food_listings f
            ON c.Food_ID = f.Food_ID
            GROUP BY 1
            ORDER By 2 DESC; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into a dataframe
            df = pd.DataFrame(result, columns =['Receiver Type','Total Claimed'])
            chart = (
                    alt.Chart(df)
                    .mark_bar(cornerRadius=5)  # rounded corners for a modern look
                    .encode(
                        y=alt.Y('Receiver Type', sort='-x', title="Receiver Type"),
                        x=alt.X('Total Claimed', title="Total Claimed (Quantity)"),
                        color=alt.Color('Receiver Type', legend=None),  # auto-color by type
                        tooltip=['Receiver Type', 'Total Claimed']
                    )
                    .properties(
                        title="Most Claimed Food by Receiver",
                        width=600,
                        height=400
                    )
                )
                
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)

    
            
        
    elif query_selection == 'Food Listings & Availability':
        q2 = st.selectbox("Select Relevant Sub-Query",
                          ['Total Food Available From All Providers',
                          'City Specific Food Listings',
                          'Most Common Available Food Type'])

         # Query 5
        if q2 == "Total Food Available From All Providers":
            query = """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
            FROM food_data.food_listings
            GROUP BY 1
            ORDER BY 2 DESC;
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into dataframe
            df = pd.DataFrame(result, columns =['Provider Type', 'Total Quantity'])
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
                df['Total Quantity'],
                labels=df['Provider Type'],
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops=dict(width=0.4)   # makes it a donut
            )
            ax.set_title("Food Contribution by Provider Type")
            st.pyplot(fig)
            #st.write(df) 

        # Query 6
        if q2 == "City Specific Food Listings":
            query = """
            SELECT p.City AS food_City, f.Location as food_location, SUM(f.Quantity) AS Number_of_food_listings
            FROM food_data.providers p
            LEFT JOIN food_data.food_listings f
            ON p.City = f.Location
            GROUP BY 1,2 
            ORDER BY 3 DESC;
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into dataframe
            df = pd.DataFrame(result, columns =['Food City','Food Location','Number of Food Listings'])
            st.write(df)


       # Query 7
        if q2 == "Most Common Available Food Type":
            query = """
            SELECT DISTINCT Food_Type, COUNT(Food_Type) AS Availability_count 
            FROM food_data.food_listings
            GROUP BY 1
            ORDER BY 2 DESC; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into dataframe
            df = pd.DataFrame(result, columns =['Food Type','Availability Count'])
            chart = (
                    alt.Chart(df)
                    .mark_bar(cornerRadius=5)
                    .encode(
                        y=alt.Y('Food Type', sort='-x', title="Food Type"),
                        x=alt.X('Availability Count', title="Count"),
                        color=alt.Color('Food Type', legend=None),
                        tooltip=['Food Type', 'Availability Count']
                    )
                    .properties(
                        title="Most Common Available Food Types",
                        width=600,
                        height=400
                    )
                )
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)     
        
    elif query_selection == 'Claims & Distribution':
        q3 = st.selectbox("Select Relevant Sub-Query",
                          ['Food Claims For Each Item',
                           'Provider with Highest Successful Food Claims',
                           'Percentage of Food Claims- Completed, Pending, Canceled'])

        # Query 8
        if q3 == "Food Claims For Each Item":
            query = """
            SELECT DISTINCT f.Food_Name AS Food_Name, f.Food_ID AS Food_ID, COUNT(c.Receiver_ID) AS Total_Food_Claims
            FROM food_data.food_listings f
            JOIN food_data.claims c
            ON f.Food_ID = c.Food_ID
            GROUP BY 1
            ORDER BY 3 DESC; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into dataframe
            df = pd.DataFrame(result, columns =['Food Name', 'Food ID', 'Total Food Claims'])
            chart = (
                    alt.Chart(df)
                    .mark_bar(cornerRadius=4)
                    .encode(
                        y=alt.Y('Food Name', sort='-x', title="Food Item"),
                        x=alt.X('Total Food Claims', title="Number of Claims"),
                        color=alt.Color('Total Food Claims', scale=alt.Scale(scheme='blues'), legend=None),
                        tooltip=['Food Name', 'Total Food Claims']
                    )
                    .properties(
                        title="Food Claims for Each Item",
                        width=700,
                        height=400
                    )
                )
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)


       # Query 9
        if q3 == "Provider with Highest Successful Food Claims":
            query = """
            SELECT DISTINCT f.Provider_Type AS Food_Provider, f.Food_Name AS Food_Name, f.Food_ID AS Food_ID, COUNT(c.Receiver_ID) AS Total_Successful_Food_Claims
            FROM food_data.food_listings f
            JOIN food_data.claims c
            ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY 1
            ORDER BY 4 DESC; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into a dataframe
            df = pd.DataFrame(result, columns =['Food Provider', 'Food Name', 'Food ID', 'Total Successful Food Claims'])
            chart = (
                    alt.Chart(df)
                    .mark_bar(cornerRadius=4)
                    .encode(
                        y=alt.Y('Food Provider', sort='-x', title="Food Item"),
                        x=alt.X('Total Successful Food Claims', title="Number of Claims"),
                        color=alt.Color('Total Successful Food Claims', scale=alt.Scale(scheme='blues'), legend=None),
                        tooltip=['Food Provider', 'Total Successful Food Claims']
                    )
                    .properties(
                        title="Food Claims By Each Providers",
                        width=700,
                        height=400
                    )
                )
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)


        # Query 10
        if q3 == "Percentage of Food Claims- Completed, Pending, Canceled":
            query = """
            SELECT Status,
    	    COUNT(*) AS Count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM food_data.claims),2) AS Percentage
            FROM food_data.claims
            GROUP BY 1; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into dataframe
            df = pd.DataFrame(result, columns =['Status','Count','Percentage'])
            chart = (
                    alt.Chart(df)
                    .mark_arc(innerRadius=70)  # donut
                    .encode(
                        theta=alt.Theta("Percentage:Q"),
                        color=alt.Color("Status:N"),
                        tooltip=["Status", "Count", "Percentage"]
                    )
                    .properties(title="Percentage of Food Claims by Status")
                )
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)    

        
    elif query_selection == 'Analysis & Insights':
        q4 = st.selectbox("Select Relevant Sub-Query",[
            'Average Quantity of Food Claimed Per Receiver',
            'Most Claimed Meal Type',
            'Total Quantity of Food Donated By Each Provider'])



    # Query 11
        if q4 == "Average Quantity of Food Claimed Per Receiver":
            query = """
            SELECT 
            r.Type AS Receiver_Type,
            COUNT(DISTINCT r.Receivers_ID) AS Total_Receivers,
            SUM(f.Quantity) AS Total_Claimed,
            ROUND(SUM(f.Quantity) * 1.0 / COUNT(DISTINCT r.Receivers_ID), 2) AS Avg_Claimed_Per_Receiver
            FROM food_data.receivers r
            JOIN food_data.claims c
                ON r.Receivers_ID = c.Receiver_ID
            JOIN food_data.food_listings f
                ON f.Food_ID = c.Food_ID
            GROUP BY r.Type
            ORDER BY Avg_Claimed_Per_Receiver DESC;
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into a. dataframe
            df = pd.DataFrame(result, columns =['Receiver Type', 'Total Receivers','Total Claimed','Avg Claimed Per Receiver'])
            chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X('Receiver Type:N', sort='-y', title='Receiver Type'),
                y=alt.Y('Avg Claimed Per Receiver:Q', title='Average Claimed Quantity'),
                color=alt.Color('Receiver Type:N', legend=None),
                tooltip=['Receiver Type', 'Total Receivers', 'Total Claimed', 'Avg Claimed Per Receiver']
            )
            .properties(
                title="Average Quantity of Food Claimed Per Receiver Type",
                width=600,
                height=400
                )
            )
        
            st.altair_chart(chart, use_container_width=True)
           # st.write(df)

    # Query 12
        if q4 == "Most Claimed Meal Type":
            query = """
            SELECT Meal_Type,
		    COUNT(*) AS Count,
		    ROUND((COUNT(*) * 100) / (SELECT COUNT(*) FROM food_data.claims),2) AS Percentage
            FROM food_data.food_listings
            GROUP BY 1
            ORDER BY 3 DESC; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into dataframe
            df = pd.DataFrame(result, columns =['Meal Type','Count','Percentage'])
            # Donut chart for Meal Type claims
            chart = (
                alt.Chart(df)
                .mark_arc(innerRadius=80)  # donut
                .encode(
                    theta=alt.Theta("Percentage:Q"),
                    color=alt.Color("Meal Type:N", legend=alt.Legend(title="Meal Type")),
                    tooltip=["Meal Type", "Count", "Percentage"]
                )
                .properties(
                    title="Most Claimed Meal Type (Percentage Share)"
                )
            )
            
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)

        # Query 13
        if q4 == "Total Quantity of Food Donated By Each Provider":
            query = """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
            FROM food_data.food_listings
            GROUP BY 1
            ORDER BY 2 DESC; 
            """

            cursor.execute(query)
            result = cursor.fetchall()
 
            # convert result into a dataframe
            df = pd.DataFrame(result, columns =['Provider Type','Total Quantity'])
            chart = (
                    alt.Chart(df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Total Quantity:Q", title="Total Quantity Donated"),
                        y=alt.Y("Provider Type:N", sort="-x", title="Provider Type"),
                        color=alt.Color("Provider Type:N", legend=None),
                        tooltip=["Provider Type", "Total Quantity"]
                    )
                    .properties(
                        title="Total Quantity of Food Donated By Each Provider",
                        width=600,
                        height=400
                    )
                )
                
            st.altair_chart(chart, use_container_width=True)
            #st.write(df)    

    else:
        st.error("Please Select Properly")

if r == 'SQL Play Field':
    st.title("SQL Query Performer")
    st.subheader("Here you can write SQL query and play with data.")
    sql_query = st.text_area("Use Semicolon at end of Query ';'")
    if sql_query:
        cursor.execute(sql_query)
        result = cursor.fetchall()

        # convert result into a dataframe
        df = pd.DataFrame(result)
        st.write(df)
    else:
        print("Write your SQL Query.")



if r == 'Contact':
    st.subheader("**Contact List of Food Providers and Receivers**")
    contact = st.selectbox("Select List Type",['Providers List','Receivers List'])
    if contact == 'Providers List':
        q1 = """ 
        SELECT * FROM providers;
        """
        cursor.execute(q1)
        result = cursor.fetchall()

        # convert result into a dataframe.
        df = pd.DataFrame(result, columns = ['Provider_ID', 'Name', 'Type', 'Address', 'City', 'Contact'])
        st.write(df)
        
    elif contact == 'Receivers List':
        q1 = """ 
        SELECT * FROM receivers;
        """
        cursor.execute(q1)
        result = cursor.fetchall()

        # convert result into a dataframe.
        df = pd.DataFrame(result, columns = ['Receiver_ID', 'Name', 'Type', 'City', 'Contact'])
        st.write(df)
    else:
        print("Select the List from dropdown.")
    
    

if r == 'About':
    st.title("About the Creator")
    st.markdown("""
    #### Name:
    Uttam Singh Chaudhary
    #### Role:
    Data Science Intern @ LabMentix Edutech Prv. Ltd.
    """)
    
