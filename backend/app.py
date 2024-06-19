import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from qna import extract_text_from_pptx, generate_qna, to_list
import google.generativeai as genai
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='build', static_url_path='/')
UPLOAD_FOLDER = 'uploads'
genai.configure(api_key="AIzaSyDG4L7ze9_nZeGZ5SKFifBoDYkpiFTfPuk")  # Replace with your actual API key
CORS(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def generate_notes(text):
    response = genai.generate_text(
        model="models/text-bison-001",
        prompt="Generate notes and list main concepts in points based on the following text:\n" + text,
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
    )
    return response.result


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    extracted_text = extract_text_from_pptx(filepath)
    notes = generate_notes(extracted_text)
    return jsonify({'notes': notes})

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    data = request.get_json()
    notes = data.get('notes', '')
    if not notes:
        return jsonify({'error': 'Notes content is missing'}), 400

    qna_text = generate_qna(notes)
    qna_list = to_list(qna_text)
    qna_list = [(html_to_text(q), html_to_text(a)) for q, a in qna_list]
    questions = [{'question': q, 'answer': a} for q, a in qna_list]
    return jsonify({'questions': questions})

@app.route('/')
def index():
  return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=5000)