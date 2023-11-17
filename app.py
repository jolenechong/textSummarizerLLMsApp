from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from peft import PeftModel, PeftConfig
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import time

import transformers
from langchain import HuggingFacePipeline, PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from gevent.pywsgi import WSGIServer

import boto3
from datetime import datetime

# from flask_socketio import SocketIO
# from threading import Lock

import os
from dotenv import load_dotenv
load_dotenv()

print("Loading model...")

config = PeftConfig.from_pretrained("jolenechong/lora-bart-cnn-1024")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
model = PeftModel.from_pretrained(model, "jolenechong/lora-bart-cnn-1024")
tokenizer = AutoTokenizer.from_pretrained("jolenechong/lora-bart-cnn-1024", from_pt=True)

def summ_pipeline(model, tokenizer, chain_type, max_length, prompt=False):
  pipeline = transformers.pipeline(
      "summarization",
      model=model,
      tokenizer=tokenizer,
      torch_dtype=torch.bfloat16,
      trust_remote_code=True,
      device_map="auto",
      max_length=max_length,
      do_sample=True,
      top_k=10,
      num_return_sequences=1,
      # eos_token_id=tokenizer.eos_token_id, # bart models don't have this eos_token_id
  )
  llm = HuggingFacePipeline(pipeline = pipeline)

  if chain_type == "map_reduce":
    if prompt:
      prompt_template = """Summarize this: ```{text}```"""
      prompt_message = PromptTemplate(template=prompt_template, input_variables=["text"])
      summary_chain = load_summarize_chain(llm=llm, chain_type=chain_type, token_max=max_length, prompt=prompt_message)
    else:
      summary_chain = load_summarize_chain(llm=llm, chain_type=chain_type, token_max=max_length)
  else:
    # can't get it to work with refine and stuff, think they updated the library but no documentation
    # on how to set token_max
    summary_chain = load_summarize_chain(llm=llm, chain_type=chain_type)
  return summary_chain

app = Flask(__name__)

# thread = None
# thread_lock = Lock()
# socketio = SocketIO(app, cors_allowed_origins='*')

def generateFileName():
    # generate using time
    time = str(datetime.timestamp(datetime.now())).split('.')[0]
    return f"{time}.txt"

# environmental var
db_url = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI']=db_url

# should be on 5432
db=SQLAlchemy(app)

print("App is ready...")

class SummarizedText(db.Model):
    __tablename__='text'

    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.String(255)) # saves link to original text in s3 (long text, better to store in s3)
    summarized=db.Column(db.String(1000)) # saves summaries
    elapsed_time=db.Column(db.Float)
    
    def __init__(self, text, summarized, elapsed_time):
        self.text=text
        self.summarized=summarized
        self.elapsed_time=elapsed_time

with app.app_context():
    db.create_all()

@app.route('/')
def index():
  # send back json "hello world"
  return jsonify({'message': 'Welcome to the LLM Summarizer!'})

@app.route('/summarize', methods=['POST'])
def summarize():
    toSummarize = request.get_json()
    text = toSummarize['text']
    # socketio.emit('summarization_progress', {'message': "Summarizing..."})
    print("Summarizing...")

    # handle long text
    max_tokens = 1024
    start_time = time.time()

    summary_chain = summ_pipeline(model, tokenizer, "map_reduce", max_tokens)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=max_tokens-100, chunk_overlap=100)

    # if tokens are within max_tokens range don't split it
    # else split it
    docs = text_splitter.create_documents([text])
    summarized = summary_chain.run(docs)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # socketio.emit('summarization_progress', {'message': "Summarized"})
    print("Summarized")

    # save text to s3
    s3 = boto3.resource('s3')
    bucket_name = "llm-text-summarizer"
    file_name = generateFileName()
    name = f"s3://{bucket_name}/{file_name}"

    object = s3.Object(bucket_name, file_name)
    object.put(Body=text)

    summarized_item = SummarizedText(text=name, summarized=summarized.replace("<s>", "").replace("</s>", ""), elapsed_time=elapsed_time)
    db.session.add(summarized_item)
    db.session.commit()
    # socketio.emit('summarization_progress', {'message': "Saved to DB"})
    print("Saved to DB")

    return jsonify({'message': summarized})

@app.route('/all', methods=['GET'])
def all():
    allSummarized = SummarizedText.query.all()
    json_list = []
    for summarized in allSummarized:
        json_list.append({'text': summarized.text, 'summarized': summarized.summarized})

    return jsonify({'message': json_list})

if __name__ == '__main__':  #python interpreter assigns "__main__" to the file you run
    # app.run(debug=True)
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    print("Server running on port 5000")
    http_server.serve_forever()