import psycopg2
import time

def run_tests(conn):
    last_count = 0
    while True:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM posts;")
            post_count = cur.fetchone()[0]
            if post_count != last_count:
                print(f"Количество постов: {post_count}")
                last_count = post_count
        time.sleep(2)


if __name__ == "__main__":
    # Подключаемся к реплике
    conn = psycopg2.connect(host='localhost', port=5433, user='postgres', password='password')
    run_tests(conn)
