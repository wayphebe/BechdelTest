import json
import requests
import sqlite3
from bs4 import BeautifulSoup
import plotly
import plotly.graph_objs as go
from secret import API_KEY
import matplotlib.pyplot as plt



# import plotly.express as px

# cache
CACHE = 'bechdeltest_cache.json'
try:
    cache = open(CACHE, 'r')
    cachecontents = cache.read()
    CACHEDICTION = json.loads(cachecontents)
    cache.close()

except:
    CACHEDICTION = {}


def params_combination(baseurl):
    return baseurl


def bechdelmovies_using_cache(baseurl):
    unique_ident = params_combination(baseurl)
    if unique_ident in CACHEDICTION:
        # print("Getting cached data...")
        return CACHEDICTION[unique_ident]
    else:
        print("Making a request for new data...")
        resp = requests.get(baseurl)
        CACHEDICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHEDICTION)
        fw = open(CACHE, "w")
        fw.write(dumped_json_cache)
        fw.close()  # Close the open file
        return CACHEDICTION[unique_ident]


# ---------------------------------------------
CACHE2 = 'omdb_cache.json'
try:
    cache2 = open(CACHE2, 'r')
    cachecontents2 = cache2.read()
    CACHEDICTION2 = json.loads(cachecontents2)
    cache2.close()

except:
    CACHEDICTION2 = {}


def params_combination2(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}={}".format(k, params[k]))
    return baseurl + "&".join(res)


def omdb_using_cache(baseurl, params):
    unique_ident = params_combination2(baseurl, params)
    if unique_ident in CACHEDICTION2:
        # print("Getting cached data...")
        return CACHEDICTION2[unique_ident]
    else:
        print("Making a request for new data...")
        resp = requests.get(baseurl, params)
        CACHEDICTION2[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHEDICTION2)
        fw = open(CACHE2, "w")
        fw.write(dumped_json_cache)
        fw.close()  # Close the open file
        return CACHEDICTION2[unique_ident]


# ---------------------------------------------
CACHE_FNAME = 'topcache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}


def get_unique_key(url):
    return url


def make_request_using_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME, "w")
        fw.write(dumped_json_cache)
        fw.close()  # Close the open file
        return CACHE_DICTION[unique_ident]

# Part 1 Data Sources
# source 1 bechdeltest api: https://bechdeltest.com/api/v1/doc#getMovieByImdbId


def get_movies():
    findmovies_url = "http://bechdeltest.com/api/v1/getAllMovies"
    # params_diction = {}
    # params_diction["title"] = movie_title
    places = bechdelmovies_using_cache(findmovies_url)
    IMDBid = []
    Bechdelid = []
    Year = []
    Title = []
    Rating = []

    with open('bechdeltest_cache.json') as json_file:
        data = json.load(json_file)
    for i in data['http://bechdeltest.com/api/v1/getAllMovies']:
        IMDBid.append(i["imdbid"])
        Bechdelid.append(i["id"])
        Year.append(i["year"])
        Title.append(i["title"])
        Rating.append(i["rating"])
    return IMDBid, Bechdelid, Year, Title, Rating

# print(get_movies()[1])


# source 2 openmoviedatabase api : http://www.omdbapi.com/
class imdbmovie():
    def __init__(self, language, country, imdbrating, boxoffice, imdbid, awards = None):
        self.language = language
        self.country = country
        self.imdbrating = imdbrating
        self.boxoffice = boxoffice
        self.awards = awards
        self.imdbid = imdbid
    def __str__(self):
        info = self.language + ' '+self.country + ' '+self.imdbrating + ' '+self.boxoffice + ' '+self.awards
        return info

def get_ombd(id):
    findomdb_url = "http://www.omdbapi.com/?"
    params_diction = {}
    params_diction["apikey"] = API_KEY
    params_diction["i"] = id
    places = omdb_using_cache(findomdb_url, params_diction)
    obj = imdbmovie(places['Language'], places['Country'], places['imdbRating'], places['BoxOffice'], places['imdbID'])
    return obj

# print (get_ombd('tt0892769'))
# source 3 single page scraping: https://bechdeltest.com/top250/


