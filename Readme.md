Shows an chatGPT generated image based on the current spiegel.de headline to display on a framed touchscreen. This Python Flask web application fetches data from an RSS feed, generates images, saves them along with the data in a SQLite database, and displays them on a web page.

```
1. Get openai api key
2. Duplicate .env.example to .env
3. Add your key
```

```
#  Windows
python -m venv venv
.\.venv\Scripts\activate
# Unix
python3 -m venv .venv
source .venv/bin/activate
# Install
pip install -r requirements.txt
flask run

```