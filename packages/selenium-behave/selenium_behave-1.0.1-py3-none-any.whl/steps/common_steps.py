from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException, NoSuchFrameException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.ui import Select
import requests
from PIL import Image, ImageChops
from io import BytesIO
import imagehash
import os
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<--------Navigation Steps-------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#
###### ---------- To open/close URL and to navigate between pages use following steps : -----------####

# 🟢 Navigate to a given URL
@given('I navigate to "{url}"')
@when('I navigate to "{url}"')
@then('I navigate to "{url}"')
def navigate_to_url(context, url):
    context.driver.get(url)
"""    if not hasattr(context, "driver") or context.driver is None:
        context.driver = webdriver.Chrome()
        context.driver.maximize_window()
    context.driver.get(url)"""

# 🟢 Navigate forward
@given("I navigate forward")
@when("I navigate forward")
@then("I navigate forward")
def navigate_forward(context):
    assert context.driver is not None, "❌ Browser is not open!"
    context.driver.forward()

# 🟢 Navigate back
@given("I navigate back")
@when("I navigate back")
@then("I navigate back")
def navigate_back(context):
    assert context.driver is not None, "❌ Browser is not open!"
    context.driver.back()

# 🟢 Refresh the page
@given("I refresh page")
@when("I refresh page")
@then("I refresh page")
def refresh_page(context):
    assert context.driver is not None, "❌ Browser is not open!"
    context.driver.refresh()


###### ---------- To switch between windows use following steps : -----------####

# store main window handle once browser is launched
@given("I store main window")
@when("I store main window")
@then("I store main window")
def step_store_main_window(context):
    context.main_window = context.driver.current_window_handle


@given("I switch to new window")
@when("I switch to new window")
@then("I switch to new window")
def step_switch_new_window(context):
    handles = context.driver.window_handles
    if len(handles) > 1:
        context.driver.switch_to.window(handles[-1])
    else:
        raise NoSuchWindowException("❌ No new window found to switch.")


@given("I switch to previous window")
@when("I switch to previous window")
@then("I switch to previous window")
def step_switch_previous_window(context):
    handles = context.driver.window_handles
    if len(handles) > 1:
        context.driver.switch_to.window(handles[-2])
    else:
        raise NoSuchWindowException("❌ No previous window found to switch.")


@given('I switch to window having title "{title}"')
@when('I switch to window having title "{title}"')
@then('I switch to window having title "{title}"')
def step_switch_by_title(context, title):
    for handle in context.driver.window_handles:
        context.driver.switch_to.window(handle)
        if context.driver.title == title:
            return
    raise NoSuchWindowException(f"❌ No window with title '{title}' found.")


@given('I switch to window having url "{url}"')
@when('I switch to window having url "{url}"')
@then('I switch to window having url "{url}"')
def step_switch_by_url(context, url):
    for handle in context.driver.window_handles:
        context.driver.switch_to.window(handle)
        if context.driver.current_url == url:
            return
    raise NoSuchWindowException(f"❌ No window with URL '{url}' found.")


@given("I close new window")
@when("I close new window")
@then("I close new window")
def step_close_new_window(context):
    handles = context.driver.window_handles
    if len(handles) > 1:
        context.driver.close()
        context.driver.switch_to.window(handles[0])  # back to first
    else:
        raise NoSuchWindowException("❌ No new window to close.")


@given("I switch to main window")
@when("I switch to main window")
@then("I switch to main window")
def step_switch_main_window(context):
    if hasattr(context, "main_window"):
        context.driver.switch_to.window(context.main_window)
    else:
        raise NoSuchWindowException("❌ Main window not stored. Use 'I store main window' first.")


###### ---------- To switch between frames use following steps : -----------####

@given('I switch to frame "{frame_name}"')
@when('I switch to frame "{frame_name}"')
@then('I switch to frame "{frame_name}"')
def step_switch_to_frame(context, frame_name):
    try:
        context.driver.switch_to.frame(frame_name)
    except Exception as e:
        raise NoSuchFrameException(f"❌ Frame '{frame_name}' not found. Error: {str(e)}")


@given("I switch to main content")
@when("I switch to main content")
@then("I switch to main content")
def step_switch_to_main_content(context):
    context.driver.switch_to.default_content()


###### ---------- To interact with browser use following steps : -----------####

@given('I resize browser window size to width {width:d} and height {height:d}')
@when('I resize browser window size to width {width:d} and height {height:d}')
@then('I resize browser window size to width {width:d} and height {height:d}')
def step_resize_browser(context, width, height):
    context.driver.set_window_size(width, height)


@given("I maximize browser window")
@when("I maximize browser window")
@then("I maximize browser window")
def step_maximize_browser(context):
    context.driver.maximize_window()

@given("I close browser")
@when("I close browser")
@then("I close browser")
def step_close_browser(context):
    context.driver.close()

###### ---------- To zoom in/out webpage use following steps : -----------####

@given("I zoom in page")
@when("I zoom in page")
@then("I zoom in page")
def step_zoom_in(context):
    context.driver.execute_script("document.body.style.zoom='125%'")   # 125% zoom

@given("I zoom out page")
@when("I zoom out page")
@then("I zoom out page")
def step_zoom_out(context):
    context.driver.execute_script("document.body.style.zoom='75%'")    # 75% zoom


###### ---------- To zoom out webpage till element is visible -----------####

def zoom_out_till_element(context, by, locator):
    zoom = 100
    while zoom >= 30:   # Zoom-out till 30%
        try:
            elem = context.driver.find_element(by, locator)
            if elem.is_displayed():
                return
        except NoSuchElementException:
            pass

        zoom -= 10
        context.driver.execute_script(f"document.body.style.zoom='{zoom}%'")
        time.sleep(0.5)

    raise AssertionError(f"❌ Element not found even after zooming out. Locator: {by}={locator}")


@given('I zoom out page till I see element having id "{elem_id}"')
@when('I zoom out page till I see element having id "{elem_id}"')
@then('I zoom out page till I see element having id "{elem_id}"')
def step_zoom_out_till_id(context, elem_id):
    zoom_out_till_element(context, By.ID, elem_id)


@given('I zoom out page till I see element having name "{name}"')
@when('I zoom out page till I see element having name "{name}"')
@then('I zoom out page till I see element having name "{name}"')
def step_zoom_out_till_name(context, name):
    zoom_out_till_element(context, By.NAME, name)


@given('I zoom out page till I see element having class "{cls}"')
@when('I zoom out page till I see element having class "{cls}"')
@then('I zoom out page till I see element having class "{cls}"')
def step_zoom_out_till_class(context, cls):
    zoom_out_till_element(context, By.CLASS_NAME, cls)


@given('I zoom out page till I see element having xpath "{xpath}"')
@when('I zoom out page till I see element having xpath "{xpath}"')
@then('I zoom out page till I see element having xpath "{xpath}"')
def step_zoom_out_till_xpath(context, xpath):
    zoom_out_till_element(context, By.XPATH, xpath)


@given('I zoom out page till I see element having css "{css}"')
@when('I zoom out page till I see element having css "{css}"')
@then('I zoom out page till I see element having css "{css}"')
def step_zoom_out_till_css(context, css):
    zoom_out_till_element(context, By.CSS_SELECTOR, css)

###### ---------- To reset webpage view -----------####

@given("I reset page view")
@when("I reset page view")
@then("I reset page view")
def step_reset_page_view(context):
    context.driver.execute_script("document.body.style.zoom='100%'")


###### ---------- To scroll webpage use following steps : -----------####

@given("I scroll to top of page")
@when("I scroll to top of page")
@then("I scroll to top of page")
def step_scroll_to_top(context):
    context.driver.execute_script("window.scrollTo(0, 0);")


@given("I scroll to end of page")
@when("I scroll to end of page")
@then("I scroll to end of page")
def step_scroll_to_end(context):
    context.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


###### ---------- To scroll webpage to specific element use following steps : -----------####

@given('I scroll to element having id "{element_id}"')
@when('I scroll to element having id "{element_id}"')
@then('I scroll to element having id "{element_id}"')
def step_scroll_to_element_by_id(context, element_id):
    element = context.driver.find_element("id", element_id)
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)


@given('I scroll to element having name "{element_name}"')
@when('I scroll to element having name "{element_name}"')
@then('I scroll to element having name "{element_name}"')
def step_scroll_to_element_by_name(context, element_name):
    element = context.driver.find_element("name", element_name)
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)


@given('I scroll to element having class "{class_name}"')
@when('I scroll to element having class "{class_name}"')
@then('I scroll to element having class "{class_name}"')
def step_scroll_to_element_by_class(context, class_name):
    element = context.driver.find_element("class name", class_name)
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)


@given('I scroll to element having xpath "{xpath}"')
@when('I scroll to element having xpath "{xpath}"')
@then('I scroll to element having xpath "{xpath}"')
def step_scroll_to_element_by_xpath(context, xpath):
    element = context.driver.find_element("xpath", xpath)
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)


@given('I scroll to element having css "{css_selector}"')
@when('I scroll to element having css "{css_selector}"')
@then('I scroll to element having css "{css_selector}"')
def step_scroll_to_element_by_css(context, css_selector):
    element = context.driver.find_element("css selector", css_selector)
    context.driver.execute_script("arguments[0].scrollIntoView(true);", element)




###### ---------- To hover over an element use following steps : -----------####

@given('I hover over element having id "{element_id}"')
@when('I hover over element having id "{element_id}"')
@then('I hover over element having id "{element_id}"')
def step_hover_element_by_id(context, element_id):
    element = context.driver.find_element("id", element_id)
    ActionChains(context.driver).move_to_element(element).perform()


@given('I hover over element having name "{element_name}"')
@when('I hover over element having name "{element_name}"')
@then('I hover over element having name "{element_name}"')
def step_hover_element_by_name(context, element_name):
    element = context.driver.find_element("name", element_name)
    ActionChains(context.driver).move_to_element(element).perform()


@given('I hover over element having class "{class_name}"')
@when('I hover over element having class "{class_name}"')
@then('I hover over element having class "{class_name}"')
def step_hover_element_by_class(context, class_name):
    element = context.driver.find_element("class name", class_name)
    ActionChains(context.driver).move_to_element(element).perform()


@given('I hover over element having xpath "{xpath}"')
@when('I hover over element having xpath "{xpath}"')
@then('I hover over element having xpath "{xpath}"')
def step_hover_element_by_xpath(context, xpath):
    element = context.driver.find_element("xpath", xpath)
    ActionChains(context.driver).move_to_element(element).perform()


@given('I hover over element having css "{css_selector}"')
@when('I hover over element having css "{css_selector}"')
@then('I hover over element having css "{css_selector}"')
def step_hover_element_by_css(context, css_selector):
    element = context.driver.find_element("css selector", css_selector)
    ActionChains(context.driver).move_to_element(element).perform()



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<--------Assertion Steps-------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#

###### ---------- To assert that page title can be found use following steps : -----------####

@given('I should see page title as "{title}"')
@when('I should see page title as "{title}"')
@then('I should see page title as "{title}"')
def step_assert_page_title(context, title):
    actual_title = context.driver.title
    assert actual_title == title, f"❌ Expected title '{title}' but got '{actual_title}'"


@given('I should not see page title as "{title}"')
@when('I should not see page title as "{title}"')
@then('I should not see page title as "{title}"')
def step_assert_not_page_title(context, title):
    actual_title = context.driver.title
    assert actual_title != title, f"❌ Expected title not to be '{title}', but it was."


@given('I should see page title having partial text as "{partial_text}"')
@when('I should see page title having partial text as "{partial_text}"')
@then('I should see page title having partial text as "{partial_text}"')
def step_assert_page_title_contains(context, partial_text):
    actual_title = context.driver.title
    assert partial_text in actual_title, f"❌ Expected partial title '{partial_text}' but got '{actual_title}'"


@given('I should not see page title having partial text as "{partial_text}"')
@when('I should not see page title having partial text as "{partial_text}"')
@then('I should not see page title having partial text as "{partial_text}"')
def step_assert_page_title_not_contains(context, partial_text):
    actual_title = context.driver.title
    assert partial_text not in actual_title, f"❌ Expected title not to contain '{partial_text}', but got '{actual_title}'"


###### ---------- To assert element text use any of the following steps ---------- ######

###### ---------- Helper function to find element ---------- ######
def find_element_1(context, locator_type, locator_value):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
    }
    return context.driver.find_element(by_map[locator_type], locator_value)



# Exact text match
@given('element having {locator_type} "{locator_value}" should have text as "{expected_text}"')
@when('element having {locator_type} "{locator_value}" should have text as "{expected_text}"')
@then('element having {locator_type} "{locator_value}" should have text as "{expected_text}"')
def step_element_text_equals(context, locator_type, locator_value, expected_text):
    elem = find_element_1(context, locator_type, locator_value)
    actual_text = elem.text.strip()
    assert actual_text == expected_text, f"❌ Expected text '{expected_text}' but got '{actual_text}'"


