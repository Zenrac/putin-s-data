from googlesearch import search
query = input("Google:")
searches = []
for url in search(query,num=1,stop=1,pause=2):
    searches.append(url)
return searches[0]
