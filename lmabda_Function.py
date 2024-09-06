import boto3
import botocore
import json
from datetime import datetime

def blog_generate_with_bedrock(blog_topic:str)->str:
    prompt = f"""
    <s>Human: Write 200 words blogon the topic {blog_topic}
    Assistant:
    """

    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.6,
        "top_p": 0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", 
                               region_name="us-east-1",
                               config=botocore.config.Config(read_timeout=300, retries={"max_attempts":3}))
        response = bedrock.invoke_model(body=json.dumps(body), modelId="meta.llama3-8b-instruct-v1:0")

        response_content = response.get("body").read()
        response_data = json.loads(response_content)
        print(response_data)

        blog_details = response_data["generation"]

        return blog_details
    except Exception as e:
        print(f"Error while generating the Blog: {e}")
        return ""
    
def save_details_s3(s3_key, s3_bucket, body):
    s3 = boto3.client("s3")

    try:
        s3.put_object(Bucket=s3_bucket, key=s3_key, body=body)
        print("Code saved to s3")
    except Exception as e:
        print(f"Error while saving the code to s3: {e}")



def lambda_handler(event, context):
    # TODO implement
    event = json.loads(event["body"])
    blogtopic =  event["blog_topic"]

    generate_blog = blog_generate_with_bedrock(blogtopic)
    
    if generate_blog:
        current_time = datetime.now().strftime("%H%M%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = "bedrockbloggeneration"
        save_details_s3(s3_key, s3_bucket, generate_blog)

    else:
        print("No blog was generated")

    return {
        'statusCode': 200,
        'body': json.dumps('Blog Generated Successfully')
    }
