import os

import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
# DATABASE_URL = os.popen('heroku config:get DATABASE_URL -a line-bot-test-alice').read()[:-1]
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True


def sql_init_user(user_id):
    cursor = conn.cursor()
    
    SQL = f'''
    SELECT * FROM user_select_day WHERE user_id = '{user_id}'
    '''
    cursor.execute(SQL)
    result = cursor.fetchone()
    if result:
        cursor.close()
    else:
        SQL = f'''
        INSERT INTO user_select_day(user_id, day)
        VALUES ('{user_id}', 0)
        '''
        cursor.execute(SQL)
        SQL = f'''
        INSERT INTO user_select_region(user_id, region)
        VALUES ('{user_id}', '')
        '''
        cursor.execute(SQL)
        SQL = f'''
        INSERT INTO schedule_table(user_id, schedule)
        VALUES ('{user_id}', '')
        '''
        cursor.execute(SQL)
        cursor.close()


def sql_set_user_select_day(user_id, day):
    cursor = conn.cursor()
    SQL = f'''
    UPDATE user_select_day
    SET day = {day}
    WHERE user_id = '{user_id}'
    '''
    cursor.execute(SQL)
    cursor.close()


def sql_set_user_select_region(user_id, region):
    cursor = conn.cursor()
    SQL = f'''
        UPDATE user_select_region
        SET region = '{region}'
        WHERE user_id = '{user_id}'
        '''
    cursor.execute(SQL)
    cursor.close()


def sql_get_user_select_day(user_id):
    cursor = conn.cursor()
    SQL = f'''
    SELECT day from user_select_day WHERE user_id = '{user_id}'
    '''
    cursor.execute(SQL)
    result = cursor.fetchone()
    cursor.close()
    return result[0]


def sql_get_user_select_region(user_id):
    cursor = conn.cursor()
    SQL = f'''
        SELECT region from user_select_region WHERE user_id = '{user_id}'
        '''
    cursor.execute(SQL)
    result = cursor.fetchone()
    cursor.close()
    return result[0]


def sql_set_user_schedule_classification(user_id, schedule, hotel, food, play, activity):
    cursor = conn.cursor()
    SQL = f'''
        UPDATE schedule_table
        SET hotel = '{hotel}', food = '{food}', play = '{play}', schedule = '{schedule}', activity = '{activity}'
        WHERE user_id = '{user_id}'
        '''
    cursor.execute(SQL)
    cursor.close()


def sql_get_user_schedule_classification(user_id):
    cursor = conn.cursor()
    SQL = f'''
                SELECT schedule, hotel, food, play, activity from schedule_table WHERE user_id = '{user_id}'
                '''
    cursor.execute(SQL)
    result = cursor.fetchone()
    cursor.close()
    return result[0], result[1], result[2], result[3], result[4]


def sql_set_schedule(user_id, schedule):
    cursor = conn.cursor()
    SQL = f'''
            UPDATE schedule_table
            SET schedule = '{schedule}'
            WHERE user_id = '{user_id}'
            '''
    cursor.execute(SQL)
    cursor.close()


def sql_set_hotel(user_id, hotel):
    cursor = conn.cursor()
    SQL = f'''
            UPDATE schedule_table
            SET hotel = '{hotel}'
            WHERE user_id = '{user_id}'
            '''
    cursor.execute(SQL)
    cursor.close()


def sql_set_food(user_id, food):
    cursor = conn.cursor()
    SQL = f'''
            UPDATE schedule_table
            SET food = '{food}'
            WHERE user_id = '{user_id}'
            '''
    cursor.execute(SQL)
    cursor.close()


def sql_set_play(user_id, play):
    cursor = conn.cursor()
    SQL = f'''
             UPDATE schedule_table
             SET play = '{play}'
             WHERE user_id = '{user_id}'
             '''
    cursor.execute(SQL)
    cursor.close()


def sql_set_activity(user_id, activity):
    cursor = conn.cursor()
    SQL = f'''
             UPDATE schedule_table
             SET activity = '{activity}'
             WHERE user_id = '{user_id}'
             '''
    cursor.execute(SQL)
    cursor.close()


def list_to_list_str(s: list):
    return ','.join([str(x) for x in s]).replace("'", "\"")
