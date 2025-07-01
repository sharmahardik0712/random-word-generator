import requests
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI()

# Mount static files (optional, for CSS/JS/images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


def dictionary(word):
    try:
        url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if data and len(data) > 0:
            return data[0]
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching dictionary data: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing dictionary response: {e}")
        return None


def random_word():
    try:
        url = 'https://random-word-api.herokuapp.com/word'
        response = requests.get(url)
        response.raise_for_status()

        word_data = response.json()
        if word_data and len(word_data) > 0:
            word = word_data[0]
            print(f"Random word: {word}")

            # Try to get dictionary data
            dict_data = dictionary(word)
            if dict_data:
                print(f"Found dictionary entry for: {word}")
                return dict_data
            else:
                print(f"No dictionary entry found for: {word}")
                # Try again with a new random word (max 3 attempts to avoid infinite recursion)
                return random_word()
        else:
            raise HTTPException(status_code=500, detail="No random word received")

    except requests.RequestException as e:
        print(f"Error fetching random word: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch random word")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# API endpoint for getting random word data (JSON)
@app.get("/api/word/random")
def get_random_word():
    return random_word()


# API endpoint for searching a specific word
@app.get("/api/word/{word}")
def search_word(word: str):
    dict_data = dictionary(word.lower().strip())
    if dict_data:
        return dict_data
    else:
        raise HTTPException(status_code=404, detail="Word not found in dictionary")


# Main route that serves the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Keep the old endpoints for backwards compatibility
@app.get("/api/word")
def get_random_word_old():
    return random_word()


@app.get("/word")
def get_word():
    return random_word()