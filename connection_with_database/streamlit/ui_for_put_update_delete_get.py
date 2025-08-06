import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Book Manager")

# Add a New Book (POST)
st.header("Add a New Book")
# book_id = st.number_input("Book ID (Integer)", min_value=0, step=1, key="add_id")
title = st.text_input("Title", key="add_title")
author = st.text_input("Author", key="add_author")
description = st.text_input("Description", key="add_description")
rating = st.number_input("Rating", min_value=0, max_value=100, step=1, key="add_rating")

if st.button("Add Book"):
    if title.strip() == "" or author.strip() == "" or description.strip() == "":
        st.error("All fields are required!")
    else:
        book = {
            # "id": book_id,
            "title": title,
            "author": author,
            "description": description,
            "rating": rating,
        }
        response = requests.post(API_URL, json=book)
        if response.status_code == 200:
            st.success("Book added successfully!")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

# Button to Fetch Available Book Indices
if st.button("Show Available Book Indices"):
    response = requests.get(API_URL)
    if response.status_code == 200:
        books = response.json()
        if books:
            st.write("Available Books:")
            for book in books:
                st.write(f"Book ID: {book['id']} - {book['title']}")  # Show book ID and title
        else:
            st.info("No books available.")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

# Fetch a Specific Book by ID (GET)
st.header("Fetch a Book by ID")
fetch_id = st.number_input("Enter Book ID", min_value=0, step=1, key="fetch_id")

if st.button("Fetch Book"):
    response = requests.get(API_URL)
    if response.status_code == 200:
        books = response.json()
        # Find the book with the matching ID
        book = next((book for book in books if book['id'] == fetch_id), None)
        if book:
            st.markdown(
                f"""
                **Book ID:** {book['id']}  
                **Title:** {book['title']}  
                **Author:** {book['author']}  
                **Description:** {book['description']}  
                **Rating:** {book['rating']}  
                """
            )
        else:
            st.warning(f"There is no book with ID {fetch_id}.")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")


# Initialize session state for the update operation
if "show_update_form" not in st.session_state:
    st.session_state.show_update_form = False
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

# Button to trigger the update operation
if st.button("Update Book"):
    response = requests.get(API_URL)
    if response.status_code == 200:
        books = response.json()
        if books:
            st.session_state.show_update_form = True  # Show the update form
            st.write("Available Books:")
            for book in books:
                st.write(f"Book ID: {book['id']} - {book['title']} by {book['author']}")  # Show book ID and title
        else:
            st.info("No books available to update.")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

# If the update form should be displayed
if st.session_state.show_update_form:
    # Input to select the book ID (not index)
    update_id = st.number_input("Enter the Book ID to update", min_value=0, step=1, key="update_id")

    # Fetch and populate fields for the selected book by ID
    response = requests.get(API_URL)
    if response.status_code == 200:
        books = response.json()
        # Find the book by the entered ID
        selected_book = next((book for book in books if book["id"] == update_id), None)
        if selected_book:
            st.session_state.selected_book = selected_book  # Load the book data into session state
        else:
            st.warning("No book found with the provided ID.")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

    if st.session_state.selected_book:
        selected_book = st.session_state.selected_book

        # Fields to update the book
        new_title = st.text_input("New Title", value=selected_book['title'], key="update_title")
        new_author = st.text_input("New Author", value=selected_book['author'], key="update_author")
        new_description = st.text_input("New Description", value=selected_book['description'], key="update_description")
        new_rating = st.number_input("New Rating", min_value=0, max_value=100, step=1, value=selected_book['rating'], key="update_rating")

        # Button to save changes
        if st.button("Save Changes"):
            updated_book = {
                "id": selected_book['id'],  # Keep the same ID
                "title": new_title,
                "author": new_author,
                "description": new_description,
                "rating": new_rating,
            }
            update_response = requests.put(f"{API_URL}/{selected_book['id']}", json=updated_book)
            if update_response.status_code == 200:
                st.success("Book updated successfully!")
                # Reset session state after update
                st.session_state.show_update_form = False
                st.session_state.selected_book = None
            else:
                st.error(f"Error: {update_response.status_code} - {update_response.text}")


# Initialize session state for deletion confirmation if it doesn't exist
if "delete_confirmed" not in st.session_state:
    st.session_state.delete_confirmed = False

# Header
st.header("Delete a Book by ID")

# Fetch available books
response = requests.get(API_URL)  # Fetch available books
if response.status_code == 200:
    books = response.json()

    # Display available books
    if books:
        st.write("Available Books:")
        for book in books:
            st.write(f"Book ID: {book['id']} - {book['title']} by {book['author']}")

        # Input for Book ID
        delete_id = st.number_input("Enter the Book ID to delete", min_value=0, step=1, key="delete_id")

        # Button to confirm delete
        if st.button("Delete Book"):
            # Find the book by ID
            selected_book = next((book for book in books if book["id"] == delete_id), None)
            if selected_book:
                # Send delete request to FastAPI
                delete_response = requests.delete(f"{API_URL}/{delete_id}")
                if delete_response.status_code == 200:
                    # Check the message from API response
                    delete_message = delete_response.json().get("message", "Book deleted successfully!")
                    st.success(delete_message)
                    st.session_state.delete_confirmed = True  # Mark delete as confirmed
                else:
                    st.error(f"Error: {delete_response.status_code} - {delete_response.text}")
            else:
                st.warning("No book found with the provided ID.")
    else:
        st.info("No books available to delete.")
else:
    st.error(f"Error fetching books: {response.status_code} - {response.text}")

# If deletion was confirmed, show a message and provide feedback
if st.session_state.delete_confirmed:
    st.info("The book has been deleted successfully.")
