import random
import time
from selenium.webdriver.common.by import By
from selenium import webdriver

browser = webdriver.Chrome()
browser.maximize_window()
browser.get("https://rendezvous.permisconduire.be/public/start")

time.sleep(2)

# Accept cookies
cookie_button = browser.find_element(By.XPATH, "(//button[contains(@class, 'cuip-button-primary')])[2]")
cookie_button.click()

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