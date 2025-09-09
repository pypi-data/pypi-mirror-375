import openai
from IPython.display import Markdown, display
import os
from langchain.llms import OpenAI
from langchain.chains import ConversationChain

def askGPT4(prompt):
    completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
    {"role": "user", "content": prompt}
    ]
    )
    return completion.choices[0].message.content

def ask(prompt):
    display(Markdown(askGPT4(prompt)))

def memy_ask(user_message:str, new=False, api_key=None):
    global conversation
    if api_key is None:
        return print('Please set your api key')
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        if new or conversation is None:
            llm = OpenAI(temperature=0.5)
            conversation = ConversationChain(llm=llm, verbose=False)
        output = conversation.predict(input=user_message)
        display(Markdown(output))
