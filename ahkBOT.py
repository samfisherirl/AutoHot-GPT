import revChatGPT.V3
from pathlib import Path
cwd = Path(__file__).parent
from shutil import copy, move
from time import sleep

class Chat:
    def __init__(self):
        self.key = self.keyGet()
        self.input = ""
        self.output = ""
        self.code = ""
        self.ahk_mod = "Develope an autohotkey script. "
        self.kill_loop = False
        self.temp = cwd / "ahk.txt"
        self.v1 = cwd / "v1.ahk"
        self.v2 = cwd / "v2.ahk"
        self.myscript = cwd / "MyScriptv2.ahk"

    def keyGet(self):
        try:
            with open(cwd / "key.txt", "r") as f:
                key = str(f.read())
                return str(key.split("=")[1].strip())
        except Exception as e:
            print("\n\nNo key found. Make sure there's a text file named key.txt\napi_key=xxxxxxxxxx\n\n" + str(e))
            return False

    def ask_user(self):
        if self.key:
            self.input = input("\nType exit to quit. Tell me about your AHKv2 script need: ")
            self.input = self.input.lower().strip()
            if self.input == "exit" or self.input == "quit":
                self.kill_loop = True
            else:
                self.input = self.ahk_mod + self.input

    def process_chat(self):
        how_much_code = self.output.count("```")
        if how_much_code == 0:
            print(self.output)
        elif how_much_code > 0:
            print(self.output)
            ar = self.output.split("```")
            self.code = ar[1]
            with open(self.temp, 'w') as f:
                f.write(self.code)
            copy(self.temp, self.v1)
            while True:
                if self.v2.is_file():
                    copy(self.v2, self.temp)
                    with open(self.temp, "r") as f:
                        self.code = f.read()
                    self.code = "\n\nHere is your AHKv2 code. This is also locate in your clipboard and next to this app:\n" + self.code + "\n"
                    print(self.code)
                    move(self.v2, self.myscript)
                    break
                else:
                    sleep(0.1)


def loop_ask():
    chat = Chat()
    key = chat.key
    chatbot = revChatGPT.V3.Chatbot(api_key=key, engine="gpt-3.5-turbo")
    while True:
        chat.ask_user()
        if chat.kill_loop:
            break
        if chat.input:
            chat.output = chatbot.ask(chat.input)
        chat.process_chat()
        

if __name__ == "__main__":
    loop_ask()

