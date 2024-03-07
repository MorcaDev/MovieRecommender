# django libraries
from django.shortcuts import render

# own modules
from Engine.algorithm import all_titles,recommend,selected

# Create your views here.
def index(request):

    # Data from dataset to show at index
    data = {
        'titles': all_titles(),
        'selected_movie': None,
        'recomendations': None,
    }

    # identifying method
    request_method = request.method
    if request_method == "POST":
        
        # title selected in html
        title_seleceted = request.POST["movie_title"]

        # provide information of user's picked movie
        data["selected_movie"] = selected(title_seleceted)

        # generate recomendation based o previous selection
        data["recomendations"]  = recommend(title_seleceted)
        
    return render(request, 'index.html', data)