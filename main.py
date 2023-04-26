"""
webdriver-prolific
"""

'''
IMPORTS & VARIABLES
'''

from selenium import webdriver
from random import randrange
from win10toast import ToastNotifier
from playsound import playsound
import sys
import time
import os
username = sys.argv[1]
password = sys.argv[2]
prolific_url = 'https://app.prolific.co/studies'
window_number = 0
wait_min_time = 3
wait_max_time_random = 5
file_dir = os.path.dirname(os.path.realpath('__file__'))
webdriver_path = os.path.join(file_dir, 'scripts\\chromedriver.exe')
notification_filename = os.path.join(file_dir, 'sound\\notification.mp3')

'''
FUNCTIONS
'''

def driver_setup():
    driver = webdriver.Chrome(executable_path=webdriver_path)
    driver.get(prolific_url)
    driver.implicitly_wait(wait_min_time)
    return driver

def login(driver, username, password):
    if driver.find_elements_by_xpath('//*[@id="id_username"]'):
        driver.find_element_by_xpath(
            '//*[@id="id_username"]').send_keys(username)
        if driver.find_element_by_xpath('//*[@id="loginForm"]/div[3]/div/div/input'):
            driver.find_element_by_xpath(
                '//*[@id="loginForm"]/div[3]/div/div/input').send_keys(password)
            if driver.find_elements_by_xpath('//*[@id="login"]'):
                driver.find_element_by_xpath('//*[@id="login"]').click()
                print("Logged in with: ")
                print(username)
                driver.implicitly_wait(wait_min_time)

def wait_until_survey(driver):
    no_survey = True  # bypass with False here if needed
    while no_survey:
        sleeping = randrange(wait_max_time_random) + wait_min_time
        print("Waiting: " + str(sleeping) + " seconds...")
        time.sleep(sleeping)
        driver.refresh()
        driver.implicitly_wait(wait_min_time)
        # gets cup image (meaning no surveys)
        if driver.find_elements_by_xpath("//*[@id=\"app\"]/div[2]/div/div/div/div/div/div/figure/img"):
            print("There are no surveys.\nRefreshing...")
        else:
            print("There are surveys")
            no_survey = False

def enter_survey(driver):
    # checks if there is a survey really
    if driver.find_elements_by_xpath("//*[@id=\"app\"]/div[2]/div/div/div/div/div[1]/ul/li/div/div[1]"):
        # enters first survey tab
        driver.find_element_by_xpath(
            '//*[@id=\"app\"]/div[2]/div/div/div/div/div[1]/ul/li/div/div[1]').click()
        print("Got a survey...")
        if driver.find_elements_by_xpath('//*[@id="app"]/div[2]/div/div/div/div/div[2]/div[1]/div[3]/button'):
            # reserves place in the survey (reserving is only for 10 min., after starting there is more time)
            driver.find_element_by_xpath(
                '//*[@id="app"]/div[2]/div/div/div/div/div[2]/div[1]/div[3]/button').click()
            print("Clicked on the survey... Reserved place...")
            if driver.find_elements_by_xpath('//*[@id="app"]/div[2]/div/div/div/section[2]/div/div[4]/div/form/button'):
                driver.find_element_by_xpath(
                    '//*[@id="app"]/div[2]/div/div/div/section[2]/div/div[4]/div/form/button').click()
                # PLAY NOTIFICATION
                notification(False, True)
                print("Reserved place in the survey...")
            else:
                notification(False, True)
                print("Didn't reserve a place in the survey. Maybe it's full.")
                print("Didn't start survey.")
                return
        else:
            print("Didn't click on the survey.")
            return
    else:
        print("Didn't find any survey tab.")
        return

def notification(windows_notification, sound_notification):
    # for this notification to work on Windows 10, Notification from other sources must be activated.
    if windows_notification:
        toaster = ToastNotifier()
        toaster.show_toast("Prolific", "New Study Found!!!")
    # play sound (run as admin to avoid errors here)
    if sound_notification:
        print("Playing sound notification...")
        playsound(notification_filename)

def wait_until_done(use_input, open_new_window, window_number):
    # wait for input
    if use_input:
        print("Write something in the terminal...")
        input()
        return 0
    # or open a new window
    if open_new_window:
        # prevent from opening new tabs if survey not finished
        while(driver.find_elements_by_xpath('//*[@id="app"]/div[2]/div/div/div/section[2]/div/div[4]/button[1]')):
            print("Waiting for survey to be finished...")
            time.sleep(wait_min_time*5)
        print("I think the survey is finished...")
        window_number = window_number + 1
        driver.execute_script("window.open('');")
        driver.implicitly_wait(wait_min_time)
        driver.switch_to.window(driver.window_handles[window_number])
        driver.get(prolific_url)
        return window_number

def restart_search():
    print("Searching again...")
    elem = driver.find_elements_by_xpath(
        '//*[@id="app"]/div[2]/nav/div[3]/div[1]/a[1]')
    if len(elem) > 0:
        elem[0].click()
    driver.implicitly_wait(wait_min_time)

'''
MAIN PROGRAM
'''

# SETUP & LOGIN
driver = driver_setup()
login(driver, username, password)
while(True):  # runs until stopped
    # IF NO SURVEY
    wait_until_survey(driver)
    # ENTER SURVEY
    enter_survey(driver)
    # WAIT UNTIL STUDY IS COMPLETED
    window_number = wait_until_done(False, True, window_number)
    # RESTART SEARCH
    restart_search()