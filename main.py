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
        host = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//cuip-cookies-consent-banner"))
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

def enter_candidate_details():
    try:
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

        browser.find_element(By.XPATH, "//button[@type='submit']").click()
    except Exception as e:
        print(f"Error entering candidate details: {e}")

def enter_test_details():
    try:
        category = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//strong[text()='Prüfungskategorie B (auto)']"))
        )
        category.click()

        exam_type = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//strong[text()='Praktische Prüfung B']"))
        )
        exam_type.click()

        situation = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//strong[text()='Ich möchte meinen ersten Führerschein erhalten.']"))
        )
        situation.click()

        training = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//span[text()='In freier Schulung']"))
        )
        training.click()

        # Preliminary driver's license (PDL) details
        pdl_type = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//span[text()=' Modell 36 Monaten ']"))
        )
        pdl_type.click()

        pdl_delivery_date = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//input[@name='pdl-delivery-date']"))
        )
        pdl_delivery_date.send_keys("24/09/2024")

        pdl_start_date = browser.find_element(By.XPATH, "//input[@name='pdl-start-date']")
        pdl_start_date.send_keys("24/09/2024")

        pdl_expiry_date = browser.find_element(By.XPATH, "//input[@name='pdl-expiration-date']")
        pdl_expiry_date.send_keys("23/09/2027")

        browser.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Instructor details
        primary_instructor_nrn = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//lib-pattern-input-text[@formcontrolname='belgianNrn']//input[@type='text']"))
        )
        primary_instructor_nrn.send_keys("74.11.21-502.14")
        browser.find_element(By.XPATH, "//button[@type='submit']").click()

        # Secondary instructor
        secondary_instructor = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//app-value-selector[@class='me-3']//div[text()=' Ja ']"))
        )
        secondary_instructor.click() 

        secondary_instructor_nrn = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//lib-pattern-input-text[@formcontrolname='belgianNrn']//input[@type='text']"))
        )
        secondary_instructor_nrn.send_keys("74.07.02-629.41")
        browser.find_element(By.XPATH, "//button[@type='submit']").click()
    except Exception as e:
        print(f"Error entering test details: {e}")

def find_test_dates():
    available_dates = []
    try:
        site = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//app-site-selector//descendant::input[@type='text']"))
        )   
        site.click()

        WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//ng-dropdown-panel[@aria-label='Options list']"))
        )
        site.send_keys("4731")

        site_eupen = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//span[text()='Führerscheinzentrum Eupen (1029)']"))
        )
        site_eupen.click()

        date_nav = WebDriverWait(browser, 10).until(
            presence_of_element_located((By.XPATH, "//app-date-navigator"))
        )

        for i in range(3):  # Loop through the next 3 months
            # Extract the month name from the date navigator
            month_name = date_nav.find_element(By.XPATH, ".//div[contains(@class, 'ngb-dp-month-name')]").text
    
            # Find all matching "simple-day" divs with an available-offer-bubble sibling
            available_days = browser.find_elements(
                By.XPATH,
                "//div[contains(@class, 'simple-day')][following-sibling::span[contains(@class, 'available-offer-bubble')]]"
            )

            for day in available_days:
                day_number = day.text.strip()
                day.click()
                WebDriverWait(browser, 10).until(
                    presence_of_element_located((By.CLASS_NAME, "sites-offers"))
                )
                # Check for offers in German language on that day
                offer_buttons = browser.find_elements(
                    By.XPATH,
                    "//app-offer-button//span[contains(@class, 'flag-icon-fr')]"
                )
                if len(offer_buttons) > 0 and offer_buttons[0].is_displayed():
                    # For simplicity, we only store the day if at least one offer is available
                    available_dates.append(f"{day_number} {month_name}")
                date_nav.click()
                WebDriverWait(browser, 10).until(
                    presence_of_element_located((By.XPATH, "//app-date-navigator"))
                )
            browser.find_element(By.XPATH, "//button[@title='Next month']").click()
            time.sleep(1)

        return available_dates
    except Exception as e:
        print(f"Error finding test dates: {e}")
        return []


options = Options()
# Try several ways to ensure opening the website in German language
options.add_argument("--lang=de")
options.add_argument("--accept-languages=de")
options.add_experimental_option("prefs", {"intl.accept_languages": "de,de_DE"})

browser = webdriver.Chrome(options=options)
browser.get("https://rendezvous.permisconduire.be/public/start")
time.sleep(2)

# Walk through the steps to book an appointment
accept_cookies()
enter_candidate_details()
enter_test_details()
available_dates = find_test_dates()

# Print all available exam dates
if not available_dates:
    print("No available test dates found.")
else:  
    print("Available test dates:")
    for date in available_dates:
        print(date)

browser.quit()
