from flask import Flask
from flask import render_template
from flask import request, jsonify
app = Flask(__name__)
import json
from collections import defaultdict
import random
import requests



#for gpt
import openai

import secrets2
openai.api_key = secrets2.SECRET_KEY

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzM5YjYzNmM2MDE5OGE2YWNiZTBkOTE4YzU2MzJjNCIsInN1YiI6IjY1MzMwZjQzNjJlODZmMDBmZGU3YWQ0MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.aXi_0trGhG3FBBADLe3cheyAQanqsFTHsH3TJh5J3Qc"
}


def get_movies(n):
    """
    return a list of n movie_ids
    """
    #randomize between popular and top rated 
    option = random.randint(1,2)
    
    if option == 1: #top rated
        page = random.randint(1, 447)
        url = "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page="+str(page)
    else: #popular
        page = random.randint(1, 500)
        url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page="+str(page)
        
    response = requests.get(url, headers=headers)
    response_data = json.loads(response.text)
    
    random_movies = random.sample(response_data["results"],n )    
    
    movie_ids = []
    for movie in random_movies:
        movie_ids.append(str(movie['id']))
    
    return movie_ids


def generate_description(movie_id, choice):
    
    #generic description based on genre, overview, reviews, tagline 
    if choice in [1,2]:
        text = ""
        #get reviews
        url = "https://api.themoviedb.org/3/movie/" + movie_id + "/reviews?language=en-US&page=1"
        reviews = requests.get(url, headers=headers)
        review_data = json.loads(reviews.text)
        if review_data['results']: 
            for i in range(len(review_data['results'])):
                text += review_data['results'][i]['content']

        #get overview
        url = "https://api.themoviedb.org/3/movie/"+ movie_id+ "?language=en-US"
        overall = requests.get(url, headers=headers)
        overall_data = json.loads(overall.text)
        for genre in overall_data['genres']:
            text += genre['name']
        text += overall_data['tagline']
        text += overall_data['overview']
        if choice == 1:
            prompt = f"generate a 'blind date with a book' description for this movie:\
                    \n\n{text}\n\n keep the description to maximum 15 words. Do NOT mention the movie's title."

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=256
            )["choices"][0]["text"]
        else:
            url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/credits?language=en-US"

            credits_response = requests.get(url, headers = headers)
            credits_data = json.loads(credits_response.text)
            actors = credits_data['cast'][0]['name'] + " and " + credits_data['cast'][1]['name'] 
            prompt = f"generate a very short description for this movie:\
                    \n\n{text}\n\n Do NOT mention the movie's title. Make sure to mention BOTH {actors} with their full names.\
                    Keep the description to maximum 15 words. "

            response = openai.Completion.create(
                engine = "text-davinci-003",
                prompt = prompt,
                max_tokens=256
            )["choices"][0]["text"]
    
    
    #description based on movie recommendation 
    elif choice == 3:
        url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/recommendations?language=en-US&page=1"
        recommend_response = requests.get(url, headers=headers)
        recommend_data = json.loads(recommend_response.text)
        if len(recommend_data['results']) > 0:
            recommend_movie = recommend_data['results'][0]['title']
            year = "(" + recommend_data['results'][0]['release_date'][:4] + ")"
            response = f"If you like {recommend_movie} {year}, you'll like this movie"
        else:
            url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/similar?language=en-US&page=1"
            recommend_response = requests.get(url, headers=headers)
            recommend_data = json.loads(recommend_response.text)
            if len(recommend_data['results']) > 0:
                recommend_movie = recommend_data['results'][0]['title']
                response = f"If you like {recommend_movie}, you'll like this movie"
            
            else:
                response = generate_description(movie_id, choice = 1)
        
        
    #description based on movie keywords 
    elif choice == 4:
        url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/keywords"
        keywords_response = requests.get(url, headers = headers)
        keywords_data = json.loads(keywords_response.text)
        keywords_response = random.sample(keywords_data['keywords'], min(4, len(keywords_data['keywords'])))
        keywords_list = []
        response = ""
        
        for item in keywords_response:
            response += item['name'] + ", "
            
        if len(response) == 0:
            response = generate_description(movie_id, choice=1)
        
    response = response.replace('\n','')

    return response

def get_link(movie_id):
    url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/watch/providers"
    response = requests.get(url, headers=headers)
    response_data = json.loads(response.text)
    if "US" in response_data['results']:
        link = response_data['results']['US']['link']
    else:
        random_country_code = random.choice(list(response_data['results'].keys()))
        link = response_data['results'][random_country_code]['link']
    
    return link

@app.route('/generate_descriptions', methods=['GET'])
def get_random_descriptions():
    movie_ids = get_movies(4)
    
    choices = [1, 2, 3, 4]
    random_choices = random.sample(choices, len(choices))
    
    blind_descriptions = []
    links = []
    for movie_id, choice in zip(movie_ids, random_choices):
        blind_descriptions.append(generate_description(movie_id, choice))
        links.append(get_link(movie_id))
        
    # return blind_descriptions, links
    response = jsonify(blind_descriptions=blind_descriptions, links=links)
    return response

    

@app.route('/')
def home():
    return render_template('home.html')   


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




