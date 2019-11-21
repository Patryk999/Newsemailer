"""
Newsemailer sends email with local news and weather for the day,
this version is designed to send information from Warsaw, it can be
redesigned to other cities/countries.

before running enter your email at "EMAIL" section and 16 digit gmail password at "PASSWORD"
"""

import requests
from bs4 import BeautifulSoup
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
        if x.get_text().strip()[-1] == "0":
            time.append(x.get_text().strip())

    temp = temp[:10]
    time = time[:10]
    output = []
    for x in range(len(time)):
        output.append("At {} there will be {} degrees celsius.".format(time[x],temp[x]))

    return output

def getlinks(news):
    links = []

    for x in news:
        i = 0
        while i < len(str(x)):
            if str(x)[i-8:i] == "a href=\"":
                tempstring = ""
                while str(x)[i] is not "\"":
                    tempstring = tempstring + str(x)[i]
                    i += 1
                if tempstring not in links:
                    links.append(tempstring)
            else:
                i += 1
    return links

def getnewsheaders():
    newsURL = "https://warszawa.wyborcza.pl/warszawa/0,54420.html"
    global headers

    newslink = requests.get(newsURL, headers=headers)

    soup = BeautifulSoup(newslink.content, features='html.parser')

    newsodd = soup.findAll("li", class_="entry even article")
    newseven = soup.findAll("li", class_="entry odd article")

    linksodd = getlinks(newsodd)
    linkseven = getlinks(newseven)

    i = j = 0
    linksoddpluseven = []

    while i < len(linksodd) or j < len(linkseven):
        if i > j:
            linksoddpluseven.append(linkseven[j])
            j += 1
        else:
            linksoddpluseven.append(linksodd[i])
            i += 1

    i = j = 0
    newsoddpluseven = []

    while i < len(newsodd) or j < len(newseven):
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

    return newsheaders, linksoddpluseven

def sendemail(news,links, weather):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("EMAIL", "PASSWORD")

    i = j = 0
    newspluslinks = []

    if len(news) != len(links):
        if len(news) > len(links):
            raise ValueError("Not every news has link")
        else:
            raise ValueError("Too many links for news")
        return

    while i < len(news) or j < len(links):
        if i > j:
            newspluslinks.append(links[j])
            j += 1
        else:
            newspluslinks.append(news[i])
            i += 1

    news = "\n".join(newspluslinks)
    weather = "\n".join(weather)

    msg = EmailMessage()

    subject = "Morning Raport"
    body = "Weather:\n{}\n\nNews:\n{}".format(weather, news)

    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "EMAIL"
    msg['To'] = "EMAIL"

    server.sendmail(
        msg['From'],
        msg['To'],
        msg.as_string()
    )
    server.close()

def main():
    weather = getweather()
    news, links = getnewsheaders()
    sendemail(news, links, weather)

if __name__ == "__main__":
    main()