# Partial text match
@given('element having {locator_type} "{locator_value}" should have partial text as "{partial_text}"')
@when('element having {locator_type} "{locator_value}" should have partial text as "{partial_text}"')
@then('element having {locator_type} "{locator_value}" should have partial text as "{partial_text}"')
def step_element_text_contains(context, locator_type, locator_value, partial_text):
    elem = find_element_1(context, locator_type, locator_value)
    actual_text = elem.text.strip()
    assert partial_text in actual_text, f"❌ Expected text to contain '{partial_text}' but got '{actual_text}'"


# Should NOT have exact text
@given('element having {locator_type} "{locator_value}" should not have text as "{unexpected_text}"')
@when('element having {locator_type} "{locator_value}" should not have text as "{unexpected_text}"')
@then('element having {locator_type} "{locator_value}" should not have text as "{unexpected_text}"')
def step_element_text_not_equals(context, locator_type, locator_value, unexpected_text):
    elem = find_element_1(context, locator_type, locator_value)
    actual_text = elem.text.strip()
    assert actual_text != unexpected_text, f"❌ Expected text not to be '{unexpected_text}', but got '{actual_text}'"


# Should NOT have partial text
@given('element having {locator_type} "{locator_value}" should not have partial text as "{partial_text}"')
@when('element having {locator_type} "{locator_value}" should not have partial text as "{partial_text}"')
@then('element having {locator_type} "{locator_value}" should not have partial text as "{partial_text}"')
def step_element_text_not_contains(context, locator_type, locator_value, partial_text):
    elem = find_element_1(context, locator_type, locator_value)
    actual_text = elem.text.strip()
    assert partial_text not in actual_text, f"❌ Expected text not to contain '{partial_text}', but got '{actual_text}'"



###### ---------- To assert element attribute use any of the following steps : ---------- ######

# ✅ Should have attribute with value
@given('element having {locator_type} "{locator_value}" should have attribute "{attr_name}" with value "{expected_value}"')
@when('element having {locator_type} "{locator_value}" should have attribute "{attr_name}" with value "{expected_value}"')
@then('element having {locator_type} "{locator_value}" should have attribute "{attr_name}" with value "{expected_value}"')
def step_element_attribute_equals(context, locator_type, locator_value, attr_name, expected_value):
    elem = find_element_1(context, locator_type, locator_value)
    actual_value = elem.get_attribute(attr_name)
    assert actual_value == expected_value, f"❌ Expected attribute '{attr_name}' to be '{expected_value}', but got '{actual_value}'"


# ❌ Should NOT have attribute with value
@given('element having {locator_type} "{locator_value}" should not have attribute "{attr_name}" with value "{unexpected_value}"')
@when('element having {locator_type} "{locator_value}" should not have attribute "{attr_name}" with value "{unexpected_value}"')
@then('element having {locator_type} "{locator_value}" should not have attribute "{attr_name}" with value "{unexpected_value}"')
def step_element_attribute_not_equals(context, locator_type, locator_value, attr_name, unexpected_value):
    elem = find_element_1(context, locator_type, locator_value)
    actual_value = elem.get_attribute(attr_name)
    assert actual_value != unexpected_value, f"❌ Expected attribute '{attr_name}' not to be '{unexpected_value}', but got '{actual_value}'"

