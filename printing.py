###############################################################################


##
### TODO:
##


###############################################################################

# prints the index accordingly. marks current current if given
def printIndex(i, current=None):
	if i < 10:
		openbracket = "( "
	else:
		openbracket = "("
	if i == current:
		print(openbracket+"-"+str(i)+"-) ", end="")
	else:
		print(openbracket, i, ") ", end="")

# print only a certain range of the search results
def printSelection(results, showType, source, start, end, showURI=False):
	if start < 0:
		start = 0
	if source == "soundcloud":
		print("(Showing tracks)")
		for i in range(start, end):
			printIndex(i)
			print(results["tracks"][i]["name"], "-", 
				  results["tracks"][i]["artists"][0]["name"])
			if showURI:
				print("URI: ", results["tracks"][i]["uri"])
	else:
		print("(Showing ", showType, ")")
		for i in range(start, end):
			printIndex(i)
			if showType == "artists":
				print(results[showType][i]["name"])
			else:
				print(results[showType][i]["name"], "-", 
					  results[showType][i]["artists"][0]["name"])
			if showURI:
				print("URI: ", results[showType][i]["uri"])

# prints only name and URI of a list of playlists
def printPlaylists(playlists=[], showURI=False):
	if not playlists or playlists==None:
		print("No playlists to print...")
		return
	for i in range(len(playlists)):
		printIndex(i)
		print(playlists[i]["name"].encode("utf8", "replace").decode(), )
		if showURI:
			print("URI: ", playlists[i]["uri"])




