from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import psycopg2
import os
from dotenv import load_dotenv
import sys

load_dotenv()

host = os.getenv('FSTR_DB_HOST')
port = os.getenv('FSTR_DB_PORT')
user = os.getenv('FSTR_DB_LOGIN')
password = os.getenv('FSTR_DB_PASS')
dbname = os.getenv('FSTR_DB_NAME')

app = Flask(__name__)
api = Api(app)


class DatabaseHandler:
    def __init__(self, host, port, user, password, dbname):
        self.conn = None
        self.cur = None
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            self.cur = self.conn.cursor()
            print("Connected to PostgreSQL.")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            sys.exit(1)

    def add_pereval_data(self, beautyTitle, title, other_titles, connect, date_added, user_id, coord_id, level_id):
        try:
            # SQL запрос для вставки данных
            insert_query = """INSERT INTO pereval_added (beautyTitle, title, other_titles, connect, date_added, user_id, coord_id, level_id)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
            # Данные для вставки
            record_to_insert = (beautyTitle, title, other_titles, connect, date_added, user_id, coord_id, level_id)

            # Выполнение команды для вставки данных
            self.cur.execute(insert_query, record_to_insert)

            # Фиксация транзакции
            self.conn.commit()

            print("Record inserted successfully into pereval table")

        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into pereval table", error)
            self.conn.rollback()  # Откат в случае ошибки

        finally:
            # Закрываем курсор
            if self.cur is not None:
                self.cur.close()

    def close_connection(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()


class PerevalAdd(Resource):
    def post(self):
        try:
            data = request.json
            db_handler = DatabaseHandler('localhost', port, user, password, dbname)
            db_handler.add_pereval_data(
                data['beautyTitle'], data['title'], data['other_titles'],
                data['connect'], data['date_added'], data['user_id'],
                data['coord_id'], data['level_id']
            )
            db_handler.close_connection()
            return {'message': 'Data added successfully.'}, 201
        except Exception as e:
            return {'message': f'An error occurred: {str(e)}'}, 500


class PerevalById(Resource):
    def get(self, id):
        try:
            db_handler = DatabaseHandler(host, port, user, password, dbname)
            db_handler.init(host, port, user, password, dbname)
            db_handler.cur.execute("SELECT * FROM pereval_added WHERE id = %s", (id,))
            result = db_handler.cur.fetchone()
            db_handler.close_connection()
            if result:
                return jsonify(result)
            else:
                return {'message': 'Record not found'}, 404
        except Exception as e:
            return {'message': str(e)}, 500


class PerevalEdit(Resource):
    def patch(self, id):
        try:
            data = request.json
            db_handler = DatabaseHandler(host, port, user, password, dbname)
            db_handler.init(host, port, user, password, dbname)
            db_handler.cur.execute("SELECT status FROM pereval_added WHERE id = %s", (id,))
            status = db_handler.cur.fetchone()
            if status[0] != 'new':
                return {'message': 'Only records with status "new" can be edited'}, 403

            # Создание запроса на обновление, исключая поля ФИО, email и номер телефона
            fields = [f"{k} = %s" for k in data.keys() if k not in ['fio', 'email', 'phone']]
            query = "UPDATE pereval_added SET " + ", ".join(fields) + " WHERE id = %s"
            values = list(data.values()) + [id]

            db_handler.cur.execute(query, values)
            db_handler.conn.commit()
            db_handler.close_connection()
            return {'message': 'Record updated successfully'}, 200
        except Exception as e:
            return {'message': str(e)}, 500

class PerevalByUserEmail(Resource):
    def get(self):
        email = request.args.get('user__email')
        try:
            db_handler = DatabaseHandler(host, port, user, password, dbname)
            db_handler.init(host, port, user, password, dbname)
            db_handler.cur.execute("SELECT * FROM pereval_added WHERE user_email = %s", (email,))
            result = db_handler.cur.fetchall()
            db_handler.close_connection()
            return jsonify(result)
        except Exception as e:
            return {'message': str(e)}, 500



api.add_resource(PerevalAdd, '/add_pereval')
api.add_resource(PerevalById, '/submitData/<int:id>')
api.add_resource(PerevalEdit, '/submitData/<int:id>')
api.add_resource(PerevalByUserEmail, '/submitData')


if __name__ == '__main__':
    app.run(debug=True)
