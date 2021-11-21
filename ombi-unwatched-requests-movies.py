import os
import requests
import json
from collections import Counter

# sudo apt update
# sudo apt install python3 python3-pip
# sudo python3 -m pip install plexapi


# OMBI vars
# http://192.168.1.10:3579/swagger/index.html
# export OMBI_API_KEY=
ombi_api_key = os.environ['OMBI_API_KEY']
ombi_api_url = 'http://192.168.1.10:3579/api/v1/'
ombi_headers = {'ApiKey': ombi_api_key, 'accept': 'application/json' }

# Plex vars
# https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
# export X_Plex_Token=
plex_token = os.environ['X_Plex_Token']
plex_api_url = 'http://192.168.1.10:32400/library/'

# from plexapi.server import PlexServer
# baseurl = 'http://192.168.1.10:32400'
# token = ''
# plex = PlexServer(baseurl, token)

# Tautulli vars
# export TAUTULLI_APIKEY=
tautulli_api_url = 'http://192.168.1.10:8282/api/v2'
tautulli_apikey = os.environ['TAUTULLI_APIKEY']
tautulli_params = {}

#Tautulli
def tautulli_search(title, user):
    watched_status = 0
    tautulli_params = {'apikey': tautulli_apikey, 'cmd': 'get_history', 'media_type': 'movie', 'search': title, 'include_activity': 1, 'user': user}
    results = requests.get(tautulli_api_url, params=tautulli_params)
    # print(results.text)
    results_json = results.json()
    histories = results_json.get('response').get('data').get('data')
    for history in histories:
        # print(watched_status)
        # print(history.get('watched_status'))
        if watched_status < history.get('watched_status'):
            watched_status = history.get('watched_status')
        # print(history.get('watched_status'))
    return watched_status    


# Get All Requests from OMBI
url = ombi_api_url + "Request/movie"
requests_movies = requests.get(url, headers=ombi_headers)
requests_movies_json = requests_movies.json()
# print(requests_movies)

request_data = []

x = 1
for request in requests_movies_json:
    #if x < 15 and request.get('available'):
    if request.get('available'):
        # print(request.get('title'))
        requestedTitle = request.get('title')
        requestedUser = request.get('requestedUser').get('userName')
        # print(request.get('requestedUser').get('userName'))
        # print(request)
        # print("requestedTitle: " + str(requestedTitle))
        # print("requestedUser: " + str(requestedUser))
        watched_status = tautulli_search(requestedTitle, requestedUser)
        data = {'title': requestedTitle, 'userName': requestedUser, 'watched_status': watched_status }
        # print(watched_status)
        request_data.append(data)
    x += 1

print("request_data: ")
print(request_data)
user_counts = {}
for request in request_data:
    user = request.get('userName')
    try:
        user_counts[user] += 1
    except KeyError:
        user_counts[user] = 1
print("")
print("user_counts: " + str(user_counts))
print("")


users = {}
for item in range(len(request_data)):
    if request_data[item]['userName'] not in users:
        users[request_data[item]['userName']] = []
    users[request_data[item]['userName']].append({'title': request_data[item]['title'], 'watched_status': request_data[item]['watched_status']})

# print(users)
for user in users:
    watch_count = 0
    unwatched_movies = []
    print(user)
    # print(users[user])
    for i in users[user]:
        if i.get('watched_status') == 1:
            watch_count += 1
        else:
            unwatched_movies.append(i.get('title'))

    if len(unwatched_movies) > 0:
        print("Unwatched_Movies: ")
        for i in unwatched_movies:
            print("  " + str(i))
    print("Watch_Count: " + str(watch_count))
    request_total  = len(users[user])
    print("Request_Total: " + str(request_total))
    watch_perc = round((watch_count / request_total) * 100,1)
    print("Watched_Percentage: " + str(watch_perc) + "%")
    print("")
    # print(len(user))


# Plex
url = plex_api_url + "sections/"
plex_params = { 'X-Plex-Token': plex_token }
# plex = requests.get(url, params=plex_params)
# print(plex.text)

# movie = plex.library.section('Movies').get('The Meg')
# history = movie.history(maxresults=9999)
# print(movie)
# print(history)


