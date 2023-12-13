# Text Summarizer for Webinars

This repository encapsulates a demo of the final application and fine-tuned model with a comprehensive exploration into long document summarization in the context of multi-speaker webinar transcripts. Dive into my in-depth research report that navigates the complexities of long document summarization and evaluations of the current available open-source and closed-source models, along with my process of fine-tuning our very own summarization model on limited resources.

Date: October-November 2023
Live site: https://llm-text-summarizer.streamlit.app/ (backend is terminated at this time)
Paper: https://github.com/jolenechong/textSummarizerLLMsApp/blob/main/Unleashing the Power of Large Language Models on Transcripts Summarization.docx

Here's a quick demo on the summarization features of the application and how it works.<br/>


<br/><br/>

### Usage
```bash
# create virtual environment
py -m venv ".venv"
cd .venv/Scripts
activate.bat # for windows
source .venv/Scripts/activate # for linux

# install relevant libraries
pip install -r requirements.txt

# initializing db
# might need to set up listen_addresses in postgresql.conf file to 'localhost' if it's your first time running it
py
from app import app, db
app.app_context().push()
db.create_all()

# frontend
streamlit run streamlit-app.py
```


### Contact
Jolene - [jolenechong7@gmail.com](mailto:jolenechong7@gmail.com) <br>