def get_top250():
    url = 'https://bechdeltest.com/top250/'
    souptext = make_request_using_cache(url)
    soup = BeautifulSoup(souptext, 'html.parser')
    bscontent = soup.find_all(class_="movie")
    Bechdelid = []
    Title = []
    IMDBid = []
    TestReustl = []
    Detail = []
    for i in bscontent:
        Bechdelid.append(int(i.find_all('a')[1]['id'][6:]))
        Title.append(i.find_all('a')[1].string)
        IMDBid.append(i.find('a')['href'][25:-1])
        if i.find('img')['src'][8] == 'n':
            TestReustl.append("This movie does not pass the BechdelTest")
        else:
            TestReustl.append('This movie pass the BechdelTest')
        Detail.append(i.find('img')['title'])
    objlst = []
    for i in IMDBid:
        objlst.append(get_ombd(i))
    return Bechdelid, Title, IMDBid, TestReustl, Detail, objlst

# get_top250()

# Part 2 Data Aceess and Storage


def init_db():
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'BechdelTest';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Top250IMDBMovies';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Top250IMDBMoviesdetail';
    '''
    cur.execute(statement)

    conn.commit()

    statement = '''
        CREATE TABLE 'BechdelTest' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'IMDBid' INTEGER NOT NULL,
            'Bechdelid' INTEGER NOT NULL,
            'Year' INTEGER NOT NULL,
            'Title' TEXT,
            'Rating' Integer
        );
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE Top250IMDBMovies (
		Id INTEGER PRIMARY KEY AUTOINCREMENT,
		Bid INTEGER NOT NULL,
		MovieTitle TEXT NOT NULL,
		IMDBid TEXT NOT NULL,
		TestResult TEXT,
		Detail TEXT,
        FOREIGN KEY (Bid) REFERENCES BechdelTest(Id)
		); 
    '''
    
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE Top250IMDBMoviesdetail(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Language TEXT,
            Country TEXT,
            imdbRating INTEGER,
            Boxoffice INTEGER,
            imdbid INTEGER,
            FOREIGN KEY (imdbid) REFERENCES Top250IMDBMoviest(Id)
		); 
    '''

    cur.execute(statement)
    conn.commit()
    conn.close()


init_db()


def insert_stuff():
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()

    delete_stmt = 'DELETE FROM BechdelTest'
    cur.execute(delete_stmt)
    conn.commit()

    insert_data1 = get_movies()
    IMDBid = insert_data1[0]
    Bechdelid = insert_data1[1]
    Year = insert_data1[2]
    Title = insert_data1[3]
    Rating = insert_data1[4]

    for i in range(len(Bechdelid)):
        insertion = (None, IMDBid[i], Bechdelid[i],
                     Year[i], Title[i], Rating[i])
        statement = 'INSERT INTO "BechdelTest"'
        statement += 'VALUES(?,?,?,?,?,?)'
        cur.execute(statement, insertion)
    conn.commit()

    return_dict = {}
    result = cur.execute("select Bechdelid, ID from BechdelTest")
    for i in result:
        return_dict[(i[0])] = i[1]


    insert_data2 = get_top250()

    Bechdelid2 = insert_data2[0]
    Title2 = insert_data2[1]
    IMDBid2 = insert_data2[2]
    TestResult = insert_data2[3]
    Detail = insert_data2[4]

    

    delete_stmt = "DELETE FROM TOP250IMDBMovies"
    cur.execute(delete_stmt)
    conn.commit()

    for i in range(len(Bechdelid2)):
        insertion = (None, return_dict[Bechdelid2[i]],
        Title2[i], IMDBid2[i], TestResult[i], Detail[i])
        statement = 'INSERT INTO "TOP250IMDBMovies"'
        statement += 'VALUES(?,?,?,?,?,?)'
        cur.execute(statement, insertion)

    conn.commit()

    
    detailinfo = insert_data2[5]
    language = []
    count = []
    imdbrating = []
    box = []
    imdbid = []
    
    for i in detailinfo:
        language.append(i.language)
        count.append(i.country)
        imdbrating.append(i.imdbrating)
        box.append(i.boxoffice)
        imdbid.append(i.imdbid)
    
    return_dict2 = {}
    result2 = cur.execute("select IMDBid, ID from TOP250IMDBMovies")
    for i in result2:
        return_dict2[(i[0])] = i[1]


    
    delete_stmt = "DELETE FROM TOP250IMDBMoviesdetail"
    cur.execute(delete_stmt)
    conn.commit()


    for i in range(len(count)):
        insertion = (None, language[i], count[i], imdbrating[i], (box[i]), return_dict2[imdbid[i]])
        statement = 'INSERT INTO "TOP250IMDBMoviesdetail"'
        statement += 'VALUES(?,?,?,?,?,?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()


