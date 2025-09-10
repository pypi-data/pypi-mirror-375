from behave import given, when, then
from selenium_behave.utils.agentic_helper import Agent

@given("I start an agentic session")
def step_start_agent(context):
    context.agent = Agent(max_steps=3)

@when('I ask the agent to "{goal}"')
def step_ask_agent(context, goal):
    context.agent_output = context.agent.run(goal)

@then('the agent should produce a final answer containing "{expected}"')
def step_agent_verify(context, expected):
    assert expected.lower() in context.agent_output.lower()
