from flask import Flask, render_template
import feedparser
import sqlite3
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import base64
from PIL import Image
import requests
from io import BytesIO
from base64 import b64decode, b64encode
import openai

app = Flask(__name__)
DATABASE = 'database.db'

def initialize_database():
    print("initialize_database")
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            original_image BLOB,
            generated_image BLOB
        )
    ''')

    connection.commit()
    connection.close()

def download_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Open the image using Pillow
        with Image.open(BytesIO(response.content)) as img:
            # Convert image to PNG
            img = img.convert("RGBA")

            # Determine the dimension to crop
            width, height = img.size
            new_size = min(width, height)

            # Calculate cropping parameters
            left = (width - new_size) / 2
            top = (height - new_size) / 2
            right = (width + new_size) / 2
            bottom = (height + new_size) / 2

            # Crop the image to make it square
            img_cropped = img.crop((left, top, right, bottom))

            # Save cropped image to a BytesIO object
            img_byte_arr = BytesIO()
            img_cropped.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            return img_byte_arr
    except requests.RequestException as e:
        print(f"Error downloading the image: {e}")
        return None
    
def fetch_and_generate():
    # Parse RSS feed and extract information
    feed = feedparser.parse("https://www.spiegel.de/schlagzeilen/tops/index.rss")
    first_story = feed.entries[0]
    title = first_story.title
    description = first_story.description
    image_url = first_story.enclosures[0]['url']
    
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Download the original image
    original_image_data = download_image(image_url)

    # Generate image using OpenAI (Placeholder - replace with actual implementation)
    prompt =  f"Create a digital painting of the following article: {description}"
    generated_image_data = generate_image_with_openai(api_key,prompt, original_image_data)
    if generate_image_with_openai:
        # Save data to SQLite database
        save_data_to_database(title, description, original_image_data, generated_image_data)


def generate_image_with_openai(api_key, prompt, original_image_data, num_variations=1, image_size="1024x1024"):
    print(f"generate_image_with_openai: {prompt}")
    # Set OpenAI API key
    openai.api_key = api_key

    # Create a client instance
    client = openai.OpenAI(api_key=api_key)

    # Assuming original_image_data is raw bytes
    # Encode it in base64 for the API request
    image_data_b64 = b64encode(original_image_data).decode('utf-8')


    try:
        # Call the new API method to generate image variations based on the prompt
        print("callapi")
        response = client.images.generate(
            #image=image_data_b64,
            prompt=prompt,
            model="dall-e-3", # Default model, change as needed
            n=num_variations,
            size=image_size,
            response_format="b64_json"
        )
        
        for i in response.data:
            if i.b64_json:
                print(i.revised_prompt)
                return b64decode(i.b64_json)

        return None


    except Exception as e:
        print(f"Error in generating images: {e}")
        return None

def save_data_to_database(title, description, original_image_data, generated_image_data):
    print("save_data_to_database")
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    # Insert new data
    cursor.execute('''
        INSERT INTO stories (title, description, original_image, generated_image)
        VALUES (?, ?, ?, ?)
    ''', (title, description, original_image_data, generated_image_data))


    # Commit changes and close connection
    connection.commit()
    connection.close()




def fetch_latest_story():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT * FROM stories ORDER BY id DESC LIMIT 1')
        data = cursor.fetchone()

        if not data:
            # No data found, call fetch_and_generate to get new data
            fetch_and_generate()
            # Query the database again
            cursor.execute('SELECT * FROM stories ORDER BY id DESC LIMIT 1')
            data = cursor.fetchone()

        if data:
            encoded_image = base64.b64encode(data[4]).decode('utf-8') if data[4] else None

            return {
                'title': data[1],
                'description': data[2],
                'original_image': data[3],
                'generated_image':encoded_image
            }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

    # Default return if no data or in case of an error
    return {
        'title': 'No Data Available',
        'description': 'No description available',
        'original_image': None,
        'generated_image': None
    }
    
print("start")
initialize_database()
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_generate, trigger="cron", hour=5)
scheduler.start()


@app.route('/')
def index():
    data = fetch_latest_story()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    
    app.run(debug=True)
