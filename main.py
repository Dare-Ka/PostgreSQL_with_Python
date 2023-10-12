import psycopg2
import config


class DataBase:
    def __init__(self, conn):
        self.conn = conn
        self.cur = self.conn.cursor()

    def create_db(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(40),
            last_name VARCHAR(40),
            email VARCHAR(40)
            );
            ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS phone_book(
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES client(id),
            phone CHAR(11) NOT NULL
            );
            ''')
        self.conn.commit()
        pass

    def add_client(self, first_name: str, last_name: str, email: str):
        self.cur.execute('''
            INSERT INTO client(first_name, last_name, email)
            VALUES (%s, %s, %s);
        ''', (first_name, last_name, email))
        self.conn.commit()
        pass

    def add_phone(self, client_id, phone):
        if self.find_client(client_id=client_id) != 'Клиент не найден':
            self.cur.execute('''
                INSERT INTO phone_book(client_id, phone)
                VALUES(%s, %s);
            ''', (client_id, phone))
            self.conn.commit()
        else:
            return 'Данного клиента нет в базе данных!'

    def chang_client(self, client_id, first_name=None, last_name=None, email=None):
        dict = {'first_name': first_name,
                'last_name': last_name,
                'email': email}
        if self.find_client(client_id=client_id) != 'Клиент не найден':
            for key, value in dict.items():
                if value:
                    self.cur.execute(f'''
                    UPDATE client 
                    SET {key}=%s WHERE id=%s;
                    ''', (value, client_id))
                    self.conn.commit()
        else:
            return 'Данного клиента нет в базе данных!'

    def delete_phone(self, client_id, phone):
        if self.find_client(client_id=client_id) != 'Клиент не найден':
            self.cur.execute('''
                DELETE FROM phone_book
                WHERE client_id=%s AND phone=%s
            ''', (client_id, phone))
            self.conn.commit()
        pass

    def delete_client(self, client_id):
        self.cur.execute('''
        SELECT phone from phone_book
        WHERE client_id=%s
        ''', (client_id,))
        phones = self.cur.fetchall()
        for phone in phones:
            self.delete_phone(client_id=client_id, phone=phone)
        self.cur.execute('''
        DELETE FROM client
        WHERE id=%s
        ''', (client_id,))
        self.conn.commit()
        pass

    def find_client(self, client_id=None, first_name=None, last_name=None, email=None, phone=None):
        dict = {'client_id': client_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phones': phone}
        for key, value in dict.items():
            if value:
                self.cur.execute(f'''
                SELECT first_name, last_name, email, phone_book.phone FROM client
                JOIN phone_book on phone_book.client_id = client.id
                WHERE {key}=%s;
                ''', (value,))
                result = self.cur.fetchall()
                return result
        else:
            return 'Клиент не найден'

    def __del__(self):
        self.cur.close()
        self.conn.close()


conn = psycopg2.connect(database='users_info', user='postgres', password=config.password)
base = DataBase(conn)
base.create_db()

base.add_client('Таня', 'Иванова', 'blablabla@gmail.com')
base.add_client('Максим', 'Кожин', 'bla@gmail.com')
base.add_client('TO DELETE', 'TO DELETE', 'TO DELETE')
base.add_phone(1, 89999999999)
base.add_phone(2, 89222222222)
base.add_phone(3, 89000000000)
base.add_phone(3, 89000000100)
base.add_phone(1, 89123456789)
base.chang_client(1, last_name='Кожина')
base.chang_client(2, email='blabla@gmail.com')
base.delete_phone(3, '89000000100')
base.delete_client(3)
print(base.find_client(first_name='TO DELETE'))
print(base.find_client(first_name='Таня'))
print(base.find_client(last_name='Кожин'))
