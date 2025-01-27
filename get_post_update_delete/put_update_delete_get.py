from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID

app = FastAPI()

class Book(BaseModel):

    # id: UUID
    id: int  # Changed from UUID to int
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)  # Ensure rating is an integer

BOOKS = []

@app.get("/")
def read_books():
    """Retrieves all books from the BOOKS list."""
    return BOOKS

@app.post("/")
def create_book(book: Book):
    """Creates a new book and adds it to the BOOKS list."""
    BOOKS.append(book)
    return book

@app.put("/{book_id}")
def update_book(book_id: int, book: Book):
    """Updates an existing book in the BOOKS list based on its ID."""
    for i, existing_book in enumerate(BOOKS):
        if existing_book.id == book_id:
            BOOKS[i] = book
            return book
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

@app.delete("/{book_id}")
def delete_book(book_id: int):
    """Deletes a book from the BOOKS list based on its ID."""
    for i, existing_book in enumerate(BOOKS):
        if existing_book.id == book_id:
            del BOOKS[i]
            return {"message": f"Book with ID {book_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

# Run the application using uvicorn (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)