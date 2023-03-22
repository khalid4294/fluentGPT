import os 
import json    
import requests
import boto3

def update_user_db(user_id, messages, role):
    
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
    cur = conn.cursor()
    
    insert_command = '''
    INSERT INTO user_messages (user_id, message, message_type) VALUES (%s, %s, %s)
    '''
    
    cur.execute(insert_command, (user_id, messages, role))
    conn.commit()
    cur.close()
    conn.close()

def get_user_context_db(user_id):
    
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
    cur = conn.cursor()
    
    select_command = '''
    SELECT message, message_type FROM user_messages WHERE user_id = %s
    '''
    
    cur.execute(select_command, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return rows

def update_user(user_id, message, role):

    # load db
    with open('db.json') as f:
        db = json.load(f)
    
    if role == 'user':
        # check if user is in db, if not, create user
        if user_id in db:
            db[user_id]['user'].append(message)
        else:
            db[user_id] = {"user": [message], "assistant": []}
    
    elif role == 'bot':
        db[user_id]['assistant'].append(message)
    
    else:
        print("role not recognized")

    # update db
    with open('db.json', 'w') as f:
        json.dump(db, f)    


def get_user_context(user_id):
    
    with open('db.json') as f:
        db = json.load(f)

    return db[user_id]


def prep_context(text, role):
    """
    takes texts and roles and returns a context
    """
    return {"role":role, "content": text}


def call_gpt(context):
    
    # prep openai - vetara call
    chatgpt = os.environ.get('CHATGPT_API')

    headers = {
    "customer-id": os.environ.get('CUSTOMER-ID'),
    "x-api-key": os.environ.get('X-API-KEY'),
    }
    
    with open('base.txt') as f:
        base_prompt = f.read()
    
    messages = [{"role": "user", "content": base_prompt}]
    # merge 2 lists into 1
    messages.extend(context)

    params = {
    "model":"gpt-3.5-turbo",
    "messages": messages
    }    
    
    reply = requests.post(chatgpt, headers=headers, json=params)

    return reply.json()['choices'][0]['message']['content']

def listen(audio):

    whisper_api = os.environ.get('WHISPER_API')
    whisper_headers = {
        "customer-id": os.environ.get('CUSTOMER-ID'),
        "x-api-key":os.environ.get('X-API-KEY'),
        }
    
    files = {
        "file": ('file.mp3', audio, "audio/mp3")
        }
    
    data = {
        "model": "whisper-1",

        }
    
    response = requests.post(whisper_api, headers=whisper_headers, files=files, data=data)
    
    try:
        return response.json()['text']
    except:
        return "Sorry, I didn't get that, could you repeat that?"


def speak(text):
    
    # set aws vars
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID') 
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    defaultRegion = 'us-east-1'
    defaultUrl = 'https://polly.us-east-1.amazonaws.com'

    #load polly client
    polly = boto3.client('polly', region_name=defaultRegion, endpoint_url=defaultUrl, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)                            

    # synthesize speech
    resp = polly.synthesize_speech(OutputFormat='mp3', Text=text, VoiceId='Arthur', LanguageCode='en-GB', Engine='neural')

    # get audio stream
    soundBytes = resp['AudioStream'].read()

    return soundBytes