###### ---------- To assert that element is enabled use any of the following steps : ---------- ######
@given('element having {locator_type} "{locator_value}" should be enabled')
@when('element having {locator_type} "{locator_value}" should be enabled')
@then('element having {locator_type} "{locator_value}" should be enabled')
def step_element_should_be_enabled(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    assert elem.is_enabled(), f"❌ Element with {locator_type} '{locator_value}' is NOT enabled!"


###### ---------- To assert that element is disabled use any of the following steps : ---------- ######
@given('element having {locator_type} "{locator_value}" should be disabled')
@when('element having {locator_type} "{locator_value}" should be disabled')
@then('element having {locator_type} "{locator_value}" should be disabled')
def step_element_should_be_disabled(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    assert not elem.is_enabled(), f"❌ Element with {locator_type} '{locator_value}' is ENABLED but expected DISABLED!"

###### ---------- Helper function to find element(s) ---------- ######
def find_element_2(context, locator_type, locator_value):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
    }
    return context.driver.find_elements(by_map[locator_type], locator_value)

###### ---------- To assert that element is present use any of the following steps : ---------- ######
@given('element having {locator_type} "{locator_value}" should be present')
@when('element having {locator_type} "{locator_value}" should be present')
@then('element having {locator_type} "{locator_value}" should be present')
def step_element_should_be_present(context, locator_type, locator_value):
    elem = find_element_2(context, locator_type, locator_value)
    assert len(elem) > 0, f"❌ Element with {locator_type} '{locator_value}' is NOT present on page!"


###### ---------- To assert that element is not present use any of the following steps: ---------- ######

@given('element having {locator_type} "{locator_value}" should not be present')
@when('element having {locator_type} "{locator_value}" should not be present')
@then('element having {locator_type} "{locator_value}" should not be present')
def step_element_should_not_be_present(context, locator_type, locator_value):
    elem = find_element_2(context, locator_type, locator_value)
    assert len(elem) == 0, f"❌ Element with {locator_type} '{locator_value}' IS present on page, but it should NOT be!"

###### ---------- To assert that checkbox is checked use any of the following steps: ---------- ######

@given('checkbox having {locator_type} "{locator_value}" should be checked')
@when('checkbox having {locator_type} "{locator_value}" should be checked')
@then('checkbox having {locator_type} "{locator_value}" should be checked')
def step_checkbox_should_be_checked(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    assert elem.is_selected(), f"❌ Checkbox with {locator_type}='{locator_value}' is NOT checked!"


###### ---------- To assert that checkbox is unchecked use any of the following steps : ---------- ######

@given('checkbox having {locator_type} "{locator_value}" should be unchecked')
@when('checkbox having {locator_type} "{locator_value}" should be unchecked')
@then('checkbox having {locator_type} "{locator_value}" should be unchecked')
def step_checkbox_should_be_unchecked(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    assert not elem.is_selected(), f"❌ Checkbox with {locator_type}='{locator_value}' is CHECKED, but expected UNCHECKED!"


###### ---------- To assert that option by text from dropdown list selected use following steps : ---------- ######

# -------- helper for dropdown text assertion --------
def _assert_dropdown_selected_by_text(context, locator_type, locator_value, expected_text):
    elem = find_element_1(context, locator_type, locator_value)
    try:
        sel = Select(elem)
    except Exception as e:
        raise AssertionError(f"❌ Element ({locator_type}='{locator_value}') is not a <select>. Error: {e}")

    expected = expected_text.strip()

    # Text extraction for selected options
    try:
        selected_texts = [o.text.strip() for o in sel.all_selected_options]
        if not selected_texts:  # single-select ke liye fallback
            selected_texts = [sel.first_selected_option.text.strip()]
    except NoSuchElementException:
        selected_texts = []

    assert expected in selected_texts, (
        f"❌ Expected option text '{expected}' to be selected in dropdown "
        f"({locator_type}='{locator_value}'), but selected: {selected_texts or '[]'}"
    )


# ---- ID ----
@given('option "{text}" by text from dropdown having id "{locator}" should be selected')
@when('option "{text}" by text from dropdown having id "{locator}" should be selected')
@then('option "{text}" by text from dropdown having id "{locator}" should be selected')
def step_dropdown_selected_text_id(context, text, locator):
    _assert_dropdown_selected_by_text(context, "id", locator, text)


# ---- NAME ----
@given('option "{text}" by text from dropdown having name "{locator}" should be selected')
@when('option "{text}" by text from dropdown having name "{locator}" should be selected')
@then('option "{text}" by text from dropdown having name "{locator}" should be selected')
def step_dropdown_selected_text_name(context, text, locator):
    _assert_dropdown_selected_by_text(context, "name", locator, text)


# ---- CLASS ----
@given('option "{text}" by text from dropdown having class "{locator}" should be selected')
@when('option "{text}" by text from dropdown having class "{locator}" should be selected')
@then('option "{text}" by text from dropdown having class "{locator}" should be selected')
def step_dropdown_selected_text_class(context, text, locator):
    _assert_dropdown_selected_by_text(context, "class", locator, text)


# ---- XPATH ----
@given('option "{text}" by text from dropdown having xpath "{locator}" should be selected')
@when('option "{text}" by text from dropdown having xpath "{locator}" should be selected')
@then('option "{text}" by text from dropdown having xpath "{locator}" should be selected')
def step_dropdown_selected_text_xpath(context, text, locator):
    _assert_dropdown_selected_by_text(context, "xpath", locator, text)


# ---- CSS ----
@given('option "{text}" by text from dropdown having css "{locator}" should be selected')
@when('option "{text}" by text from dropdown having css "{locator}" should be selected')
@then('option "{text}" by text from dropdown having css "{locator}" should be selected')
def step_dropdown_selected_text_css(context, text, locator):
    _assert_dropdown_selected_by_text(context, "css", locator, text)



###### ---------- To assert that option by value from dropdown list selected use following steps : ---------- ######



# -------- helper for dropdown value assertion --------
def _assert_dropdown_selected_by_value(context, locator_type, locator_value, expected_value):
    elem = find_element_1(context, locator_type, locator_value)
    try:
        sel = Select(elem)
    except Exception as e:
        raise AssertionError(f"❌ Element ({locator_type}='{locator_value}') is not a <select>. Error: {e}")

    expected = expected_value.strip()

    # selected options ke values nikal lo
    try:
        selected_values = [o.get_attribute("value").strip() for o in sel.all_selected_options]
        if not selected_values:  # Fallback for single-select
            selected_values = [sel.first_selected_option.get_attribute("value").strip()]
    except NoSuchElementException:
        selected_values = []

    assert expected in selected_values, (
        f"❌ Expected option value '{expected}' to be selected in dropdown "
        f"({locator_type}='{locator_value}'), but selected: {selected_values or '[]'}"
    )


# ---- ID ----
@given('option "{value}" by value from dropdown having id "{locator}" should be selected')
@when('option "{value}" by value from dropdown having id "{locator}" should be selected')
@then('option "{value}" by value from dropdown having id "{locator}" should be selected')
def step_dropdown_selected_value_id(context, value, locator):
    _assert_dropdown_selected_by_value(context, "id", locator, value)


# ---- NAME ----
@given('option "{value}" by value from dropdown having name "{locator}" should be selected')
@when('option "{value}" by value from dropdown having name "{locator}" should be selected')
@then('option "{value}" by value from dropdown having name "{locator}" should be selected')
def step_dropdown_selected_value_name(context, value, locator):
    _assert_dropdown_selected_by_value(context, "name", locator, value)


# ---- CLASS ----
@given('option "{value}" by value from dropdown having class "{locator}" should be selected')
@when('option "{value}" by value from dropdown having class "{locator}" should be selected')
@then('option "{value}" by value from dropdown having class "{locator}" should be selected')
def step_dropdown_selected_value_class(context, value, locator):
    _assert_dropdown_selected_by_value(context, "class", locator, value)


# ---- XPATH ----
@given('option "{value}" by value from dropdown having xpath "{locator}" should be selected')
@when('option "{value}" by value from dropdown having xpath "{locator}" should be selected')
@then('option "{value}" by value from dropdown having xpath "{locator}" should be selected')
def step_dropdown_selected_value_xpath(context, value, locator):
    _assert_dropdown_selected_by_value(context, "xpath", locator, value)


# ---- CSS ----
@given('option "{value}" by value from dropdown having css "{locator}" should be selected')
@when('option "{value}" by value from dropdown having css "{locator}" should be selected')
@then('option "{value}" by value from dropdown having css "{locator}" should be selected')
def step_dropdown_selected_value_css(context, value, locator):
    _assert_dropdown_selected_by_value(context, "css", locator, value)


###### ---------- To assert that option by text from dropdown list unselected use following steps : ---------- ######

# -------- helper for dropdown text unselected assertion --------
def _assert_dropdown_unselected_by_text(context, locator_type, locator_value, expected_text):
    elem = find_element_1(context, locator_type, locator_value)
    try:
        sel = Select(elem)
    except Exception as e:
        raise AssertionError(f"❌ Element ({locator_type}='{locator_value}') is not a <select>. Error: {e}")

    expected = expected_text.strip()

    try:
        selected_texts = [o.text.strip() for o in sel.all_selected_options]
        if not selected_texts:  # fallback
            selected_texts = [sel.first_selected_option.text.strip()]
    except NoSuchElementException:
        selected_texts = []

    assert expected not in selected_texts, (
        f"❌ Option text '{expected}' is unexpectedly SELECTED in dropdown "
        f"({locator_type}='{locator_value}'). Currently selected: {selected_texts or '[]'}"
    )


# ---- ID ----
@given('option "{text}" by text from dropdown having id "{locator}" should be unselected')
@when('option "{text}" by text from dropdown having id "{locator}" should be unselected')
@then('option "{text}" by text from dropdown having id "{locator}" should be unselected')
def step_dropdown_unselected_text_id(context, text, locator):
    _assert_dropdown_unselected_by_text(context, "id", locator, text)


# ---- NAME ----
@given('option "{text}" by text from dropdown having name "{locator}" should be unselected')
@when('option "{text}" by text from dropdown having name "{locator}" should be unselected')
@then('option "{text}" by text from dropdown having name "{locator}" should be unselected')
def step_dropdown_unselected_text_name(context, text, locator):
    _assert_dropdown_unselected_by_text(context, "name", locator, text)


# ---- CLASS ----
@given('option "{text}" by text from dropdown having class "{locator}" should be unselected')
@when('option "{text}" by text from dropdown having class "{locator}" should be unselected')
@then('option "{text}" by text from dropdown having class "{locator}" should be unselected')
def step_dropdown_unselected_text_class(context, text, locator):
    _assert_dropdown_unselected_by_text(context, "class", locator, text)


# ---- XPATH ----
@given('option "{text}" by text from dropdown having xpath "{locator}" should be unselected')
@when('option "{text}" by text from dropdown having xpath "{locator}" should be unselected')
@then('option "{text}" by text from dropdown having xpath "{locator}" should be unselected')
def step_dropdown_unselected_text_xpath(context, text, locator):
    _assert_dropdown_unselected_by_text(context, "xpath", locator, text)


# ---- CSS ----
@given('option "{text}" by text from dropdown having css "{locator}" should be unselected')
@when('option "{text}" by text from dropdown having css "{locator}" should be unselected')
@then('option "{text}" by text from dropdown having css "{locator}" should be unselected')
def step_dropdown_unselected_text_css(context, text, locator):
    _assert_dropdown_unselected_by_text(context, "css", locator, text)

###### ---------- To assert that option by value from dropdown list unselected use following steps : ---------- ######

# -------- helper for dropdown value unselected assertion --------
def _assert_dropdown_unselected_by_value(context, locator_type, locator_value, expected_value):
    elem = find_element_1(context, locator_type, locator_value)
    try:
        sel = Select(elem)
    except Exception as e:
        raise AssertionError(f"❌ Element ({locator_type}='{locator_value}') is not a <select>. Error: {e}")

    expected = expected_value.strip()

    try:
        selected_values = [o.get_attribute("value").strip() for o in sel.all_selected_options if o.get_attribute("value")]
        if not selected_values:  # fallback
            selected_values = [sel.first_selected_option.get_attribute("value").strip()]
    except NoSuchElementException:
        selected_values = []

    assert expected not in selected_values, (
        f"❌ Option value '{expected}' is unexpectedly SELECTED in dropdown "
        f"({locator_type}='{locator_value}'). Currently selected: {selected_values or '[]'}"
    )


# ---- ID ----
@given('option "{value}" by value from dropdown having id "{locator}" should be unselected')
@when('option "{value}" by value from dropdown having id "{locator}" should be unselected')
@then('option "{value}" by value from dropdown having id "{locator}" should be unselected')
def step_dropdown_unselected_value_id(context, value, locator):
    _assert_dropdown_unselected_by_value(context, "id", locator, value)


# ---- NAME ----
@given('option "{value}" by value from dropdown having name "{locator}" should be unselected')
@when('option "{value}" by value from dropdown having name "{locator}" should be unselected')
@then('option "{value}" by value from dropdown having name "{locator}" should be unselected')
def step_dropdown_unselected_value_name(context, value, locator):
    _assert_dropdown_unselected_by_value(context, "name", locator, value)


# ---- CLASS ----
@given('option "{value}" by value from dropdown having class "{locator}" should be unselected')
@when('option "{value}" by value from dropdown having class "{locator}" should be unselected')
@then('option "{value}" by value from dropdown having class "{locator}" should be unselected')
def step_dropdown_unselected_value_class(context, value, locator):
    _assert_dropdown_unselected_by_value(context, "class", locator, value)


# ---- XPATH ----
@given('option "{value}" by value from dropdown having xpath "{locator}" should be unselected')
@when('option "{value}" by value from dropdown having xpath "{locator}" should be unselected')
@then('option "{value}" by value from dropdown having xpath "{locator}" should be unselected')
def step_dropdown_unselected_value_xpath(context, value, locator):
    _assert_dropdown_unselected_by_value(context, "xpath", locator, value)


# ---- CSS ----
@given('option "{value}" by value from dropdown having css "{locator}" should be unselected')
@when('option "{value}" by value from dropdown having css "{locator}" should be unselected')
@then('option "{value}" by value from dropdown having css "{locator}" should be unselected')
def step_dropdown_unselected_value_css(context, value, locator):
    _assert_dropdown_unselected_by_value(context, "css", locator, value)


###### ---------- To assert that radio button selected use any of the following steps : ---------- ######

# -------- helper for asserting radio button selected --------
def _assert_radio_selected(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    assert elem.is_selected(), (
        f"❌ Radio button with {locator_type}='{locator_value}' is NOT selected!"
    )


# ---- ID ----
@given('radio button having id "{locator}" should be selected')
@when('radio button having id "{locator}" should be selected')
@then('radio button having id "{locator}" should be selected')
def step_radio_selected_id(context, locator):
    _assert_radio_selected(context, "id", locator)


# ---- NAME ----
@given('radio button having name "{locator}" should be selected')
@when('radio button having name "{locator}" should be selected')
@then('radio button having name "{locator}" should be selected')
def step_radio_selected_name(context, locator):
    _assert_radio_selected(context, "name", locator)


# ---- CLASS ----
@given('radio button having class "{locator}" should be selected')
@when('radio button having class "{locator}" should be selected')
@then('radio button having class "{locator}" should be selected')
def step_radio_selected_class(context, locator):
    _assert_radio_selected(context, "class", locator)


# ---- XPATH ----
@given('radio button having xpath "{locator}" should be selected')
@when('radio button having xpath "{locator}" should be selected')
@then('radio button having xpath "{locator}" should be selected')
def step_radio_selected_xpath(context, locator):
    _assert_radio_selected(context, "xpath", locator)


# ---- CSS ----
@given('radio button having css "{locator}" should be selected')
@when('radio button having css "{locator}" should be selected')
@then('radio button having css "{locator}" should be selected')
def step_radio_selected_css(context, locator):
    _assert_radio_selected(context, "css", locator)


###### ---------- To assert that radio button not selected use any of the following steps : ---------- ######

# -------- helper for asserting radio button unselected --------
def _assert_radio_unselected(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    assert not elem.is_selected(), (
        f"❌ Radio button with {locator_type}='{locator_value}' IS selected, but expected to be UNSELECTED!"
    )


# ---- ID ----
@given('radio button having id "{locator}" should be unselected')
@when('radio button having id "{locator}" should be unselected')
@then('radio button having id "{locator}" should be unselected')
def step_radio_unselected_id(context, locator):
    _assert_radio_unselected(context, "id", locator)


# ---- NAME ----
@given('radio button having name "{locator}" should be unselected')
@when('radio button having name "{locator}" should be unselected')
@then('radio button having name "{locator}" should be unselected')
def step_radio_unselected_name(context, locator):
    _assert_radio_unselected(context, "name", locator)


# ---- CLASS ----
@given('radio button having class "{locator}" should be unselected')
@when('radio button having class "{locator}" should be unselected')
@then('radio button having class "{locator}" should be unselected')
def step_radio_unselected_class(context, locator):
    _assert_radio_unselected(context, "class", locator)


# ---- XPATH ----
@given('radio button having xpath "{locator}" should be unselected')
@when('radio button having xpath "{locator}" should be unselected')
@then('radio button having xpath "{locator}" should be unselected')
def step_radio_unselected_xpath(context, locator):
    _assert_radio_unselected(context, "xpath", locator)


# ---- CSS ----
@given('radio button having css "{locator}" should be unselected')
@when('radio button having css "{locator}" should be unselected')
@then('radio button having css "{locator}" should be unselected')
def step_radio_unselected_css(context, locator):
    _assert_radio_unselected(context, "css", locator)


###### ---------- To assert that radio button group selected by text use any of the following steps : ---------- ######

# -------- helper for asserting radio group option selected by text --------
def _assert_radio_group_selected_by_text(context, locator_type, locator_value, option_text):
    elems = find_element_2(context, locator_type, locator_value)  # list of all group of radio buttons
    matched = False

    for elem in elems:
        # Check value element or label of radio button
        if elem.get_attribute("value") == option_text or elem.text.strip() == option_text:
            matched = True
            assert elem.is_selected(), (
                f"❌ Radio button option '{option_text}' in group ({locator_type}='{locator_value}') is NOT selected!"
            )
            break

    assert matched, (
        f"❌ No radio button option with text/value '{option_text}' found in group ({locator_type}='{locator_value}')!"
    )


# ---- ID ----
@given('option "{option_text}" by text from radio button group having id "{locator}" should be selected')
@when('option "{option_text}" by text from radio button group having id "{locator}" should be selected')
@then('option "{option_text}" by text from radio button group having id "{locator}" should be selected')
def step_radio_group_selected_id(context, option_text, locator):
    _assert_radio_group_selected_by_text(context, "id", locator, option_text)


# ---- NAME ----
@given('option "{option_text}" by text from radio button group having name "{locator}" should be selected')
@when('option "{option_text}" by text from radio button group having name "{locator}" should be selected')
@then('option "{option_text}" by text from radio button group having name "{locator}" should be selected')
def step_radio_group_selected_name(context, option_text, locator):
    _assert_radio_group_selected_by_text(context, "name", locator, option_text)


# ---- CLASS ----
@given('option "{option_text}" by text from radio button group having class "{locator}" should be selected')
@when('option "{option_text}" by text from radio button group having class "{locator}" should be selected')
@then('option "{option_text}" by text from radio button group having class "{locator}" should be selected')
def step_radio_group_selected_class(context, option_text, locator):
    _assert_radio_group_selected_by_text(context, "class", locator, option_text)


# ---- XPATH ----
@given('option "{option_text}" by text from radio button group having xpath "{locator}" should be selected')
@when('option "{option_text}" by text from radio button group having xpath "{locator}" should be selected')
@then('option "{option_text}" by text from radio button group having xpath "{locator}" should be selected')
def step_radio_group_selected_xpath(context, option_text, locator):
    _assert_radio_group_selected_by_text(context, "xpath", locator, option_text)


# ---- CSS ----
@given('option "{option_text}" by text from radio button group having css "{locator}" should be selected')
@when('option "{option_text}" by text from radio button group having css "{locator}" should be selected')
@then('option "{option_text}" by text from radio button group having css "{locator}" should be selected')
def step_radio_group_selected_css(context, option_text, locator):
    _assert_radio_group_selected_by_text(context, "css", locator, option_text)


###### ---------- To assert that radio button group selected by value use any of the following steps : ---------- ######

# -------- Helper for asserting radio button group by VALUE --------
def _assert_radio_group_selected_by_value(context, locator_type, locator_value, option_value):
    # Get all radio buttons in the group
    elems = find_element_2(context, locator_type, locator_value)
    matched = False
    for elem in elems:
        # Match the radio button by "value" attribute
        if elem.get_attribute("value") == option_value:
            matched = True
            # Assert that the matched radio button is selected
            assert elem.is_selected(), (
                f"❌ Radio button option with value '{option_value}' in {locator_type}='{locator_value}' "
                f"is NOT selected!"
            )
            break
    # If no radio with that value found, fail the step
    assert matched, f"❌ No radio button with value '{option_value}' found in {locator_type}='{locator_value}'!"


# ---- ID ----
@given('option "{option_value}" by value from radio button group having id "{locator}" should be selected')
@when('option "{option_value}" by value from radio button group having id "{locator}" should be selected')
@then('option "{option_value}" by value from radio button group having id "{locator}" should be selected')
def step_radio_group_selected_id_value(context, option_value, locator):
    _assert_radio_group_selected_by_value(context, "id", locator, option_value)


# ---- NAME ----
@given('option "{option_value}" by value from radio button group having name "{locator}" should be selected')
@when('option "{option_value}" by value from radio button group having name "{locator}" should be selected')
@then('option "{option_value}" by value from radio button group having name "{locator}" should be selected')
def step_radio_group_selected_name_value(context, option_value, locator):
    _assert_radio_group_selected_by_value(context, "name", locator, option_value)


# ---- CLASS ----
@given('option "{option_value}" by value from radio button group having class "{locator}" should be selected')
@when('option "{option_value}" by value from radio button group having class "{locator}" should be selected')
@then('option "{option_value}" by value from radio button group having class "{locator}" should be selected')
def step_radio_group_selected_class_value(context, option_value, locator):
    _assert_radio_group_selected_by_value(context, "class", locator, option_value)


# ---- XPATH ----
@given('option "{option_value}" by value from radio button group having xpath "{locator}" should be selected')
@when('option "{option_value}" by value from radio button group having xpath "{locator}" should be selected')
@then('option "{option_value}" by value from radio button group having xpath "{locator}" should be selected')
def step_radio_group_selected_xpath_value(context, option_value, locator):
    _assert_radio_group_selected_by_value(context, "xpath", locator, option_value)


# ---- CSS ----
@given('option "{option_value}" by value from radio button group having css "{locator}" should be selected')
@when('option "{option_value}" by value from radio button group having css "{locator}" should be selected')
@then('option "{option_value}" by value from radio button group having css "{locator}" should be selected')
def step_radio_group_selected_css_value(context, option_value, locator):
    _assert_radio_group_selected_by_value(context, "css", locator, option_value)

###### ---------- To assert that radio button group not selected by text use any of the following steps : ---------- ######

# -------- Helper for asserting radio button group UNSELECTED by TEXT --------
def _assert_radio_group_unselected_by_text(context, locator_type, locator_value, option_text):
    # Get all radio buttons in the group
    elems = find_element_2(context, locator_type, locator_value)
    matched = False
    for elem in elems:
        # Match by label text
        label = elem.get_attribute("value") or elem.text
        if label.strip() == option_text:
            matched = True
            # Assert that the matched radio button is NOT selected
            assert not elem.is_selected(), (
                f"❌ Radio button option with text '{option_text}' in {locator_type}='{locator_value}' "
                f"is unexpectedly SELECTED!"
            )
            break
    # If no matching radio found, fail
    assert matched, f"❌ No radio button with text '{option_text}' found in {locator_type}='{locator_value}'!"


# ---- ID ----
@given('option "{option_text}" by text from radio button group having id "{locator}" should be unselected')
@when('option "{option_text}" by text from radio button group having id "{locator}" should be unselected')
@then('option "{option_text}" by text from radio button group having id "{locator}" should be unselected')
def step_radio_group_unselected_id_text(context, option_text, locator):
    _assert_radio_group_unselected_by_text(context, "id", locator, option_text)


# ---- NAME ----
@given('option "{option_text}" by text from radio button group having name "{locator}" should be unselected')
@when('option "{option_text}" by text from radio button group having name "{locator}" should be unselected')
@then('option "{option_text}" by text from radio button group having name "{locator}" should be unselected')
def step_radio_group_unselected_name_text(context, option_text, locator):
    _assert_radio_group_unselected_by_text(context, "name", locator, option_text)


# ---- CLASS ----
@given('option "{option_text}" by text from radio button group having class "{locator}" should be unselected')
@when('option "{option_text}" by text from radio button group having class "{locator}" should be unselected')
@then('option "{option_text}" by text from radio button group having class "{locator}" should be unselected')
def step_radio_group_unselected_class_text(context, option_text, locator):
    _assert_radio_group_unselected_by_text(context, "class", locator, option_text)


# ---- XPATH ----
@given('option "{option_text}" by text from radio button group having xpath "{locator}" should be unselected')
@when('option "{option_text}" by text from radio button group having xpath "{locator}" should be unselected')
@then('option "{option_text}" by text from radio button group having xpath "{locator}" should be unselected')
def step_radio_group_unselected_xpath_text(context, option_text, locator):
    _assert_radio_group_unselected_by_text(context, "xpath", locator, option_text)


# ---- CSS ----
@given('option "{option_text}" by text from radio button group having css "{locator}" should be unselected')
@when('option "{option_text}" by text from radio button group having css "{locator}" should be unselected')
@then('option "{option_text}" by text from radio button group having css "{locator}" should be unselected')
def step_radio_group_unselected_css_text(context, option_text, locator):
    _assert_radio_group_unselected_by_text(context, "css", locator, option_text)


###### ---------- To assert that radio button group not selected by value use any of the following steps : ---------- ######

# -------- Helper for asserting radio button group UNSELECTED by VALUE --------
def _assert_radio_group_unselected_by_value(context, locator_type, locator_value, option_value):
    # Get all radio buttons in the group
    elems = find_element_2(context, locator_type, locator_value)
    matched = False
    for elem in elems:
        # Match by "value" attribute
        value = elem.get_attribute("value")
        if value == option_value:
            matched = True
            # Assert that the matched radio button is NOT selected
            assert not elem.is_selected(), (
                f"❌ Radio button option with value '{option_value}' in {locator_type}='{locator_value}' "
                f"is unexpectedly SELECTED!"
            )
            break
    # If no matching radio found, fail
    assert matched, f"❌ No radio button with value '{option_value}' found in {locator_type}='{locator_value}'!"


# ---- ID ----
@given('option "{option_value}" by value from radio button group having id "{locator}" should be unselected')
@when('option "{option_value}" by value from radio button group having id "{locator}" should be unselected')
@then('option "{option_value}" by value from radio button group having id "{locator}" should be unselected')
def step_radio_group_unselected_id_value(context, option_value, locator):
    _assert_radio_group_unselected_by_value(context, "id", locator, option_value)


# ---- NAME ----
@given('option "{option_value}" by value from radio button group having name "{locator}" should be unselected')
@when('option "{option_value}" by value from radio button group having name "{locator}" should be unselected')
@then('option "{option_value}" by value from radio button group having name "{locator}" should be unselected')
def step_radio_group_unselected_name_value(context, option_value, locator):
    _assert_radio_group_unselected_by_value(context, "name", locator, option_value)


# ---- CLASS ----
@given('option "{option_value}" by value from radio button group having class "{locator}" should be unselected')
@when('option "{option_value}" by value from radio button group having class "{locator}" should be unselected')
@then('option "{option_value}" by value from radio button group having class "{locator}" should be unselected')
def step_radio_group_unselected_class_value(context, option_value, locator):
    _assert_radio_group_unselected_by_value(context, "class", locator, option_value)


# ---- XPATH ----
@given('option "{option_value}" by value from radio button group having xpath "{locator}" should be unselected')
@when('option "{option_value}" by value from radio button group having xpath "{locator}" should be unselected')
@then('option "{option_value}" by value from radio button group having xpath "{locator}" should be unselected')
def step_radio_group_unselected_xpath_value(context, option_value, locator):
    _assert_radio_group_unselected_by_value(context, "xpath", locator, option_value)


# ---- CSS ----
@given('option "{option_value}" by value from radio button group having css "{locator}" should be unselected')
@when('option "{option_value}" by value from radio button group having css "{locator}" should be unselected')
@then('option "{option_value}" by value from radio button group having css "{locator}" should be unselected')
def step_radio_group_unselected_css_value(context, option_value, locator):
    _assert_radio_group_unselected_by_value(context, "css", locator, option_value)

###### ---------- To assert that link is present use following steps : ---------- ######

# ---------- Helper for asserting link presence ----------
def _assert_link_present(context, locator_type, locator_value):
    by_map = {
        "text": By.LINK_TEXT,
        "partial_text": By.PARTIAL_LINK_TEXT,
    }
    elems = context.driver.find_elements(by_map[locator_type], locator_value)
    assert len(elems) > 0, f"❌ Link with {locator_type}='{locator_value}' is NOT present on the page!"


# ---- LINK TEXT ----
@given('link having text "{locator}" should be present')
@when('link having text "{locator}" should be present')
@then('link having text "{locator}" should be present')
def step_link_present_text(context, locator):
    _assert_link_present(context, "text", locator)


# ---- PARTIAL LINK TEXT ----
@given('link having partial text "{locator}" should be present')
@when('link having partial text "{locator}" should be present')
@then('link having partial text "{locator}" should be present')
def step_link_present_partial_text(context, locator):
    _assert_link_present(context, "partial_text", locator)

###### ---------- To assert that link is not present use following steps : ---------- ######

# ---------- Helper for asserting link NOT present ----------
def _assert_link_not_present(context, locator_type, locator_value):
    by_map = {
        "text": By.LINK_TEXT,
        "partial_text": By.PARTIAL_LINK_TEXT,
    }
    elems = context.driver.find_elements(by_map[locator_type], locator_value)
    assert len(elems) == 0, f"❌ Link with {locator_type}='{locator_value}' IS present on the page, but it should NOT be!"


# ---- LINK TEXT ----
@given('link having text "{locator}" should not be present')
@when('link having text "{locator}" should not be present')
@then('link having text "{locator}" should not be present')
def step_link_not_present_text(context, locator):
    _assert_link_not_present(context, "text", locator)


# ---- PARTIAL LINK TEXT ----
@given('link having partial text "{locator}" should not be present')
@when('link having partial text "{locator}" should not be present')
@then('link having partial text "{locator}" should not be present')
def step_link_not_present_partial_text(context, locator):
    _assert_link_not_present(context, "partial_text", locator)

###### ---------- To assert text on javascipt pop-up alert use following step : ---------- ######

# To assert text on JavaScript pop-up alert
@given('I should see alert text as "{expected_text}"')
@when('I should see alert text as "{expected_text}"')
@then('I should see alert text as "{expected_text}"')
def step_assert_alert_text(context, expected_text):
    try:
        # Switch to the alert
        alert = context.driver.switch_to.alert
        # Get the text from the alert
        actual_text = alert.text
        # Assert if the alert text matches the expected text
        assert actual_text == expected_text, f"❌ Expected alert text '{expected_text}', but got '{actual_text}'"
        # Optionally dismiss the alert if you want to proceed with closed alerts
        alert.accept()
    except NoSuchElementException:
        raise AssertionError("❌ No alert was present to assert text.")

###### ---------- To assert difference in actual image and expected image (from remotely hosted) use following steps : ---------- ######


def compare_images(img1, img2, diff_threshold=0):
    """Compare two PIL images, return True if they are similar within threshold"""
    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if bbox is None:
        return True  # Images are identical
    # Check number of different pixels
    diff_pixels = sum(diff.getdata())
    return diff_pixels <= diff_threshold


###### ---------- Steps for Asserting Image Similarity ---------- ######
# Locator-based Image Comparison
@given('compare expected image from locator "{locator_type}"="{locator_value}" with image at url "{expected_url}"')
@when('compare expected image from locator "{locator_type}"="{locator_value}" with image at url "{expected_url}"')
@then('compare expected image from locator "{locator_type}"="{locator_value}" with image at url "{expected_url}"')
def step_assert_image_similarity(context, locator_type, locator_value, expected_url):
    # Get actual image element
    elem = find_element_1(context, locator_type, locator_value)
    actual_src = elem.get_attribute("src")

    # Load actual image
    actual_img = Image.open(BytesIO(requests.get(actual_src).content))

    # Load expected image
    expected_img = Image.open(BytesIO(requests.get(expected_url).content))

    # Resize to same size for fair comparison
    if actual_img.size != expected_img.size:
        expected_img = expected_img.resize(actual_img.size)

    # Compare images
    is_similar = compare_images(actual_img.convert("RGB"), expected_img.convert("RGB"))
    assert is_similar, f"❌ Images are NOT similar! Locator: {locator_type}='{locator_value}'"


###### ---------- Step for Image-to-Image comparison by URL ---------- ######
# URL-Based Image Comparison
@given('compare image urls "{actual_url}" and "{expected_url}"')
@when('compare image urls "{actual_url}" and "{expected_url}"')
@then('compare image urls "{actual_url}" and "{expected_url}"')
def step_assert_image_similarity_by_url(context, actual_url, expected_url):
    actual_img = Image.open(BytesIO(requests.get(actual_url).content))
    expected_img = Image.open(BytesIO(requests.get(expected_url).content))

    # Resize if required
    if actual_img.size != expected_img.size:
        expected_img = expected_img.resize(actual_img.size)

    # Compare
    is_similar = compare_images(actual_img.convert("RGB"), expected_img.convert("RGB"))
    assert is_similar, f"❌ Images from URLs are NOT similar! ({actual_url} vs {expected_url})"


###### ---------- To assert difference in actual image and expected image (from local machine) use following steps : ---------- ######

# Helper function to compare images
def compare_images_local(actual_image, expected_img_name):
    # Assuming local images are stored in a folder named 'images' in project root
    expected_img_path = os.path.join("images", expected_img_name)

    if not os.path.exists(expected_img_path):
        raise FileNotFoundError(f"❌ Expected image not found at path: {expected_img_path}")

    expected_img = Image.open(expected_img_path)

    # Compute hash for both images
    hash1 = imagehash.average_hash(actual_image)
    hash2 = imagehash.average_hash(expected_img)

    # Difference threshold
    cutoff = 5
    return hash1 - hash2 < cutoff

# Step definition for local image comparison
def _assert_images_similar_local(context, locator_type, locator_value, expected_img_name):
    elem = find_element_1(context, locator_type, locator_value)
    screenshot = elem.screenshot_as_png
    actual_img = Image.open(BytesIO(screenshot))

    if not compare_images_local(actual_img, expected_img_name):
        raise AssertionError(
            f"❌ Images are not similar for element with {locator_type}='{locator_value}' "
            f"and expected image '{expected_img_name}'"
        )

# ---------- Step Definitions ---------- #

@given('actual image having id "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@when('actual image having id "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@then('actual image having id "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
def step_img_similarity_id_local(context, locator, expected_img_name):
    _assert_images_similar_local(context, "id", locator, expected_img_name)


@given('actual image having name "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@when('actual image having name "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@then('actual image having name "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
def step_img_similarity_name_local(context, locator, expected_img_name):
    _assert_images_similar_local(context, "name", locator, expected_img_name)


@given('actual image having class "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@when('actual image having class "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@then('actual image having class "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
def step_img_similarity_class_local(context, locator, expected_img_name):
    _assert_images_similar_local(context, "class", locator, expected_img_name)


@given('actual image having xpath "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@when('actual image having xpath "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@then('actual image having xpath "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
def step_img_similarity_xpath_local(context, locator, expected_img_name):
    _assert_images_similar_local(context, "xpath", locator, expected_img_name)


@given('actual image having css "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@when('actual image having css "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
@then('actual image having css "{locator}" and expected image having image_name "{expected_img_name}" should be similar')
def step_img_similarity_css_local(context, locator, expected_img_name):
    _assert_images_similar_local(context, "css", locator, expected_img_name)


# For comparing actual image URL with local image
@given('actual image having url "{actual_img_url}" and expected image having image_name "{expected_img_name}" should be similar')
@when('actual image having url "{actual_img_url}" and expected image having image_name "{expected_img_name}" should be similar')
@then('actual image having url "{actual_img_url}" and expected image having image_name "{expected_img_name}" should be similar')
def step_img_similarity_url_local(context, actual_img_url, expected_img_name):
    response = requests.get(actual_img_url)
    actual_img = Image.open(BytesIO(response.content))

    if not compare_images_local(actual_img, expected_img_name):
        raise AssertionError(
            f"❌ Images from URL '{actual_img_url}' and local image '{expected_img_name}' are not similar."
        )


###### ---------- To assert difference in actual image and expected image (from same webpage) use following steps : ---------- ######


# Helper function to compare two PIL images
def compare_two_images(img1, img2):
    hash1 = imagehash.average_hash(img1)
    hash2 = imagehash.average_hash(img2)
    cutoff = 5  # threshold for similarity
    return hash1 - hash2 < cutoff

# Common helper to assert similarity between two elements from DOM
def _assert_images_similar_samepage(context, locator_type, actual_locator, expected_locator):
    elem1 = find_element_1(context, locator_type, actual_locator)
    elem2 = find_element_1(context, locator_type, expected_locator)

    img1 = Image.open(BytesIO(elem1.screenshot_as_png))
    img2 = Image.open(BytesIO(elem2.screenshot_as_png))

    if not compare_two_images(img1, img2):
        raise AssertionError(
            f"❌ Images from element with {locator_type}='{actual_locator}' and "
            f"{locator_type}='{expected_locator}' are not similar."
        )

# ---------- Step Definitions ---------- #

@given('actual image having id "{actual}" and expected image having id "{expected}" should be similar')
@when('actual image having id "{actual}" and expected image having id "{expected}" should be similar')
@then('actual image having id "{actual}" and expected image having id "{expected}" should be similar')
def step_img_similarity_id_samepage(context, actual, expected):
    _assert_images_similar_samepage(context, "id", actual, expected)


@given('actual image having name "{actual}" and expected image having name "{expected}" should be similar')
@when('actual image having name "{actual}" and expected image having name "{expected}" should be similar')
@then('actual image having name "{actual}" and expected image having name "{expected}" should be similar')
def step_img_similarity_name_samepage(context, actual, expected):
    _assert_images_similar_samepage(context, "name", actual, expected)


@given('actual image having class "{actual}" and expected image having class "{expected}" should be similar')
@when('actual image having class "{actual}" and expected image having class "{expected}" should be similar')
@then('actual image having class "{actual}" and expected image having class "{expected}" should be similar')
def step_img_similarity_class_samepage(context, actual, expected):
    _assert_images_similar_samepage(context, "class", actual, expected)


@given('actual image having xpath "{actual}" and expected image having xpath "{expected}" should be similar')
@when('actual image having xpath "{actual}" and expected image having xpath "{expected}" should be similar')
@then('actual image having xpath "{actual}" and expected image having xpath "{expected}" should be similar')
def step_img_similarity_xpath_samepage(context, actual, expected):
    _assert_images_similar_samepage(context, "xpath", actual, expected)


@given('actual image having css "{actual}" and expected image having css "{expected}" should be similar')
@when('actual image having css "{actual}" and expected image having css "{expected}" should be similar')
@then('actual image having css "{actual}" and expected image having css "{expected}" should be similar')
def step_img_similarity_css_samepage(context, actual, expected):
    _assert_images_similar_samepage(context, "css", actual, expected)


# For comparing URLs directly from the same page
@given('actual image having url "{actual}" and expected image having url "{expected}" should be similar')
@when('actual image having url "{actual}" and expected image having url "{expected}" should be similar')
@then('actual image having url "{actual}" and expected image having url "{expected}" should be similar')
def step_img_similarity_url_samepage(context, actual, expected):
    resp1 = requests.get(actual)
    resp2 = requests.get(expected)

    img1 = Image.open(BytesIO(resp1.content))
    img2 = Image.open(BytesIO(resp2.content))

    if not compare_two_images(img1, img2):
        raise AssertionError(
            f"❌ Images from URL '{actual}' and '{expected}' are not similar."
        )


###### ---------- To enter text into input field use following steps : ---------- ######

# Common helper function to enter text in input fields
def _enter_text_into_input(context, locator_type, locator_value, text):
    elem = find_element_1(context, locator_type, locator_value)
    elem.clear()   # clear existing text
    elem.send_keys(text)

# ---------------- Step Definitions ---------------- #

@given('I enter "{text}" into input field having id "{locator}"')
@when('I enter "{text}" into input field having id "{locator}"')
@then('I enter "{text}" into input field having id "{locator}"')
def step_enter_text_id(context, text, locator):
    _enter_text_into_input(context, "id", locator, text)


@given('I enter "{text}" into input field having name "{locator}"')
@when('I enter "{text}" into input field having name "{locator}"')
@then('I enter "{text}" into input field having name "{locator}"')
def step_enter_text_name(context, text, locator):
    _enter_text_into_input(context, "name", locator, text)


@given('I enter "{text}" into input field having class "{locator}"')
@when('I enter "{text}" into input field having class "{locator}"')
@then('I enter "{text}" into input field having class "{locator}"')
def step_enter_text_class(context, text, locator):
    _enter_text_into_input(context, "class", locator, text)


@given('I enter "{text}" into input field having xpath "{locator}"')
@when('I enter "{text}" into input field having xpath "{locator}"')
@then('I enter "{text}" into input field having xpath "{locator}"')
def step_enter_text_xpath(context, text, locator):
    _enter_text_into_input(context, "xpath", locator, text)


@given('I enter "{text}" into input field having css "{locator}"')
@when('I enter "{text}" into input field having css "{locator}"')
@then('I enter "{text}" into input field having css "{locator}"')
def step_enter_text_css(context, text, locator):
    _enter_text_into_input(context, "css", locator, text)


###### ---------- To clear input field use following steps : ---------- ######

# Common helper function to clear input fields
def _clear_input_field(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    elem.clear()

# ---------------- Step Definitions ---------------- #

@given('I clear input field having id "{locator}"')
@when('I clear input field having id "{locator}"')
@then('I clear input field having id "{locator}"')
def step_clear_input_id(context, locator):
    _clear_input_field(context, "id", locator)


@given('I clear input field having name "{locator}"')
@when('I clear input field having name "{locator}"')
@then('I clear input field having name "{locator}"')
def step_clear_input_name(context, locator):
    _clear_input_field(context, "name", locator)


@given('I clear input field having class "{locator}"')
@when('I clear input field having class "{locator}"')
@then('I clear input field having class "{locator}"')
def step_clear_input_class(context, locator):
    _clear_input_field(context, "class", locator)


@given('I clear input field having xpath "{locator}"')
@when('I clear input field having xpath "{locator}"')
@then('I clear input field having xpath "{locator}"')
def step_clear_input_xpath(context, locator):
    _clear_input_field(context, "xpath", locator)


@given('I clear input field having css "{locator}"')
@when('I clear input field having css "{locator}"')
@then('I clear input field having css "{locator}"')
def step_clear_input_css(context, locator):
    _clear_input_field(context, "css", locator)


###### ---------- To select option by text from dropdown use following steps : ---------- ######


# Common helper to select option by visible text
def _select_dropdown_by_text(context, locator_type, locator_value, option_text):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)
    select.select_by_visible_text(option_text)

# ---------------- Step Definitions ---------------- #

@given('I select "{option_text}" option by text from dropdown having id "{locator}"')
@when('I select "{option_text}" option by text from dropdown having id "{locator}"')
@then('I select "{option_text}" option by text from dropdown having id "{locator}"')
def step_select_dropdown_id(context, option_text, locator):
    _select_dropdown_by_text(context, "id", locator, option_text)


@given('I select "{option_text}" option by text from dropdown having name "{locator}"')
@when('I select "{option_text}" option by text from dropdown having name "{locator}"')
@then('I select "{option_text}" option by text from dropdown having name "{locator}"')
def step_select_dropdown_name(context, option_text, locator):
    _select_dropdown_by_text(context, "name", locator, option_text)


@given('I select "{option_text}" option by text from dropdown having class "{locator}"')
@when('I select "{option_text}" option by text from dropdown having class "{locator}"')
@then('I select "{option_text}" option by text from dropdown having class "{locator}"')
def step_select_dropdown_class(context, option_text, locator):
    _select_dropdown_by_text(context, "class", locator, option_text)


@given('I select "{option_text}" option by text from dropdown having xpath "{locator}"')
@when('I select "{option_text}" option by text from dropdown having xpath "{locator}"')
@then('I select "{option_text}" option by text from dropdown having xpath "{locator}"')
def step_select_dropdown_xpath(context, option_text, locator):
    _select_dropdown_by_text(context, "xpath", locator, option_text)


@given('I select "{option_text}" option by text from dropdown having css "{locator}"')
@when('I select "{option_text}" option by text from dropdown having css "{locator}"')
@then('I select "{option_text}" option by text from dropdown having css "{locator}"')
def step_select_dropdown_css(context, option_text, locator):
    _select_dropdown_by_text(context, "css", locator, option_text)


###### ---------- To select option by index from dropdown use following steps : ---------- ######

# Common helper to select option by index
def _select_dropdown_by_index(context, locator_type, locator_value, index):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)
    select.select_by_index(index)

# ---------------- Step Definitions ---------------- #

@given('I select {index:d} option by index from dropdown having id "{locator}"')
@when('I select {index:d} option by index from dropdown having id "{locator}"')
@then('I select {index:d} option by index from dropdown having id "{locator}"')
def step_select_dropdown_id_index(context, index, locator):
    _select_dropdown_by_index(context, "id", locator, index)


@given('I select {index:d} option by index from dropdown having name "{locator}"')
@when('I select {index:d} option by index from dropdown having name "{locator}"')
@then('I select {index:d} option by index from dropdown having name "{locator}"')
def step_select_dropdown_name_index(context, index, locator):
    _select_dropdown_by_index(context, "name", locator, index)


@given('I select {index:d} option by index from dropdown having class "{locator}"')
@when('I select {index:d} option by index from dropdown having class "{locator}"')
@then('I select {index:d} option by index from dropdown having class "{locator}"')
def step_select_dropdown_class_index(context, index, locator):
    _select_dropdown_by_index(context, "class", locator, index)


@given('I select {index:d} option by index from dropdown having xpath "{locator}"')
@when('I select {index:d} option by index from dropdown having xpath "{locator}"')
@then('I select {index:d} option by index from dropdown having xpath "{locator}"')
def step_select_dropdown_xpath_index(context, index, locator):
    _select_dropdown_by_index(context, "xpath", locator, index)


@given('I select {index:d} option by index from dropdown having css "{locator}"')
@when('I select {index:d} option by index from dropdown having css "{locator}"')
@then('I select {index:d} option by index from dropdown having css "{locator}"')
def step_select_dropdown_css_index(context, index, locator):
    _select_dropdown_by_index(context, "css", locator, index)

###### ---------- To select option by value from dropdown use following steps : ---------- ######

# Common helper to select option by value
def _select_dropdown_by_value(context, locator_type, locator_value, option_value):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)
    select.select_by_value(option_value)

# ---------------- Step Definitions ---------------- #

@given('I select "{option_value}" option by value from dropdown having id "{locator}"')
@when('I select "{option_value}" option by value from dropdown having id "{locator}"')
@then('I select "{option_value}" option by value from dropdown having id "{locator}"')
def step_select_dropdown_id_value(context, option_value, locator):
    _select_dropdown_by_value(context, "id", locator, option_value)


@given('I select "{option_value}" option by value from dropdown having name "{locator}"')
@when('I select "{option_value}" option by value from dropdown having name "{locator}"')
@then('I select "{option_value}" option by value from dropdown having name "{locator}"')
def step_select_dropdown_name_value(context, option_value, locator):
    _select_dropdown_by_value(context, "name", locator, option_value)


@given('I select "{option_value}" option by value from dropdown having class "{locator}"')
@when('I select "{option_value}" option by value from dropdown having class "{locator}"')
@then('I select "{option_value}" option by value from dropdown having class "{locator}"')
def step_select_dropdown_class_value(context, option_value, locator):
    _select_dropdown_by_value(context, "class", locator, option_value)


@given('I select "{option_value}" option by value from dropdown having xpath "{locator}"')
@when('I select "{option_value}" option by value from dropdown having xpath "{locator}"')
@then('I select "{option_value}" option by value from dropdown having xpath "{locator}"')
def step_select_dropdown_xpath_value(context, option_value, locator):
    _select_dropdown_by_value(context, "xpath", locator, option_value)


@given('I select "{option_value}" option by value from dropdown having css "{locator}"')
@when('I select "{option_value}" option by value from dropdown having css "{locator}"')
@then('I select "{option_value}" option by value from dropdown having css "{locator}"')
def step_select_dropdown_css_value(context, option_value, locator):
    _select_dropdown_by_value(context, "css", locator, option_value)

###### ---------- To select option by text from multiselect dropdown use following steps : ---------- ######

# Common helper to select option by text in multiselect dropdown
def _select_multiselect_by_text(context, locator_type, locator_value, option_text):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)

    if not select.is_multiple:
        raise AssertionError(f"❌ Dropdown with {locator_type}='{locator_value}' is not a multiselect dropdown!")

    select.select_by_visible_text(option_text)


# ---------------- Step Definitions ---------------- #

@given('I select "{option_text}" option by text from multiselect dropdown having id "{locator}"')
@when('I select "{option_text}" option by text from multiselect dropdown having id "{locator}"')
@then('I select "{option_text}" option by text from multiselect dropdown having id "{locator}"')
def step_select_multiselect_id_text(context, option_text, locator):
    _select_multiselect_by_text(context, "id", locator, option_text)


@given('I select "{option_text}" option by text from multiselect dropdown having name "{locator}"')
@when('I select "{option_text}" option by text from multiselect dropdown having name "{locator}"')
@then('I select "{option_text}" option by text from multiselect dropdown having name "{locator}"')
def step_select_multiselect_name_text(context, option_text, locator):
    _select_multiselect_by_text(context, "name", locator, option_text)


@given('I select "{option_text}" option by text from multiselect dropdown having class "{locator}"')
@when('I select "{option_text}" option by text from multiselect dropdown having class "{locator}"')
@then('I select "{option_text}" option by text from multiselect dropdown having class "{locator}"')
def step_select_multiselect_class_text(context, option_text, locator):
    _select_multiselect_by_text(context, "class", locator, option_text)


@given('I select "{option_text}" option by text from multiselect dropdown having xpath "{locator}"')
@when('I select "{option_text}" option by text from multiselect dropdown having xpath "{locator}"')
@then('I select "{option_text}" option by text from multiselect dropdown having xpath "{locator}"')
def step_select_multiselect_xpath_text(context, option_text, locator):
    _select_multiselect_by_text(context, "xpath", locator, option_text)


@given('I select "{option_text}" option by text from multiselect dropdown having css "{locator}"')
@when('I select "{option_text}" option by text from multiselect dropdown having css "{locator}"')
@then('I select "{option_text}" option by text from multiselect dropdown having css "{locator}"')
def step_select_multiselect_css_text(context, option_text, locator):
    _select_multiselect_by_text(context, "css", locator, option_text)

###### ---------- To select option by index from multiselect dropdown use following steps : ---------- ######

# Common helper to select option by index in multiselect dropdown
def _select_multiselect_by_index(context, locator_type, locator_value, index):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)

    if not select.is_multiple:
        raise AssertionError(f"❌ Dropdown with {locator_type}='{locator_value}' is not a multiselect dropdown!")

    select.select_by_index(index)


# ---------------- Step Definitions ---------------- #

@given('I select {index:d} option by index from multiselect dropdown having id "{locator}"')
@when('I select {index:d} option by index from multiselect dropdown having id "{locator}"')
@then('I select {index:d} option by index from multiselect dropdown having id "{locator}"')
def step_select_multiselect_id_index(context, index, locator):
    _select_multiselect_by_index(context, "id", locator, index)


@given('I select {index:d} option by index from multiselect dropdown having name "{locator}"')
@when('I select {index:d} option by index from multiselect dropdown having name "{locator}"')
@then('I select {index:d} option by index from multiselect dropdown having name "{locator}"')
def step_select_multiselect_name_index(context, index, locator):
    _select_multiselect_by_index(context, "name", locator, index)


@given('I select {index:d} option by index from multiselect dropdown having class "{locator}"')
@when('I select {index:d} option by index from multiselect dropdown having class "{locator}"')
@then('I select {index:d} option by index from multiselect dropdown having class "{locator}"')
def step_select_multiselect_class_index(context, index, locator):
    _select_multiselect_by_index(context, "class", locator, index)


@given('I select {index:d} option by index from multiselect dropdown having xpath "{locator}"')
@when('I select {index:d} option by index from multiselect dropdown having xpath "{locator}"')
@then('I select {index:d} option by index from multiselect dropdown having xpath "{locator}"')
def step_select_multiselect_xpath_index(context, index, locator):
    _select_multiselect_by_index(context, "xpath", locator, index)


@given('I select {index:d} option by index from multiselect dropdown having css "{locator}"')
@when('I select {index:d} option by index from multiselect dropdown having css "{locator}"')
@then('I select {index:d} option by index from multiselect dropdown having css "{locator}"')
def step_select_multiselect_css_index(context, index, locator):
    _select_multiselect_by_index(context, "css", locator, index)

###### ---------- To select option by value from multiselect dropdown use following steps : ---------- ######

# Common helper to select option by value in multiselect dropdown
def _select_multiselect_by_value(context, locator_type, locator_value, option_value):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)

    if not select.is_multiple:
        raise AssertionError(f"❌ Dropdown with {locator_type}='{locator_value}' is not a multiselect dropdown!")

    select.select_by_value(option_value)


# ---------------- Step Definitions ---------------- #

@given('I select "{option_value}" option by value from multiselect dropdown having id "{locator}"')
@when('I select "{option_value}" option by value from multiselect dropdown having id "{locator}"')
@then('I select "{option_value}" option by value from multiselect dropdown having id "{locator}"')
def step_select_multiselect_id_value(context, option_value, locator):
    _select_multiselect_by_value(context, "id", locator, option_value)


@given('I select "{option_value}" option by value from multiselect dropdown having name "{locator}"')
@when('I select "{option_value}" option by value from multiselect dropdown having name "{locator}"')
@then('I select "{option_value}" option by value from multiselect dropdown having name "{locator}"')
def step_select_multiselect_name_value(context, option_value, locator):
    _select_multiselect_by_value(context, "name", locator, option_value)


@given('I select "{option_value}" option by value from multiselect dropdown having class "{locator}"')
@when('I select "{option_value}" option by value from multiselect dropdown having class "{locator}"')
@then('I select "{option_value}" option by value from multiselect dropdown having class "{locator}"')
def step_select_multiselect_class_value(context, option_value, locator):
    _select_multiselect_by_value(context, "class", locator, option_value)


@given('I select "{option_value}" option by value from multiselect dropdown having xpath "{locator}"')
@when('I select "{option_value}" option by value from multiselect dropdown having xpath "{locator}"')
@then('I select "{option_value}" option by value from multiselect dropdown having xpath "{locator}"')
def step_select_multiselect_xpath_value(context, option_value, locator):
    _select_multiselect_by_value(context, "xpath", locator, option_value)


@given('I select "{option_value}" option by value from multiselect dropdown having css "{locator}"')
@when('I select "{option_value}" option by value from multiselect dropdown having css "{locator}"')
@then('I select "{option_value}" option by value from multiselect dropdown having css "{locator}"')
def step_select_multiselect_css_value(context, option_value, locator):
    _select_multiselect_by_value(context, "css", locator, option_value)

###### ---------- To select all options from multiselect use following steps : ---------- ######

# Common helper to select all options in multiselect dropdown
def _select_all_options_in_multiselect(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)

    if not select.is_multiple:
        raise AssertionError(f"❌ Dropdown with {locator_type}='{locator_value}' is not a multiselect dropdown!")

    for option in select.options:
        select.select_by_value(option.get_attribute("value"))


# ---------------- Step Definitions ---------------- #

@given('I select all options from multiselect dropdown having id "{locator}"')
@when('I select all options from multiselect dropdown having id "{locator}"')
@then('I select all options from multiselect dropdown having id "{locator}"')
def step_select_all_multiselect_id(context, locator):
    _select_all_options_in_multiselect(context, "id", locator)


@given('I select all options from multiselect dropdown having name "{locator}"')
@when('I select all options from multiselect dropdown having name "{locator}"')
@then('I select all options from multiselect dropdown having name "{locator}"')
def step_select_all_multiselect_name(context, locator):
    _select_all_options_in_multiselect(context, "name", locator)


@given('I select all options from multiselect dropdown having class "{locator}"')
@when('I select all options from multiselect dropdown having class "{locator}"')
@then('I select all options from multiselect dropdown having class "{locator}"')
def step_select_all_multiselect_class(context, locator):
    _select_all_options_in_multiselect(context, "class", locator)


@given('I select all options from multiselect dropdown having xpath "{locator}"')
@when('I select all options from multiselect dropdown having xpath "{locator}"')
@then('I select all options from multiselect dropdown having xpath "{locator}"')
def step_select_all_multiselect_xpath(context, locator):
    _select_all_options_in_multiselect(context, "xpath", locator)


@given('I select all options from multiselect dropdown having css "{locator}"')
@when('I select all options from multiselect dropdown having css "{locator}"')
@then('I select all options from multiselect dropdown having css "{locator}"')
def step_select_all_multiselect_css(context, locator):
    _select_all_options_in_multiselect(context, "css", locator)

###### ---------- To unselect all options from multiselect use following steps : ---------- ######

# Common helper to unselect all options in multiselect dropdown
def _unselect_all_options_in_multiselect(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    select = Select(elem)

    if not select.is_multiple:
        raise AssertionError(f"❌ Dropdown with {locator_type}='{locator_value}' is not a multiselect dropdown!")

    select.deselect_all()


# ---------------- Step Definitions ---------------- #

@given('I unselect all options from multiselect dropdown having id "{locator}"')
@when('I unselect all options from multiselect dropdown having id "{locator}"')
@then('I unselect all options from multiselect dropdown having id "{locator}"')
def step_unselect_all_multiselect_id(context, locator):
    _unselect_all_options_in_multiselect(context, "id", locator)


@given('I unselect all options from multiselect dropdown having name "{locator}"')
@when('I unselect all options from multiselect dropdown having name "{locator}"')
@then('I unselect all options from multiselect dropdown having name "{locator}"')
def step_unselect_all_multiselect_name(context, locator):
    _unselect_all_options_in_multiselect(context, "name", locator)


@given('I unselect all options from multiselect dropdown having class "{locator}"')
@when('I unselect all options from multiselect dropdown having class "{locator}"')
@then('I unselect all options from multiselect dropdown having class "{locator}"')
def step_unselect_all_multiselect_class(context, locator):
    _unselect_all_options_in_multiselect(context, "class", locator)


@given('I unselect all options from multiselect dropdown having xpath "{locator}"')
@when('I unselect all options from multiselect dropdown having xpath "{locator}"')
@then('I unselect all options from multiselect dropdown having xpath "{locator}"')
def step_unselect_all_multiselect_xpath(context, locator):
    _unselect_all_options_in_multiselect(context, "xpath", locator)


@given('I unselect all options from multiselect dropdown having css "{locator}"')
@when('I unselect all options from multiselect dropdown having css "{locator}"')
@then('I unselect all options from multiselect dropdown having css "{locator}"')
def step_unselect_all_multiselect_css(context, locator):
    _unselect_all_options_in_multiselect(context, "css", locator)

###### ---------- To check the checkbox use following steps : ---------- ######

# Common helper to check the checkbox
def _check_checkbox(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    if not elem.is_selected():
        elem.click()

# To check the checkbox

@given('I check the checkbox having id "{locator}"')
@when('I check the checkbox having id "{locator}"')
@then('I check the checkbox having id "{locator}"')
def step_check_checkbox_id(context, locator):
    _check_checkbox(context, "id", locator)


@given('I check the checkbox having name "{locator}"')
@when('I check the checkbox having name "{locator}"')
@then('I check the checkbox having name "{locator}"')
def step_check_checkbox_name(context, locator):
    _check_checkbox(context, "name", locator)


@given('I check the checkbox having class "{locator}"')
@when('I check the checkbox having class "{locator}"')
@then('I check the checkbox having class "{locator}"')
def step_check_checkbox_class(context, locator):
    _check_checkbox(context, "class", locator)


@given('I check the checkbox having xpath "{locator}"')
@when('I check the checkbox having xpath "{locator}"')
@then('I check the checkbox having xpath "{locator}"')
def step_check_checkbox_xpath(context, locator):
    _check_checkbox(context, "xpath", locator)


@given('I check the checkbox having css "{locator}"')
@when('I check the checkbox having css "{locator}"')
@then('I check the checkbox having css "{locator}"')
def step_check_checkbox_css(context, locator):
    _check_checkbox(context, "css", locator)

###### ---------- To uncheck the checkbox use following steps : ---------- ######

# Common helper to uncheck the checkbox
def _uncheck_checkbox(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    if elem.is_selected():
        elem.click()

# To uncheck the checkbox

@given('I uncheck the checkbox having id "{locator}"')
@when('I uncheck the checkbox having id "{locator}"')
@then('I uncheck the checkbox having id "{locator}"')
def step_uncheck_checkbox_id(context, locator):
    _uncheck_checkbox(context, "id", locator)


@given('I uncheck the checkbox having name "{locator}"')
@when('I uncheck the checkbox having name "{locator}"')
@then('I uncheck the checkbox having name "{locator}"')
def step_uncheck_checkbox_name(context, locator):
    _uncheck_checkbox(context, "name", locator)


@given('I uncheck the checkbox having class "{locator}"')
@when('I uncheck the checkbox having class "{locator}"')
@then('I uncheck the checkbox having class "{locator}"')
def step_uncheck_checkbox_class(context, locator):
    _uncheck_checkbox(context, "class", locator)


@given('I uncheck the checkbox having xpath "{locator}"')
@when('I uncheck the checkbox having xpath "{locator}"')
@then('I uncheck the checkbox having xpath "{locator}"')
def step_uncheck_checkbox_xpath(context, locator):
    _uncheck_checkbox(context, "xpath", locator)


@given('I uncheck the checkbox having css "{locator}"')
@when('I uncheck the checkbox having css "{locator}"')
@then('I uncheck the checkbox having css "{locator}"')
def step_uncheck_checkbox_css(context, locator):
    _uncheck_checkbox(context, "css", locator)

###### ---------- To toggle checkbox use following steps : ---------- ######

# Common helper to toggle the checkbox
def _toggle_checkbox(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    elem.click()

# To toggle the checkbox

@given('I toggle checkbox having id "{locator}"')
@when('I toggle checkbox having id "{locator}"')
@then('I toggle checkbox having id "{locator}"')
def step_toggle_checkbox_id(context, locator):
    _toggle_checkbox(context, "id", locator)


@given('I toggle checkbox having name "{locator}"')
@when('I toggle checkbox having name "{locator}"')
@then('I toggle checkbox having name "{locator}"')
def step_toggle_checkbox_name(context, locator):
    _toggle_checkbox(context, "name", locator)


@given('I toggle checkbox having class "{locator}"')
@when('I toggle checkbox having class "{locator}"')
@then('I toggle checkbox having class "{locator}"')
def step_toggle_checkbox_class(context, locator):
    _toggle_checkbox(context, "class", locator)


@given('I toggle checkbox having xpath "{locator}"')
@when('I toggle checkbox having xpath "{locator}"')
@then('I toggle checkbox having xpath "{locator}"')
def step_toggle_checkbox_xpath(context, locator):
    _toggle_checkbox(context, "xpath", locator)


@given('I toggle checkbox having css "{locator}"')
@when('I toggle checkbox having css "{locator}"')
@then('I toggle checkbox having css "{locator}"')
def step_toggle_checkbox_css(context, locator):
    _toggle_checkbox(context, "css", locator)

###### ---------- To select radio button use following steps : ---------- ######

# Common helper to select a radio button
def _select_radio_button(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    if not elem.is_selected():
        elem.click()

# ---------------- Step Definitions ---------------- #

@given('I select radio button having id "{locator}"')
@when('I select radio button having id "{locator}"')
@then('I select radio button having id "{locator}"')
def step_select_radio_button_id(context, locator):
    _select_radio_button(context, "id", locator)


@given('I select radio button having name "{locator}"')
@when('I select radio button having name "{locator}"')
@then('I select radio button having name "{locator}"')
def step_select_radio_button_name(context, locator):
    _select_radio_button(context, "name", locator)


@given('I select radio button having class "{locator}"')
@when('I select radio button having class "{locator}"')
@then('I select radio button having class "{locator}"')
def step_select_radio_button_class(context, locator):
    _select_radio_button(context, "class", locator)


@given('I select radio button having xpath "{locator}"')
@when('I select radio button having xpath "{locator}"')
@then('I select radio button having xpath "{locator}"')
def step_select_radio_button_xpath(context, locator):
    _select_radio_button(context, "xpath", locator)


@given('I select radio button having css "{locator}"')
@when('I select radio button having css "{locator}"')
@then('I select radio button having css "{locator}"')
def step_select_radio_button_css(context, locator):
    _select_radio_button(context, "css", locator)

###### ---------- To select one radio button by text from radio button group use following steps : ---------- ######

# Common helper to select a radio button by text from a radio button group
def _select_radio_button_by_text(context, locator_type, locator_value, option_text):
    elements = find_element_2(context, locator_type, locator_value)
    found = False
    for elem in elements:
        # Check sibling or associated label for text
        label = elem.get_attribute("value") or elem.text
        if label.strip() == option_text:
            found = True
            if not elem.is_selected():
                elem.click()
            break

    if not found:
        raise AssertionError(f"❌ No radio button option with text '{option_text}' found in group ({locator_type}='{locator_value}')!")

# ---------------- Step Definitions ---------------- #

@given('I select "{option_text}" option by text from radio button group having id "{locator}"')
@when('I select "{option_text}" option by text from radio button group having id "{locator}"')
@then('I select "{option_text}" option by text from radio button group having id "{locator}"')
def step_select_radio_by_text_id(context, option_text, locator):
    _select_radio_button_by_text(context, "id", locator, option_text)


@given('I select "{option_text}" option by text from radio button group having name "{locator}"')
@when('I select "{option_text}" option by text from radio button group having name "{locator}"')
@then('I select "{option_text}" option by text from radio button group having name "{locator}"')
def step_select_radio_by_text_name(context, option_text, locator):
    _select_radio_button_by_text(context, "name", locator, option_text)


@given('I select "{option_text}" option by text from radio button group having class "{locator}"')
@when('I select "{option_text}" option by text from radio button group having class "{locator}"')
@then('I select "{option_text}" option by text from radio button group having class "{locator}"')
def step_select_radio_by_text_class(context, option_text, locator):
    _select_radio_button_by_text(context, "class", locator, option_text)


@given('I select "{option_text}" option by text from radio button group having xpath "{locator}"')
@when('I select "{option_text}" option by text from radio button group having xpath "{locator}"')
@then('I select "{option_text}" option by text from radio button group having xpath "{locator}"')
def step_select_radio_by_text_xpath(context, option_text, locator):
    _select_radio_button_by_text(context, "xpath", locator, option_text)


@given('I select "{option_text}" option by text from radio button group having css "{locator}"')
@when('I select "{option_text}" option by text from radio button group having css "{locator}"')
@then('I select "{option_text}" option by text from radio button group having css "{locator}"')
def step_select_radio_by_text_css(context, option_text, locator):
    _select_radio_button_by_text(context, "css", locator, option_text)

###### ---------- To select one radio button by value from radio button group use following steps : ---------- ######

# Common helper to select a radio button by value from a radio button group
def _select_radio_button_by_value(context, locator_type, locator_value, option_value):
    elements = find_element_2(context, locator_type, locator_value)
    found = False
    for elem in elements:
        # Check the radio button's value attribute
        value = elem.get_attribute("value")
        if value == option_value:
            found = True
            if not elem.is_selected():
                elem.click()
            break

    if not found:
        raise AssertionError(f"❌ No radio button option with value '{option_value}' found in group ({locator_type}='{locator_value}')!")

# ---------------- Step Definitions ---------------- #

@given('I select "{option_value}" option by value from radio button group having id "{locator}"')
@when('I select "{option_value}" option by value from radio button group having id "{locator}"')
@then('I select "{option_value}" option by value from radio button group having id "{locator}"')
def step_select_radio_by_value_id(context, option_value, locator):
    _select_radio_button_by_value(context, "id", locator, option_value)


@given('I select "{option_value}" option by value from radio button group having name "{locator}"')
@when('I select "{option_value}" option by value from radio button group having name "{locator}"')
@then('I select "{option_value}" option by value from radio button group having name "{locator}"')
def step_select_radio_by_value_name(context, option_value, locator):
    _select_radio_button_by_value(context, "name", locator, option_value)


@given('I select "{option_value}" option by value from radio button group having class "{locator}"')
@when('I select "{option_value}" option by value from radio button group having class "{locator}"')
@then('I select "{option_value}" option by value from radio button group having class "{locator}"')
def step_select_radio_by_value_class(context, option_value, locator):
    _select_radio_button_by_value(context, "class", locator, option_value)


@given('I select "{option_value}" option by value from radio button group having xpath "{locator}"')
@when('I select "{option_value}" option by value from radio button group having xpath "{locator}"')
@then('I select "{option_value}" option by value from radio button group having xpath "{locator}"')
def step_select_radio_by_value_xpath(context, option_value, locator):
    _select_radio_button_by_value(context, "xpath", locator, option_value)


@given('I select "{option_value}" option by value from radio button group having css "{locator}"')
@when('I select "{option_value}" option by value from radio button group having css "{locator}"')
@then('I select "{option_value}" option by value from radio button group having css "{locator}"')
def step_select_radio_by_value_css(context, option_value, locator):
    _select_radio_button_by_value(context, "css", locator, option_value)

###### ---------- To click on web element use following steps : ---------- ###### also ###### ---------- To click on web element with a particular text use the following steps : ---------- ######

# Unified helper function (handles with/without expected text)
def _click_on_element(context, locator_type, locator_value, expected_text=None):
    if expected_text is None:
        # Single element case
        element = find_element_1(context, locator_type, locator_value)
        element.click()
    else:
        # Multiple elements, match by text
        elements = find_element_2(context, locator_type, locator_value)
        for elem in elements:
            actual_text = elem.text.strip()
            if actual_text == expected_text:
                elem.click()
                return
        raise AssertionError(
            f"❌ No element with {locator_type}='{locator_value}' and text '{expected_text}' found!"
        )

# ---------------- Step Definitions ---------------- #

@given('I click on element having id "{locator}"')
@when('I click on element having id "{locator}"')
@then('I click on element having id "{locator}"')
@given('I click on element having id "{locator}" and text "{expected_text}"')
@when('I click on element having id "{locator}" and text "{expected_text}"')
@then('I click on element having id "{locator}" and text "{expected_text}"')
def step_click_element_id(context, locator, expected_text=None):
    _click_on_element(context, "id", locator, expected_text)


@given('I click on element having name "{locator}"')
@when('I click on element having name "{locator}"')
@then('I click on element having name "{locator}"')
@given('I click on element having name "{locator}" and text "{expected_text}"')
@when('I click on element having name "{locator}" and text "{expected_text}"')
@then('I click on element having name "{locator}" and text "{expected_text}"')
def step_click_element_name(context, locator, expected_text=None):
    _click_on_element(context, "name", locator, expected_text)


@given('I click on element having class "{locator}"')
@when('I click on element having class "{locator}"')
@then('I click on element having class "{locator}"')
@given('I click on element having class "{locator}" and text "{expected_text}"')
@when('I click on element having class "{locator}" and text "{expected_text}"')
@then('I click on element having class "{locator}" and text "{expected_text}"')
def step_click_element_class(context, locator, expected_text=None):
    _click_on_element(context, "class", locator, expected_text)


@given('I click on element having xpath "{locator}"')
@when('I click on element having xpath "{locator}"')
@then('I click on element having xpath "{locator}"')
@given('I click on element having xpath "{locator}" and text "{expected_text}"')
@when('I click on element having xpath "{locator}" and text "{expected_text}"')
@then('I click on element having xpath "{locator}" and text "{expected_text}"')
def step_click_element_xpath(context, locator, expected_text=None):
    _click_on_element(context, "xpath", locator, expected_text)


@given('I click on element having css "{locator}"')
@when('I click on element having css "{locator}"')
@then('I click on element having css "{locator}"')
@given('I click on element having css "{locator}" and text "{expected_text}"')
@when('I click on element having css "{locator}" and text "{expected_text}"')
@then('I click on element having css "{locator}" and text "{expected_text}"')
def step_click_element_css(context, locator, expected_text=None):
    _click_on_element(context, "css", locator, expected_text)


###### ---------- To forcefully click on web element use following steps (if above steps do not work) : ---------- ######

# Common helper to forcefully click on a web element using JavaScript
def _forcefully_click_on_element(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    context.driver.execute_script("arguments[0].click();", elem)

# ---------------- Step Definitions ---------------- #

@given('I forcefully click on element having id "{locator}"')
@when('I forcefully click on element having id "{locator}"')
@then('I forcefully click on element having id "{locator}"')
def step_force_click_element_id(context, locator):
    _forcefully_click_on_element(context, "id", locator)


@given('I forcefully click on element having name "{locator}"')
@when('I forcefully click on element having name "{locator}"')
@then('I forcefully click on element having name "{locator}"')
def step_force_click_element_name(context, locator):
    _forcefully_click_on_element(context, "name", locator)


@given('I forcefully click on element having class "{locator}"')
@when('I forcefully click on element having class "{locator}"')
@then('I forcefully click on element having class "{locator}"')
def step_force_click_element_class(context, locator):
    _forcefully_click_on_element(context, "class", locator)


@given('I forcefully click on element having xpath "{locator}"')
@when('I forcefully click on element having xpath "{locator}"')
@then('I forcefully click on element having xpath "{locator}"')
def step_force_click_element_xpath(context, locator):
    _forcefully_click_on_element(context, "xpath", locator)


@given('I forcefully click on element having css "{locator}"')
@when('I forcefully click on element having css "{locator}"')
@then('I forcefully click on element having css "{locator}"')
def step_force_click_element_css(context, locator):
    _forcefully_click_on_element(context, "css", locator)


###### ---------- To double click on web element use following steps : ---------- ######


# Common helper to double-click on a web element
def _double_click_on_element(context, locator_type, locator_value):
    elem = find_element_1(context, locator_type, locator_value)
    action_chains = ActionChains(context.driver)
    action_chains.double_click(elem).perform()

# ---------------- Step Definitions ---------------- #

@given('I double click on element having id "{locator}"')
@when('I double click on element having id "{locator}"')
@then('I double click on element having id "{locator}"')
def step_double_click_element_id(context, locator):
    _double_click_on_element(context, "id", locator)


@given('I double click on element having name "{locator}"')
@when('I double click on element having name "{locator}"')
@then('I double click on element having name "{locator}"')
def step_double_click_element_name(context, locator):
    _double_click_on_element(context, "name", locator)


@given('I double click on element having class "{locator}"')
@when('I double click on element having class "{locator}"')
@then('I double click on element having class "{locator}"')
def step_double_click_element_class(context, locator):
    _double_click_on_element(context, "class", locator)


@given('I double click on element having xpath "{locator}"')
@when('I double click on element having xpath "{locator}"')
@then('I double click on element having xpath "{locator}"')
def step_double_click_element_xpath(context, locator):
    _double_click_on_element(context, "xpath", locator)


@given('I double click on element having css "{locator}"')
@when('I double click on element having css "{locator}"')
@then('I double click on element having css "{locator}"')
def step_double_click_element_css(context, locator):
    _double_click_on_element(context, "css", locator)


###### ---------- To click on links use following steps : ---------- ######

# Common helper to click on a link by its text
def _click_on_link_by_text(context, text, partial=False):
    if partial:
        elem = context.driver.find_element(By.PARTIAL_LINK_TEXT, text)
    else:
        elem = context.driver.find_element(By.LINK_TEXT, text)
    elem.click()

# ---------------- Step Definitions ---------------- #

@given('I click on link having text "{text}"')
@when('I click on link having text "{text}"')
@then('I click on link having text "{text}"')
def step_click_link_by_text(context, text):
    _click_on_link_by_text(context, text, partial=False)


@given('I click on link having partial text "{text}"')
@when('I click on link having partial text "{text}"')
@then('I click on link having partial text "{text}"')
def step_click_link_by_partial_text(context, text):
    _click_on_link_by_text(context, text, partial=True)


###### ---------- To wait for specific time use following step : ---------- ######

# Step to wait for a specific amount of time
@given('I wait for {duration:d} sec')
@when('I wait for {duration:d} sec')
@then('I wait for {duration:d} sec')
def step_wait_for_time(context, duration):
    sleep(duration)

###### ---------- To wait for specific element to display use following steps : ---------- ######

# Common helper to wait for an element to be visible
def _wait_for_element_to_display(context, locator_type, locator_value, timeout=30):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
    }
    try:
        WebDriverWait(context.driver, int(timeout)).until(
            EC.visibility_of_element_located((by_map[locator_type], locator_value))
        )
    except Exception as e:
        raise AssertionError(
            f"❌ Element with {locator_type}='{locator_value}' not visible within {timeout} seconds. Error: {e}"
        )

# Step Definitions for waiting for an element to be visible
@given('I wait {timeout:d} seconds for element having id "{locator}" to display')
@when('I wait {timeout:d} seconds for element having id "{locator}" to display')
@then('I wait {timeout:d} seconds for element having id "{locator}" to display')
def step_wait_for_element_id_display(context, timeout, locator):
    _wait_for_element_to_display(context, "id", locator, timeout)

@given('I wait {timeout:d} seconds for element having name "{locator}" to display')
@when('I wait {timeout:d} seconds for element having name "{locator}" to display')
@then('I wait {timeout:d} seconds for element having name "{locator}" to display')
def step_wait_for_element_name_display(context, timeout, locator):
    _wait_for_element_to_display(context, "name", locator, timeout)

@given('I wait {timeout:d} seconds for element having class "{locator}" to display')
@when('I wait {timeout:d} seconds for element having class "{locator}" to display')
@then('I wait {timeout:d} seconds for element having class "{locator}" to display')
def step_wait_for_element_class_display(context, timeout, locator):
    _wait_for_element_to_display(context, "class", locator, timeout)

@given('I wait {timeout:d} seconds for element having xpath "{locator}" to display')
@when('I wait {timeout:d} seconds for element having xpath "{locator}" to display')
@then('I wait {timeout:d} seconds for element having xpath "{locator}" to display')
def step_wait_for_element_xpath_display(context, timeout, locator):
    _wait_for_element_to_display(context, "xpath", locator, timeout)

@given('I wait {timeout:d} seconds for element having css "{locator}" to display')
@when('I wait {timeout:d} seconds for element having css "{locator}" to display')
@then('I wait {timeout:d} seconds for element having css "{locator}" to display')
def step_wait_for_element_css_display(context, timeout, locator):
    _wait_for_element_to_display(context, "css", locator, timeout)

###### ---------- To wait for specific element to enable use following steps : ---------- ######

# ---------- Helper Function ----------
def _wait_for_element_to_be_clickable(context, locator_type, locator_value, timeout=30):
    by_map = {
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "xpath": By.XPATH,
        "css": By.CSS_SELECTOR,
    }
    try:
        WebDriverWait(context.driver, int(timeout)).until(
            EC.element_to_be_clickable((by_map[locator_type], locator_value))
        )
    except Exception as e:
        raise AssertionError(
            f"❌ Element with {locator_type}='{locator_value}' not clickable within {timeout} seconds. Error: {e}"
        )

# ---------- Step Definitions ----------

@given('I wait {timeout:d} seconds for element having id "{locator}" to be clickable')
@when('I wait {timeout:d} seconds for element having id "{locator}" to be clickable')
@then('I wait {timeout:d} seconds for element having id "{locator}" to be clickable')
def step_wait_for_element_id_clickable(context, timeout, locator):
    _wait_for_element_to_be_clickable(context, "id", locator, timeout)


@given('I wait {timeout:d} seconds for element having name "{locator}" to be clickable')
@when('I wait {timeout:d} seconds for element having name "{locator}" to be clickable')
@then('I wait {timeout:d} seconds for element having name "{locator}" to be clickable')
def step_wait_for_element_name_clickable(context, timeout, locator):
    _wait_for_element_to_be_clickable(context, "name", locator, timeout)


@given('I wait {timeout:d} seconds for element having class "{locator}" to be clickable')
@when('I wait {timeout:d} seconds for element having class "{locator}" to be clickable')
@then('I wait {timeout:d} seconds for element having class "{locator}" to be clickable')
def step_wait_for_element_class_clickable(context, timeout, locator):
    _wait_for_element_to_be_clickable(context, "class", locator, timeout)


@given('I wait {timeout:d} seconds for element having xpath "{locator}" to be clickable')
@when('I wait {timeout:d} seconds for element having xpath "{locator}" to be clickable')
@then('I wait {timeout:d} seconds for element having xpath "{locator}" to be clickable')
def step_wait_for_element_xpath_clickable(context, timeout, locator):
    _wait_for_element_to_be_clickable(context, "xpath", locator, timeout)


@given('I wait {timeout:d} seconds for element having css "{locator}" to be clickable')
@when('I wait {timeout:d} seconds for element having css "{locator}" to be clickable')
@then('I wait {timeout:d} seconds for element having css "{locator}" to be clickable')
def step_wait_for_element_css_clickable(context, timeout, locator):
    _wait_for_element_to_be_clickable(context, "css", locator, timeout)



###### ---------- To handle javascript pop-up use following steps : ---------- ######

# Step to accept an alert pop-up
@given('I accept alert')
@when('I accept alert')
@then('I accept alert')
def step_accept_alert(context):
    try:
        alert = context.driver.switch_to.alert  # Switch to the alert
        alert.accept()  # Accept the alert
    except Exception as e:
        raise AssertionError(f"❌ No alert present to accept. Error: {str(e)}")

# Step to dismiss an alert pop-up
@given('I dismiss alert')
@when('I dismiss alert')
@then('I dismiss alert')
def step_dismiss_alert(context):
    try:
        alert = context.driver.switch_to.alert  # Switch to the alert
        alert.dismiss()  # Dismiss the alert
    except Exception as e:
        raise AssertionError(f"❌ No alert present to dismiss. Error: {str(e)}")


###### ---------- To take screenshot use following step : ---------- ######

# Step to take a screenshot
@given('I take screenshot')
@when('I take screenshot')
@then('I take screenshot')
def step_take_screenshot(context):
    if not hasattr(context, "screenshot_dir"):
        # Set a default directory for storing screenshots if not set
        context.screenshot_dir = os.path.join(os.getcwd(), "screenshots")

    # Ensure the screenshots directory exists
    if not os.path.exists(context.screenshot_dir):
        os.makedirs(context.screenshot_dir)

    # Create a timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = os.path.join(context.screenshot_dir, f"screenshot_{timestamp}.png")

    # Save the screenshot
    try:
        context.driver.save_screenshot(screenshot_file)
        print(f"✅ Screenshot saved successfully: {screenshot_file}")
    except Exception as e:
        raise AssertionError(f"❌ Failed to take screenshot. Error: {str(e)}")

###### ---------- To print testing configuration use following step : ---------- ######

# Step to print the current testing configuration
@given('I print configuration')
@when('I print configuration')
@then('I print configuration')
def step_print_configuration(context):
    try:
        # Example configuration details; these should be adjusted to reflect your actual configuration structure
        config_details = {
            "Browser": context.browser if hasattr(context, "browser") else "Not specified",
            "Base URL": context.base_url if hasattr(context, "base_url") else "Not specified",
            "Headless": context.headless if hasattr(context, "headless") else "Not specified",
            "Timeout": context.timeout if hasattr(context, "timeout") else "Not specified",
        }

        # Print configuration details
        print("🔧 Current Testing Configuration:")
        for key, value in config_details.items():
            print(f"  - {key}: {value}")

    except Exception as e:
        raise AssertionError(f"❌ Failed to print configuration. Error: {str(e)}")

###### ---------- To tap on app element use following steps : ---------- ######



###### ---------- To Tap on back button of device use following step : ---------- ######



###### ---------- To perform swipe using app elements use following steps : ---------- ######



###### ---------- To perform swipe using co-ordinates ---------- ######



###### ---------- To perform swipe using direction ---------- ######



###### ---------- To perform swipe using app element with direction use following steps : ---------- ######



###### ---------- To perform swipe using co-ordinates with direction use following steps : ---------- ######



###### ---------- To perform long tap with default duration of 2 seconds on app elements use following steps : ---------- ######



###### ---------- To perform long tap with customized duration of seconds on app elements use following steps : ---------- ######



###### ---------- To perform long tap with default duration of 2 seconds using co-ordinates use following step : ---------- ######



###### ---------- To perform long tap with customized duration of seconds using co-ordinates use following step : ---------- ######



###### ---------- Close app step : -----------####

# 🟢 Close the app

@given("I close app")
@when("I close app")
@then("I close app")
def close_app(context):
    if hasattr(context, "driver") and context.driver:
        context.driver.quit()
        context.driver = None