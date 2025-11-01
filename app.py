import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
from werkzeug.security import check_password_hash

from face_detection import FaceDetection
from sqldatabase import SqlDatabase
from loginsql import StudLoginDatabase, TechLoginDatabase

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_dev_key_if_not_set')

DATABASE_URL = os.getenv('DATABASE_URL')
DCC_PI_URL = os.getenv('DCC_PI_URL')
GENERAL_PI_URL = os.getenv('GENERAL_PI_URL')

try:
    student_db = StudLoginDatabase(DATABASE_URL)
    teacher_db = TechLoginDatabase(DATABASE_URL)
    db = SqlDatabase(DATABASE_URL)
except Exception as e:
    print(f"CRITICAL: Failed to initialize databases. Check DATABASE_URL. Error: {e}")
    
face_detector = FaceDetection("dataset")
login_mode = {"type": None}
@app.route('/')
def index():
    return render_template('Login.html')

@app.route('/set_mode/<role>', methods=['POST'])
def set_mode(role):
    login_mode["type"] = role
    return '', 204

@app.route('/login', methods=['POST'])
def login():
    if login_mode["type"] == "teacher":
        teacher_id = request.form.get("Teacher_Id")
        password = request.form.get("password")
        result = teacher_db.Fetch_data(teacher_id)

        if result:
            db_password_hash, subject, teacher_name = result[0] 
            
            # Securely check the password hash
            if check_password_hash(db_password_hash, password):
                session['user_id'] = teacher_id
                session['role'] = 'teacher'
                session['subject'] = subject
                session['teacher_name'] = teacher_name # Store name in session
                return redirect(url_for('serve_teacher_subject', subject=subject))
            else:
                flash("❌ Incorrect password for teacher", "error")
        else:
            flash("❌ Teacher ID not found", "error")

    elif login_mode["type"] == "student":
        scholar_number = request.form.get("Student_Id")
        password = request.form.get("password")
        result = student_db.Fetch_data(scholar_number)

        if result:
            db_password_hash = result[0][0]
            if check_password_hash(db_password_hash, password):
                session['user_id'] = scholar_number
                session['role'] = 'student'
                return redirect(url_for('serve_student_page', scholar_id=scholar_number))
            else:
                flash("❌ Incorrect password for student", "error")
        else:
            flash("❌ Scholar Number not found", "error")

    else:
        flash("❌ Login mode not selected", "error")

    return redirect(url_for('index'))

@app.route('/<subject>.html')
def serve_teacher_subject(subject):
    if session.get('role') != 'teacher' or session.get('subject') != subject:
        flash("❌ You are not authorized to view this page.", "error")
        return redirect(url_for('index'))
    return render_template(f"{subject}.html")

@app.route('/<scholar_id>.html')
def serve_student_page(scholar_id):
    if session.get('role') != 'student' or session.get('user_id') != scholar_id:
        flash("❌ You are not authorized to view this page.", "error")
        return redirect(url_for('index'))
    return render_template(f"{scholar_id}.html")

