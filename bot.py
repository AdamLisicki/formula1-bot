import os 
import requests
import json
from twitchio.ext import commands
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import cloudscraper 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(
    token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL1'], os.environ['CHANNEL2']]
)


@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{os.environ['BOT_NICK']} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return
    await ctx.channel.send(ctx.content)

@bot.command(name='drivers')    
async def drivers(ctx, driver):
    url = f'http://ergast.com/api/f1/drivers/{driver}.json'
    response = requests.get(url).json()

    name = json.dumps(response['MRData']["DriverTable"]["Drivers"][0]["givenName"], indent=4).replace('"', '')
    surname = json.dumps(response['MRData']["DriverTable"]["Drivers"][0]["familyName"], indent=4).replace('"', '')
    number = json.dumps(response['MRData']["DriverTable"]["Drivers"][0]["permanentNumber"], indent=4).replace('"', '')
    birth = json.dumps(response['MRData']["DriverTable"]["Drivers"][0]["dateOfBirth"], indent=4).replace('"', '')
    nationality = json.dumps(response['MRData']["DriverTable"]["Drivers"][0]["nationality"], indent=4).replace('"', '')
    url_wiki = json.dumps(response['MRData']["DriverTable"]["Drivers"][0]["url"], indent=4).replace('"', '')

    await ctx.send(f'{name}\n {surname}\n | Number: {number}\n | Birthday: {birth}\n | Nationality: {nationality}\n | More info: {url_wiki}\n')

@bot.command(name='results')    
async def results(ctx, driver, year, round):
    url = f'http://ergast.com/api/f1/{year}/drivers/{driver}/results.json'
    response = requests.get(url).json()
    
    raceName = json.dumps(response["MRData"]["RaceTable"]["Races"][int(round)-1]["raceName"], indent=4).replace('"', '')
    date = json.dumps(response["MRData"]["RaceTable"]["Races"][int(round)-1]["date"], indent=4).replace('"', '')
    driverName = json.dumps(response["MRData"]["RaceTable"]["Races"][int(round)-1]["Results"][0]["Driver"]["givenName"], indent=4).replace('"', '')
    driverLastname = json.dumps(response["MRData"]["RaceTable"]["Races"][int(round)-1]["Results"][0]["Driver"]["familyName"], indent=4).replace('"', '')
    position = json.dumps(response["MRData"]["RaceTable"]["Races"][int(round)-1]["Results"][0]["position"], indent=4).replace('"', '')
 
    await ctx.send(f'{raceName} | {date} | {driverName} {driverLastname} | Position: {position}')

@bot.command(name='GPresults')    
async def GPresults(ctx, year, round):
    url = f'http://ergast.com/api/f1/{year}/{round}/results.json'
    response = requests.get(url).json()
    string = ''
    GP = json.dumps(response["MRData"]["RaceTable"]["Races"][0]["raceName"], indent=4).replace('"', '')
    for i in range(20):
        driver = json.dumps(response["MRData"]["RaceTable"]["Races"][0]["Results"][i]["Driver"]["code"], indent=4).replace('"', '')
        string = string + str(i+1) + "." + driver + " "

    await ctx.send(f' {GP} | {string}')

@bot.command(name='last_race')    
async def last_race(ctx):
    url = 'http://ergast.com/api/f1/current/last/results.json'
    response = requests.get(url).json()
    string = ''
    driver = ''
    GP = json.dumps(response["MRData"]["RaceTable"]["Races"][0]["raceName"], indent=4).replace('"', '')
    for i in range(20):
        driver = json.dumps(response["MRData"]["RaceTable"]["Races"][0]["Results"][i]["Driver"]["givenName"], indent=4, ensure_ascii=False).replace('"', '') + " "
        driver+= json.dumps(response["MRData"]["RaceTable"]["Races"][0]["Results"][i]["Driver"]["familyName"], indent=4, ensure_ascii=False).replace('"', '')
        
        string = string + str(i+1) + "." + driver + " | "

    await ctx.send(f' {GP} | {string}')
