import grpc
from myapp.books_pb2 import BookRequest, Empty
from myapp.books_pb2_grpc import BookServiceStub

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        client = BookServiceStub(channel)

        # Получение списка всех книг
        response = client.GetAllBooks(Empty())
        print("Список всех книг:")
        for book in response.books:
            print(f"ID: {book.id}, Title: {book.title}, Author: {book.author}")

        # Получение книги по ID
        book_id = 1  # Замените на нужный ID
        response = client.GetBookById(BookRequest(id=book_id))
        print("Книга по ID:")
        print(f"ID: {response.id}, Title: {response.title}, Author: {response.author}")

if __name__ == '__main__':
    run()
