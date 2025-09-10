from behave import given, when, then
from selenium_behave.utils.bedrock_client import get_kb_response, bedrock_claude_chat
from selenium_behave.utils.evaluation_utils import ai_similarity_score,detect_hallucination,coverage_check,extract_links,verify_link_validity

@given('I ask the chatbot "{faq}"')
def step_impl(context, faq):
    context.faq = faq
    context.actual = bedrock_claude_chat(faq)

@when('I fetch the expected answer from KB for "{faq}"')
def step_impl(context, faq):
    context.expected = get_kb_response(faq)

@then('the similarity between expected and actual should be at least 75')
def step_impl(context):
    score = ai_similarity_score(context.expected, context.actual)
    assert score >= 75, f"Similarity {score} < 75"

@then('the output should not hallucinate')
def step_impl(context):
    hallu = detect_hallucination(context.expected, context.actual)
    assert "no" in hallu.lower(), f"Hallucination detected: {hallu}"

@then('important points should be covered')
def step_impl(context):
    coverage = coverage_check(context.expected, context.actual)
    assert "missing" not in coverage.lower(), f"Coverage issue: {coverage}"

@then('links should be valid')
def step_impl(context):
    links = extract_links(context.actual)
    validity = verify_link_validity(links)
    for url, status, _ in validity:
        assert status == "Valid", f"Invalid link: {url}"
