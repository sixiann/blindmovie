# Blind Date with a Movie

🍿 Inspired by [Blind Date with a Book](https://blinddatewithabook.org/). It’s like a regular blind date where you don’t know what you’re getting until you get there. But, with movies! 🎥

Blind Date with a Movie is a Flask application that displays some random movies with blind date descriptions. When you click on a description, it reveals a link to the movie. The blind date descriptions are generated using the OpenAI API (GPT-3.5), and the movies are sourced from the TMDB API. 

## Live Demo

Check out the [**live demo**](https://blind-movie.vercel.app/). Netflix and chill?

## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python
- **HTML & CSS**: For structuring and styling the web pages
- **jQuery**: A fast, small, and feature-rich JavaScript library
- [**OpenAI API**](https://platform.openai.com/): Used for generating blind date descriptions
- [**TMDB API**](https://developer.themoviedb.org/reference/intro/getting-started): Used for fetching movie data

## Installation instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/sixiann/blindmovie.git
2. Navigate to project directory:
    ```bash
    cd blindmovie
3. Install the required dependencies using pip:
    ```bash
    pip install -r requirements.txt
4. Run the app:
    ```bash
    python server.py
5. Open your web browser and navigate to http://localhost:5000 to view the application.
