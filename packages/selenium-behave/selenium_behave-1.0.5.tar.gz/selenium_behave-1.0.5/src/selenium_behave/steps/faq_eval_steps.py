from behave import given, when, then
from selenium_behave.utils.bot_client import get_bot_response
from selenium_behave.utils.bedrock_client import get_kb_response
from selenium_behave.utils.evaluation_utils import (
    ai_similarity_score, detect_hallucination,
    coverage_check, extract_links, compare_links,
    verify_link_validity, factual_check
)
from selenium_behave.utils.report_generator import ReportLogger

report_logger = ReportLogger()

@given("I have AWS Bedrock and Bot API configured")
def step_impl(context):
    context.configured = True

@when('I send FAQ "{faq}"')
def step_impl(context, faq):
    context.faq = faq
    context.actual, context.session_id = get_bot_response(faq)
    context.expected = get_kb_response(faq)

@then("I should get a Bot response")
def step_impl(context):
    assert context.actual, "Bot response was empty"

@then("I should get an Expected KB response")
def step_impl(context):
    assert context.expected, "KB response was empty"

@then("I evaluate similarity score between Expected and Actual")
def step_impl(context):
    context.sim_score = ai_similarity_score(context.expected, context.actual)
    assert context.sim_score is not None, "Similarity score failed"

@then("I check hallucination")
def step_impl(context):
    context.hallucination = detect_hallucination(context.expected, context.actual)

@then("I check coverage")
def step_impl(context):
    context.coverage = coverage_check(context.expected, context.actual)

@then("I validate links")
def step_impl(context):
    expected_links = extract_links(context.expected)
    actual_links = extract_links(context.actual)
    context.link_comparison = compare_links(expected_links, actual_links)
    context.link_validity = verify_link_validity(actual_links)

@then("I verify factual accuracy")
def step_impl(context):
    context.fact_check = factual_check(context.actual)

@then("I log the result into the report")
def step_impl(context):
    pass_fail = "✅Pass" if context.sim_score >= 75 else "❌Fail"
    report_logger.log_result(
        context.session_id,
        context.faq,
        context.expected,
        context.actual,
        context.sim_score,
        pass_fail,
        context.hallucination,
        context.coverage,
        context.link_comparison,
        context.link_validity,
        context.fact_check
    )
