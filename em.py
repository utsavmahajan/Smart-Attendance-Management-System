import os
from email.message import EmailMessage
import ssl
import smtplib

class Email:
    def Send_mail(self, col_subject, Name, Enroll_no):
        email_sender = os.getenv("Email Address")
        email_password = os.getenv("Password")
        email_receiver = Enroll_no + "@medicaps.ac.in"

        subject_details = {
            "dcc": ("Distributed and Cloud Computing", "IT3CO35", os.getenv("DCC PROF")),
            "se": ("Software Engineering", "IT3CO36", os.getenv("SE PROF")),
            "cd": ("Compiler Design", "IT3CO37", os.getenv("CD PROF")),
            "pr": ("Pattern Recognition", "IT3EA06", os.getenv("PR PROF")),
            "nlp": ("Natural Language Processing", "IT3EA06", os.getenv("NLP PROF")),
        }
        col_subject, subject_code, teacher_name = subject_details.get(
            col_subject,
            ("R-Programming", "OE00051", os.getenv("R Prog PROF"))
        )

        subject = f"Low Attendance Alert for {col_subject} {subject_code}"
        body = f"""
Dear {Name},

I hope you are doing well.

This is to inform you that your attendance in {col_subject} {subject_code} is currently below 75%. As per the attendance policy, students with less than 75% attendance will not be permitted to sit for the upcoming examinations unless the shortfall is covered before the exams.

Please take the necessary steps to improve your attendance to meet the required percentage. If you have any concerns, feel free to reach out for clarification.

Best regards,
{teacher_name}
Medicaps-University
"""
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

