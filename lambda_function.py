import json
from sms_spam_classifier_utilities import one_hot_encode
from sms_spam_classifier_utilities import vectorize_sequences
import boto3
import email
import os


#print(email.message_from_string("111"))

def send_msg_to_visitor(sender,email_address,msg):
    client = boto3.client('ses', region_name="us-west-2")
    response = client.send_email(
        Source=sender,
        Destination={'ToAddresses': [email_address], },
        Message={
            'Subject': {
                'Data': 'string',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {'Charset': "UTF-8",
                         'Data': msg,
                         }, }}
    )

def lambda_handler(event, context):
    sender=os.environ["sender"]
    endpoint=os.environ["endpoint"]
    print(endpoint)
    BUCKET_NAME,KEY_NAME=event["Records"][0]["s3"]["bucket"]["name"],event["Records"][0]["s3"]["object"]["key"]
    s3=boto3.client("s3")
    response=s3.get_object(Bucket=BUCKET_NAME, Key=KEY_NAME)
    emailcontent = response['Body'].read().decode('utf-8')
    text=email.message_from_string(emailcontent)
    content=str(text.get_payload()[0]).split("\n")
    print(content)
    content=[" ".join(content[2:-1])] if len(content)>=2 else content
    print(content)
    subject,received_date,email_address=text.get("subject"),text.get("Date"),text.get("From")
    print(subject,received_date,email_address)
    # exit()
    # email=re.search("Return-Path: <.*>", emailcontent).group(0)[14:-1]
    # received_date=re.findall("Date: .*\r\n",emailcontent)[-1][6:].replace("\r\n","")
    # subject=re.findall("Subject: .*\r\n",emailcontent)[-1][9:].replace("\r\n","")
    # print(received_date,subject)
    # emailcontent=emailcontent.split("\r\n")
    # print(json.dumps(emailcontent,indent=2))
    # pos1=emailcontent.index("Content-Type: text/plain; charset=\"UTF-8\"")
    # # print(pos1)
    # uni=emailcontent[pos1-1]
    # # print(uni)
    # start,end=None,None
    # for i,v in enumerate(emailcontent):
    #     if uni==v:
    #         if start is None:
    #             start=i
    #         elif end is None:
    #             end=i
    #         else:
    #             break
    # # print(start,end)
    # content=[" ".join([v for v in emailcontent[start+3:end-1] if v!="\n"])]
    # print(content)
    #test_messages = ["FreeMsg: Txt: CALL to No: 86888 & claim your reward of 3 hours talk time to use from your phone now! ubscribe6GBP/ mnth inc 3hrs 16 stop?txtStop"]
    vocabulary_length = 9013
    one_hot_test_messages = one_hot_encode(content, vocabulary_length)
    encoded_test_messages = vectorize_sequences(one_hot_test_messages, vocabulary_length)
    #endpoint="sms-spam-classifier-mxnet-2020-05-09-11-08-10-423"
    contentType = "application/json"
    runtime=boto3.client('sagemaker-runtime')
    response = runtime.invoke_endpoint(EndpointName=endpoint,
                                       ContentType=contentType,
                                       Body=json.dumps(encoded_test_messages.tolist()))
    res=json.loads(response["Body"].read().decode())
    label="spam" if res["predicted_label"][0][0]>0.5 else "normal"
    probability=res["predicted_probability"][0][0]*100

    m1="We received your email sent at {} with the subject {}.".format(received_date,subject)
    m2="Here is a 240 character sample of the email body:"
    m3=content[0][:240]
    m4="The email was categorized as {} with a {}% confidence.".format(label,probability)
    msg="\n".join([m1,m2,m3,m4])
    print(msg)
    send_msg_to_visitor(sender,email_address,msg)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

if __name__=="__main__":
    event={
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-2",
                "eventTime": "2019-09-03T19:37:27.192Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
                },
                "requestParameters": {
                    "sourceIPAddress": "205.255.255.255"
                },
                "responseElements": {
                    "x-amz-request-id": "D82B88E5F771F645",
                    "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
                    "bucket": {
                        "name": "hw4-yy2979",
                        "ownerIdentity": {
                            "principalId": "A3I5XTEXAMAI3E"
                        },
                        "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
                    },
                    "object": {
                        "key": "m431o4681vjt8nbmdkv7vvarmla1io9fm7u6uk81",
                        #"key":"cq4d5rrf3jmn4utjdhh5v9kohpni4laqflccnt81",
                        #"key":"3klp6fqld9hdfaibq3ljanc5430opusmh5ivdi01",
                        "size": 1305107,
                        "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
                        "sequencer": "0C0F6F405D6ED209E1"
                    }
                }
            }
        ]
    }
    os.environ["sender"]="jamesyuanyuzhang@gmail.com"
    os.environ["endpoint"]="t1"
    lambda_handler(event,"")
#     send_msg_to_visitor("18718691881@163.com","james lebron")
