# --- EEG Experiment for Cog Neuro ---



# --- REMEMBER TO CHECK OUT THE CHECKLIST ---
# remember triggers



# loading modules
from psychopy import gui, core, visual, event
from psychopy.hardware import keyboard
import pandas as pd
import random
from datetime import datetime
import os

# define window
win = visual.Window(color = "black", fullscr = True)

# initialize text stim
emotions = ["happy", "sad"]

# initialize condition instructions
focus_word_stim = visual.TextStim(
    win,
    text="Focus on the WORD in the next trials.\n\nPress s or h to begin.",
    color="white",
    height=0.08,
    wrapWidth=1.4
)

focus_face_stim = visual.TextStim(
    win,
    text="Focus on the FACE in the next trials.\n\nPress s or h to begin.",
    color="white",
    height=0.08,
    wrapWidth=1.4
)

conditions = [
    ("word", focus_word_stim),
    ("face", focus_face_stim)
]

# randomize condition order
random.shuffle(conditions)

# initialize fixation cross
fixation = visual.TextStim(win, text="+", color="white")

# read img file names
path_happy = "happy/"
path_sad = "sad/"

happy_img = os.listdir(path_happy)
sad_img = os.listdir(path_sad)

all_images = (
    [(path_happy + img, "happy") for img in happy_img] +
    [(path_sad + img, "sad") for img in sad_img]
)

# stimuli
image_stim = visual.ImageStim(win, size=(.8, 1.3), pos=(0, 0))
text_stim = visual.TextStim(win, height=.3, color="white", pos=(0, 0), ori = 45, anchorHoriz='center', anchorVert='center', alignText='center')

# RT
rt_clock = core.Clock()

# trials
n_trials = 4 # len(all_images) -- tbd
n_congruent = n_trials // 2
n_incongruent = n_trials // 2

trial_list = []

for _ in range(n_congruent):
    img_file, emotion_image = random.choice(all_images)
    emotion_text = emotion_image
    trial_list.append((img_file, emotion_image, emotion_text, True))

for _ in range(n_incongruent):
    img_file, emotion_image = random.choice(all_images)
    emotion_text = "sad" if emotion_image == "happy" else "happy"
    trial_list.append((img_file, emotion_image, emotion_text, False))

random.shuffle(trial_list)

# experimental loop
trials = []

participant_id = random.randint(1000, 9999)

for condition, instruction_stim in conditions:
    instruction_stim.draw()
    win.flip()
    event.waitKeys(keyList=["s","h"])
    
    for img_file, emotion_image, emotion_text, stim_congruence in trial_list:
        # show fixation cross for 400 ms
        fixation.draw()
        win.flip()
        core.wait(.4)

        # initialize stim
        image_stim.image = img_file
        text_stim.text = emotion_text

        # show stim
        image_stim.draw()
        text_stim.draw()

        # start timer
        win.callOnFlip(rt_clock.reset)
        win.flip()

        # initialize keys
        response, rt = event.waitKeys(keyList=["s", "h"], timeStamped=rt_clock)[0]

        # evaluate response
        response_label = "sad" if response == "s" else "happy"
        if condition == "face":
            correct_response = (response_label == emotion_image)
        else:
            correct_response = (response_label == emotion_text)

        # log data
        trials.append({
            "participant_id": participant_id,
            "condition": condition,
            "image": img_file,
            "emotion_image": emotion_image,
            "emotion_text": emotion_text,
            "stim_congruence": stim_congruence,
            "response": response,
            "correct_response": correct_response,
            "rt": rt
        })

# get datetime for unique logfile name
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# create logfile path and name
logfile_name = f"logfiles/logfile_{timestamp}.csv"

logfile = pd.DataFrame(trials, columns = ["participant_id", "condition", "image", "emotion_image", "emotion_text", "stim_congruence", "response", "correct_response", "rt"])
logfile.to_csv(logfile_name, index = False)

win.close()
core.quit()