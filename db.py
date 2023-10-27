import mysql.connector

# Replace these values with your actual database credentials
host = "localhost"
user = "root"
password = "*****"
database = "soportetpi"

def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
        
    except mysql.connector.Error as e:
        print("Error:", e)
        return None
    
def close_database_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("Connection closed")

def inserMany(data):
    connection = get_database_connection()
    try:
        cursor = connection.cursor()
        
        insert_query = "INSERT INTO test (name, create_time) VALUES (%s,%s)"
        cursor.executemany(insert_query, data)        
        connection.commit()
        print("New tasks inserted successfully")
        
    except mysql.connector.Error as e:
        print("Error:", e)

def getQuestionsAndAnswers():
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            select_query = "SELECT * FROM questions"
            cursor.execute(select_query)
            result = cursor.fetchall()
            data = []

            for row in result:                              
                qDic = {'id' : row[0],'title' : row[1],'link' : row[2],'time' : row[3],'score' : row[4],'tags' : row[5],'answers' : []}
                q = "select * from answers where questionId = " + str(row[0])
                cursor.execute(q)
                answers = cursor.fetchall()
                for answer in answers:
                    qDic['answers'].append({
                        'id' : answer[0],'score' : answer[1],'isHighestScore' : answer[2],
                        'answerAcceptedOrSuggested' : answer[3],'html' : answer[4],'texts' : answer[5],'questionId' : answer[6]
                    })
                data.append(qDic)
            
            return data         
        except mysql.connector.Error as e:
            print("Error:", e)

        finally:
            close_database_connection(connection)

def delete (id):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            delete_query = "DELETE FROM test WHERE id = %s"
            cursor.execute(delete_query, (id,))
            connection.commit()
            print("Task deleted successfully")
        
        except mysql.connector.Error as e:
            print("Error:", e)

        finally:
            close_database_connection(connection)

def deleteAll ():
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            delete_query = "DELETE FROM test"
            cursor.execute(delete_query)
            connection.commit()
            print("Task deleted successfully")
        
        except mysql.connector.Error as e:
            print("Error:", e)

        finally:
            close_database_connection(connection)
