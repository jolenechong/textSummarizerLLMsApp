from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from peft import PeftModel, PeftConfig
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from gevent.pywsgi import WSGIServer

from flask_socketio import SocketIO
from threading import Lock

print("Loading model...")

config = PeftConfig.from_pretrained("jolenechong/lora-bart-cnn-1024")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
model = PeftModel.from_pretrained(model, "jolenechong/lora-bart-cnn-1024")
tokenizer = AutoTokenizer.from_pretrained("jolenechong/lora-bart-cnn-1024", from_pt=True)

# Downloading (…)/adapter_config.json: 100% 448/448 [00:00<00:00, 1.76MB/s]
# Downloading (…)lve/main/config.json: 100% 1.58k/1.58k [00:00<00:00, 6.20MB/s]
# Downloading pytorch_model.bin: 100% 1.63G/1.63G [03:24<00:00, 7.95MB/s]
# Downloading (…)neration_config.json: 100% 363/363 [00:00<00:00, 1.43MB/s]
# Downloading adapter_model.bin: 100% 4.77M/4.77M [00:00<00:00, 6.08MB/s]
# Downloading (…)okenizer_config.json: 100% 1.25k/1.25k [00:00<00:00, 3.89MB/s]
# Downloading (…)olve/main/vocab.json: 100% 798k/798k [00:00<00:00, 11.7MB/s]
# Downloading (…)olve/main/merges.txt: 100% 456k/456k [00:00<00:00, 1.30MB/s]
# Downloading (…)/main/tokenizer.json: 100% 2.11M/2.11M [00:00<00:00, 4.15MB/s]
# Downloading (…)in/added_tokens.json: 100% 75.0/75.0 [00:00<00:00, 314kB/s]
# Downloading (…)cial_tokens_map.json: 100% 167/167 [00:00<00:00, 476kB/s]
# seeems to take 10mins to start up

app = Flask(__name__)

thread = None
thread_lock = Lock()
socketio = SocketIO(app, cors_allowed_origins='*')

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost/llm_summarizer_db'

# should be on 5432
db=SQLAlchemy(app)

print("App is ready...")

class SummarizedText(db.Model):
    __tablename__='text'

    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.String(10000))
    summarized=db.Column(db.String(10000))
    
    def __init__(self,text,summarized):
        self.text=text
        self.summarized=summarized

@app.route('/')
def index():
  # send back json "hello world"
  return jsonify({'message': 'Welcome to the LLM Summarizer!'})

@app.route('/summarize', methods=['POST'])
def summarize():
    toSummarize = request.get_json()
    text = toSummarize['text']
    socketio.emit('summarization_progress', {'message': "Summarizing..."})
    print("Summarizing...")
    
    inputs = tokenizer(text, return_tensors="pt")
    model.eval()
    with torch.no_grad():
        outputs = model.generate(input_ids=inputs["input_ids"])
        summarized = tokenizer.batch_decode(outputs.detach().cpu().numpy())[0].replace("<s>", "").replace("</s>", "")
        socketio.emit('summarization_progress', {'message': "Summarized"})
        print("Summarized")

        summarized_item = SummarizedText(text=text, summarized=summarized)
        db.session.add(summarized_item)
        db.session.commit()
        socketio.emit('summarization_progress', {'message': "Saved to DB"})
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