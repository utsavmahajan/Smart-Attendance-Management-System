import cv2
import numpy as np
import os
import time
import requests
from sklearn.metrics.pairwise import cosine_similarity
from insightface.app import FaceAnalysis
from threading import Thread, Event
from sqldatabase import SqlDatabase, l

db = SqlDatabase(l)

PI_IP = "http://"+os.getenv("PI's IP")

class FaceDetection:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.running = Event()
        self.detected_names = []
        self.thread = None
        self.subject = None
        self.message = ""

    def Process_Dataset(self):
        face_db = {}
        app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=0, det_size=(640, 640))

        for person in os.listdir(self.dataset_path):
            person_path = os.path.join(self.dataset_path, person)
            if os.path.isdir(person_path):
                embeddings = []
                for img_name in os.listdir(person_path):
                    img_path = os.path.join(person_path, img_name)
                    img = cv2.imread(img_path)
                    faces = app.get(img)
                    if faces:
                        embeddings.append(faces[0].normed_embedding)
                if embeddings:
                    face_db[person] = np.mean(embeddings, axis=0)

        np.save("face_database.npy", face_db)
        print("? Face database updated successfully!")

    def _send_to_pi(self, endpoint, data):
        try:
            url = f"{PI_IP}/{endpoint}"
            requests.post(url, json=data)
        except Exception as e:
            print(f"?? Could not reach Pi: {e}")

    def _detect_faces(self):
        face_db = np.load("face_database.npy", allow_pickle=True).item()
        app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        app.prepare(ctx_id=0, det_size=(640, 640))

        cap = cv2.VideoCapture(0)

        while self.running.is_set() and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            faces = app.get(frame)
            for face in faces:
                embedding = face.normed_embedding.reshape(1, -1)
                best_match = "Unknown"
                best_score = 0.0

                for name, db_embedding in face_db.items():
                    score = cosine_similarity(embedding, db_embedding.reshape(1, -1))[0][0]
                    if score > best_score and score > 0.5:
                        best_match = name
                        best_score = score

                self._send_to_pi("face_status", {"status": best_match})

                if best_match not in self.detected_names and best_match != "Unknown":
                    self.detected_names.append(best_match)

            time.sleep(1)

        cap.release()

    def start_detection(self, subject, message=""):
        print(f"🔴 Starting detection for {subject}")  # Debug log
        if not self.running.is_set():
            self.subject = subject
            self.message = message
            db.Update_AutoData(subject)  # Should happen exactly once
            self._send_to_pi("subject", {"subject": subject})
            if message:
                self._send_to_pi("broadcast_msg", {"message": message})
            if not self.running.is_set():
                self.running.set()
                self.thread = Thread(target=self._detect_faces)
                self.thread.start()
        else:
            print("⚠️ Detection already running!")

    def stop_detection(self, subject):
        self.running.clear()
        db.Update_Data(subject, self.detected_names)
        if self.thread:
            self.thread.join()
        return self.detected_names