import io
from helper import *
from pydub import AudioSegment

def handle_message(update, _):
    
    # prep db
    user_id = str(update.message.from_user.id)
    message = update.message.text
    update_user(user_id, message, "user")


    # prep context
    context = []
    db_context = get_user_context(user_id)
    for role in db_context:
        for message in db_context[role]:
            context.append(prep_context(message, role))
    
    # db_context = get_user_context_db(user_id)
    # for row in db_context:
    #     context.append(prep_context(row[0], row[1]))
    
    # call chatgpt
    reply = call_gpt(context)

    # send messaage
    update.message.reply_voice(speak(reply), caption=reply)
    update_user(user_id, reply, "bot")


def handle_voice(update, _):
    
    # create an AudioSegment object from the Ogg audio data
    ogg_audio_data = update.message.voice.get_file().download_as_bytearray()
    mp3_audio = AudioSegment.from_file(io.BytesIO(ogg_audio_data), format="ogg").export(format="mp3")   

    # prep db
    user_id = str(update.message.from_user.id)
    message = listen(mp3_audio)
    update_user(user_id, message, "user")


    # prep context
    context = []
    db_context = get_user_context(user_id)
    for role in db_context:
        for message in db_context[role]:
            context.append(prep_context(message, role))
    
    # db_context = get_user_context_db(user_id)
    # for row in db_context:
    #     context.append(prep_context(row[0], row[1]))

    # call chatgpt
    reply = call_gpt(context)

    # send messaage
    update.message.reply_voice(speak(reply), caption=reply)
    update_user(user_id, reply, "bot")
