# --- EEG Experiment for Cog Neuro 2026 ---
from psychopy import core, visual, event
from psychopy.hardware import keyboard
import pandas as pd
import random
from datetime import datetime
import os
import triggers # UNCOMMENT AFTER TRIGGERS INSERTED

if not os.path.exists("logfiles"):
    os.makedirs("logfiles")

def check_exit():
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()

# define window
win = visual.Window(color = "black", fullscr = True)

# trigger codes
## response trigger
RESPONSE_CORRECT = 10
RESPONSE_INCORRECT = 11

## condition triggers
WORD_CONGRUENT = 20
WORD_INCONGRUENT = 21

FACE_CONGRUENT = 30
FACE_INCONGRUENT = 31

def get_cond_trigger(condition, congruency):
    if condition == "word":
        return WORD_CONGRUENT if congruency else WORD_INCONGRUENT
    elif condition == "face":
        return FACE_CONGRUENT if congruency else FACE_INCONGRUENT        

# initialize text stim
emotions = ["happy", "sad"]

# initialize condition instructions
focus_word_stim = visual.TextStim(
    win,
    text="You may take a break before proceeding.\n\nFocus on the WORD in the next trials.\n\nPress s or h to begin.",
    color="white",
    height=0.08,
    wrapWidth=1.4
)

focus_face_stim = visual.TextStim(
    win,
    text="You may take a break before proceeding.\n\nFocus on the FACE in the next trials.\n\nPress s or h to begin.",
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
kb = keyboard.Keyboard()

# trials
reps = 12  # MUST BE EVEN OR CODE WILL BREAK YA DUMMY

trial_list = []

for img_file, emotion_image in all_images:
    for i in range(reps):
        if i % 2 == 0:
            emotion_text = emotion_image
            stim_congruence = True
        else:
            emotion_text = "sad" if emotion_image == "happy" else "happy"
            stim_congruence = False

        trial_list.append((
            img_file, 
            emotion_image, 
            emotion_text, 
            stim_congruence))

random.shuffle(trial_list)

# Welcome page
intro = visual.TextStim(
    win,
    text="""
    In this experiment, you will see faces with a word written across them. 
    Sometimes the emotions of the word and the facial expressions will match, and sometimes they won't.
    
    Your task is to respond to either the word or the face - you will be told which one to focus on before each block.
    
    Press s if the emotion is sad, and h if the emotion is happy. Try to respond as quickly and accurately as possible.
    
    If you wish to exit, you can press escape at any time. But plz don't.
    
    Press any key to begin.
    """,
    color="white",
    height=0.08,
    wrapWidth=1.4
)
intro.draw()
win.flip()
check_exit()
event.waitKeys()

# experimental loop setup
trials = []

participant_id = random.randint(1000, 9999)

pullTriggerDown = False

# trial count
trial = 0

# ACTUAL EFFIN' LOOP LET'S GOOOOO
for condition, instruction_stim in conditions:
    instruction_stim.draw()
    win.flip()
    check_exit()
    event.waitKeys(keyList=["s","h"])
        
    for img_file, emotion_image, emotion_text, stim_congruence in trial_list:
        # show fixation cross for 400 ms
        fixation.draw()
        win.flip()
        check_exit()
        core.wait(.4)

        # initialize stim
        image_stim.image = img_file
        text_stim.text = emotion_text

        # prepare stim
        image_stim.draw()
        text_stim.draw()

        # start timer and trigger
        win.callOnFlip(rt_clock.reset)
        win.callOnFlip(kb.clock.reset)
        win.callOnFlip(kb.clearEvents)
        
        # --- cond_trigger ---
        if pullTriggerDown:
            win.callOnFlip(setParallelData, 0)
            pullTriggerDown = False

        cond_trigger = get_cond_trigger(condition, stim_congruence)
        win.callOnFlip(setParallelData, cond_trigger)
        pullTriggerDown = True
        # --------------------
        
        # flip window
        win.flip()
        check_exit()
        
        # initialize keys
        keys = kb.waitKeys(keyList=["s", "h"])
        response, rt = keys[0].name, keys[0].rt

#        setParallelData(RESPONSE)
#        core.wait(0.005)
#        setParallelData(0)
        
        # evaluate response
        response_label = "sad" if response == "s" else "happy"
        if condition == "face":
            correct_response = (response_label == emotion_image)
            setParallelData(RESPONSE_CORRECT) if correct_response else setParallelData(RESPONSE_INCORRECT)
            core.wait(0.005)
            setParallelData(0)
        else:
            correct_response = (response_label == emotion_text)
            setParallelData(RESPONSE_CORRECT) if correct_response else setParallelData(RESPONSE_INCORRECT)
            core.wait(0.005)
            setParallelData(0)

        # log data
        trials.append({
            "participant_id": participant_id,
            "trial": trial,
            "condition": condition,
            "image": img_file,
            "emotion_image": emotion_image,
            "emotion_text": emotion_text,
            "stim_congruence": stim_congruence,
            "response": response,
            "correct_response": correct_response,
            "rt": rt
        })
        trial += 1

# get datetime for unique logfile name
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# create logfile path and name
logfile_name = f"logfiles/logfile_{timestamp}.csv"

logfile = pd.DataFrame(trials, columns = [
    "participant_id",
    "trial",
    "condition", 
    "image", 
    "emotion_image", 
    "emotion_text", 
    "stim_congruence", 
    "response", 
    "correct_response", 
    "rt"])

logfile.to_csv(logfile_name, index = False)

win.close()
core.quit()