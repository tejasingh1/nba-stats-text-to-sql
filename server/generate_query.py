# generate_query.py
import tiktoken
from langchain.llms import OpenAI
import re

def read_file(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    return file_contents


def generate_queries(sql_prompt):
    with open('trek_health_schema.txt', 'r') as file:
        schema = file.read()
    with open('sample_for_prompt.csv', 'r') as file:
        sample = file.read()
    sql_prompt = re.sub(r'{{sample}}', sample, sql_prompt)
    sql_prompt = re.sub(r'{{schema}}', schema, sql_prompt)
    # print sql prompt
    print(f"sql_prompt: {sql_prompt}")
    llm = OpenAI(temperature=0.5, model_name="gpt-4")
    json_output = (llm(sql_prompt))
    return json_output
