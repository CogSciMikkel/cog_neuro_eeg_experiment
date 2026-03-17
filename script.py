# --- EEG Experiment for Cog Neuro ---
from psychopy import core, visual, event
from psychopy.hardware import keyboard
import pandas as pd
import random
from datetime import datetime
import os
# import triggers

# define window
win = visual.Window(color = "black", fullscr = True)

# suggested trigger codes
WORD_BLOCK = 10
FACE_BLOCK = 11

WORD_CONGRUENT = 20
WORD_INCONGRUENT = 21
FACE_CONGRUENT = 22
FACE_INCONGRUENT = 23

RESPONSE_CORRECT = 30
RESPONSE_INCORRECT = 31

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
image_stim = visual.ImageStim(
    win, 
    size=(.8, 1.3), 
    pos=(0, 0)
    )

text_stim = visual.TextStim(
    win, 
    height=.3, 
    color="white", 
    pos=(0, 0), 
    ori = 45, 
    anchorHoriz='center', 
    anchorVert='center', 
    alignText='center'
    )

# RT
rt_clock = core.Clock()

# trials
reps = 10  # must be even for balance

trial_list = []

for img_file, emotion_image in all_images:
    for i in range(reps):
        if i % 2 == 0:
            emotion_text = emotion_image
            stim_congruence = True
        else:
            emotion_text = "sad" if emotion_image == "happy" else "happy"
            stim_congruence = False

        trial_list.append((img_file, emotion_image, emotion_text, stim_congruence))

random.shuffle(trial_list)

# experimental loop
trials = []

participant_id = random.randint(1000, 9999)

pullTriggerDown = False

for condition, instruction_stim in conditions:
    instruction_stim.draw()
    win.flip()
    event.waitKeys(keyList=["s","h"])
    
    # --- TRIGGER? ---
#    if condition == "word":
#        block_trigger = WORD_BLOCK
#    else:
#        block_trigger = FACE_BLOCK
#
#    fixation.draw()
#    win.callOnFlip(setParallelData, block_trigger)
#    pullTriggerDown = True
#    win.flip()

#    if pullTriggerDown:
#        fixation.draw()
#        win.callOnFlip(setParallelData, 0)
#        pullTriggerDown = False
#        win.flip()
    # --- ---
    
    for img_file, emotion_image, emotion_text, stim_congruence in trial_list:
        # show fixation cross for 400 ms
        fixation.draw()
        win.flip()
        core.wait(.4)

        # initialize stim
        image_stim.image = img_file
        text_stim.text = emotion_text

        # prepare stim
        image_stim.draw()
        text_stim.draw()

        # start timer and trigger
        win.callOnFlip(rt_clock.reset)
        
        # --- TRIGGER ---
        
        # flip window
        win.flip()

        # initialize keys
        response, rt = event.waitKeys(keyList=["s", "h"], timeStamped=rt_clock)[0]
        
        # ___ TRIGGER ---
        
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