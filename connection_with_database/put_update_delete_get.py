from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
# import connection_with_database.models as models
# from database import engine, SessionLocal
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal

# from connection_with_database import models
# from connection_with_database.database import engine, SessionLocal


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = FastAPI()

# models.Base.metadata.createall(bind=engine)
models.Base.metadata.create_all(bind=engine)




def get_db():
    try:
        db = SessionLocal()
        yield db 
    finally:
        db.close()

class Book(BaseModel):

    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)  # Ensure rating is an integer

BOOKS = []

@app.get("/")
def read_api(db: Session = Depends(get_db)):
    """Retrieves all books from the BOOKS list."""
    return db.query(models.Books).all()

@app.post("/")
def create_book(book: Book, db:Session = Depends(get_db)):
    """Creates a new book and adds it to the BOOKS list."""
    book_model = models.Books()
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.add(book_model)
    db.commit()
    return book

@app.put("/{book_id}")
def update_book(book_id: int, book: Book, db: Session = Depends(get_db)):

    """Updates an existing book in the BOOKS list based on its ID."""
    book_model  = db.query(models.Books).filter(models.Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Book with ID {book_id} not found"
        )
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.add(book_model)
    db.commit()
    return book

@app.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Deletes a book from the BOOKS list based on its ID."""
    book_model  = db.query(models.Books).filter(models.Books.id == book_id).first()
    
    if book_model is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Book with ID {book_id} not found"
        )
    
    db.query(models.Books).filter(models.Books.id == book_id).delete()
    db.commit()
    # for i, existing_book in enumerate(BOOKS):
    #     if existing_book.id == book_id:
    #         del BOOKS[i]
    #         return {"message": f"Book with ID {book_id} deleted successfully"}
    # raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

# Run the application using uvicorn (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
    