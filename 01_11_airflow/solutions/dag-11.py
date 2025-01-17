from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook


def find_active_user():
    postgres = PostgresHook(postgres_conn_id="startml_feed")
    with postgres.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT
                user_id
                , COUNT(*)
            FROM feed_action
            WHERE action = 'like'
            GROUP BY user_id
            ORDER BY COUNT(*) DESC
            LIMIT 1
            """)
            return cursor.fetchone()


with DAG(
    'hw_11_i-vekhov',
    default_args={
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),  # timedelta из пакета datetime
    },
    description='hw_11_i-vekhov',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 3, 29),
    catchup=False,
    tags=['hw_11_i-vekhov'],
) as dag:
    select_active_user = PythonOperator(
        task_id='select_active_user',
        python_callable=find_active_user
    )


''' Example 
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresHook
from airflow.operators.python import PythonOperator


with DAG(
    'simple_dag_db',
    default_args={
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),  # timedelta из пакета datetime
    },
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:

    def get_active_user():
        from psycopg2.extras import RealDictCursor
        postgres = PostgresHook(postgres_conn_id="startml_feed")
        # .get_conn() работает схоже с psycopg2
        with postgres.get_conn() as conn:
            # как и в psycopg2, необходимо создавать курсор
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT f.user_id, COUNT(f.user_id)
                    FROM feed_action f
                    WHERE f.action = 'like'
                    GROUP BY f.user_id
                    ORDER BY COUNT(f.user_id) DESC
                    LIMIT 1
                    """
                )
                results = cursor.fetchone()
        return results


    t1 = PythonOperator(
        task_id="postgres_query",
        python_callable=get_active_user
    )

    # В принципе, он не обязателен - в задании просят только вернуть словарь
    t2 = PythonOperator(
        task_id="print_operator",
        doc_md="Распечатать значение",
        python_callable=lambda ti: print(ti.xcom_pull(task_ids="postgres_query", key="return_value"))
    )
    t1 >> t2

    # еще один вариант
    def get_active_user_base_hook():
        from airflow.hooks.base import BaseHook
        import psycopg2
        from psycopg2.extras import RealDictCursor

        creds = BaseHook.get_connection("startml_feed")
        with psycopg2.connect(
            f"postgresql://{creds.login}:{creds.password}"
            f"@{creds.host}:{creds.port}/{creds.schema}"
        ) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT f.user_id, COUNT(f.user_id)
                    FROM feed_action f
                    WHERE f.action = 'like'
                    GROUP BY f.user_id
                    ORDER BY COUNT(f.user_id) DESC
                    LIMIT 1
                    """
                )
                results = cursor.fetchone()
        return results

    t3 = PythonOperator(
        task_id="another_sql_query",
        python_callable=get_active_user_base_hook,
    )
'''
