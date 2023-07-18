from flask import jsonify, request
import mysql.connector
from mysql.connector import Error
import os


mysql_password = os.environ.get('MYSQL_PASSWORD')



def save_content(content, mydb):
    cursor = mydb.cursor()

    try:
        insert_query = """
        INSERT INTO History (title, userPrompt, sqlPrompt, prePrompt, jsonOutput, sqlResults, output) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            content['title'],
            content['userPrompt'],
            content['sqlPrompt'],
            content['prePrompt'],
            content['jsonOutput'],
            content['sqlResults'],
            content['output'],
        )
        cursor.execute(insert_query, data)
        mydb.commit()
        cursor.close()

        return {"message": "Document saved successfully"}, 200
    except Error as e:
        print(f"Error: {e}")
        return {"message": "An error occurred while saving the document"}, 500
    
def update_content(content, mydb):
    cursor = mydb.cursor()

    try:
        # First check if the title exists
        select_query = "SELECT title FROM History WHERE title = %s"
        cursor.execute(select_query, (content['title'],))
        result = cursor.fetchone()
        
        if result is None:
            return {"message": "The template name does not exist"}, 400

        # If it does, update the existing record
        update_query = """
        UPDATE History
        SET userPrompt = %s, sqlPrompt = %s, prePrompt = %s, jsonOutput = %s, sqlResults = %s, output = %s
        WHERE title = %s
        """
        data = (
            content['userPrompt'],
            content['sqlPrompt'],
            content['prePrompt'],
            content['jsonOutput'],
            content['sqlResults'],
            content['output'],
            content['title'],
        )
        cursor.execute(update_query, data)
        mydb.commit()
        cursor.close()

        return {"message": "Document updated successfully"}, 200
    except Error as e:
        print(f"Error: {e}")
        return {"message": "An error occurred while updating the document"}, 500


# Commit your changes in the database