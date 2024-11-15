import psycopg2
from psycopg2 import sql
import random
import threading
import time

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS tags (
                id SERIAL PRIMARY KEY,
                name VARCHAR(30) UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER REFERENCES posts(id),
                tag_id INTEGER REFERENCES tags(id),
                PRIMARY KEY (post_id, tag_id)
            );

            CREATE INDEX idx_users_username ON users(username);
            CREATE INDEX idx_posts_user_id ON posts(user_id);
        """)
        conn.commit()

def populate_data(conn):
    with conn.cursor() as cur:
        # Добавляем пользователей
        for i in range(1, 6):
            cur.execute("""
                INSERT INTO users (username, email) VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING;
            """, (f'user{i}', f'user{i}@example.com'))

        # Добавляем теги
        tags = ['python', 'docker', 'postgres', 'testing', 'replication']
        for tag in tags:
            cur.execute("""
                INSERT INTO tags (name) VALUES (%s)
                ON CONFLICT (name) DO NOTHING;
            """, (tag,))
        conn.commit()

def continuously_populate(conn):
    while True:
        with conn.cursor() as cur:
            # Выбираем случайного пользователя
            cur.execute("SELECT id FROM users ORDER BY RANDOM() LIMIT 1;")
            user_id = cur.fetchone()[0]

            # Добавляем пост
            content = f"Sample content {random.randint(1, 1000)}"
            cur.execute("""
                INSERT INTO posts (user_id, content) VALUES (%s, %s) RETURNING id;
            """, (user_id, content))
            post_id = cur.fetchone()[0]

            # Присваиваем теги
            cur.execute("SELECT id FROM tags ORDER BY RANDOM() LIMIT 2;")
            tag_ids = cur.fetchall()
            for tag_id in tag_ids:
                cur.execute("""
                    INSERT INTO post_tags (post_id, tag_id) VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (post_id, tag_id[0]))
            conn.commit()
        time.sleep(3)

if __name__ == "__main__":
    conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')
    create_tables(conn)
    populate_data(conn)

    # Запускаем непрерывное заполнение данных в отдельном потоке
    threading.Thread(target=continuously_populate, args=(conn,)).start()
