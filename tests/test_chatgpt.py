import openai
import bot.config as config

def test_chatgpt():
    openai.api_key = config.OPENAI_KEY
    question = "What is computer science?"
    response = openai.Completion.create(engine='text-davinci-003', prompt=question, max_tokens=1000)
    aimsg = response['choices'][0]['text']

    assert aimsg is not None, "ChatGPT did not respond."

def test_makeimage():
    openai.api_key = config.OPENAI_KEY
    description = "A cute cat"
    response = openai.Image.create(prompt=description, n=1, size='256x256')
    image_url = response['data'][0]['url']

    assert image_url is not None, "GPT did not generate an image."