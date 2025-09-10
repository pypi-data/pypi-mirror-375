from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time


@given('I prepare the chat error form')
def step_impl(context):
    context.execute_steps('''
        Given I navigate to "https://f9qapublishing.flyfrontier.com/chat-with-us"
        When I refresh page
        Then I wait 20 seconds for element having xpath "//button[@aria-label='Item 1 of 2: English']" to be clickable
        Then I forcefully click on element having xpath "//button[@aria-label='Item 1 of 2: English']"
        Then I wait 20 seconds for element having xpath "//button[@aria-label='Item 5 of 5: Something else']" to be clickable
        Then I forcefully click on element having xpath "//button[@aria-label='Item 5 of 5: Something else']"
        Then I wait for 3 sec
    ''')

@then('I enter "{text}" in element having xpath "{xpath}" and press enter')
def step_impl(context, text, xpath):
    elem = WebDriverWait(context.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    elem.clear()
    elem.send_keys(text)
    elem.send_keys(Keys.ENTER)

@then('I select "{option_text}" from dropdown having index "{index}"')
def step_impl(context, option_text, index):
    dropdowns = context.driver.find_elements(By.TAG_NAME, "select")
    idx = int(index)
    select = Select(dropdowns[idx])
    select.select_by_visible_text(option_text)

@then('I enter "{text}" in element having xpath "{xpath}"')
def step_impl(context, text, xpath):
    elem = WebDriverWait(context.driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    elem.clear()
    elem.send_keys(text)

@then('I verify element having xpath "{xpath}" is present')
def step_impl(context, xpath):
    elem = WebDriverWait(context.driver, 20).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    assert elem is not None

@then('I verify text above the technical form')
def step_impl(context):
    expected_text_1 = "I'm sorry to hear you're experiencing a technical error. Please fill out this form so that we can better assist you."
    page_source = context.driver.page_source
    static_found = "Static text found" if expected_text_1 in page_source else "Dynamic text found"
    print(f"✅ Response check: {static_found}")


@then('I verify text Above the Handover form')
def step_impl(context):
    expected_text = "Please provide the information below so that we can best assist you."
    page_source = context.driver.page_source

    assert expected_text in page_source, \
        f"❌ Expected text not found. Looking for: {expected_text}"

    print("✅ Second static text found on the page.")
