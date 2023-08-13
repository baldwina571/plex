import requests
import json
import urllib.parse
import time
import datetime
import re
import requests
from unidecode import unidecode

server_ip = '192.168.1.155'
sonarr_port = '9999'
radarr_port = '8310'
sonarr_endpoint = '/api/v3/series'
sonarr_api_key = '49992782350e4674ab8178bb2043c53b'
radarr_api_key = '486258e862f646438f6e58ce7a800e42'
themoviedb_api_key_v3 = '05ebc0015f05f55dfc28572481f18e26'
themoviedb_api_key_v4 = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwNWViYzAwMTVmMDVmNTVkZmMyODU3MjQ4MWYxOGUyNiIsInN1YiI6IjYzZTE3N2M3MzY3OWExMDA3ZjhmYzAxYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.7qDlIvbUbglJ5Xvwo0_rpKr5nGs-rXtOdZV54m7xyZg'

#Identify show genres
def tv_genres():
    result = requests.get(f'https://api.themoviedb.org/3/genre/tv/list?api_key=05ebc0015f05f55dfc28572481f18e26').text
    print(result)

#Get the shows currently on Sonarr
def get_shows():
    shows_json = requests.get(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}', headers={"X-Api-Key": sonarr_api_key}).text
    shows = json.loads(shows_json)
    for show in shows:
        try:
            try:
                year = re.findall('[\d]{4}', show['firstAired'])[0]
            except:
                year = 0
            show_rating(re.sub('\([\d\w]+\)$', '', show['title']), show['id'], show['monitored'], year)
            #print(f"{show['title']}, {show['monitored']}, {show['id']}")
            time.sleep(0.15)
        except:
            print(f'{show["title"]} fucked up')

