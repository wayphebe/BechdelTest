import unittest
from final import *


class TestData(unittest.TestCase):
    def test_access(self):
        results = get_movies()

        self.assertEqual(type(results[0]), list)

    def test_class(self):
        try:
            imdbmovie('English', 'US', 8.1, '$216,900,000', 1,None)
        except:
            self.fail()


class TestDatabase(unittest.TestCase):

    def test_bechtel_table(self):
        conn = sqlite3.connect('movies.sqlite')
        cur = conn.cursor()

        sql = 'SELECT Title FROM BechdelTest'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Cinderella',), result_list)
        self.assertEqual(len(result_list), 8286)

        sql = '''
            SELECT Rating, Title
            FROM BechdelTest
            WHERE Rating = 1
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 1821)
        self.assertEqual((result_list[0][0]), 1)
       

        conn.close()

    def test_top_table(self):
        conn = sqlite3.connect('movies.sqlite')
        cur = conn.cursor()

        sql = '''
            SELECT id, MovieTitle
            FROM Top250IMDBMovies
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((2, 'Inception'), result_list)
        self.assertEqual(len(result_list), 242)

        conn.close()
    
    def test_imdb_table(self):
        conn = sqlite3.connect('movies.sqlite')
        cur = conn.cursor()

        sql = '''
                SELECT id, Language
                FROM Top250IMDBMoviesdetail
            '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((1, 'English'), result_list)
        self.assertEqual(len(result_list), 242)

        conn.close()
    
class dataviz(unittest.TestCase):

    def test_trend(self):
        try:
            process_command_trend()
        except:
            self.fail()
    
    def test_ratio(self):
        try:
            process_command_ratio('2000')
        except:
            self.fail()
    
    def test_rating(self):
        try: 
            process_command_rating()
        except:
            self.fail()

    def test_fail(self):
        try: 
            process_command_fail()
        except:
            self.fail()

    # def test_show_nearby_map(self):
    #     site1 = NationalSite('National Monument',
    #         'Sunset Crater Volcano', 'A volcano in a crater.')
    #     site2 = NationalSite('National Park',
    #         'Yellowstone', 'There is a big geyser there.')
    #     try:
    #         plot_nearby_for_site(site1)
    #         plot_nearby_for_site(site2)
    #     except:

if __name__ == "__main__":
	unittest.main(verbosity=2)