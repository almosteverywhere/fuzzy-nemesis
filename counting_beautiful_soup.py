#!/usr/bin/python

from bs4 import BeautifulSoup
from collections import Counter
import re, os, sys

# Where our data be at? Sorry, I couldn't help myself. 
basedir = "/Users/julielavoie/PycharmProjects/saymyname/files/"
default_artist = "Kanye-west"
default_dir = basedir + default_artist
# Pardon the swearing
bad_words = ['bitch','ho', 'dick', 'pussy', 'nigga']

# Given an artist name, return a list of all song files
# files are organized as files/artist-name/{song1,song2}...
def make_song_list(artist_name=default_artist):
    allfiles = []
    dir = basedir + artist_name
    filenames = os.listdir(dir)
    for f in filenames:
            if re.search( '\.git', f):
                continue
            else:
                allfiles.append(os.path.join(dir,f))
    return allfiles

# Given a file containing one song, return the lyrics as a string 
def scrape_lyrics_from_song(file):
    f = open(file, 'r')
    page = f.read()
    # using beautiful soup to navigate the dom and get
    # back the stuff that we need
    soup = BeautifulSoup(page)
    soup.prettify()
    lyrics = soup.select(".lyrics")
    if lyrics:
        lyrics_string = lyrics[0].text
        lyrics_string = re.sub("\n", " ", lyrics_string)
        return lyrics_string
    else:
        return ""

# Given lyrics and a dict of bad words, count the occurrences
# of each bad word and return a dictionary of results
def count_words_for_one_song(lyrics, bad_words=bad_words):
    mydict = {}

    for word in bad_words:
        # we need this because b**** only really matches itself + plural
        # but hoes matches all kinds of other words 
        if word == 'ho':
            matches = re.findall(r'\bhoe?s?\b', lyrics, re.IGNORECASE)
        else:
            matches = re.findall(word, lyrics, re.IGNORECASE)
        mydict[word] = len(matches) or 0
    return mydict

def print_dict(dict):
    for key in dict.keys():
        print str(key) + " : " + str(dict[key]) + "\n"

# do all the artists and put in a big dictionary
# should be call count_for_all_artists
def count_for_all_artists(dir=basedir, testing=False):
    results = {}
    artists = os.listdir(dir)
    if testing:
        for artist in artists:
            if re.search('\.git', artist):
                continue
            print "Artist " + artist
            results[artist] = count_for_one_artist(artist)    
    else: 
        for artist in artists:
            if re.search('\.git', artist):
                continue
            print "Artist " + artist
            results[artist] = count_for_one_artist(artist)
    return results

def count_for_one_artist(artist, bad_words=bad_words):
    
    # start with empty dictionary
    artist_dict = {}
    
    # get the list of all songs for artist, one song per file
    file_list = make_song_list(artist)
    for f in file_list:
        
        lyrics = scrape_lyrics_from_song(f)
        song_name = os.path.basename(f)
        # this still returns: 
        # 'Kanye-west-cant-tell-me-nothing-roc-remix-lyrics.html'
        artist_dict[song_name] = Counter(count_words_for_one_song(lyrics))
    return artist_dict

# given an dict with all the counts for the artists, calculate a bunch of stats 
# and return a dict with the stats. There must be a better data structure for all
# this stuff, maybe Pandas? 
def make_stats_dict(dict):
    # ok, let's make a dict of results
    results = {}

    # there must be a better way to do this! 
    for artist in dict.keys():
        
        num_songs = len(dict[artist])
        # DEBUG
        if num_songs == 0:
            print "artist has no songs:" + artist
            continue
        results[artist] = {}
        # for each bad word, store the total but also calculate an average
        # over the number of songs
        for word in bad_words:
            word_total = word + "_total"
            word_avg = word + "_avg" 
            count = 0 
            # import pdb; pdb.set_trace()
            for song in dict[artist].keys():
                count += dict[artist][song][word]
            results[artist][word_avg] = "%.2f" % (float(count) / float(num_songs))
            results[artist][word_total] = count
            # average = "%.2f" % average
        results[artist]["num_songs"] = num_songs
    import pdb; pdb.set_trace()
    return results    

# get the results dict, print out the stats to a file
def print_stats_to_file(results, results_file="results.txt"):
    f = open(results_file, "w")
    for artist in results.keys():
        f.write("Artist: %s\n" % artist)
        for key in results[artist].keys():
            f.write(key +" " + str(results[artist][key]) + " \n")
        f.write("\n\n")   
    f.close()

# key tells us what to sort on
def get_sorted_stats(results, mykey):
    # f = open("results_sorted.txt", "w")
    sorted_stats = sorted(results.items(), key=lambda x: x[1][mykey], reverse=True)
    return sorted_stats

# should be a better way to do this, it's just once the stats are sorted
# they are put into a list instead of a dict
def print_sorted_stats(results, mykey, results_file="results.txt"): 
    f = open(results_file, "w")
    myresults = get_sorted_stats(results, mykey)
    for artist in myresults:
        # artist[0] is the name
        f.write("Artist: %s\n" % artist[0])
        # print the one we care about the most first
        f.write(mykey + " " + str(artist[1][mykey]) + " \n")
        for key in artist[1].keys():
            if key != mykey:
                f.write(key + " " + str(artist[1][key]) + " \n") 
        f.write("\n\n")   
    f.close()

# to put into plotly
def print_csv(results, mykey='bitch_avg', results_file="results.csv.txt"):
    f = open(results_file, "w")
    myresults = get_sorted_stats(results, mykey)
    for artist in myresults:
        # artist[0] is the name
        f.write("%s, %s\n" % (artist[0], artist[1][mykey]))
    f.close()

if __name__ == '__main__':
    # we can do the stats for just one artist 
    if sys.argv[1:]:
        import pdb; pdb.set_trace()
        name = sys.argv[1]
        dict = count_for_one_artist(name)
        make_stats_dict(dict)

    else:
        results = count_for_all_artists(testing=True)
        stats = make_stats_dict(results) 
        # This should be a command-line flag of what we want to sort on. 
        # print_sorted_stats(stats, 'bitch_avg')  
        import pdb; pdb.set_trace()  
        print_csv(stats, 'bitch_avg', "bitch_results_csv.txt")
        print_csv(stats, 'pussy_avg', "pussy_results_csv.txt")
        print_csv(stats, 'ho_avg', "ho_results_csv.txt")
        print_csv(stats, 'dick_avg', "dick_results_csv.txt") 
        print_csv(stats, 'nigga_avg', "nigga_results_csv.txt") 
