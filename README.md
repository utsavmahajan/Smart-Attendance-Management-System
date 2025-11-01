# Face Recognition-Based Attendance Management System

This is a mini-project report for a "Face Recognition-Based Attendance Management System" developed by **Utsav Mahajan** under the guidance of **Prof. [cite_start]Deepa Pandit** for Medicaps University[cite: 10, 13, 17].

The system replaces traditional manual attendance with a high-accuracy, automated solution using AI-driven face recognition, a web-based dashboard, and IoT integration.

## 📋 Abstract

[cite_start]Traditional attendance systems are time-consuming, susceptible to proxy fraud, and lack real-time analytics[cite: 63]. [cite_start]This project presents an automated solution using the **InsightFace** AI model, a **PostgreSQL** database, and a **Flask** backend to provide contactless, high-accuracy attendance tracking[cite: 64].

[cite_start]The system achieves **92.7% recognition accuracy** [cite: 64, 81] [cite_start]and is **87% faster** than manual roll calls[cite: 88]. [cite_start]It features role-based dashboards for teachers and students [cite: 69][cite_start], automated email alerts for low attendance (<75%) [cite: 70][cite_start], and Raspberry Pi integration for broadcasting classroom announcements[cite: 71].

## ✨ Key Features

* [cite_start]**Role-Based Dashboards:** Separate, secure web portals for Teachers and Students[cite: 69].
* [cite_start]**Real-Time Face Recognition:** Uses classroom cameras to detect and identify students [cite: 67][cite_start], generating 512-D embeddings via the InsightFace model [cite: 74] [cite_start]and matching them using cosine similarity[cite: 75].
* [cite_start]**Automated Attendance Logging:** Teachers can start/stop attendance sessions from the dashboard[cite: 641, 643]. [cite_start]Recognized students are automatically logged in the PostgreSQL database[cite: 68].
* [cite_start]**Low Attendance Alerts:** Automatically sends email alerts to students whose attendance drops below the 75% threshold[cite: 70].
* [cite_start]**Classroom Announcement System:** Allows teachers to send messages from the dashboard [cite: 656][cite_start], which are broadcast via a speaker connected to a Raspberry Pi in the classroom[cite: 71, 83].
* [cite_start]**Student Attendance Summary:** Students can log in to view a personalized dashboard showing their attendance percentage for each subject, color-coded for clarity[cite: 727, 730].
* [cite_start]**Secure Authentication:** Both students and teachers have unique login credentials to access their respective dashboards[cite: 141].

## 🏗️ System Architecture & Design

[cite_start]The system is built on a modular, RESTful architecture[cite: 766].

1.  [cite_start]**Face Recognition (AI Model):** The **InsightFace** model generates 512-dimensional embeddings for each face[cite: 788]. [cite_start]These are compared to registered student embeddings using **Cosine Similarity** to find a match[cite: 787].
2.  [cite_start]**Backend (API):** A **Flask** server provides REST API endpoints for login, starting/stopping attendance, fetching reports, and sending messages [cite: 768, 770-775].
3.  [cite_start]**Database:** A **PostgreSQL** database, hosted on **Supabase**, stores all user credentials and attendance records[cite: 597, 765].
4.  [cite_start]**Frontend (UI):** A user-friendly web interface built with **HTML, CSS, and JavaScript** provides the dashboards for teachers and students [cite: 584-586].
5.  [cite_start]**Hardware (IoT):** A **Raspberry Pi** connected to the network acts as an HTTP server to receive and broadcast announcements[cite: 597, 775]. [cite_start]A standard USB camera captures the classroom video feed[cite: 82].


## 🛠️ Technology Stack

| Category | Tools Used |
| :--- | :--- |
| **Face Recognition** | [cite_start]InsightFace, OpenCV, Cosine Similarity [cite: 597] |
| **Backend** | [cite_start]Flask, REST APIs [cite: 597] |
| **Database** | [cite_start]PostgreSQL (hosted on Supabase) [cite: 597] |
| **Frontend** | [cite_start]HTML, CSS, JavaScript [cite: 584] |
| **Email** | [cite_start]SMTP (Gmail) [cite: 597] |
| **Hardware** | [cite_start]Raspberry Pi (HTTP server) [cite: 597] |
| **Development** | [cite_start]VS Code, Python 3.x [cite: 578, 588] |

## 🚀 Performance Metrics

| Metric | Performance |
| :--- | :--- |
| **Recognition Accuracy** | [cite_start]92.7% [cite: 81] |
| **Processing Speed** | [cite_start]~0.8 sec/student [cite: 81] |
| **Email Alert Latency** | [cite_start]< 2 minutes [cite: 81] |
| **Efficiency (vs. Manual)** | [cite_start]87% faster than roll calls [cite: 88] |

## 📸 Screenshots

* [cite_start]**Login Page:** Role-based login for Teachers and Students[cite: 657, 731].
* [cite_start]**Teacher Dashboard:** Main interface to start/stop attendance, send messages, and view reports[cite: 663].
* [cite_start]**Student Dashboard:** Personalized summary of attendance with percentage bars[cite: 732].

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/your-project-repo.git](https://github.com/your-username/your-project-repo.git)
    cd your-project-repo
    ```

2.  **Install Dependencies**
    A virtual environment is recommended.
    ```bash
    pip install flask opencv-python insightface psycopg2-binary smtplib requests 
    ```
    [cite_start][cite: 629]

3.  **Database Setup**
    * [cite_start]Create a new project on **Supabase**[cite: 631].
    * [cite_start]Use the SQL schema from the project (or `database.py`) to create the `students_login`, `teacher_login`, and `students_attendance` tables [cite: 504-506, 631].
    * Add your Supabase database credentials to your environment variables or config file.

4.  **Raspberry Pi Configuration**
    * [cite_start]Deploy the provided `app.py` (or equivalent) HTTP server on the Raspberry Pi[cite: 633].
    * [cite_start]Ensure it has an endpoint (e.g., `/broadcast_msg`) for receiving messages[cite: 633].
    * [cite_start]Connect a speaker to the Pi[cite: 275].

5.  **Run the System**
    * Start the main Flask server.
    ```bash
    python app.py
    ```
    [cite_start][cite: 636]
    * [cite_start]The application will be running at `http://localhost:80`[cite: 636].

## 🔮 Future Scope

This project lays a strong foundation for several potential enhancements:

* [cite_start]**Anti-Spoofing:** Improve the recognition model to detect and prevent spoofing attacks using photos or videos[cite: 845].
* [cite_start]**Mobile Notifications:** Integrate SMS or push notifications (e.g., Firebase Cloud Messaging) for real-time alerts[cite: 838, 839].
* [cite_start]**Offline Synchronization:** Implement local caching so the system can function during network outages and sync with the database once connectivity is restored[cite: 843, 844].
* [cite_start]**Advanced Analytics:** Build a comprehensive admin dashboard for generating detailed reports and analyzing attendance trends[cite: 841].
* [cite_start]**Voice Feedback:** Add audio confirmation (e.g., "Attendance Marked") in addition to visual feedback[cite: 847].