@bot.command(name='driver_standings')    
async def driver_standings(ctx):
    url = "http://ergast.com/api/f1/2023/driverStandings.json"
    url = "http://ergast.com/api/f1/2023/driverStandings.json"
    response = requests.get(url).json()
    result = ''
    for i in range(len(json.dumps(response["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"], indent=4).split(","))):
        try:
            result += json.dumps(response["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][i]["position"], indent=4, ensure_ascii=False).replace('"', "") + "."
            result += json.dumps(response["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][i]["Driver"]["givenName"], indent=4, ensure_ascii=False).replace('"', "") + " "
            result += json.dumps(response["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][i]["Driver"]["familyName"], indent=4, ensure_ascii=False).replace('"', "") + " "
            result += json.dumps(response["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][i]["points"], indent=4, ensure_ascii=False).replace('"', "") + " | "
        except:
            break
    await ctx.send(result)
@bot.command(name='next_race')
async def next_race(ctx):
    url = "http://ergast.com/api/f1/current/next.json"
    r = requests.get(url).json()
    date = json.dumps(r["MRData"]["RaceTable"]["Races"][0]["date"], indent=4).replace('"', "")
    time = json.dumps(r["MRData"]["RaceTable"]["Races"][0]["time"], indent=4).replace('"', "").replace("Z", "")
    country = json.dumps(r["MRData"]["RaceTable"]["Races"][0]["Circuit"]["Location"]["country"], indent=4).replace('"', "")
    raceName = json.dumps(r["MRData"]["RaceTable"]["Races"][0]["raceName"], indent=4).replace('"', "")
    circuit = json.dumps(r["MRData"]["RaceTable"]["Races"][0]["Circuit"]["circuitName"], indent=4).replace('"', "")
    split_date = date.split("-")
    split_time = time.split(":")
    my_datetime = datetime(int(split_date[0]), int(split_date[1]), int(split_date[2]), int(split_time[0]), int(split_time[1]), tzinfo= pytz.timezone('UTC'))
    race_time_pl = my_datetime.astimezone(pytz.timezone("Europe/Warsaw")).strftime('%Y-%m-%d %H:%M %Z')
    await ctx.send(f'Date and time: {race_time_pl}, Country: {country}, Race name: {raceName}, Circuit: {circuit}')

@bot.command(name='update')
async def update(ctx):


    url="https://videoharambe.com/"
# scraper = cloudscraper.create_scraper(delay=10, browser="chrome") 
# content = scraper.get(url).text
    scraper = cloudscraper.create_scraper()
    cookies = scraper.get(url).cookies.get_dict()

    options = Options()
    options.headless = True  # This runs Chrome in headless mode, remove this line if you want to see the browser in action
    browser = webdriver.Chrome(options=options)

    browser.get(url)
        
    # Add Cloudscraper's cookies to the Selenium browser instance
    for key, value in cookies.items():
        browser.add_cookie({'name': key, 'value': value})

    # Reload the page now that we've added the cookies
    browser.get(url)

    time.sleep(2)
        
    # Wait for JavaScript to load (can also use more advanced waits)
    browser.implicitly_wait(10)

    html = browser.page_source
    browser.quit()

    imgur = html.find("imgur.com/")

    # print(html[imgur+10:imgur+17])

    imgur_to_end = html[imgur+10:]

    space = imgur_to_end.find(" ")

    response = requests.get(f'https://i.imgur.com/{html[imgur+10:imgur+10+space]}')
    if response.status_code != 200:
        await ctx.send('Błąd aktualizacji wyników. Spróbuj jeszcze raz.')
        return

    f = open("wynik.txt", "a")
    f.write(f'https://i.imgur.com/{html[imgur+10:imgur+10+space]}')
    f.close()
    await ctx.send(f'Wyniki losowania zaktualizowane. Nowe wyniki: https://i.imgur.com/{html[imgur+10:imgur+10+space]}')

@bot.command(name='wyniki')
async def wyniki(ctx):
    f = open("wynik.txt", "r")
    wynik = f.read()
    f.close()
    await ctx.send(wynik)
if __name__ == "__main__":
    bot.run()
