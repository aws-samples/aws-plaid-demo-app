import boto3
from botocore.exceptions import ClientError

# AWS Region
AWS_REGION = "us-east-2"

# Create a new SES resource and specify a region.

def send_email(sender, recipient):
    AWS_REGION = "us-east-2"
    client = boto3.client('ses',region_name=AWS_REGION)

    msg = MIMEMultipart()
    msg['Subject'] = 'Your Requested Documents from CaseSwift'
    msg['From'] = sender
    msg['To'] = recipient

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'Your CaseSwift Documents.\n'

    # the message body
    part = MIMEText('Howdy -- here are your requested Documents')
    msg.attach(part)

    my_canvas = canvas.Canvas(recipient + '_caseswift_documents.pdf')
    my_canvas.drawString(100, 750, "Here are your requested Documents, courtesy of CaseSwif!")
    my_canvas.save()

    # the attachment
    part = MIMEApplication(open(recipient + '_caseswift_documents.pdf', 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=recipient + '_caseswift_documents.pdf')
    msg.attach(part)


    # and send the message
    try: 

        response = client.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']],
            RawMessage={
            'Data': msg.as_string()
        },)

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

# # first draft minus attachment sending
# # The HTML body of the email.  Can customize to make it CaseSwift-y.  Also do not even need this; optional value.
# BODY_HTML = """<html>
# <head></head>
# <body>
#   <h1>CaseSwift: The GOAT PI Software</h1>
#   <p>This email was sent with
#     <a href='https://aws.amazon.com/ses/'>Amazon SES</a>
#   </p>
# </body>
# </html>
#             """            
# # The character encoding for the email.
# CHARSET = "UTF-8"
# def send_email(sender, recipient, subject, body_text):
#     # Try to send the email.
#     try:
#         response = client.send_email(
#             Destination={
#                 'ToAddresses': [
#                     recipient,
#                 ],
#             },
#             Message={
#                 'Body': {
#                     'Html': {
#                         'Charset': CHARSET,
#                         'Data': BODY_HTML,
#                     },
#                     'Text': {
#                         'Charset': CHARSET,
#                         'Data': body_text,
#                     },
#                 },
#                 'Subject': {
#                     'Charset': CHARSET,
#                     'Data': subject,
#                 },
#             },
#             Source=sender
#         )
    
#     # Display an error if something goes wrong.	
#     except ClientError as e:
#         print(e.response['Error']['Message'])
#     else:
#         print("Email sent! Message ID:"),
#         print(response['MessageId'])
#         return response