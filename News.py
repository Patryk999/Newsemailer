import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib
from email.message import EmailMessage

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}

def getweather():
    weatherURL = "https://pogoda.onet.pl/prognoza-pogody/warszawa-357732"
    global headers

    weatherlink = requests.get(weatherURL, headers=headers)

    soup = BeautifulSoup(weatherlink.content, features='html.parser')

    weatherfortheday = soup.findAll("div", class_="temp")
    timeofweatheroftheday = soup.findAll("div", class_="time")

    temp = []
    time = []

    for x in weatherfortheday:
        temp.append(x.get_text().strip()[:-1])

    temp = temp[1:]
    for x in timeofweatheroftheday:
        time.append(x.get_text().strip())

    temp = temp[:10]
    time = time[:10]
    output = []
    for x in range(len(time)):
        output.append("O godzinie {} bedzie {} stopni Celsjusza".format(time[x],temp[x]))

    return output

def getnewsheaders():
    newsURL = "https://warszawa.wyborcza.pl/warszawa/0,54420.html"
    global headers

    newslink = requests.get(newsURL, headers=headers)

    soup = BeautifulSoup(newslink.content, features = 'html.parser')

    newsodd = soup.findAll("li", class_="entry even article")
    newseven = soup.findAll("li", class_="entry odd article")

    i = 0
    j = 0
    newsoddpluseven = []
    while i < len(newsodd) and j < len(newseven):
        if i > j:
            newsoddpluseven.append(newseven[j].get_text().strip())
            j += 1
        else:
            newsoddpluseven.append(newsodd[i].get_text().strip())
            i += 1

    newsheaders = []
    c = 0
    for x in newsoddpluseven:
        for y in range(len(x)):
            if x[y] == '\n':
                newsheaders.append(x[:y])
                break

    return newsheaders

def sendemail(news, weather):
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('patryk.saffer99@gmail.com',"vxyqiiebahkpokan")

    news = "\n".join(news)
    weather = "\n".join(weather)

    msg = EmailMessage()

    subject = "Poranny Raport"
    body = "Pogoda:\n{}\n\nNewsy:\n{}".format(weather, news)

    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] ="patryk.saffer99@gmail.com"
    msg['To'] = "patryk.saffer99@gmail.com"

    server.sendmail(
        msg['From'],
        msg['To'],
        msg.as_string()
    )
    server.close()

def shownewsdetails(news, weather):
    newsURL = "https://warszawa.wyborcza.pl/warszawa/0,54420.html"
    for x in weather:
        print(x)

    for x in range(len(news)):
        print("Artykul nr {}: {}".format(x + 1, news[x]))

    najciekawszyartykul = int(input())
    driver = webdriver.Firefox()
    driver.get(newsURL)
    elem1 = driver.find_element_by_link_text(news[najciekawszyartykul - 1])
    elem1.click()


weather = getweather()
news = getnewsheaders()
sendemail(news,weather)
shownewsdetails(news,weather)