@app.route('/dcc/start', methods=['POST'])
def start_dcc_attendance():
    try:
        if not face_detector.running.is_set():
            face_detector.start_detection("dcc")
            return jsonify({"message": "DCC attendance started!"}), 200
        return jsonify({"message": "Attendance already running!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/dcc/stop', methods=['POST'])
def stop_dcc_attendance():
    try:
        detected_students = face_detector.stop_detection("dcc")
        return jsonify({
            "message": f"DCC attendance stopped. Detected: {len(detected_students)} students"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/dcc/message', methods=['POST'])
def send_dcc_message():
    try:
        message = request.json.get('message', '')
        if not message:
            return jsonify({"message": "Message cannot be empty!"}), 400
        prof_name = session.get('teacher_name', 'Your Professor')
        full_msg = f"Attention DCC class. Message from {prof_name}. {message}"
        response = requests.post(
            f"{DCC_PI_URL}/broadcast_msg",
            json={"message": full_msg},
            timeout=3
        )

        if response.status_code == 200:
            return jsonify({"message": "Message broadcasted successfully!"}), 200
        else:
            return jsonify({"message": "Pi responded with error"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Failed to reach Pi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/dcc/attendance')
def get_dcc_attendance():
    try:
        attendance_data = db.Display_Data_Teacher("dcc")
        result = []
        for row in attendance_data:
            result.append({
                "s_no": row[0], "enrollment_no": row[1], "name": row[2],
                "dcc_tca": row[3], "dcc_tc": row[4], "dcc_percentage": row[5]
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/dcc/send_emails', methods=['POST'])
def send_dcc_emails():
    try:
        db.Send_Email("dcc")
        return jsonify({"message": "Email alerts sent for students with <75% attendance!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
@app.route('/r_prog/start', methods=['POST'])
def start_r_prog_attendance():
    try:
        if not face_detector.running.is_set():
            face_detector.start_detection("r_prog")
            return jsonify({"message": "R Programming attendance started!"}), 200
        return jsonify({"message": "Attendance already running!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/r_prog/stop', methods=['POST'])
def stop_r_prog_attendance():
    try:
        detected_students = face_detector.stop_detection("r_prog")
        db.Update_Data("r_prog", detected_students)
        return jsonify({
            "message": f"R Programming attendance stopped. Detected: {len(detected_students)} students"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/r_prog/message', methods=['POST'])
def send_r_prog_message():
    try:
        message = request.json.get('message', '')
        if not message:
            return jsonify({"message": "Message cannot be empty!"}), 400

        # Get professor name from session
        prof_name = session.get('teacher_name', 'Your Professor')
        full_msg = f"Attention R Programming class. Message from {prof_name}. {message}"
        response = requests.post(
            f"{GENERAL_PI_URL}/broadcast_msg",
            json={"message": full_msg},
            timeout=3
        )

        if response.status_code == 200:
            return jsonify({"message": "Message broadcasted successfully!"}), 200
        else:
            return jsonify({"message": "Pi responded with error"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Failed to reach Pi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/r_prog/attendance')
def get_r_prog_attendance():
    try:
        attendance_data = db.Display_Data_Teacher("r_prog")
        result = []
        for row in attendance_data:
            result.append({
                "s_no": row[0], "enrollment_no": row[1], "name": row[2],
                "r_prog_tca": row[3], "r_prog_tc": row[4], "r_prog_percentage": row[5]
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/r_prog/send_emails', methods=['POST'])
def send_r_prog_emails():
    try:
        db.Send_Email("r_prog")
        return jsonify({"message": "Email alerts sent for students with <75% attendance!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/nlp/start', methods=['POST'])
def start_nlp_attendance():
    try:
        if not face_detector.running.is_set():
            face_detector.start_detection("nlp")
            return jsonify({"message": "NLP attendance started!"}), 200
        return jsonify({"message": "Attendance already running!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/nlp/stop', methods=['POST'])
def stop_nlp_attendance():
    try:
        detected_students = face_detector.stop_detection("nlp")
        db.Update_Data("nlp", detected_students)
        return jsonify({
            "message": f"NLP attendance stopped. Detected: {len(detected_students)} students"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/nlp/message', methods=['POST'])
def send_nlp_message():
    try:
        message = request.json.get('message', '')
        if not message:
            return jsonify({"message": "Message cannot be empty!"}), 400
        prof_name = session.get('teacher_name', 'Your Professor')
        full_msg = f"Attention NLP class. Message from {prof_name}. {message}"
        response = requests.post(
            f"{GENERAL_PI_URL}/broadcast_msg", # Use loaded URL
            json={"message": full_msg},
            timeout=3
        )

        if response.status_code == 200:
            return jsonify({"message": "Message broadcasted successfully!"}), 200
        else:
            return jsonify({"message": "Pi responded with error"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Failed to reach Pi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/nlp/attendance')
def get_nlp_attendance():
    try:
        attendance_data = db.Display_Data_Teacher("nlp")
        result = []
        for row in attendance_data:
            result.append({
                "s_no": row[0], "enrollment_no": row[1], "name": row[2],
                "nlp_tca": row[3], "nlp_tc": row[4], "nlp_percentage": row[5]
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/nlp/send_emails', methods=['POST'])
def send_nlp_emails():
    try:
        db.Send_Email("nlp")
        return jsonify({"message": "Email alerts sent for students with <75% attendance!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/se/start', methods=['POST'])
def start_se_attendance():
    try:
        if not face_detector.running.is_set():
            face_detector.start_detection("se")
            return jsonify({"message": "SE attendance started!"}), 200
        return jsonify({"message": "Attendance already running!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/se/stop', methods=['POST'])
def stop_se_attendance():
    try:
        detected_students = face_detector.stop_detection("se")
        db.Update_Data("se", detected_students)
        return jsonify({
            "message": f"SE attendance stopped. Detected: {len(detected_students)} students"
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/se/message', methods=['POST'])
def send_se_message():
    try:
        message = request.json.get('message', '')
        if not message:
            return jsonify({"message": "Message cannot be empty!"}), 400
        prof_name = session.get('teacher_name', 'Your Professor')
        full_msg = f"Attention SE class. Message from {prof_name}. {message}"
        response = requests.post(
            f"{GENERAL_PI_URL}/broadcast_msg",
            json={"message": full_msg},
            timeout=3
        )

        if response.status_code == 200:
            return jsonify({"message": "Message broadcasted successfully!"}), 200
        else:
            return jsonify({"message": "Pi responded with error"}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Failed to reach Pi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/se/attendance')
def get_se_attendance():
    try:
        attendance_data = db.Display_Data_Teacher("se")
        result = []
        for row in attendance_data:
            result.append({
                "s_no": row[0], "enrollment_no": row[1], "name": row[2],
                "se_tca": row[3], "se_tc": row[4], "se_percentage": row[5]
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/se/send_emails', methods=['POST'])
def send_se_emails():
    try:
        db.Send_Email("se")
        return jsonify({"message": "Email alerts sent for students with <75% attendance!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
@app.route('/Placement')
def Placement():
    return render_template('Error.html')

if __name__ == "__main__":
    port = int(os.getenv('FLASK_RUN_PORT', 80))
    app.run(host="0.0.0.0", port=port, debug=True)