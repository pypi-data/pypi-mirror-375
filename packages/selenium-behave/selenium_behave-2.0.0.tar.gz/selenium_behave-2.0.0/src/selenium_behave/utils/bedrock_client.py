import os, json, boto3
from dotenv import load_dotenv

load_dotenv()

bedrock_agent_runtime = boto3.client(
    "bedrock-agent-runtime",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

bedrock_runtime = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

knowledge_base_id = os.getenv("KB_ID")
model_arn = os.getenv("MODEL_ARN")
model_id = os.getenv("MODEL_ID")

def get_kb_response(user_question):
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={"text": user_question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": knowledge_base_id,
                "modelArn": model_arn
            }
        }
    )
    return response["output"]["text"]

def bedrock_claude_chat(prompt):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.2
    }
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json"
    )
    result = json.loads(response['body'].read())
    return result["content"][0]["text"]
