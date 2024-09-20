import grpc
from concurrent import futures
import time
from sqlalchemy.orm import Session
from myapp import models, crud
from myapp.database import SessionLocal, engine
import myapp.books_pb2_grpc as pb2_grpc
import myapp.books_pb2 as pb2

class BookService(pb2_grpc.BookServiceServicer):
    def GetBookById(self, request, context):
        db: Session = SessionLocal()
        book = crud.get_book(db, request.id)
        if book is None:
            context.set_details("Book not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return pb2.Book()  # Return an empty book
        return pb2.Book(id=book.id, title=book.title, author=book.author, published_date=book.published_date)

    def ListBooks(self, request, context):
        db: Session = SessionLocal()
        books = crud.get_books(db)
        return pb2.ListBooksResponse(books=[pb2.Book(id=book.id, title=book.title, author=book.author, published_date=book.published_date) for book in books])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(86400)  # Sleep for 1 day
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
