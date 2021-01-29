import base64
import requests
import time
import boto3
from search_criteria import *   ### Import search criteria from search_criteria.py file
from aggressive_words import *  ### Import aggressive words  from aggresive_words.py file
from harmful_words import *     ### Import harmful words  from harmful_words.py file
from incident_words import *    ### Import incident words  from incident_words.py file
from context_words import *     ### Import context words from incident_words.py file
from baskin_robbins import *    ### Import flavor of the month words from baskin_robbins.py file
from fake_news import *         ### Import fake news words to whitelist from fake_news.py file
from username_white_list import *         ### Import fake news words to whitelist from fake_news.py file
from api_keys import *          #### Import API keys
from botocore.exceptions import ClientError ###Provides detailed error descriptions on boto issues
from textblob import TextBlob


username_white_list = [element.lower() for element in username_white_list]  #Convert username white list to lowercase

key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
b64_encoded_key = base64.b64encode(key_secret)
b64_encoded_key = b64_encoded_key.decode('ascii')

base_url = 'https://api.twitter.com/'
auth_url = '{}oauth2/token'.format(base_url)

auth_headers = {
    'Authorization': 'Basic {}'.format(b64_encoded_key),
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
}

auth_data = {
    'grant_type': 'client_credentials'
}

auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

# Check status code okay
auth_resp.status_code

# Keys in data response are token_type (bearer) and access_token (your access token)
auth_resp.json().keys()

access_token = auth_resp.json()['access_token']

search_headers = {
    'Authorization': 'Bearer {}'.format(access_token)    
}

def sendEmail():
	time.sleep(.1)
	# Initial Email Values
	SENDER = "Your Email <yours@yours.com>"
	RECIPIENT = search_entry[1] ##Grabbing email distro list from distro_lists.py via import into search_queries.py
	AWS_REGION = "us-west-2"
	SUBJECT = "Gamera Alert" # {}".format(term)

	# The email body for recipients with non-HTML email clients.
	BODY_TEXT = ("Gamera Alert Text")
				
	# The HTML body of the email.
	BODY_HTML = """<html>
	<head></head>
	<body>
	 <i>Risk score:</i> <b>{}</b> <br /><br />
     <i>User:</i> {} <br /><br />
     <i>Hit for:</i> {} <br /><br />
     <i>Text:</i> {}  <br /><br />
     <i>Translated Text:</i> {}  <br /><br />
     <i>Created at:</i> {} <br /><br />
     <i>Language:</i> {} <br /><br />
    <i>Tweet ID: </i> <a href="https://twitter.com/anyuser/status/{}">{}</a> <br /><br />
    <i>subjectivity: objective vs. subjective (+0.0 => +1.0):</i> {} <br /><br />
     <i>polarity: negative vs. positive (-1.0 => +1.0) :</i> {} <br /><br />

	</body>
	</html>
				""".format(str(risk_score), str(x['user']['screen_name']), str(search_entry[0]), str(x['full_text']), translatedText,  str(x['created_at']),  str(x['lang']), str(x['id']), str(x['id']), sentiments.subjectivity, sentiments.polarity  )           

	# The character encoding for the email.
	CHARSET = "UTF-8"

	# Create a new SES resource and specify a region.
	client = boto3.client('ses',region_name=AWS_REGION)

	# Try to send the email.
	try:
		#Provide the contents of the email.
		response = client.send_email(
			Destination={
				'ToAddresses': 
					RECIPIENT,
				
			},
			Message={
				'Body': {
					'Html': {
						'Charset': CHARSET,
						'Data': BODY_HTML,
					},
					'Text': {
						'Charset': CHARSET,
						'Data': BODY_TEXT,
					},
				},
				'Subject': {
					'Charset': CHARSET,
					'Data': SUBJECT,
				},
			},
			Source=SENDER,
			# If you are not using a configuration set, comment or delete the
			# following line
			#ConfigurationSetName=CONFIGURATION_SET,
		)
	# Display an error if something goes wrong.	
	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		print("Email sent! Message ID:"),
		print(response['MessageId'])

############End of Email Function

def grinder1(risk_score, has_context):  ###Default Grinder

    #print('in grinder')
    if any(word in x['full_text'].lower() for word in aggressive_words):  ###cuss words
        risk_score += 3
            
    if any(word in x['full_text'].lower() for word in context_words):     ###context
        risk_score += 3
        has_context += 1  ##Tweet contains context
            
    if any(word in x['full_text'].lower() for word in harmful_words):     ###harmful
        risk_score += 10
            
    if any(word in x['full_text'].lower() for word in baskin_robbins):    ###Flavor of the day 
        risk_score += 6
        
    if any(word in x['full_text'].lower() for word in fake_news_words):    ###Fake news 
        #print ("whitelisted term")
        risk_score -= 50
            
    if any(word in x['full_text'].lower() for word in incident_words):    ####protest, gathering
        #print ("Incident Word hit")
        risk_score += 10
    #print(risk_score)
    return(risk_score, has_context)
    ############# End grinder function
    
