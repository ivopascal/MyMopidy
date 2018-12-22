from core import send, M
from printing import printSelection

# plays whatever the user wants via input and search
def search(search_terms=None, adding=False):
	if isinstance(search_terms, list) and not search_terms:
		search_terms = None
	if not search_terms:
		queryTerm = input("What to search for? ")
		search_terms = queryTerm.split()
		if not search_terms:
			print("No search terms were given...")
			return

	if adding:
		queryType = "any"
	else:
		queryType = input("Search for artist, album or track/any? ").lower()
		if queryType not in ["artist", "album", "track", "any"]:
			print("Invalid query type...")
			return
		if queryType == "track":
			queryType = "any"
	results = send(timeout=5, method=M['library']['search'], query={queryType:search_terms})

	source = input("Show results from google, spotify or soundcloud? ").lower()
	if source not in ["google", "spotify", "soundcloud"]:
		print("Invalid source type...")
		return
	results = getResultsOfSource(results, source)
	if results == None:
		print("Results did not get returned from source...")
		return

	uris = None
	if queryType == "artist":
		uris = printAndGetURIs(results, "artists", source)
	if queryType == "album":
		uris = printAndGetURIs(results, "albums", source)
	if queryType == "any":
		uris = printAndGetURIs(results, "tracks", source)
		if uris == None:
			uris = printAndGetURIs(results, "albums", source)
		if uris == None:
			uris = printAndGetURIs(results, "artists", source)

	if uris != None:
		if isinstance(uris, list):
			send(getReply=0, method=M['tracklist']['add'], uris=uris)
		else:
			send(getReply=0, method=M['tracklist']['add'], uris=[uris])
		if not adding:
			send(getReply=0, method=M['playback']['play'])

# returns correct list from results depending on source
def getResultsOfSource(results, source):
	if results == None or source == None:
		print("Results or source are None...")
	for i in range(len(results)):
		if "tracks" in results[i]:
			if source == "soundcloud" and "soundcloud" in results[i]["tracks"][i]["uri"]:
				return results[i]
			if source == "spotify" and "spotify" in results[i]["tracks"][i]["uri"]:
				return results[i]
			if source == "google" and "gmusic" in results[i]["tracks"][i]["uri"]:
				return results[i]
	return None

# accepts results[i] (so either google results or spotify etc)
# returns a list of song URIs 
def printAndGetURIs(results, showType, source, showAll=False):
	if source == "soundcloud":
		showType = "tracks"
	if showAll:
		for i in range(len(results[showType])):
			if source == "soundcloud":
				print(results[showType][i]["name"], " : ", 
					  results[showType][i]["artists"][0]["name"], " : ",
					  results[showType][i]["uri"])
			else:
				print(results[showType][i]["__model__"], " : ", 
					  results[showType][i]["name"], " : ", 
					  results[showType][i]["uri"])
	if len(results[showType]) > 1:
		print("Total of ", len(results[showType]), " results for ", showType)
	choice = getChoice(results, showType, source)
	if choice == None:
		return None
	if showType == "artists":
		return getURIsFromLookup(choice, 10)
	if showType == "albums":
		return getURIsFromLookup(choice, 10)
	if showType == "tracks":
		return choice

# accepts artist/album URI and amount
# returns list of song URIs
def getURIsFromLookup(uri, amount):
	uris = []
	info = send(method=M['library']['lookup'], uris=[uri])
	if not info:
		print("No information was returned...")
		return None
	info = info[uri]
	if amount > len(info):
		amount = len(info)
	for i in range(amount):
		uris.append(info[i]["uri"])
	return uris

# find a uri from results via user input
def getChoice(results, showType, source):
	start  = 0
	end    = 9
	choice = -2
	if source == "soundcloud":
		showType = "tracks"
	numResults = len(results[showType])
	if numResults == 1:
		print("Choosing the only option to choose from!")
		return results[showType][0]["uri"]
	while True:
		if end >= numResults:
			printSelection(results, showType, source, end-10, numResults)
			start = 0
			end   = 9
		else:
			printSelection(results, showType, source, start, end)
			start += 10
			end   += 10
		choice = int(input("Choose an option (-1 : cancel | -2 : show more) "))
		if choice in range(numResults):
			return results[showType][choice]["uri"]
		if choice == -1:
			return None

