# Text Summarizer for Webinars Server

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