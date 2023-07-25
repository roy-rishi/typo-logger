from pynput import keyboard
from Levenshtein import distance
import threading
import time

WORDS_DB="google-10000-english"


def on_press(key):
    try:
        print(f"{key.char} PRESSED")
        if len(unreleased_modifiers) == 0 and key.char.isalnum():
            edit_word(key.char)
    # is non-alphnumeric
    except AttributeError:
        print(f"{key} PRESSED M")
        if str(key) in MODIFIERS:
            if str(key)[-1] == "r":
                key = str(key)[:-2]
            unreleased_modifiers.append(str(key))
        if str(key) == "Key.backspace":
            edit_word(str(key))
        if str(key) == "Key.space" or str(key) == "Key.enter":
            register_word()

def on_release(key):
    global unreleased_modifiers
    print(f"{key} RELEASED")
    if str(key) in MODIFIERS:
        if str(key)[-1] == "r":
                key = str(key)[:-2]
        unreleased_modifiers = [i for i in unreleased_modifiers if i != str(key)]
    print(unreleased_modifiers)


def keyboard_listener():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()
# start the keyboard listener in a separate thread
keyboard_thread = threading.Thread(target=keyboard_listener)
keyboard_thread.start()

MODIFIERS=["Key.cmd", "Key.alt", "Key.ctrl", "Key.cmd_r", "Key.alt_r", "Key.ctrl_r"]
RIGHT_MODIFIERS=["Key.cmd_r", "Key.alt_r", "Key.ctrl_r"]
unreleased_modifiers = []

global_word = ""
global_edited = False
def edit_word(key_val):
    global global_word
    global global_edited
    if key_val != "Key.backspace":
        print("ADDITION" + str(key_val))
        global_word += key_val
    else:
        print("DELETION")
        if "Key.cmd" in unreleased_modifiers or "Key.alt" in unreleased_modifiers:
            global_word = ""
        global_word = global_word[:-1]
        global_edited = True
    print("WORD", global_word)

def register_word():
    global global_word
    global global_edited
    timestamp = int(time.time())
    correction = correct_word(global_word)

    print("REGISTERING", global_word)
    with open("log.csv", "a") as log:
        # timestamp, word as spelled, corrected word, if backspace was used, if word was typed correctly
        log.write(f"{timestamp}, {global_word}, {correction}, {global_edited}, {global_word == correction and not global_edited}\n")

    global_word = ""
    global_edited = False

with open(WORDS_DB, 'r') as f:
    words = f.readlines()
# remove \n, make lowercase
words = [x.strip().lower() for x in words]

def correct_word(word):
    distances = []
    for i in words:
        # d = distance(word, i, weights=(1,1,1), score_cutoff=3)
        d = distance(word, i, weights=(1,1,1), score_cutoff=6)
        distances.append(d)
        if d == 0:
            return i

    min_distance = min(distances)
    closest_word = words[distances.index(min_distance)]
    return closest_word
