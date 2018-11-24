
# coding: utf-8

# In[52]:


#imports
import requests
import re
from operator import itemgetter


# In[53]:


#get steam speacials search page
def getSteamSpecials():
    """
    Signature: getSteamSpecials()
    Purpose: gets the page of the steam specials, needs requests package
    Type: regquests.get object
    """
    steamSpecialsUrl="https://store.steampowered.com/search/"
    steamSpecialsPageNumber=1
    steamSpecialsPayload={'specials':1,'page':steamSpecialsPageNumber}
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}#chrome
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}#Firefox

    #get page
    page = requests.get(steamSpecialsUrl,params=steamSpecialsPayload,headers=headers)
    
    return page;

page=getSteamSpecials()
#debug
#print(page.url)
#print(page.text)


# In[54]:


#retrieve rows
def retrieveSteamSpecialsRows():
    """
    Signature: retrieveSteamSpecialsRows()
    Purpose: extracts the listing of the steam specials page
    Type: an array of listings from the specials page
    """
    rePattern='<span class="title">.*?</span>.*?<span>-[0-9][0-9]%</span>'
    rePattern='<a href.*?<span class="title">.*?</span>.*?<span>-[0-9][0-9]%</span>.*?</a>'
    re1=re.compile(rePattern,re.S)
    resultList=re1.findall(page.text)
    resultList.pop(0)#removes first irrelevant stuff
    return resultList;

resultList=retrieveSteamSpecialsRows();
#debug
#for result in resultList:
#    print("======================================")
#    print(result)


# In[55]:


#retrieve game store page link
def retrieveGameStorePageLink():
    """
    Signature: retrieveGameStorePageLink()
    Purpose: extracts the steam store page link for games
    Type: an array of html strings linking to the steam store page
    """
    rePattern='href=".*?"'
    re2=re.compile(rePattern,re.S)
    steamGameStorePageUrlList=re2.findall(str(resultList))
    steamGameStorePageUrlListFiltered=[]
    for steamGameStorePageUrl in steamGameStorePageUrlList:
        steamGameStorePageUrl=steamGameStorePageUrl.replace('href="','')
        steamGameStorePageUrl=steamGameStorePageUrl.replace('"','')
        steamGameStorePageUrlListFiltered.append(steamGameStorePageUrl)
    return steamGameStorePageUrlListFiltered;
    
steamGameStorePageUrlListFiltered=retrieveGameStorePageLink();
#debug
#for steamGameStorePageUrl in steamGameStorePageUrlListFiltered:
#    print("======================================")
#    print(steamGameStorePageUrl)


# In[56]:


#retrieve game titles
def retrieveGameTitles():
    """
    Signature: retrieveGameTitles()
    Purpose: retrievs game titles
    Type: a string array of game titles
    """
    rePattern='<span class="title">.*?</span>'
    re3=re.compile(rePattern)
    gameTitleList=re3.findall(str(resultList))

    gameTitleListFiltered=[]
    for gameTitle in gameTitleList:
        gameTitle=gameTitle.replace('<span class="title">','')
        gameTitle=gameTitle.replace('</span>','')
        gameTitleListFiltered.append(gameTitle)
    return gameTitleListFiltered;

gameTitleListFiltered=retrieveGameTitles();  
#debug
#for gameTitle in gameTitleListFiltered:
#    print(gameTitle)


# In[57]:


#retrieve game discount
def retrieveGameDiscount():
    """
    Signature: retrieveGameDiscount()
    Purpose: retrievs game discount
    Type: a string array of game discounts
    """
    rePattern='-..%'
    re4=re.compile(rePattern)
    gameDiscountList=re4.findall(str(resultList))
    return gameDiscountList;

gameDiscountList=retrieveGameDiscount();
#debug
#for gameDiscount in gameDiscountList:
#    print(gameDiscount)


# In[58]:


#zip up found game details
def zipGameDetails():
    """
    Signature: zipGameDetails()
    Purpose: zip up game details into a new array
    Type: a string array of game titles,links, and discounts
    """
    gameDetailsList=zip(gameTitleListFiltered,steamGameStorePageUrlListFiltered,gameDiscountList)
    return gameDetailsList;

gameDetailsList=zipGameDetails()
#debug
#for gameDetail in gameDetailsList:
#    print(gameDetail)


# In[59]:


#remove special characters
def removeSpecialCharacters():
    """
    Signature: removeSpecialCharacters()
    Purpose: remove special characters from game titles
    Type: a string array of game titles (without special characters),links, and discounts
    """
    gameList=[]
    for gameDetails in gameDetailsList:
        gameTitle=re.sub('™','',str(gameDetails[0]))
        gameTitle=re.sub('©','',gameTitle)
        gameTitle=re.sub('®','',gameTitle)
        newGameDetail=[gameTitle,gameDetails[1],gameDetails[2]]
        gameList.append(newGameDetail)
    return gameList;
gameDetailsList=removeSpecialCharacters()
#debug
#for game in gameDetailsList:
#    print(game)


# In[60]:


