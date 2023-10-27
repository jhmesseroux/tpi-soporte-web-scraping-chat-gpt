from db import get_database_connection, close_database_connection
from typing import Dict, Any
from tqdm import tqdm
import mysql.connector
import time
import requests
from bs4 import BeautifulSoup

def getPostData(postId : int) -> Dict[str, Any]:        
    html = requests.get('https://stackoverflow.com/questions/' + postId).text
    soup = BeautifulSoup(html, 'lxml')
    _content = soup.find('div', id='content')
    qHeader = _content.find('div', id='question-header')
    if not qHeader:
        return None   

    fullPost: Dict[str, Any] = {}
    title  = _content.a.text
    link = _content.a['href']
    time = _content.time['datetime']
    fullPost['title'] = title
    fullPost['link'] = 'https://stackoverflow.com' + link
    fullPost['time'] = time

    # get info about the question 
    _question = soup.find('div', id='question')
    questionScore = _question['data-score']
    # questionHtml = _question.find('div', class_='js-post-body')
    # questionTexts = _question.find('div', class_='js-post-body').text
    questionTagList = _question.find_all('li', class_='js-post-tag-list-item')
    questionTags = []
    for tag in questionTagList:
        questionTags.append(tag.text)

    fullPost['question'] = {
        'score' : questionScore,
        # 'html' : questionHtml,
        # 'texts' : questionTexts,
        'tags' : questionTags
    }

    # get responses
    _answers = soup.find_all('div', class_='answer')
    fullPost['answers'] = []
    for answer in _answers:
        answerScore = answer['data-score']
        isHighestScore = answer['data-highest-scored']  # 0 or 1
        answerAcceptedOrSuggested = answer['itemprop'] # acceptedAnswer or suggestedAnswer
        answerHtml = answer.find('div', class_='js-post-body')
        answerTexts = answer.find('div', class_='js-post-body').text
        fullPost['answers'].append({
            'score' : answerScore,
            'isHighestScore' : isHighestScore,
            'answerAcceptedOrSuggested' : answerAcceptedOrSuggested,
            'html' : answerHtml,
            'text' : answerTexts
        })
    return fullPost

def insert (data : Dict[str, Any],id : int):
    if( len(data['answers']) >= 4 ): 
        connection = get_database_connection()
        if connection:
            try:
                cursor = connection.cursor()       
                insert_query = "INSERT INTO questions (id,title,link,time,score,tags,answers) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(insert_query, (id,data['title'],data['link'],data['time'], data['question']['score'], ', '.join(data['question']['tags']), len(data['answers']) ))
                j = 1
                for answer in data['answers']:
                    insert_query = "INSERT INTO answers (id,score, isHighestScore, answerAcceptedOrSuggested, html, texts,questionId) VALUES (%s,%s, %s,%s, %s,%s,%s)"
                    cursor.execute(insert_query, (j + int(round(time.time() * 1000)), int(answer['score']), int(answer['isHighestScore']), answer['answerAcceptedOrSuggested'], str(answer['html']), str(answer['text']),id))
                    j=j+1
                connection.commit()            
            except mysql.connector.Error as e:
                print("Error:", e)
            finally:
                close_database_connection(connection)

# fill database 
def fillDatabase(id):
    notFound = []
    for item in tqdm(range(2),desc="procesando...", unit="item") :
        res = getPostData(str( id + item))
        if res:
            insert(res,id + item)
        else:
            notFound.append(str(id + item))
    print('NOT FOUND QUESTIONs  :: ',len(notFound))

fillDatabase(95000)