import streamlit as st
import sqlite3
import requests

# Set up Streamlit app
st.title("Example UI")

# Section 1: Database Query
st.header("SQL Database Query")
query = st.text_area("Enter your SQL query:")
if st.button("Run Query"):
    try:
        # Example with SQLite (replace with your DB connection details)
        conn = sqlite3.connect('example.db')  # Replace with your database connection
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        # Display results
        st.success("Query executed successfully!")
        st.write(results)
    except Exception as e:
        st.error(f"Error: {e}")

# Section 2: POST Request
st.header("Send POST Request")
url = st.text_input("Enter the URL:")
data = st.text_area("Enter the POST request data (in JSON format):")
if st.button("Send POST Request"):
    try:
        # Send POST request
        response = requests.post(url, json=eval(data))
        st.success("POST request sent successfully!")
        st.write("Response:")
        st.write(response.json())
    except Exception as e:
        st.error(f"Error: {e}")
