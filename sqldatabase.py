import psycopg2
import psycopg2.extras
from em import Email
import os

class SqlDatabase:
    def __init__(self, config_list):
        self.hostname = os.getenv("DATABASE_HOSTNAME")
        self.database = os.getenv("DATABASE_NAME")
        self.username = os.getenv("DATABASE_USERNAME")
        self.pwd = os.getenv("DATABASE_PASSWORD")
        self.port_id = os.getenv("DATABASE_PORT")
        self.conn = None
        self.cur = None
        self.autoexecute()

    def autoexecute(self):
        try:
            self.conn = psycopg2.connect(
                host=self.hostname,
                dbname=self.database,
                user=self.username,
                password=self.pwd,
                port=self.port_id,
            )
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("✅ Database connection established!")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

    def Create_Table(self, create_script):
        self.cur.execute(create_script)
        self.conn.commit()

    def Insert_Data(self,sno,EnrollMent_no, name):
        insert_script = (
            "INSERT INTO Students_attendance (s_no,EnrollMent_No, Name) VALUES (%s ,%s, %s)"
        )
        insert_value = (sno,EnrollMent_no, name)
        self.cur.execute(insert_script, insert_value)
        self.conn.commit()

    def Delete_Data(self, EnrollMent_no):
        delete_script = "DELETE FROM Students_Attendance WHERE EnrollMent_No = %s"
        self.cur.execute(delete_script, (EnrollMent_no,))
        self.conn.commit()

    def Update_Percentage(self, subject, enrollment_no=None):
        update_script = f"""
        UPDATE Students_Attendance 
        SET {subject}_Percentage = CASE 
            WHEN {subject}_TC > 0 THEN ROUND(({subject}_TCA::DECIMAL / {subject}_TC) * 100, 2)
            ELSE 0 
        END
        """
        if enrollment_no:
            update_script += " WHERE EnrollMent_No = %s"
            self.cur.execute(update_script, (enrollment_no,))
        else:
            self.cur.execute(update_script)

        self.conn.commit()

    def Update_AutoData(self, subject):
        with self.conn:  # Ensures transaction
            self.cur.execute(
                f"UPDATE Students_Attendance SET {subject}_TC = {subject}_TC + 1"
            )
            print(f"➕ Incremented {subject}_TC")  # Debug log

    def Update_Data(self, subject, enrollment_list):
        for enrollment_no in enrollment_list:
            update_script = f"""
            UPDATE Students_Attendance 
            SET {subject}_TCA = COALESCE({subject}_TCA, 0) + 1
            WHERE EnrollMent_No = %s
            """
            self.cur.execute(update_script, (enrollment_no,))
            self.conn.commit()
            self.Update_Percentage(subject, enrollment_no)

    def Modify_Data(self, subject, enrollment_no, value):
        update_script = f"""
        UPDATE Students_Attendance 
        SET {subject}_TCA = %s
        WHERE EnrollMent_No = %s
        """
        self.cur.execute(update_script, (value, enrollment_no))
        self.conn.commit()
        self.Update_Percentage(subject, enrollment_no)

    def Display_Data_Teacher(self, subject):
        display_query = f"""
        SELECT S_NO, EnrollMent_No, Name, {subject}_TCA, {subject}_TC, {subject}_Percentage 
        FROM Students_Attendance order by s_no
        """
        self.cur.execute(display_query)
        return self.cur.fetchall()

    def Display_Data_HOD(self):
        self.cur.execute("SELECT * FROM Students_Attendance order by s_no")
        return self.cur.fetchall()

    def Display_Data_Student(self, enrollment_no):
        display_query = '''SELECT enrollment_no,	name,	dcc_tc,	dcc_tca,	dcc_percentage,	se_tc,	se_tca,	se_percentage,	cd_tc,	cd_tca,
        	cd_percentage,	pr_tc,	pr_tca,	pr_percentage,	nlp_tc,	nlp_tca	nlp_percentage,	r_prog_tc,	r_prog_tca,	r_prog_percentage FROM Students_Attendance WHERE EnrollMent_No = %s'''
        self.cur.execute(display_query, (enrollment_no,))
        return self.cur.fetchall()

    def Destroy_Obj(self):
        self.cur.close()
        self.conn.close()
        print("✅ Database connection closed!")

    def Send_Email(self, subject):
        fetch_script = f"""
        select name, enrollment_no from Students_Attendance where  {subject}_percentage > 75.00;
        """
        self.cur.execute(fetch_script)
        list = self.cur.fetchall()
        e = Email()
        for i in range(len(list)):
            name = list[i][0]
            Enroll_no = list[i][1]
            e.Send_mail(subject, name, Enroll_no.lower())

