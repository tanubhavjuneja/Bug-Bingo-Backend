from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import random
import time
import json
import os
import threading 
import requests
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
def load_questions1(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as file:
        questions = json.load(file)
    return questions
PY_QUESTIONS1 = load_questions1("python.json")
CPP_QUESTIONS1 = load_questions1("cpp.json")
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
    selected_questions = random.sample(questions, min(25, len(questions)))
    return jsonify(selected_questions)
@app.route('/set_questions1', methods=['POST'])
def set_questions1():
    data = request.get_json()
    language = data.get("language", "python").lower()
    questions = PY_QUESTIONS1 if language == "python" else CPP_QUESTIONS1
    if not questions:
        return jsonify({"error": "No questions available"}), 404
    selected_questions = random.sample(questions, min(25, len(questions)))
    response = {"questions": selected_questions}
    return jsonify(response)
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
            output_command = "print"
        elif language == "c++":
            suffix = ".cpp"
            command = ["g++", "{}", "-o", "{}.out"]
            output_command = "cout"
        else:
            return jsonify({"incorrect": False, "message": "Unsupported language!"})
        code_lines = user_code.splitlines()
        if len(expected_output)>1:
            cpp_output_block = ""
            for line in code_lines:
                line = line.strip()
                if language == "python":
                    if output_command in line and expected_output in line:
                        return jsonify({"incorrect": False, "message": "Cheating detected!"})
                elif language == "c++":
                    if "cout" in line:
                        cpp_output_block += line
                        if ";" in line: 
                            if expected_output in cpp_output_block:
                                return jsonify({"incorrect": False, "message": "Cheating detected!"})
                            cpp_output_block = "" 
                    elif cpp_output_block: 
                        cpp_output_block += line
                        if ";" in line: 
                            if expected_output in cpp_output_block:
                                return jsonify({"incorrect": False, "message": "Cheating detected!"})
                            cpp_output_block = ""
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
@app.route('/execute1', methods=['POST'])
def execute1():
    data = request.json
    user_code = data.get("code", "").strip()
    test_cases = data.get("test_cases", [])
    language = data.get("language", "python").lower()
    user_info = data.get("user", {})
    if not user_code:
        return jsonify({"incorrect": False, "message": "No code provided!"})
    try:
        if language == "python":
            suffix = ".py"
            command = ["python", "{}"]
            output_command = "print"
        elif language == "c++":
            suffix = ".cpp"
            command = ["g++", "{}", "-o", "{}.out"]
            output_command = "cout"
        else:
            return jsonify({"incorrect": False, "message": "Unsupported language!"})
        code_lines = user_code.splitlines()
        for line in code_lines:
            line = line.strip()
            if output_command in line:
                return jsonify({"incorrect": False, "message": "Cheating detected!"})
        start_time = time.time()
        results=[]
        correct=0
        for i, test_case in enumerate(test_cases[:5]):
            expected_output = test_case["expected_output"].strip()
            input_data = test_case.get("input", "")
            user_code=user_code+"\n"+input_data
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as temp_file:
                temp_file.write(user_code)
                temp_file_name = temp_file.name
                user_code=user_code.replace("\n"+input_data,"")
            if language == "cpp":
                result = subprocess.run(
                    [temp_file_name + ".out"],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            else:
                result = subprocess.run(
                    ["python", temp_file_name],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
            actual_output = result.stdout.strip()
            is_correct = actual_output == expected_output
            correct+=1
            results.append({
                "test_case": i + 1,
                "expected": expected_output,
                "actual": actual_output,
                "correct": is_correct
            })
        execution_time = round(time.time() - start_time, 3)
        print(results)
        return jsonify(results)
    except subprocess.TimeoutExpired:
        return jsonify({"incorrect": False, "message": "Code execution timed out!"})
    except Exception as e:
        return jsonify({"incorrect": False, "message": f"Error: {str(e)}"})
def keep_server_awake():
    def ping():
        try:
            requests.get("https://bug-bingo-backend.onrender.com/ping")
        except Exception as e:
            print(f"Ping failed: {e}")
        threading.Timer(60, ping).start()
    ping()
if __name__ == "__main__":
    keep_server_awake()
    app.run(host="0.0.0.0", port=80, debug=True)
