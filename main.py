import config
import asyncio
import random
from telethon import TelegramClient, events
from ollama import ChatResponse
from ollama import AsyncClient


api_id = config.telegram_api_id
api_hash = config.telegram_api_hash
client = TelegramClient('anon', api_id, api_hash)

SYSTEM_PROMPT = config.SYSTEM_PROMPT

@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    current_message = event.text
    if not current_message:  # Игнорируем пустые сообщения
        return
    
    
    peer = await event.get_input_chat()

    await asyncio.sleep(random.randint(5, 60))

    history = await client.get_messages(peer, limit=100, offset_id=event.id)
    message_history = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    for msg in reversed(history):  # Разворачиваем, чтобы было в хронологическом порядке
        sender = "assistant" if msg.out else "user"
        text = msg.text if msg.text else ""
        if text:
            message_history.append({'role': sender, 'content': text})
    
    response: ChatResponse = await AsyncClient().chat(
            model='llama3.2', 
            messages=[*message_history,{'role': 'user','content': current_message}],
            options={
                'temperature': 0.5,
                'num_ctx': 8192
                })

    answer = response.message.content
    
    
    async with client.action(peer, 'typing'):
        typing_duration = len(answer) / 10
        wait_typing = max(5, min(typing_duration, 25))
        await asyncio.sleep(wait_typing)
    
    await asyncio.sleep(random.uniform(5, 30))

    await event.respond(answer)
    
with client:
    client.run_until_disconnected()