
# coding: utf-8

# In[1]:


#get steam sale game list
#get gamespot score for each game in game list
#output html file 'rankings.html'
#-table of game names, hyperlink to gamespot review
#--only include %50 discounted or more
#--sort by review score, highest first
#--remove '©''
#--remove '®'
#--": Steam Edition"
#--": Digital Edition"


# In[2]:


#https://stackoverflow.com/questions/37372603/how-to-remove-specific-substrings-from-a-set-of-strings-in-python


# In[3]:


#imports
import requests
import re
from operator import itemgetter


# In[4]:


#get steam speacials search page
steamSpecialsUrl="https://store.steampowered.com/search/"
steamSpecialsPageNumber=1
steamSpecialsPayload={'specials':1,'page':steamSpecialsPageNumber}
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}#chrome
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}#Firefox

#get page
page = requests.get(steamSpecialsUrl,params=steamSpecialsPayload,headers=headers)

#debug
#print(page.url)
#print(page.text)


# In[5]:


#retrieve rows
rePattern='<span class="title">.*?</span>.*?<span>-[0-9][0-9]%</span>'
rePattern='<a href.*?<span class="title">.*?</span>.*?<span>-[0-9][0-9]%</span>.*?</a>'
re1=re.compile(rePattern,re.S)
resultList=re1.findall(page.text)
resultList.pop(0)#removes first irrelevant stuff

#debug
#for result in resultList:
#    print("======================================")
#    print(result)


# In[6]:


#retrieve game store page link
rePattern='href=".*?"'
re2=re.compile(rePattern,re.S)
steamGameStorePageUrlList=re2.findall(str(resultList))
steamGameStorePageUrlListFiltered=[]
for steamGameStorePageUrl in steamGameStorePageUrlList:
    steamGameStorePageUrl=steamGameStorePageUrl.replace('href="','')
    steamGameStorePageUrl=steamGameStorePageUrl.replace('"','')
    steamGameStorePageUrlListFiltered.append(steamGameStorePageUrl)
    
#debug
#for steamGameStorePageUrl in steamGameStorePageUrlListFiltered:
#    print("======================================")
#    print(steamGameStorePageUrl)


# In[7]:


#retrieve game titles
rePattern='<span class="title">.*?</span>'
re3=re.compile(rePattern)
gameTitleList=re3.findall(str(resultList))

gameTitleListFiltered=[]
for gameTitle in gameTitleList:
    gameTitle=gameTitle.replace('<span class="title">','')
    gameTitle=gameTitle.replace('</span>','')
    gameTitleListFiltered.append(gameTitle)
    
#debug
#for gameTitle in gameTitleListFiltered:
#    print(gameTitle)


# In[8]:


#retrieve game discount
rePattern='-..%'
re4=re.compile(rePattern)
gameDiscountList=re4.findall(str(resultList))

#debug
#for gameDiscount in gameDiscountList:
#    print(gameDiscount)


# In[9]:


gameDetailsList=zip(gameTitleListFiltered,steamGameStorePageUrlListFiltered,gameDiscountList)

#debug
#for gameDetail in gameDetailsList:
#    print(gameDetail[1])


# In[10]:


#search gamespot site
gameSpotUrl='http://www.gamespot.com'
gameSpotSearchUrl='http://www.gamespot.com/search/'
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}#chrome
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}#Firefox

gameDetailsWithReviewList=[]
for gameDetail in gameDetailsList:
    gameSpotPayload={'q':gameDetail[0],'i':'reviews'}
    page = requests.get(gameSpotSearchUrl,params=gameSpotPayload,headers=headers)
    rePattern='<a.*?'+gameDetail[0]+' Review</a>'
    re5=re.compile(rePattern,re.I)
    match=re5.search(str(page.text))
    if match:
        rePattern='".*?"'
        re6=re.compile(rePattern)
        submatch=re6.search(match.group())
        result=submatch.group()
        result=result.replace('"','')
        result=gameSpotUrl+result
    else:
        result='Unavailable'
        
        
    gameDetailsWithReviewList.append([gameDetail[0],gameDetail[1],gameDetail[2],result])
    
