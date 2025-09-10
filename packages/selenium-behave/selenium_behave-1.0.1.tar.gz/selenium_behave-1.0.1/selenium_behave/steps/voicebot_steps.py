from behave import given, when, then
from selenium_behave.utils.ui_utils import launch_copilot, click_mic_button
from selenium_behave.utils.voice_handler import speak_text, record_system_audio, transcribe_audio_file
from selenium_behave.utils.excel_utils import get_common_keywords
import os

@given("I have Copilot opened")
def step_impl(context):
    context.driver = launch_copilot()

@given("the mic button is ready")
def step_impl(context):
    # Already handled in launch_copilot, but reusable step
    pass

@when("I click on the mic button")
def step_impl(context):
    click_mic_button(context.driver)
    if record_system_audio("welcome.wav"):
        context.transcript = transcribe_audio_file("welcome.wav")
        os.remove("welcome.wav")

@then("I should hear a welcome message")
def step_impl(context):
    assert "copilot" in context.transcript.lower(), f"Unexpected welcome: {context.transcript}"

@when('I speak "{input_text}"')
def step_impl(context, input_text):
    speak_text(input_text)
    record_system_audio("response.wav")
    context.response = transcribe_audio_file("response.wav")
    os.remove("response.wav")

@then("I should get a response containing at least 2 common keywords")
def step_impl(context):
    keywords = get_common_keywords()
    response_words = context.response.lower().split()
    matched_keywords = [word for word in response_words if word in keywords]
    assert len(matched_keywords) >= 2, f"FAIL — Found {len(matched_keywords)} ➜ {matched_keywords}"


@given("I initialize the voice chatbot")
def step_init_voicebot(context):
    context.voicebot = context.speak_text()

@when('I say "{text}"')
def step_user_says(context, text):
    context.last_response = context.context.speak_text()

@then('the bot should respond with a greeting')
def step_bot_response(context):
    assert "hello" in context.last_response.lower()
