import requests
import winamp
import time
import os
import sys


def cls():
	os.system('cls' if os.name=='nt' else 'clear')

class Song:
	def __init__(self, artist, title, url):
		self.artist = artist
		self.title = title
		self.url = url

	def __str__(self):
		result_txt = '[' + self.artist + ' - ' + self.title
		result_txt += '] - ' + self.url
		return result_txt

class Fetcher:
	def fetch_page(self, url):
		with requests.Session() as session:
			response = session.get(url)
		return response.content

	def search_song(self, artist, title):
		destination_url = 'http://www.tekstowo.pl/wyszukaj.html?search-title='
		destination_url += title + '&search-artist='
		destination_url += artist
		return self.fetch_page(destination_url)

	def fetch_lyrics(self, song):
		url = song.url
		return self.fetch_page(url)

class Parser:
	def parse_search_results(self, results):
		songs_list = []
		results = results.decode('utf-8')
		if 'Znalezieni artyści' in results:
			results = results.split('Znalezieni artyści:')[0]
		operation_array = results.split('<div class="box-przeboje">')[1:]
		for item in operation_array:
			temp_artist_title = item.split('title="')[1].split('">')[0]
			temp_artist = temp_artist_title.split(' - ')[0]
			temp_title = temp_artist_title.split(' - ')[1]
			temp_url = 'http://www.tekstowo.pl'
			temp_url += item.split('a href="')[1].split('.html')[0]
			temp_url += '.html'
			songs_list.append(Song(temp_artist, temp_title, temp_url))

		return songs_list

	def parse_song_lyrics(self, html):
		lyrics = html.decode('utf-8')
		lyrics = lyrics.split('<h2>Tekst piosenki:</h2><br />')[1]
		lyrics = lyrics.split('<p>&nbsp;</p>')[0]
		lyrics = lyrics.replace('<br />', '\n')
		lyrics = lyrics.replace('\n\n', '\n')
		lyrics = lyrics.strip()  # remove leading and trailing spaces
		return lyrics

class Main:
	def run(self):
		if os.name == 'nt':
			os.system('chcp 65001')
		self._fetcher = Fetcher()
		self._parser = Parser()
		self._winamp = winamp.winamp()
		self.last_played = ""
		while True:
			current = self.current_song()
			if current:
				cls()
				print(self.get_lyrics(current))
			time.sleep(1)

	def current_song(self):
		playing = self._winamp.getCurrentTrackName()
		playing = playing.replace(' [Stopped]', '')
		if playing != self.last_played:
			self.last_played = playing
			return playing
		self.last_played = playing

	def get_lyrics(self, song, n=0):
		song = '. '.join(song.split('. ')[1:])[:-9].split(' - ')
		artist = song[0]
		title = song[1]
		temp_txt = self._fetcher.search_song(artist, title)
		temp_results = self._parser.parse_search_results(temp_txt)
		try:
			temp_txt = self._fetcher.fetch_lyrics(temp_results[n])  # 1st song
		except IndexError:
			return "Song not found on tekstowo.pl!"
		temp_txt = self._parser.parse_song_lyrics(temp_txt)
		return temp_txt

if __name__ == '__main__':
	Main().run()