def grinder2(risk_score, has_context):  ###Forced Notification Grinder
    risk_score += 99
    return(risk_score, has_context)

while True:  ####Main Logic Below
    print (time.strftime("%Y-%m-%d %H:%M"))
    for search_entry in search_queries:
        grinder_selection = search_entry[2]  ##Do we want notification regardless of the risk score
        forced_context = search_entry[3]      ##Do we want to require the presence of a context word in the tweet in order to fire
        has_context = 0
        #print (search_entry[1])
        print ('Searching For: ' + str(search_entry[0]))
        search_params = {
            'q': search_entry[0],
            'result_type': 'recent',
            'count': 100,
            'tweet_mode':'extended' ### switches results from text to full text
        }

        search_url = '{}1.1/search/tweets.json'.format(base_url)

        search_resp = requests.get(search_url, headers=search_headers, params=search_params)

        search_resp.status_code

        tweet_data = search_resp.json()

        for x in tweet_data['statuses']: ####Setting a risk score of 99 if forced_notification is set
            risk_score = 0

            #print(x)
            #print(x['full_text'] + '\n')
            #print('##################')

            if grinder_selection == 1:
                grindResults = grinder1(risk_score, has_context)  #Call Grinder1 Function
            elif grinder_selection == 2:
                grindResults = grinder2(risk_score, has_context) 
            else:
                pass
                
            risk_score = grindResults[0]
            has_context = grindResults[1]
            
            ###username whitelist
            tweet_user_name = str(x['user']['screen_name'])
            if tweet_user_name.lower()  in username_white_list:
                #print ('This tweet is from a whitelisted user. Passing.')
                risk_score = 0
            else:
                pass
            
            if risk_score > 5:
                #print (str(search_entry[4]))
                #print (x['id'])
                #response = table.get_item(Key={ "tweet_id": x['id'] , "distro_list": str(search_entry[4]) })
                
                #item = response['Item']
                #print (item)
                #print (str(search_entry[4]))
                #print (x['id'])
                if forced_context == 1 and has_context == 0 :
                    print('Passing Due to lack of Context')
                    pass
                else:
                    try:
                        response = table.get_item(Key={ "tweet_id": x['id'], 'distro_list': search_entry[4]	 })
                        item = response['Item']
                        #print (item)
                        #print(str(item) + ' is already in the database.')
                        time.sleep(1)  ###One second delay to try to stay within the parameters of AWS dynamoDB free tier. Can ease up if need be.
                        pass
                    except:
                        print('\nRisk score: ' + str(risk_score))
                        print('Hit for: ' + str(search_entry))
                        print('Text: ' + str(x['full_text']) + '\n')
                        print('ID#: ' + str(x['id']) + '\n')  ### 
                        print('Created at: ' + str(x['created_at']) + '\n')
                        print('User: ' + str(x['user']['screen_name']) + '\n') 
                        if str(x['lang']) == "en":   ####Start of Translation Engine using AWS translate
                            translatedText = 'N/A'
                            sentiments=TextBlob(str(x['full_text']))  ##Test for ML
                            pass
                        elif str(x['lang']) == "unk": ##Don't try to translate unknown since we don't have a good source language
                            translatedText = 'N/A'
                            sentiments=TextBlob(str(x['full_text']))   ##Test for ML
                            pass
                        else:
                            try:
                                result = translate.translate_text(Text=str(x['full_text']), SourceLanguageCode=str(x['lang']), TargetLanguageCode="en")
                                print('TranslatedText: ' + result.get('TranslatedText'))
                                #print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
                                #print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
                                translatedText = result.get('TranslatedText')
                                sentiments=TextBlob(translatedText) ##Test for ML
                            except:
                                print('Failed to translate')
                                translatedText = 'N/A'
                                sentiments=TextBlob('Failed to translate')
                        sendEmail()
                        try:
                            table.put_item( Item={'tweet_id': x['id'], 'distro_list': search_entry[4]	} )  ##### Insert tweet_id into the gamera_index table in my dynamoDB
                        except:
                            print('Error in Database Insert')
                        print('##################')

    print('Waiting Between Runs')        
    time.sleep(120)

