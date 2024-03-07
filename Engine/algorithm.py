# libraries for AI
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# module used to get images
import requests

# reading dataset of movies
df = pd.read_csv("movie_dataset.csv")


# Setting attributes as "content" to describe better a movie
def combine_features(row):
    return row['keywords'] +" "+ row['cast'] +" "+ row["genres"] +" "+ row["director"]

# dealing with missing data
def missingdata():

    features    = ['keywords','cast','genres','director']

    for feature in features:
        df[feature] = df[feature].fillna('')

# to get title based on an index
def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]

# to get index based on title
def get_index_from_title(title):
    return df[df.title == title]["index"].values[0]

# to get all tiles
def all_titles():

    return df["title"].tolist()

# working with images
def fetch_poster(title):

    # setting format to look for url
    title_format = ""
    for letter in title:

        if letter == " ":
            title_format += '+'
        else:
            title_format += letter

    # request to API for images
    try:

        # to get ID of a movie
        url         = "http://api.themoviedb.org/3/search/movie?api_key=[personal_api_key_from_tmd]&language=en-US&query={}".format(title_format)
        data        = requests.get(url)
        data        = data.json()
        title_id    = data["results"][0]["id"]

        # to get POSTER of a movie
        url         = "https://api.themoviedb.org/3/movie/{}?api_key=person_key_from__&language=en-US".format(title_id)
        data        = requests.get(url)
        data        = data.json()
        poster_path = data['poster_path']
        full_path   = "https://image.tmdb.org/t/p/w500/"+ poster_path
    
    except:

        # covered in html
        full_path   = None

    return full_path

# to get many elements that become a part of an answer in list format
def getting_list(attribute,movie_title):

    # selecting correct movie and attributes
    movie_csv = df.query(f'title == "{movie_title}"')
    csv_data  = movie_csv[attribute].to_list()[0] # "a1 a2 a3 ... an"
    list      = []
    element   = ""

    # setting format from a string 
    for letter in csv_data:

        if letter != " ":

            element += letter 
        
        else:

            list.append(element)
            element = ""
        
        if letter == csv_data[-1] :

            list.append(element)

    return list

# information of the movie selected by user to use as base for next recomendations
def selected(movie_title):

    # data to show of selected movie
    selected_movie = {
        "title": None,
        "synapsis": None,
        "image": None,
        "genres": None,
        "keywords": None,
        "cast": None,
        "director": None,
        "rating": None,
    }

    # one element as answer
    selected_movie["title"]     = movie_title
    selected_movie["image"]     = fetch_poster(movie_title)
    selected_movie["synapsis"]  = df.query(f'title == "{movie_title}"')["overview"].to_list()[0]

    # n elements as answer
    selected_movie["genres"]    = getting_list("genres",movie_title)
    selected_movie["keywords"]  = getting_list("keywords",movie_title)
    selected_movie["cast"]      = getting_list("cast",movie_title)
    selected_movie["director"]  = getting_list("director",movie_title)

    # logic to get stars rating  
    # 0 -> no color in star
    # 1 -> color in star
    rating_punctuation          = round(df.query(f'title == "{movie_title}"')["vote_average"].to_list()[0])
    selected_movie["rating"]     = [0 for i in range(0,10)] 
    for i in range(0,rating_punctuation):

        selected_movie["rating"][i] = 1

    return selected_movie

# to generate recomendation
def recommend(movie_title):

    # cleaning csv
    missingdata()

    # setting "content"
    df["combined_features"] = df.apply(combine_features,axis=1)

    # to calculate similar movies to selected one
    cv              = CountVectorizer()
    count_matrix    = cv.fit_transform(df["combined_features"])
    cosine_sim      = cosine_similarity(count_matrix) # [ [1, 0.9, .03, .05 ...] , [0.01, 1, 0.2, 0.03 ... ] , ... ]

    movie_index             = get_index_from_title(movie_title)
    similar_movies          = list(enumerate(cosine_sim[movie_index])) # [ [index, similarity] , .... ]
    sorted_similar_movies   = sorted(similar_movies,key=lambda x:x[1],reverse=True)[1:]

    i=0
    recomendations      = []    
    for element in sorted_similar_movies:
 
        index       = element[0]
        similarity  = round(element[1], 2)

        recomendations.append({
            "title": get_title_from_index(index),
            "image": fetch_poster(get_title_from_index(index)),
            "percetange": round(similarity * 100)
        })

        i=i+1
        if i>=5:
            break
    
    return recomendations
