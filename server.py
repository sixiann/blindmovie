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

def get_movies(n, mainstream):
    """
    return a list of n movie_ids
    """

    #randomize between popular and top rated 
    option = random.randint(1,2)
    
    if option == 1: #top rated
        if mainstream == "1": 
            page = random.randint(1,50)
        else:
            page = random.randint(51, 447)
        url = "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page="+str(page)
    else: #popular
        if mainstream == "1": 
            page = random.randint(1,50)
        else:
            page = random.randint(51, 500)
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
                    \n\n{text}\n\n keep the description to maximum 10 words!!! Do NOT mention the movie's title."

            messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(model=model,
            messages=messages,
            max_tokens=100).choices[0].message.content


        else:
            url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/credits?language=en-US"

            credits_response = requests.get(url, headers = headers)
            credits_data = json.loads(credits_response.text)
            actors = credits_data['cast'][0]['name'] + " and " + credits_data['cast'][1]['name'] 
            prompt = f"generate a short description for this movie:\
                    \n\n{text}\n\n Do NOT mention the movie's title. Make sure to mention BOTH {actors} with their full names.\
                    Keep the description to maximum 10 words. "

            messages = [{"role": "user", "content": prompt}]

            response = client.chat.completions.create(model=model,
            messages=messages,
            max_tokens=100).choices[0].message.content
    
    
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
        else:
            response = response[:-2]
        
    # response = response.replace('\n','')

    return response

def get_link(movie_id):
    url = "https://api.themoviedb.org/3/movie/"+ movie_id + "/watch/providers"
    response = requests.get(url, headers=headers)
    response_data = json.loads(response.text)
    if "US" in response_data['results']:
        link = response_data['results']['US']['link']
    else:
        try:
            random_country_code = random.choice(list(response_data['results'].keys()))
            link = response_data['results'][random_country_code]['link']
        except:
            url = "https://api.themoviedb.org/3/movie/"+movie_id+"?language=en-US"
            response = requests.get(url, headers=headers)
            response_data = json.loads(response.text)
            original_title = response_data['original_title']
            link = f'https://www.google.com/search?q={original_title}%20movie'
    return link

@app.route('/generate_descriptions', methods=['GET'])
def get_random_descriptions():
    mainstream = request.args.get('mainstream', 1, type=int)  # Default to 1 if not specified
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





