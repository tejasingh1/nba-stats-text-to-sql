from flask import Flask, send_from_directory, request, jsonify
import json
from flask_cors import CORS  # new
import mysql.connector
import traceback
from mysql.connector import connect, Error, pooling
from saveContent import save_content
import os
from generate_query import generate_queries
from execute_query import execute_queries
from saveContent import save_content, update_content
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import tiktoken
import re

app = Flask(__name__, static_folder='../client/build')

# Create connection pool
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name = "mypool",
        pool_size = 20,  # Change this to the maximum number of concurrent connections your MySQL server can handle
        host='localhost',
        user='root',
        password=os.environ.get('MYSQL_PASSWORD'),
        database='trek_health'
    )
except Error as err:
    print(f"Failed to create connection pool: {err}")
    exit(1)  # Terminate the application if pool creation fails

CORS(app, origins=["http://localhost:3000"])


@app.route('/api/data', methods=['POST'])
def process_data():
    # print("\n\nGENERATE QUERY", request.json['sqlPrompt'])
    # Retrieve the user prompt from the client request
    sql_prompt = request.json.get('sqlPrompt')
    is_test = request.json.get('test')

    if is_test:
        # Generate the SQL queries
        return {'response': sql_prompt}
    json_output = generate_queries(sql_prompt)
    return {'response': json_output}

@app.route('/api/execute', methods=['POST'])
def execute_data():
    # print("\n\nEXECUTE QUERY", request.json['jsonOutput'])
    try:
        mydb = pool.get_connection()
        json_output_str = request.json['jsonOutput']
        json_start_index = json_output_str.find("{")
        if json_start_index == -1:
            raise ValueError("Invalid JSON input")
        json_output = json.loads(json_output_str[json_start_index:]) 
        
        query = json_output['SQL']
        if not query:
            return {'response': "No data returned from query."}
        result = execute_queries(query, mydb)
        mydb.close()
        return {'response': result}
    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        return {'response': "No data returned from query."}, 500 


    
def count_tokens(str):
    return len(tiktoken.encoding_for_model("gpt-4").encode(str))
    
@app.route('/api/answer', methods=['POST'])
def generate_answer():
    # print("Generating answer")
    too_long = False
    pre_prompt = request.json.get('prePrompt')
    
    sql_results = request.json.get('sqlResults')
    # print(f"sql_results: {sql_results}")
    if (sql_results == "No data returned from query."):
        return {'response': "No data found from the prompt."}
    # print(f"sql results: {sql_results}")
    if count_tokens(sql_results) + count_tokens(pre_prompt) > 4096:
        sql_results_cut = sql_results[:4096 - count_tokens(pre_prompt) - 1]
        pre_prompt = re.sub(r'{{sql_results}}', sql_results_cut, pre_prompt)
        print("TOO LONG")
        too_long = True
    else:
        pre_prompt = re.sub(r'{{sql_results}}', sql_results, pre_prompt)
    
    llm = OpenAI(temperature=0.5, model_name="gpt-3.5-turbo", max_tokens=1000)
    # set max_tokens to 1000
    # print("Pre Prompt: ", pre_prompt)
    print("\n\PRE PROMPT: ", pre_prompt)
    answer = llm(pre_prompt)
    if too_long:
        answer += "\n\nNote: This is only part of the result, as full results were too long to display"
    return {'response': answer}


# Serve the static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and path != "api/data":
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/history', methods=['GET'])
def get_history():
    mydb = pool.get_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT title FROM history")
    titles = cursor.fetchall()
    titles = [title[0] for title in titles]
    mydb.close()  # if titles are tuples, flatten to list
    return jsonify(titles), 200



@app.route('/api/save', methods=['POST'])
def save():
    content = request.json
    print(f"content: {content}")
    # return {"response": "success"}
    mydb = pool.get_connection()
    response, status_code = save_content(content, mydb)
    mydb.close()
    return jsonify(response), status_code
    
@app.route('/api/loadHistoryContent', methods=['POST'])
def load_history_content():
    mydb = pool.get_connection()
    # Parse the request data
    data = request.get_json()
    title = data['title']
    
    # Create a SQL query to fetch the history item
    query = "SELECT * FROM history WHERE title = %s"
    values = (title, )

    # Execute the query
    mycursor = mydb.cursor()
    mycursor.execute(query, values)
    result = mycursor.fetchone()
    mycursor.close()
    mydb.close()



    # Convert the result to a JSON response
    response = {
            'userPrompt': result[2],
            'sqlPrompt': result[3],
            'jsonOutput': result[5],
            'sqlResults': result[6],
            'prePrompt': result[4],
            'output': result[7],
        }
    return jsonify(response), 200

@app.route('/api/update', methods=['POST'])
def update():
    mydb = pool.get_connection()
    content = request.get_json()
    response, status_code = update_content(content, mydb)
    mydb.close()
    return jsonify(response), status_code




    



# Start the Flask server
if __name__ == '__main__':
    print("hello starting server")
    app.run(port=3002, debug=True)