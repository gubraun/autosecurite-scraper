#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    element_to_be_clickable
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import ssl
import random
import time


# Cronjob: Zusätzliche Bibliothek, um das Skript ohne GUI auszuführen
# from pyvirtualdisplay import Display

def accept_cookies():
    try:
        print("Wait for cookie banner...")
        
        host = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//cuip-cookies-consent-banner"))
        )

        print(
            "Check if accept button is present and clickable..."
        )

        def consent_button_clickable(_driver):
                element = host.find_element(By.XPATH, "//cuip-cookies-consent-banner//descendant::button")
                return (
                    element
                    if element.is_displayed() and element.is_enabled()
                    else False
                )

        consent_button = WebDriverWait(browser, 10).until(consent_button_clickable)
        consent_button.click()
    except Exception as e:
        print(f"Error accepting cookies: {e}")


options = Options()
# Try several ways to ensure opening the website in German language
options.add_argument("--lang=de")
options.add_argument("--accept-languages=de")
options.add_experimental_option("prefs", {"intl.accept_languages": "de,de_DE"})

browser = webdriver.Chrome(options=options)
browser.get("https://rendezvous.permisconduire.be/public/start")

time.sleep(2)

# Accept cookies
accept_cookies()

# Fill in the cadidate form
first_name = browser.find_element(By.XPATH, "//input[@id='firstName']")
first_name.send_keys("Marlene")

last_name = browser.find_element(By.XPATH, "//input[@id='lastName']")
last_name.send_keys("Braun")

bday_day = browser.find_element(By.XPATH, "//input[@name='bday-day']")
bday_day.send_keys("18")

bday_month = browser.find_element(By.XPATH, "//input[@name='bday-month']")
bday_month.send_keys("02")

bday_year = browser.find_element(By.XPATH, "//input[@name='bday-year']")
bday_year.send_keys("2007")

belgian_nrn = browser.find_element(By.XPATH, "//lib-pattern-input-text[@formcontrolname='belgianNrn']//input[@type='text']")
belgian_nrn.send_keys("07021826069")

submit_button = browser.find_element(By.XPATH, "//button[@type='submit']")
submit_button.click()

# Wait for the next page to load
time.sleep(2)

select_category = browser.find_element(By.XPATH, "//strong[text()='Prüfungskategorie B (auto)']")
select_category.click()
time.sleep(1)

select_exam = browser.find_element(By.XPATH, "//strong[text()='Praktische Prüfung B']")
select_exam.click()
time.sleep(1)

select_situation = browser.find_element(By.XPATH, "//strong[text()='Ich möchte meinen ersten Führerschein erhalten.']")
select_situation.click()
time.sleep(1)

candidate_type = browser.find_element(By.XPATH, "//span[text()='In freier Schulung']")
candidate_type.click()
time.sleep(2)

# Preliminary driver's license (PDL) form
pdl_type = browser.find_element(By.XPATH, "//span[text()=' Modell 36 Monaten ']")
pdl_type.click()

pdl_delivery_date = browser.find_element(By.XPATH, "//input[@name='pdl-delivery-date']")
pdl_delivery_date.send_keys("24/09/2024")

pdl_start_date = browser.find_element(By.XPATH, "//input[@name='pdl-start-date']")
pdl_start_date.send_keys("24/09/2024")

pdl_exp_date = browser.find_element(By.XPATH, "//input[@name='pdl-expiration-date']")
pdl_exp_date.send_keys("23/09/2027")

submit_button = browser.find_element(By.XPATH, "//button[@type='submit']")
submit_button.click()
time.sleep(2)

parent1_belgian_nrn = browser.find_element(By.XPATH, "//lib-pattern-input-text[@formcontrolname='belgianNrn']//input[@type='text']")
parent1_belgian_nrn.send_keys("07021826069")



time.sleep(5)


browser.quit()