insert_stuff()


# Part 3 Data Processing

def process_command_year(YEAR):
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()
    # COMMAND YEAR
    statement = '''SELECT Title
    FROM BechdelTest
    WHERE Rating = 3 AND Year = ''' + YEAR
    
    results = cur.execute(statement)
    conn.commit()
    results = results.fetchall()
    ls = []
    for i in results:
        ls.append(i[0]) 
    n = 1
    for i in ls:
        n = n+1
        print(n)
        print (i)
        print ("-----------")
    conn.close()
    return  ls

def process_command_trend():
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()
    statement = ''' SELECT COUNT(ID), Year
    FROM BechdelTest
    Where rating = 3
    GROUP BY Year
    ORDER By Year DESC
    '''
    results = cur.execute(statement)
    conn.commit()
    results = results.fetchall()
    conn.close()
    ploty = []
    plotx = []
    for i in results:
        ploty.append(i[0])
        plotx.append(i[1])

    plt.ioff()

    plt.plot(plotx, ploty)
    plt.ylabel('Numbers of moview pass the Bechdeltest')
    plt.xlabel('Year')
    # plt.draw()


    plt.show()

    
# process_command_trend()

def process_command_ratio(Year):
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()
    statement = ''' SELECT COUNT(ID), Rating
    From BechdelTest
    Where Year = 
    ''' + Year + ''' Group by Rating'''
    cur.execute(statement)
    conn.commit()
    # results.fetchall()
    num = []
    for i in cur:
        num.append(i[0])
    labels = 'score0 complete fail', 'score1 has at least two women character', 'score2 they have conversation', 'score3 complete pass'
    sizes = [num[0], num[1], num[2], num[3]]
    explode = (0.1, 0, 0, 0)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode = explode, labels= labels, autopct = '%1.1f%%', shadow = False, startangle = 90)
    ax1.axis = ('equal')
    plt.show()
    
def process_command_rating():
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()
    statement = ''' SELECT   imdbRating
    from Top250IMDBMoviesdetail
    '''
    results = cur.execute(statement)
    conn.commit()
    results = results.fetchall()
    conn.close()
    ploty = []
    # plotx = []
    for i in results:
        ploty.append(i[0])
        # plotx.append(i[1])

    plt.ioff()

    plt.plot(ploty)
    plt.ylabel('Rating')
    plt.xlabel('distance')
    # plt.draw()


    plt.show()

# process_command_rating()

def process_command_fail():
    conn = sqlite3.connect('movies.sqlite')
    cur = conn.cursor()
    statement = ''' SELECT COUNT(ID), Year
    FROM BechdelTest
    Where rating = 0
    GROUP BY Year
    ORDER By Year DESC
    '''
    results = cur.execute(statement)
    conn.commit()
    results = results.fetchall()
    conn.close()
    ploty = []
    plotx = []
    for i in results:
        ploty.append(i[0])
        plotx.append(i[1])

    plt.ioff()

    plt.plot(plotx, ploty)
    plt.ylabel('Numbers of moview fail the Bechdeltest')
    plt.xlabel('Year')
    # plt.draw()


    plt.show()

# process_command_fail()



def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response.lower() != 'exit':
        response = input ('Enter a command, "help", or "exit": ')
        command = response.split()
        if response.lower()== 'help':
            print(help_text)
            continue
        elif response.lower() == 'exit':
            print ('Thanks for your visit. See you next time.')
            break
        
        if command[0] =='year':
            process_command_year(command[1])

        if command[0] == 'trend':
            process_command_trend()
        
        if command[0] == 'ratio':
            process_command_ratio(command[1])

        if command[0] == 'rating':
            process_command_rating()

        if command[0] == 'fail':
            process_command_fail()
           
    

if __name__ == "__main__":
    interactive_prompt()