#debug
#for row in gameDetailsWithReviewList:
#    print(row)


# In[11]:


#remove special characters
gameList=[]
for gameDetails in gameDetailsWithReviewList:
    gameTitle=re.sub('™','',str(gameDetails[0]))
    gameTitle=re.sub('©','',gameTitle)
    gameTitle=re.sub('®','',gameTitle)
    newGameDetail=[gameTitle,gameDetails[1],gameDetails[2],gameDetails[3]]
    gameList.append(newGameDetail)
    
#debug
#for game in gameList:
#    print(game)


# In[12]:


#get review score
completedGameList=[]
for game in gameList:
    if game[3]!="Unavailable":
        page = requests.get(game[3],headers=headers)
        rePattern='<div class="gs-score__cell">.*?</div>'
        re6=re.compile(rePattern,re.S)
        match=re6.search(str(page.text))
        match=re.sub('<.*?>','',match.group())
        match=match.replace(' ','').replace('\t','').replace('\n','')
    else:
        match='Unavailable'
    game.append(match)
    completedGameList.append(game)
        
#debug
for game in gameList:
    print(game)


# In[13]:


#completedGameList
#[GameTitle,GameSteamURl,Discount,GamespotUrl,GamespotScore]


# In[14]:


#sort by score
sortedCompletedGameList=[]
gameListWithScore=[]
gameListWithoutScore=[]
for gameDetail in completedGameList:
    if(gameDetail[4]!='Unavailable'):
        gameListWithScore.append(gameDetail)
    else:
        gameListWithoutScore.append(gameDetail)

sortedGameList=sorted(gameListWithScore, key=lambda gameDetail: gameDetail[4],reverse=True)
for game in gameListWithScore:
    sortedCompletedGameList.append(game)
for game in gameListWithoutScore:
    sortedCompletedGameList.append(game)
    
#debug
#for game in sortedCompletedGameList:
#    print(game)


# In[15]:


#remove games discounted lower than 50
finalGameList=[]
for game in sortedCompletedGameList:
    discount=game[2]
    discount=discount.replace('-','')
    discount=discount.replace('%','')
    if(int(float(discount))>50):
        finalGameList.append(game)
        
#debug
for game in finalGameList:
    print(game)


# In[16]:


#html code
htmlCode=''

htmlTop="""
<html lang="en">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<head>
<title>Steam Special Sale Games with GameSpot Review Scores</title>
</head>
"""
htmlBodyStart='<body>'
header='<h1>Steam Special Sale Games with GameSpot Review Scores</h1>'
tableStart='<table border=1>'

tableHeaders='<tr>'
tableHeaders+='<th>Game</th>'
tableHeaders+='<th>Discount</th>'
tableHeaders+='<th>GameSpot Score</th>'
tableHeaders+='</tr>'

tableRows=''

tableEnd='</table>'

htmlBodyEnd='</body>'
htmlBottom='</html>'

htmlCode=htmlTop+htmlBodyStart+header
htmlCode+=tableStart+tableHeaders+tableRows+tableEnd
htmlCode+=htmlBodyEnd+htmlBottom

#completedGameList
#[GameTitle,GameSteamURl,Discount,GamespotUrl,GamespotScore]
#create rows
for entry in finalGameList:
    #game,steam url
    tableRows+='<tr><td>'
    tableRows+='<a href="'+entry[1]+'">'
    tableRows+=entry[0]+'</a></td>'
    
    #discount
    tableRows+='<td>'+entry[2]+'</td>'
    
    #gamespot score,gamesport url
    if(entry[3]!='Unavailable'):
        tableRows+='<td><a href="'+entry[3]+'">'
        tableRows+=entry[4]+'</a>'
        tableRows+='</td></tr>'
    else:
        tableRows+='<td>Gamespot score not found</td></tr>'
        
#build html code
htmlCode=htmlTop+htmlBodyStart+header
htmlCode+=tableStart+tableHeaders+tableRows+tableEnd
htmlCode+=htmlBodyEnd+htmlBottom

#debug
#print(htmlCode)


# In[17]:


#write to file
with open("rankings.html", "w") as file:
    file.write(htmlCode)

