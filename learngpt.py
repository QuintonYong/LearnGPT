from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os
import serial
import time
from colorama import init, Fore, Back, Style
import cv2
import numpy as np
import tensorflow as tf

init(convert=True)

LEARN = 0
TEST = 1
HISTORY = 2

NO_INTRO = 0
NO_CODE = 1
NO_SOLVE = 2
UNDERSTAND = 3

ser = serial.Serial(
    port = "COM3",
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS
)

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer: 
"""

pad_no_intro = "Can you respond like you know nothing about "
pad_no_code = "Can you respond like you only know a little bit about, but don't know the code for, "
pad_no_solve = "Can give a short response like you don't know much about "
pad_understand = "Can you give a short response about "

modes = ["learn", "test", "history"]
stages = ["no_intro", "no_code", "no_solve", "understand"] 

mode = modes[TEST]
stage = stages[NO_INTRO]

model = OllamaLLM(model="llama3.2")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

interpreter = tf.lite.Interpreter(model_path = "model_unquant.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

def learning_conversation():
    context = ""

    topic = input(Fore.LIGHTRED_EX + "(Learning Mode) What are we learning about today? ")
    topic = topic.lower()

    if topic == "exit":
        return

    if not os.path.exists(topic):
        os.makedirs(topic)    

    while True:
        curr_stage = get_stage(topic)
        stage = stages[curr_stage]

        user_input = input(Fore.LIGHTBLUE_EX + "You: ")
        if user_input.lower() == "exit":
            break
        
        padding = ""
        if stage == "no_intro":
            padding = pad_no_intro
        elif stage == "no_code":
            padding = pad_no_code
        elif stage == "no_solve":
            padding = pad_no_solve
        elif stage == "understand":
            padding = pad_understand
        
        padded_input = padding + topic + "? " + user_input

        result = chain.invoke({"context":"", "question": padded_input})
        print(Fore.LIGHTGREEN_EX + "Bot:", result)

        new_context = f"\nUser: {user_input}\nAI: {result}"
        context += f"\nUser: {user_input}\nAI: {result}"

        add_to_stage_file(topic, user_input, new_context)


def add_to_stage_file(topic, user_input, new_context):
    filename = ""

    if "code for" in user_input.lower() or "code is" in user_input.lower():
        filename = topic + "/code.txt"
    elif " is " in user_input.lower() or " are " in user_input.lower():
        filename = topic + "/intro.txt"
    else:
        filename = topic + "/solve.txt"

    with open(filename, "a") as text_file:
        text_file.write(new_context)


def get_stage(topic):
    if not os.path.isdir(topic):
        return NO_INTRO
    
    introfile = topic + "/intro.txt"
    codefile = topic + "/code.txt"
    solvefile = topic + "/solve.txt"

    if not os.path.isfile(introfile):
        return NO_INTRO
    else:
        with open(introfile, 'r') as file:
            history = file.read()
            num_exchanges = history.count("AI:")

            if num_exchanges < 2:
                return NO_INTRO
            
    if not os.path.isfile(codefile):
        return NO_CODE
    else:
        with open(codefile, 'r') as file:
            history = file.read()
            num_exchanges = history.count("AI:")

            if num_exchanges < 3:
                return NO_CODE
            
    if not os.path.isfile(solvefile):
        return NO_SOLVE
    else:
        with open(solvefile, 'r') as file:
            history = file.read()
            num_exchanges = history.count("AI:")

            if num_exchanges < 3:
                return NO_SOLVE
            
    return UNDERSTAND
    

def test_questions():
    topic = input(Fore.LIGHTRED_EX + "(Testing Mode) What is the test topic? ")
    topic = topic.lower()

    if topic == "exit":
        return

    curr_stage = get_stage(topic)
    stage = stages[curr_stage]

    test_pad_no_intro = "Can you give a short response and give the wrong answer but you think it's right?"
    test_pad_no_code = "Can you give just the code with completely wrong code?"
    test_pad_no_solve = "Can you give just the code with many logic errors?"
    test_pad_understand = "Can you give just the code?"
    
    test_padding = ""
    if stage == "no_intro":
        test_padding = test_pad_no_intro
    elif stage == "no_code":
        test_padding = test_pad_no_code
    elif stage == "no_solve":
        test_padding = test_pad_no_solve
    elif stage == "understand":
        test_padding = test_pad_understand

    while True:
        question = input(Fore.LIGHTBLUE_EX + "Test Question: ")

        if question.lower() == "exit":
            break

        test_padded_input = question + " " + test_padding
        
        answer = model.invoke(input=test_padded_input)
        print(Fore.LIGHTGREEN_EX + "Bot:", answer)


def show_history():
    topic = input(Fore.LIGHTRED_EX + "(History Mode) What is topic? ")
    topic = topic.lower()

    if topic == "exit":
        return
    
    introfile = topic + "/intro.txt"
    codefile = topic + "/code.txt"
    solvefile = topic + "/solve.txt"

    print()
    print(Fore.LIGHTRED_EX + "The following conversations contain introductions of the topic:")
    print_conversation(introfile)
    print()
    print(Fore.LIGHTRED_EX + "The following conversations contain code explanations:")
    print_conversation(codefile)
    print()
    print(Fore.LIGHTRED_EX + "The following conversations contains additional problem solving explanations:")
    print_conversation(solvefile)


def print_conversation(convo_file):
    if not os.path.isfile(convo_file):
        print()
    else:
        with open(convo_file, 'r') as file:
            color = Fore.LIGHTBLUE_EX
            for line in file:
                if "User: " in line:
                    color = Fore.LIGHTBLUE_EX
                elif "AI: " in line:
                    color = Fore.LIGHTGREEN_EX

                print(color + line.strip())


def login():
    time.sleep(2)
    print(Fore.LIGHTRED_EX + "Please look at your camera to log in.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        input_image = cv2.resize(frame, (224, 224))
        input_image = np.expand_dims(input_image, axis = 0)
        input_image = input_image.astype(np.float32) / 255.0

        interpreter.set_tensor(input_details[0]['index'], input_image)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])

        predicted_class = np.argmax(predictions)
        confidence = np.max(predictions)

        if predicted_class == 0 and confidence > 0.8:
            ser.write(b"LOGIN\n")
            break

        cv2.imshow("Webcam", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.LIGHTRED_EX + "Welcome to LearnGPT!")

    login()

    print()
    print(Fore.LIGHTRED_EX + "Welcome back Quinton!")

    while True:
        print()
        print(Fore.LIGHTRED_EX + "Please select a mode on your LearnGPT device.")
        mode = str(ser.readline())[2:][:-5]

        if mode == "L":
            learning_conversation()
        elif mode == "T":
            test_questions()
        elif mode == "H":
            show_history()

    print(Style.RESET_ALL)
    ser.close()
