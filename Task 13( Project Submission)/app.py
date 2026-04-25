from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ====================== GOOGLE GEMINI API SETUP ======================
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# uploads folder automatically create karo
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -----------------------------
# Extract Resume Text from PDF
# -----------------------------
def extract_resume_text(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
        return ""

# -----------------------------
# Simple ATS Score
# -----------------------------
def analyze_resume(text):
    score = min(len(text) // 50, 100)
    suggestions = [
        "Add measurable achievements with numbers (e.g., Increased sales by 45%)",
        "Use strong action verbs (Led, Developed, Optimized, Achieved)",
        "Include relevant ATS keywords from job description",
        "Add a dedicated Technical Skills section",
        "Keep resume clean and 1-2 pages maximum"
    ]
    return score, suggestions

# -----------------------------
# Generate Cover Letter with Gemini (Stable Model)
# -----------------------------
def generate_cover_letter(text):
    try:
        prompt = f"""You are a professional career coach. Write a concise, powerful, and personalized cover letter 
based on the resume below. Keep it professional, enthusiastic, and well-structured.

Resume:
{text[:2000]}"""

        response = client.chat.completions.create(
            model="gemini-2.5-flash-lite",      # Stable aur fast model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

# -----------------------------
# Generate Interview Questions
# -----------------------------
def generate_questions(text):
    try:
        prompt = f"""Based on the following resume, generate 5 strong interview questions 
(3 technical + 2 behavioral) that an interviewer might ask this candidate.

Resume:
{text[:1500]}"""

        response = client.chat.completions.create(
            model="gemini-2.5-flash-lite",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating questions: {str(e)}"

# -----------------------------
# Evaluate Interview Answer
# -----------------------------
def evaluate_answer(answer):
    try:
        prompt = f"""You are an expert interview coach with 15+ years of experience. 
Give honest, professional and constructive feedback on the candidate's answer.

Answer:
{answer}

Provide feedback on:
- Clarity and Structure
- Confidence & Communication
- Relevance to the question
- Areas of improvement
- A suggested better version of the answer"""

        response = client.chat.completions.create(
            model="gemini-2.5-flash-lite",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error evaluating answer: {str(e)}"

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files['resume']
        if file.filename == '':
            return jsonify({"error": "No file selected"})

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        resume_text = extract_resume_text(filepath)

        if not resume_text:
            return jsonify({"error": "Could not extract text from PDF. Please use a text-based PDF."})

        ats_score, suggestions = analyze_resume(resume_text)
        cover_letter = generate_cover_letter(resume_text)
        questions = generate_questions(resume_text)

        return jsonify({
            "ats_score": ats_score,
            "suggestions": suggestions,
            "cover_letter": cover_letter,
            "questions": questions
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"})

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        answer = data.get('answer', '').strip()

        if not answer:
            return jsonify({"error": "Answer cannot be empty"})

        feedback_result = evaluate_answer(answer)
        return jsonify({"feedback": feedback_result})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)