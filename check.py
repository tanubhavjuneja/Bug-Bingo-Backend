from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import subprocess
import tempfile
app = Flask(__name__)
CORS(app)
def load_questions(file_path):
    questions = []
    if not os.path.exists(file_path):
        return questions
    with open(file_path, "r") as file:
        content = file.read().strip()
    blocks = content.split("---")
    for i, block in enumerate(blocks):
        parts = block.strip().split("Expected Output:")
        if len(parts) == 2:
            problem, expected_output = parts
            questions.append({
                "id": i,
                "problem": problem.strip(),
                "expected_output": expected_output.strip()
            })
    return questions
PY_QUESTIONS = load_questions("problems_python.txt")
CPP_QUESTIONS = load_questions("problems_cpp.txt")
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Server is awake!"}), 200
@app.route('/set_questions', methods=['POST'])
def set_questions():
    data = request.get_json()
    language = data.get("language", "python").lower()
    questions = PY_QUESTIONS if language == "python" else CPP_QUESTIONS
    if not questions:
        return jsonify({"error": "No questions available"}), 404
    selected_questions = random.sample(questions, min(9, len(questions)))
    return jsonify(selected_questions)
@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    user_code = data.get("code", "").strip()
    expected_output = data.get("expected_output", "").strip()
    language = data.get("language", "python").lower()
    if not user_code:
        return jsonify({"incorrect": False, "message": "No code provided!"})
    try:
        if language == "python":
            suffix = ".py"
            command = ["python", "{}"]
        elif language == "c++":
            suffix = ".cpp"
            command = ["g++", "{}", "-o", "{}.out"]
        else:
            return jsonify({"incorrect": False, "message": "Unsupported language!"})
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as temp_file:
            temp_file.write(user_code)
            temp_file_name = temp_file.name
        if language == "cpp":
            compile_result = subprocess.run(
                command[0:3] + [temp_file_name, temp_file_name + ".out"],
                capture_output=True,
                text=True
            )
            if compile_result.returncode != 0:
                return jsonify({"incorrect": False, "message": "Compilation failed!"})
            result = subprocess.run(
                [temp_file_name + ".out"],
                capture_output=True,
                text=True,
                timeout=3
            )
        else:
            result = subprocess.run(
                [command[0], temp_file_name],
                capture_output=True,
                text=True,
                timeout=3
            )
        actual_output = result.stdout.strip()
        if actual_output == expected_output:
            return jsonify({"correct": True})
        else:
            return jsonify({"incorrect": False, "message": f"Expected: {expected_output}, Got: {actual_output}"})
    except subprocess.TimeoutExpired:
        return jsonify({"incorrect": False, "message": "Code execution timed out!"})
    except Exception as e:
        return jsonify({"incorrect": False, "message": f"Error: {str(e)}"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)