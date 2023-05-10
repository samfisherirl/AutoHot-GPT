import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from threading import Thread
from progress.bar import ShadyBar
from time import sleep

# load values from the .env file if it exists
load_dotenv()
monitor = 0
# configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = """<<PUT THE PROMPT HERE>>"""

TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": new_question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

class process_response:
    def __init__(self, txt):
        self.txt = txt
        self.before_code = ""
        self.code = ""
        self.after_code = ""
        self.mode = 0 #before code == 0, if code found == 1, if code ends and the rest of the message is shown == 2
        
    def splitter(self):
        for i in self.txt.splitlines():
            if self.mode == 0 and "```" not in i:
                self.before_code = self.before_code + i.replace("```", "") + "\n"
            elif self.mode == 0 and "```" in i:
                self.mode = 1
                self.code = self.code + i.replace("```", "") + "\n"
            elif self.mode == 1:
                if "```" in i:
                    self.code = self.code + i.replace("```", "") + "\n"
                    self.mode = 2
                else:
                    self.code = self.code + i + "\n"
            elif self.mode == 2:
                self.after_code = self.after_code + i + "\n"
        return str(self.before_code + self.code + self.after_code)
    
    def writer(self):
        if self.code != "":
            print("FoundCOde")
            with open("log.txt", "w") as f:
                f.write(str((self.txt).split("```")[1]))
                f.close()
        else:
            print("no code")
            
    def listener(self):
        global monitor
        x = True
        y = False
        print(str(Fore.CYAN + Style.BRIGHT + self.txt + self.code))
        print("\n\nlistening for ahk.....if this persists your app folder got moved.")
        while x:
            try:
                if os.path.exists("return.txt"):
                    with open("return.txt", "r") as f:
                        self.code = str(f.read())
                        x = False
                        self.stripper()
                        monitor = 1
                        print(str(Fore.WHITE + Style.BRIGHT + '\n\n\n\n========Here is you\'re v2 code==========\n\n\n\n' + (self.code).strip() + "\n"))
                    # os.remove("return.txt")
                    return
                else:
                    pass
            except Exception as e:
                pass

    def stripper(self):
        x = 0
        newstring = "\n"
        for i in self.code.splitlines():
            x+=1
            if x > 1:
                newstring = newstring + i + "\n"
            else:
                continue
        self.code = newstring

    @staticmethod
    def bar():
        global monitor
        bar = ShadyBar('Processing', max=20)
        for i in range(20):
        # Do some work
            if monitor == 1:
                bar.finish()
                monitor = 0
                break
            else:
                bar.next()
                sleep(0.2)
        bar.finish()
        
    @staticmethod
    def manage(new_question):
        previous_questions_and_answers = []
        response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)
        proc_obj = process_response(str(response))
        proc_obj.splitter()
        proc_obj.writer()
        t = Thread(target = proc_obj.listener)
        t.start()
        t.join()
        # add the new question and answer to the list of previous questions and answers
        previous_questions_and_answers.append((new_question, response))
        with open("code.ahk", "w") as f:
            f.write(proc_obj.code)



def main():
    os.system("cls" if os.name == "nt" else "clear")
    # keep track of previous questions and answers
    while True:
        # ask the user for their question
        new_question = input(
            Fore.GREEN + Style.BRIGHT + "What can I get you?: " + Style.RESET_ALL
        )
        #save
        #save
        #save
        #save
        if new_question.strip() == "save":
            pass
        # check the question is safe
        errors = get_moderation(new_question)
        if errors:
            print(
                Fore.RED
                + Style.BRIGHT
                + "Sorry, you're question didn't pass the moderation check:"
            )
            for error in errors:
                print(error)
            print(Style.RESET_ALL)
            continue
        x = Thread(target = process_response.manage, args=[new_question])
        j = Thread(target = process_response.bar)
        j.start()
        x.start()
        j.join()
        x.join()

        # print the response

if __name__ == "__main__":
    main()


    """
And every night before he went to bed, Alexander would tell his children the story of the giant wolf and how he learned that bravery and kindness are the most important qualities a person can have.
What can I get you?: i need an autohotkey script that shows a listview and opens a file select menu
Here you go: Here's an AutoHotkey script that shows a ListView and opens a file select menu when an item in the ListView is double-clicked:

```
#NoEnv
#SingleInstance Force

Gui, Add, ListView, r10 w300 h200 vMyListView, Column1|Column2
Gui, Add, Button, x10 y220 w100 h30 gOpenFile, Open File

Loop, 10
{
    Gui, MyListView, Add, % "Item" . A_Index . "|Description " . A_Index
}

Gui, Show, w320 h260, ListView Example
Return

OpenFile:
Gui, Submit
SelectedItem := MyListView.GetSelected()
If (SelectedItem <> "")
{
    FileSelectFile, SelectedFile, 3, , Select a file to open
    If (SelectedFile <> "")
    {
        Run, %SelectedFile%
    }
}
Return
```

This script creates a GUI window with a ListView control and a button labeled "Open File". The ListView has two columns and ten rows of sample data. When an item in the ListView is double-clicked, the script opens a file select dialog box. If a file is selected, the script runs the file.

You can customize this script by changing the number of columns and rows in the ListView, modifying the text displayed in the ListView items, and changing the behavior of the file select dialog box.
What can I get you?:



    """