from flask import Flask, request, render_template, jsonify
import json
import random
import requests
from dotenv import load_dotenv
import os 
from openai import OpenAI


app = Flask(__name__, static_url_path='/static')
load_dotenv()

moviedb_key = os.environ.get('moviedb_key')
openai_key = os.environ.get('openai_key')


client = OpenAI(api_key=openai_key)
model = "gpt-3.5-turbo"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + moviedb_key
}

#----------------- some helper functions ------------------# 

def get_tmdb_response(url):
    response = requests.get(url, headers=headers)
    response_data = json.loads(response.text)
    return response_data

#keep this here so that you can easily modify it in the future when 
#openai updates their api yet again
def get_gpt_response(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
                messages=messages,
                max_tokens=100).choices[0].message.content

    return response
#------------------------------------------------------------#

def get_movies(n, mainstream):
    """
    return a list of n movie_ids
    """

    #randomize between popular and top rated 
    option = random.randint(1,2)
    endpoints = {
        1: "top_rated",
        2: "popular"
    }

    #if user chose mainstream
    if mainstream == "1": 
        page_range = (1, 50)

    #if user chose surprise me 
    else:
        page_range = (51, 447) if option == 1 else (51, 500)

    page = random.randint(*page_range)
    url = f"https://api.themoviedb.org/3/movie/{endpoints[option]}?language=en-US&page={page}"
    response_data = get_tmdb_response(url)
    random_movies = random.sample(response_data["results"],n )    
    
    movie_ids = []
    for movie in random_movies:
        movie_ids.append(str(movie['id']))
    
    return movie_ids


def generate_description(movie_id, choice):
    '''generate blind date style description for movie_id based on choice
       1: description based on genre, overview, reviews, tagline (e.g. romance meets sci-fi, smalltown romcom)
       2: description mentions what actors are in movie (e.g. join xx and yy on an adventure)
       3: description based on similar movies (e.g. if you like xxx and yyy, you'll like this movie)
       4: description based on keywords of movie (e.g. fantasy world, motherhood, patriarchy)

    '''
    if choice in [1,2]:
        text = "" #this will be passed to chatgpt prompt

        #get reviews
        url = "https://api.themoviedb.org/3/movie/" + movie_id + "/reviews?language=en-US&page=1"
        review_data = get_tmdb_response(url)
        if review_data['results']: 
            for i in range(len(review_data['results'])):
                text += review_data['results'][i]['content']

        #get overview
        url = "https://api.themoviedb.org/3/movie/"+ movie_id+ "?language=en-US"
        overall_data = get_tmdb_response(url)
        for genre in overall_data['genres']:
            text += genre['name']
        text += overall_data['tagline']
        text += overall_data['overview']

        #generic description based on genre, overview, reviews, tagline 
        if choice == 1:
            prompt = f"generate a 'blind date with a book' description for this movie:\
                    \n\n{text}\n\n keep the description to maximum 10 words!!! Do NOT mention the movie's title."
            
        #description mentions what actors are in movie
        else:
            url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/credits?language=en-US"
            credits_data = get_tmdb_response(url)
            actors = credits_data['cast'][0]['name'] + " and " + credits_data['cast'][1]['name'] 
            prompt = f"generate a short description for this movie:\
                    \n\n{text}\n\n Do NOT mention the movie's title. Make sure to mention BOTH {actors} with their full names.\
                    Keep the description to maximum 10 words. "

        
        #give gpt the prompt and let it generate the description
        response = get_gpt_response(prompt)
    
    
    #description based on similar movies recommendations
    elif choice == 3:

        #recommendations movies endpoint
        url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/recommendations?language=en-US&page=1"
        recommend_data = get_tmdb_response(url)
        if len(recommend_data['results']) > 0:
            recommend_movie = recommend_data['results'][0]['title']
            year = "(" + recommend_data['results'][0]['release_date'][:4] + ")"
            response = f"If you like {recommend_movie} {year}, you'll like this movie" #include the year if possible so people have a better idea of the movie

        #similar movies endpoint
        else:
            url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/similar?language=en-US&page=1"
            recommend_data = get_tmdb_response(url)
            if len(recommend_data['results']) > 0:
                recommend_movie = recommend_data['results'][0]['title']
                response = f"If you like {recommend_movie}, you'll like this movie"
            
            else:
                #couldn't find any movies using both the above endpoints, default to description type 1
                response = generate_description(movie_id, choice = 1)
        
        
    #description based on movie keywords 
    elif choice == 4:
        url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/keywords"
        keywords_data = get_tmdb_response(url)

        #get a maximum of 4 keywords  
        keywords_response = random.sample(keywords_data['keywords'], min(4, len(keywords_data['keywords'])))

        response = ""
        for item in keywords_response:
            response += item['name'] + ", "
            
        if len(response) == 0:
            #couldn't find any keywords using the endpoint, default to description type 1
            response = generate_description(movie_id, choice=1)
        else:
            response = response[:-2]

    return response

def get_link(movie_id):
    '''get the watch provider links for movies'''

    url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/watch/providers"
    response_data = get_tmdb_response(url)

    #return the US providers link if available
    if "US" in response_data['results']:
        link = response_data['results']['US']['link']
    
    #if not, try a random other country_code
    else:
        try:
            random_country_code = random.choice(list(response_data['results'].keys()))
            link = response_data['results'][random_country_code]['link']

        #couldn't find any providers links, get the original movie title and return google search link
        except:
            url = "https://api.themoviedb.org/3/movie/"+movie_id+"?language=en-US"
            response_data = get_tmdb_response(url)
            original_title = response_data['original_title']
            link = f'https://www.google.com/search?q={original_title}%20movie'
    return link

@app.route('/generate_descriptions', methods=['GET'])
def get_random_descriptions():
    '''
        return 4 random blind date movie descriptions and their associated links
    '''
    mainstream = request.args.get('mainstream', 1, type=int)  # Default to 1 if not specified

    #stick to 4 movies for now, maybe change in the future
    movie_ids = get_movies(4, mainstream)
   
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
    return render_template('index.html')   


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)





