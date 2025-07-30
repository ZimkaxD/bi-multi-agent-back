import psycopg2, psycopg2.extras, os
from dotenv import load_dotenv
load_dotenv()

class ExecuteSQLAgent:
    def __init__(self, connection_string: str = os.environ.get("DB_CONNECTION")):
        self.connection = psycopg2.connect(connection_string)
        self.connection.autocommit = False

    def execute_sql(self, sql: str)->list:
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(sql)
            try:
                rows = cursor.fetchall()
            except psycopg2.ProgrammingError:
                rows = []
        self.connection.commit()
        return rows


    def safe_execute(self, sql: str)->dict:
        try:
            data = self.execute_sql(sql)
            return {"success": True, "data":  data}
        except Exception as e:
            self.connection.rollback()
            return {"success": False, "error": str(e)}
