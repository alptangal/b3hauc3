import os
import random
import re
import time

import gradio as gr
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

load_dotenv()

from bhn import Behance

BHN_USERNAME = os.getenv("username")
BHN_PASSWORD = os.getenv("password")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
new_behance = Behance(username=BHN_USERNAME, password=BHN_USERNAME)


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


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/images", methods=["POST"])
async def upload_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Không tìm thấy phần file"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Chưa chọn file"}), 400
        # Có file và hợp lệ
        if file and allowed_file(file.filename):
            # Bảo mật tên file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            # Lưu file
            file.save(file_path)
            name = request.form.get("name", "")
            description = request.form.get("description", "")
            await new_behance.login()
            new_project = await new_behance.createProject()
            return "123"
            if new_project:
                results = await new_behance.uploadImage(new_project["id"], file_path)
                return jsonify({"data": str(results)}), 201
        return jsonify({"error": "something went wrong"}), 403
    except Exception as error:
        return jsonify({"error": str(error)}), 403


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    # send_from_directory rất an toàn, tránh directory traversal attack
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