def delete_show(show_id):
    shows_json = requests.get(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
    show = json.loads(shows_json)
    quality = show["qualityProfileId"]
    seriesType = show["seriesType"]
    seasonFolder = show["seasonFolder"]
    rootFolderPath = show["rootFolderPath"]
    tags = show["tags"]
    load = f'"seriesIds": [{show_id}], "monitored": false, "qualityProfileId": {quality}, "seriesType": "{seriesType}", "seasonFolder": true, "rootFolderPath": "{rootFolderPath}", "tags": {tags}, "applyTags": "add", "moveFiles": true, "deleteFiles": true, "addImportListExclusion": true'
    load = "{"+load+"}"
    #print(load)
    result = requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/editor', headers={"X-Api-Key": sonarr_api_key}, data=load)
    print(result)

def show_exclusion(tvdbId, title, id):
    exclusion_endpoint = "/api/v3/importlistexclusion"
    #title = urllib.parse.quote_plus(title)
    load = f'"id": 0, "tvdbId": "{tvdbId}", "title": "{title}"'
    load = "{" + load + "}"
    print(load)
    get_result = requests.post(f'http://{server_ip}:{sonarr_port}{exclusion_endpoint}', headers={"X-Api-Key": sonarr_api_key, "Content-Type": "application/json; Charset=UTF-8"}, data=load)
    print(get_result.status_code)
    #print(get_result.text)
    time.sleep(0.2)

#Gets info about show from TMDB
def show_rating(show_name, show_id, monitored, year):
    encoded_show = urllib.parse.quote_plus(show_name)
    result = requests.get(f'https://api.themoviedb.org/3/search/tv?api_key=05ebc0015f05f55dfc28572481f18e26&language=en-US&query={encoded_show}&page=1&include_adult=false&first_air_date_year={year}')
    show_json = json.loads(result.text)
    if len(show_json["results"]) == 0:
        result = requests.get(
            f'https://api.themoviedb.org/3/search/tv?api_key=05ebc0015f05f55dfc28572481f18e26&language=en-US&query={encoded_show}&page=1&include_adult=false')
        show_json = json.loads(result.text)
    try:
        show = show_json["results"][0]
        name = show["original_name"]
        rating = show["vote_average"]
        votes = show["vote_count"]
        popularity = show["popularity"]
        genres = show["genre_ids"]
        tvdbId = show["id"]
        if 99 in genres:
            pass
        elif rating < 6.0:
            print(f'FAILURE {name}: Rating too low')
            print(
                f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #show_exclusion(tvdbId, name, show_id)
            delete_show(show_id)
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
        elif votes < 1:
            print(f'FAILURE {name}: Too few votes')
            print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
            delete_show(show_id)
        elif 10762 in genres:
            print(f'FAILURE {name}: Kids genre')
            print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
            delete_show(show_id)
        elif 10764 in genres:
            print(f'FAILURE {name}: Reality show')
            print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
            #delete_show(show_id)
        elif 10767 in genres:
            print(f'FAILURE {name}: Talk show')
            print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
            delete_show(show_id)
        elif 10766 in genres:
            print(f'FAILURE {name}: Soap show')
            print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
            delete_show(show_id)
        elif 10763 in genres:
            print(f'FAILURE {name}: News')
            print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
            #requests.delete(f'http://{server_ip}:{sonarr_port}{sonarr_endpoint}/{show_id}', headers={"X-Api-Key": sonarr_api_key}).text
            #show_exclusion(tvdbId, name, show_id)
            delete_show(show_id)
        else:
            pass
            #print(f'SUCCESS {name}')
            #print(f'name: {name}, rating: {rating}, votes: {votes}, popularity: {popularity}, id: {show_id}, monitored: {monitored}, year: {year}')
    except:
        print(f'"{show_name}", id: {show_id}, from {year} not found')

#==================================== MOVIES


def movie_genres():
    result = requests.get(f'https://api.themoviedb.org/3/genre/movie/list?api_key=05ebc0015f05f55dfc28572481f18e26').text
    print(result)

def get_movies():
    radarr_endpoint = '/api/v3/movie'
    movies_json = requests.get(f'http://{server_ip}:{radarr_port}{radarr_endpoint}',
                              headers={"X-Api-Key": radarr_api_key}).text
    movies = json.loads(movies_json)
    with open('good_movies.txt') as good_movies:
        good_movies_list = good_movies.read().splitlines()
    for movie in movies:
        try:
            release_date = movie["inCinemas"]
            release_year = int(re.findall('[\d]{4}', f'{release_date}')[0])
            release_month = int(re.findall('-([\d]{2})-', f'{release_date}')[0])
            release_day = int(re.findall('-([\d]{2})T', f'{release_date}')[0])
            release_epoch = datetime.datetime(release_year, release_month, release_day, 0, 0).timestamp()
            today = time.time()
            release_delta = (today - release_epoch) / 60 / 60 / 24
        except:
            release_delta = 100
            release_date = year
        try:
            title = movie["title"]
            id = movie["id"]
            tmdbId = movie["tmdbId"]
            imdb_votes = movie["ratings"]["imdb"]["votes"]
            imdb_score = movie["ratings"]["imdb"]["value"]
            year = movie["year"]
            genre = movie["genres"]
            exempt_movies = ['A Star Is Born', '8 Mile', 'Bohemian Rhapsody', 'Whiplash', 'Rocketman', 'Marley']
            if title in exempt_movies or release_delta < 90 or title in good_movies_list:
                #print(f'{title} is a new movie released {release_date}')
                pass
            elif imdb_score <= 6.3:
                print("Rating too low")
                print(f'{title} - id: {id} - votes: {imdb_votes} - score: {imdb_score} - year: {year}')
                #print(movie["genres"])
                movie_exclusion(id, tmdbId, title, year)
                delete_movie(id)
            elif "Music" in genre:
                print(f'{title} is Music genre')
                movie_exclusion(id, tmdbId, title, year)
                delete_movie(id)
            elif "TV Movie" in genre:
                print(f'{title} is TV genre')
                movie_exclusion(id, tmdbId, title, year)
                delete_movie(id)
            elif "Romance" in genre and len(genre) == 1:
                print(f'{title} is Romance genre')
                movie_exclusion(id, tmdbId, title, year)
                delete_movie(id)
            else:
                #print(f'{title} - id: {id} - votes: {imdb_votes} - score: {imdb_score} - year: {year}')
                with open('good_movies.txt','a') as good_movies:
                    good_movies.write(f'{title}\n')
        except:
            if release_delta < 90:
                #print(f'{title} is a new movie released {release_date}')
                pass
            else:
                pass
                print(f'{movie["title"]} year: {year} delta = {release_delta} fucked up')
                #print(movie["genres"])
                movie_exclusion(tmdbId, title, year)
                delete_movie(id)


def delete_movie(movie_id):
    try:
        radarr_endpoint = '/api/v3/movie'
        movie_json = requests.get(f'http://{server_ip}:{radarr_port}{radarr_endpoint}/{movie_id}',
                                  headers={"X-Api-Key": radarr_api_key}).text
        movie = json.loads(movie_json)
        quality = movie["qualityProfileId"]
        rootFolderPath = unidecode(movie["path"])
        tags = movie["tags"]
        load = f'"movieIds": [{movie_id}], "monitored": false, "qualityProfileId": {quality}, "minimumAvailability": "tba", "rootFolderPath": "{rootFolderPath}", "tags": {tags}, "applyTags": "add", "moveFiles": true, "deleteFiles": true, "addImportListExclusion": true'
        load = "{" + load + "}"
        result = requests.delete(f'http://{server_ip}:{radarr_port}/api/v3/movie/editor', headers={"X-Api-Key": radarr_api_key, "Content-Type": "application/json; Charset=UTF-8"}, data=load)
        print(result.status_code)
    except:
        pass

def movie_exclusion(id, tmdbid, title, year):
    try:
        title = urllib.parse.quote_plus(title)
        exclusion_endpoint = "/api/v3/exclusions/"
        #title = urllib.parse.quote_plus(title)
        load = f'"id": {id}, "movieTitle": "{title}", "movieYear": {year}'
        load = "{" + load + "}"
        get_result = requests.post(f'http://{server_ip}:{radarr_port}{exclusion_endpoint}', headers={"X-Api-Key": radarr_api_key, "Content-Type": "application/json; Charset=UTF-8"}, data=load)
        print(get_result.status_code)
        print(get_result.text)
        #result = requests.put(f'http://{server_ip}:{radarr_port}{exclusion_endpoint}/{movie_id}', headers={"X-Api-Key": radarr_api_key, "Content-Type": "application/json"}, data=load)
        time.sleep(60)
    except:
        pass
        print("Exclusion Failed")
        time.sleep(60)

def find_movies():
    exclude_genres = [10402, 10770]
    page = 1
    while page < 1000:
        top_movies = requests.get(
            f'https://api.themoviedb.org/3/movie/popular?api_key=05ebc0015f05f55dfc28572481f18e26&language=en-US&page={page}')
        show_json = json.loads(top_movies.text)
        results = show_json["results"]
        for movie in results:
            if 10402 in movie["genre_ids"] or 10770 in movie["genre_ids"]:
                break
            if movie["vote_count"] > 200 and movie["vote_average"] > 6.5:
                id = movie["id"]
                title = movie["title"]
                title = "Black Adam"
                print(f'{title}')
                load = f'"tmdbId": {id}, "title": "{title}", "monitored": true, "QualityProfileId": 4'
                load = "{" + load + "}"
                result = requests.post(f'http://{server_ip}:{radarr_port}/api/v3/movie',headers={"X-Api-Key": radarr_api_key, "Content-Type": "application/json; Charset=UTF-8"},data=load)
                print(result.text)
                break
        page += 1
        break




#movie_genres()

#get_movies()

#find_movies()

#one_show()

get_shows()

#delete_show()

#tv_genres()

#show_rating("Snitch","2564","true",2021)