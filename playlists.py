from core import send, M
from printing import printPlaylists
import time

# plays whatever playlist the user wants via input and search
def playPlaylist(filterTerm=None):
	if isinstance(filterTerm, list):
		if not filterTerm:
			filterTerm = None
		else:
			filterTerm = filterTerm[0]
	if not filterTerm:
		filterTerm = input("Provide a search term: ")
		if not filterTerm:
			print("Showing all options: ")
			showAllPlaylists()
			return
		else:
			filterTerm = filterTerm.split()[0]

	# if filter term is an integer within range, pick playlist straight away?
	# then you can just pick one by number

	playlists = send(method=M['playlists']["as_list"])
	playlist = findPlaylist(playlists, filterTerm)
	if playlist:
		uris = getURIsFromPlaylist(playlist["uri"])
		if uris != None:
			send(getReply=0, method=M['tracklist']['clear'])
			send(getReply=0, method=M['tracklist']['add'], uris=uris)
			time.sleep(2)
			send(getReply=0, method=M['playback']['play'])

# shows all playlists. if args given, then filter first
def showAllPlaylists(filterTerm=None):
	if isinstance(filterTerm, list):
		if not filterTerm:
			filterTerm = None
		else:
			filterTerm = filterTerm[0]
	if filterTerm:
		playlistsTemp = send(method=M['playlists']['as_list'])
		printPlaylists(filteredPlaylists(playlistsTemp, filterTerm))
	else:
		printPlaylists(send(method=M['playlists']['as_list']))

# accepts a list of playlists and a search term
# returns a filtered list of playlist URIs 
def filteredPlaylists(playlists=[], filterTerm=None):
	filtered = []
	if not filterTerm:
		print("No filter term provided to playlist filter...")
		return None
	if not playlists:
		print("No playlists provided to playlist filter...")
		return None
	for i in range(len(playlists)):
		if filterTerm.lower() in playlists[i]["name"].lower():
			filtered.append(playlists[i])
	return filtered

# finds a specific playlist based on a search term
# narrows down search via user input
def findPlaylist(playlists=[], filterTerm=None):
	filtered = filteredPlaylists(playlists, filterTerm)
	if filtered == None or len(filtered)==0:
		print("None found...")
		return None
	if not filterTerm:
		print("No arguments provided to find...")
		return None
	if not playlists:
		print("No playlists provided to find...")
		return None
	if len(filtered) == 1:
		print("Playing only result: ", filtered[0]["name"].encode("utf8", "replace").decode())
		return filtered[0]
	printPlaylists(filtered)
	inp = int(input("Which playlist? (-1 : filter again | -2 : cancel) "))
	if inp == -2:
		return None
	if inp != -1:
		return filtered[inp]
	inputTerm = input("Add a search term: ")
	return findPlaylist(filtered, inputTerm)

# accepts a playlist URI (directly or via args)
# returns a list of song URIs from that playlist
def getURIsFromPlaylist(uri=None):
	if uri == None:
		print("No URI provided...")
		return None
	songs = send(method=M['playlists']["get_items"], uri=uri)
	if songs == None:
		print("No results.. possibly invalid uri?")
		return None
	uris = []
	for i in range(len(songs)):
		uris.append(songs[i]["uri"])
	return uris

# play a specific playlist from playlist uri
def playSpecificPlaylist(uri=None):
	if uri:
		uris = getURIsFromPlaylist(uri)
		if uris != None:
			send(getReply=0, method=M['tracklist']['clear'])
			send(getReply=0, method=M['tracklist']['add'], uris=uris)
			time.sleep(2)
			send(getReply=0, method=M['playback']['play'])