#search gamespot site
def searchGameInformerSite():
    """
    Signature: searchGameInformerSite()
    Purpose: search gameinformer for game reviews
    Type: a string array of game titles (without special characters),links, and discounts
    """
    gameInformerUrl='https://www.gameinformer.com/'
    gameInformerSearchUrl='https://www.gameinformer.com/search?'
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}#chrome
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}#Firefox

    gameDetailsWithReviewList=[]
    for gameDetail in gameDetailsList:
        gameInformerPayload={'keyword':gameDetail[0]+' review'}
        page = requests.get(gameInformerSearchUrl,params=gameInformerPayload,headers=headers)
        #print(page.text)
        #print(page.url)
        rePattern='<a.*?'+gameDetail[0]+' Review.*?</a>'
        re5=re.compile(rePattern,re.I)
        match=re5.search(str(page.text))
        if match:
            rePattern='".*?"'
            re6=re.compile(rePattern)
            submatch=re6.search(match.group())
            result=submatch.group()
            result=result.replace('"','')
            result=gameInformerUrl+result
        else:
            result='Unavailable'

        gameDetailsWithReviewList.append([gameDetail[0],gameDetail[1],gameDetail[2],result])
    return gameDetailsWithReviewList;

gameList=searchGameInformerSite()
#debug
#for row in gameList:
#    print(row)


# In[61]:


#get review score
def getReviewScore():
    """
    Signature: getReviewScore()
    Purpose: search gameinformer for game review score
    Type: a string array of game titles (without special characters),links, discounts, and scores
    """
    completedGameList=[]
    for game in gameList:
        #print(game)
        if game[3]!="Unavailable":
            page = requests.get(game[3])
            rePattern='<div class="review-summary-score">.*?<div class="review-summary-score-system tooltip-container">'
            re6=re.compile(rePattern,re.S)
            match=re6.search(str(page.text))
            match=re.sub('<.*?>','',match.group())
            match=match.replace(' ','').replace('\t','').replace('\n','')
        else:
            match='Unavailable'
        game.append(match)
        completedGameList.append(game)
    return completedGameList;

completedGameList=getReviewScore()
#debug
#for game in completedGameList:
#    print(game)


# In[63]:


#sort by score
def sortByScore():
    """
    Signature: sortByScore()
    Purpose: sort array of game details by gameinformer score
    Type: a string array of game details sorted by score
    """
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
    return sortedCompletedGameList;

sortedCompletedGameList=sortByScore()
#debug
#for game in sortedCompletedGameList:
#    print(game)


# In[64]:


#remove games discounted lower than 50
def removeDiscounts():
    """
    Signature: removeDiscounts()
    Purpose: removes games with less than 50% discounts
    Type: a string array of game details with greater than 50% discounts
    """
    finalGameList=[]
    for game in sortedCompletedGameList:
        discount=game[2]
        discount=discount.replace('-','')
        discount=discount.replace('%','')
        if(int(float(discount))>=50):
            finalGameList.append(game)
    return finalGameList;

finalGameList=removeDiscounts()
#debug
#for game in finalGameList:
#    print(game)


# In[65]:


#html code
def buildHtmlCode():
    """
    Signature: buildHtmlCode()
    Purpose: builds html code based on found game details
    Type: an html string
    """
    
    htmlCode=''

    htmlTop="""
    <html lang="en">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <head>
    <title>Steam Special Sale Games with GameInformer Review Scores</title>
    </head>
    """
    htmlBodyStart='<body>'
    header='<h1>Steam Special Sale Games with GameInformer Review Scores</h1>'
    tableStart='<table border=1>'

    tableHeaders='<tr>'
    tableHeaders+='<th>Game</th>'
    tableHeaders+='<th>Discount</th>'
    tableHeaders+='<th>GameInformer Score</th>'
    tableHeaders+='</tr>'

    tableRows=''

    tableEnd='</table>'

    htmlBodyEnd='</body>'
    htmlBottom='</html>'

    htmlCode=htmlTop+htmlBodyStart+header
    htmlCode+=tableStart+tableHeaders+tableRows+tableEnd
    htmlCode+=htmlBodyEnd+htmlBottom

    #completedGameList
    #[GameTitle,GameSteamURl,Discount,GameInformerUrl,GameInformerScore]
    #create rows
    for entry in finalGameList:
        #game,steam url
        tableRows+='<tr><td>'
        tableRows+='<a href="'+entry[1]+'">'
        tableRows+=entry[0]+'</a></td>'

        #discount
        tableRows+='<td>'+entry[2]+'</td>'

        #GameInformer score,GameInformer url
        if(entry[3]!='Unavailable'):
            tableRows+='<td><a href="'+entry[3]+'">'
            tableRows+=entry[4]+'</a>'
            tableRows+='</td></tr>'
        else:
            tableRows+='<td>GameInformer score not found</td></tr>'

    #build html code
    htmlCode=htmlTop+htmlBodyStart+header
    htmlCode+=tableStart+tableHeaders+tableRows+tableEnd
    htmlCode+=htmlBodyEnd+htmlBottom
    
    return htmlCode;
htmlCode=buildHtmlCode()
#debug
#print(htmlCode)


# In[66]:


#write to file
def writeToFile():
    """
    Signature: writeToFile()
    Purpose: writes a string to an html file
    """
    with open("rankings.html", "w") as file:
        file.write(htmlCode)

writeToFile()

