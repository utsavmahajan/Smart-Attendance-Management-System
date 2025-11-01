import psycopg2
import psycopg2.extras
import os

class StudLoginDatabase:
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

    def Insert_Data(self,Scholar_No,name,Password):
        insert_script = (
            "INSERT INTO Students_Login (Scholar_No,name, Password) VALUES (%s ,%s, %s)"
        )
        insert_value = (Scholar_No,name, Password)
        self.cur.execute(insert_script, insert_value)
        self.conn.commit()

    def Delete_Data(self, Scholar_No):
        delete_script = "DELETE FROM Students_Login WHERE Scholar_No = %s"
        self.cur.execute(delete_script, (Scholar_No,))
        self.conn.commit()

    def Modify_Data(self, value,Scholar_No):
        update_script = """
        UPDATE Students_Login 
        SET Password = %s
        WHERE Scholar_No = %s
        """
        self.cur.execute(update_script, (value,Scholar_No))
        self.conn.commit()

    def Fetch_data(self, Scholar_No):
        display_query = """
        SELECT Password
        FROM Students_Login where Scholar_No = %s
        """
        self.cur.execute(display_query,(Scholar_No,))
        return self.cur.fetchall()


class TechLoginDatabase:
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

    def Insert_Data(self,Teacher_ID,name,Password,Subject):
        insert_script = (
            "INSERT INTO Teacher_Login (Teacher_ID,name, Password,Subject) VALUES (%s ,%s, %s,%s)"
        )
        insert_value = (Teacher_ID,name, Password,Subject)
        self.cur.execute(insert_script, insert_value)
        self.conn.commit()

    def Delete_Data(self, Teacher_ID):
        delete_script = "DELETE FROM Teacher_Login WHERE Teacher_ID = %s"
        self.cur.execute(delete_script, (Teacher_ID,))
        self.conn.commit()

    def Modify_Data(self, value,Teacher_ID):
        update_script = """
        UPDATE Teacher_Login
        SET Password = %s
        WHERE Teacher_ID = %s
        """
        self.cur.execute(update_script, (value,Teacher_ID))
        self.conn.commit()

    def Fetch_data(self, Teacher_ID):
        display_query = """
        SELECT Password,subject
        FROM Teacher_Login where Teacher_ID = %s
        """
        self.cur.execute(display_query,(Teacher_ID,))
        return self.cur.fetchall()