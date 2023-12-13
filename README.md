# Text Summarizer for Webinars

This repository encapsulates a demo of the final application and fine-tuned model with a comprehensive exploration into long document summarization in the context of multi-speaker webinar transcripts. Dive into my in-depth research report that navigates the complexities of long document summarization and evaluations of the current available open-source and closed-source models, along with my process of fine-tuning our very own summarization model on limited resources.

Date: October-November 2023<br/>
Live site: https://llm-text-summarizer.streamlit.app/ (backend is terminated at this time)<br/>
Paper: [https://github.com/jolenechong/textSummarizerLLMsApp/blob/main/Unleashing the Power of Large Language Models on Transcripts Summarization.docx](https://github.com/jolenechong/textSummarizerLLMsApp/blob/main/Unleashing%20the%20Power%20of%20Large%20Language%20Models%20on%20Transcripts%20Summarization.docx)<br/>

Here's a quick demo on the summarization features of the application and how it works.<br/>

https://github.com/jolenechong/textSummarizerLLMsApp/assets/77100254/3dbea24c-ad10-48b7-8911-ca7266f127c8

<br/>

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
