import random
import string
import openai
from decouple import config
from textdistance import jaro_winkler
from tqdm import tqdm
import matplotlib.pyplot as plt
from db import getQuestionsAndAnswers
import time

openai.api_key = config("OPENAI_API_KEY")


def generate_random_text(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def askChatGPT3(question):
    try:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question }    ])
        return completion.choices
    except Exception as e:
        print('Exception ::: ', e)
        return None

# process data to get the similarity between the answers of the stackoverflow and the answers of the GPT3
def process():
    stackData = getQuestionsAndAnswers()
    # stackData =  [1,2]
    scores = []
    dificulties = []
    diferenceBetweenHumanAndChatGpt = []

    plotHumanScore = []
    plotChatGptScore = []
    randomPrefix = generate_random_text(5)
    fileName = 'outputs/results/' + randomPrefix + '.txt'
    outPutText = f"ARCHIVO DE RESULTADOS {randomPrefix} \n\n"

    for item in tqdm(range(len(stackData)),desc="<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<PROCESANDO>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" , unit="item") :
        resGPT = askChatGPT3(stackData[item]['title'] + '\n' + stackData[item]['tags'])
        # resGPT ={}
        # resGPT[0]['message']['content']
        outPutText += f"PREGUNTAS #{item} CON ID : {stackData[item]['id']} \n"
        maxChatGptScore = 0
        for i in range(len(stackData[item]['answers'])):
            similarity = jaro_winkler(stackData[item]['answers'][i]['texts'],resGPT[0]['message']['content'])
            print()
            if similarity > maxChatGptScore:
                maxChatGptScore = similarity
                chatGptScore = stackData[item]['answers'][i]['score']
            if stackData[item]['answers'][i]['isHighestScore'] == 1:
                humanScore = stackData[item]['answers'][i]['score']  
            outPutText += f"     RESPUESTA #{i + 1:02d} CON SIMILARIDAD {round(similarity,4)} LO VATARON {stackData[item]['answers'][i]['score']:03d} veces\n"
        outPutText += f"\n"
        
        plotChatGptScore.append(round(maxChatGptScore,4))
        plotHumanScore.append(humanScore)
        scores.append(( stackData[item]['score'],humanScore - chatGptScore)) 
        dificulties.append(stackData[item]['score'] ) # tomando como dificultad el score de la pregunta -> cantidad de votos
        diferenceBetweenHumanAndChatGpt.append(humanScore - chatGptScore)
        if(item % 3 == 0):
            time.sleep(45)

    outPutText += f"\n\nscore and diff :: {scores}\n"
    outPutText += f"CHAT_GPT SCORES    :: {plotChatGptScore}\n"
    outPutText += f"HUMANO_SCORES      :: {plotHumanScore}\n"
    outPutText += f"DIFICULTADES       :: {dificulties}\n"
    outPutText += f"DIF_HUMANO_GPT     :: {diferenceBetweenHumanAndChatGpt}\n"


    with open(fileName, 'a') as file:
        file.write(outPutText)

    
    imgName = 'outputs/images/' + randomPrefix

    # plt.plot(dificulties,diferenceBetweenHumanAndChatGpt)
    plt.scatter(dificulties, diferenceBetweenHumanAndChatGpt, marker='.', color='b', label='Puntos')
    plt.xlabel('Dificuldades de las preguntas')
    plt.ylabel('Diferencia entre la respuesta humana y la respuesta de GPT3')
    plt.title("GRAFICA 01")
    # plt.show()
    plt.savefig(imgName + '_1.png')

    # grafica de los votos humanos vs los votos de GPT3
    plt.plot(plotHumanScore,plotChatGptScore)
    plt.scatter(plotHumanScore, plotChatGptScore, marker='*', color='r', label='Puntos')
    plt.xlabel('Score de las respuestas humanas)')
    plt.ylabel('Score de las respuestas de GPT3')
    plt.title("GRAFICA 02")
    # plt.show()
    plt.savefig(imgName + '2.png')

    return scores

