# TA API - Development V1
# Scrape data from TeachAssist Login Credentials

# Imports

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
# from flask import Flask, request, jsonify
from selenium.webdriver.chrome.options import Options
import discord
from discord.ext import commands
import os
# Debugging
# app = Flask(__name__) 

# Selenium Scraper
class Browser:
    browser, service = None, None

    # Initialize service and browser
    def __init__(self):
        options = Options()
        options.headless = True
        self.service = Service("chromedriver.exe")
        self.browser = webdriver.Chrome(service=self.service, options=options)

    # Open url
    def open_page(self, url: str):
        self.browser.get(url)

    # Close url
    def close_browser(self):
        self.browser.close()
    
    # Scan all courses within dashboard
    def scan_courses(self):
        d = self.browser.find_elements(by=By.CLASS_NAME, value='green_border_message')
        print(len(d))
        tbody = d[1].find_element(by = By.TAG_NAME, value='tbody')
        rows = tbody.find_elements(by = By.TAG_NAME, value='tr')
        courses = []
        percentages = []
        for row in rows:
            if (row != rows[0]):
                cells = row.find_elements(By.TAG_NAME, value='td')
                course = cells[0].text.strip()
                courses.append(course)
                mark = cells[2].text.strip()
                for span in cells[2].find_elements(By.TAG_NAME, value='span'):
                    mark = mark.replace(span.text.strip(),"").strip()
                percentages.append(mark)
        return courses, percentages

    #Add credentials
    def add_input(self, by: By, value: str, text: str): 
        # use: find the field using [by] & [value]-> then type in [text]
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)
        # time.sleep(1)

    #Submit item
    def click_button(self, by:By, value:str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        # time.sleep(1)

    #Set a login 
    def login_ta(self, username: str, password: str):
        self.add_input(by=By.NAME, value="username", text=username)
        self.add_input(by=By.NAME, value="password", text=password)
        self.click_button(by=By.NAME, value="submit")
        time.sleep(0.5)
        url = self.browser.current_url
        if "students" in url:
            return True
        else:
            return False

"""  
@app.route('/')
def home():
    return '<h1> hi guys </h1>'

# Provide User & Password to provide Login Credentials
@app.route('/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    browser = Browser()
    browser.open_page('https://ta.yrdsb.ca/yrdsb/')
    if browser.login_ta(username, password) == True:
        courses, marks = browser.scan_courses()
        user_data = {
            "courses" : courses,
            "marks" : marks
        }
        browser.close_browser()
        return jsonify(user_data), 200
    else:
        browser.close_browser()
        response = {
            "error" : "invalid credentials"
        }
        return jsonify(response), 400
"""
    
bot = commands.Bot(command_prefix="7!", intents=discord.Intents.all())

@bot.tree.command(name="find_marks")
async def find_marks(interaction: discord.Interaction, username: str, password : str):
    await interaction.response.defer()
    browser = Browser()
    browser.open_page('https://ta.yrdsb.ca/yrdsb/')
    login = browser.login_ta(username, password)
    if (login):
        courses, percentages = browser.scan_courses()
        browser.close_browser()
        embed = discord.Embed()
        embed.set_author(name=interaction.user.name + "'s Grades")
        for num in range(len(courses)):
            print(courses[num])
            if percentages[num] != "Please see teacher for current status regarding achievement in the course":
                embed.add_field(name = courses[num], value = percentages[num])
        await interaction.edit_original_response(embed=embed)              
    else:
        browser.close_browser()
        await interaction.edit_original_response(content="Invalid Login Details")

@bot.event
async def on_ready():
    print("up and ready")
    try: 
        sync = await bot.tree.sync()
        print(bot.tree.get_commands())
    except Exception as e:
        print(e)

token = os.environ
bot.run(token["KEY"])
