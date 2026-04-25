from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Chatbot logic
def get_response(user_input):
    user_input = user_input.lower()

    if "admission" in user_input:
        return "Admissions are open! You need FSC/ICS or equivalent with at least 60% marks."

    elif "deadline" in user_input:
        return "The admission deadline is 30th September."

    elif "programs" in user_input:
        return "We offer BSCS, BBA, BS IT, and Engineering programs."

    elif "fee" in user_input:
        return "The average semester fee is around 50,000 PKR."

    elif "hello" in user_input or "hi" in user_input:
        return "Hello! How can I help you with university admissions?"

    else:
        return "Sorry, I didn't understand. Please ask about admissions, programs, or fees."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot():
    user_input = request.form["msg"]
    response = get_response(user_input)
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)