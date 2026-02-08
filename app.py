import gradio as gr
from flask import Flask, jsonify, request


def hello(name):
    return f"Xin chào {name}!"


demo = gr.Interface(
    fn=hello,
    inputs="text",
    outputs="text",
    title="API Test",
    api_name="say_hello",  # <-- quan trọng nếu muốn custom endpoint
)

if __name__ == "__main__":
    demo.launch()

app = Flask(__name__)

# Dữ liệu giả (thay vì database thật)
books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Python Crash Course", "author": "Eric Matthes"},
]


# GET - Lấy tất cả sách
@app.route("/api/books", methods=["GET"])
def get_books():
    return jsonify(books)


# GET - Lấy 1 cuốn sách theo id
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


# POST - Thêm sách mới
@app.route("/api/books", methods=["POST"])
def create_book():
    if not request.json or "title" not in request.json:
        return jsonify({"error": "Title is required"}), 400

    new_book = {
        "id": len(books) + 1,
        "title": request.json["title"],
        "author": request.json.get("author", ""),
    }
    books.append(new_book)
    return jsonify(new_book), 201


# PUT - Cập nhật sách
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    data = request.json
    book["title"] = data.get("title", book["title"])
    book["author"] = data.get("author", book["author"])

    return jsonify(book)


# DELETE - Xóa sách
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    book = next((b for b in books if b["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    books = [b for b in books if b["id"] != book_id]
    return jsonify({"message": "Book deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
