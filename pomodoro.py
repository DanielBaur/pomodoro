
# This Python program is used to implement a pomodoro timer.
# see: https://en.wikipedia.org/wiki/Pomodoro_Technique
# This code is based on Johanes Alt's version of the program. I only adapted it to also become familiar with the os interfacing.
# $ python3 /path/to/file/pomodoro.py
# or
# $ python3 /path/to/file/pomodoro.py 25 5 15 4


# summary
docstring1 = "\t'pomodoro.py' is a software tool helping you to stay focussed according to the Pomodoro method."
docstring2 = "\tWorking shifts of 't_pomodori_min' minutes are followed by pauses of 't_pause_short_min' minutes."
docstring3 = "\tAfter every 'n_pmodori' shifts a short pause is replaced by a long pause of 't_pause_long_min' minutes."


# controls
docstring4 = "\t'ctrl+c' end the pomodoro.py session"
docstring5 = "\t'ctrl+q+p' preemptively start a pause during a work shift"
docstring6 = "\t'ctrl+q+w' preemptively start a work session during a pause"




##################################################
### Imports
##################################################

import time
import argparse
import sys
import os
import subprocess
import datetime
import keyboard
import json





##################################################
### Helper Definitions
##################################################


default_pomodoro_parameters = {
    "t_pomodori_min" : 25,
    "t_pause_short_min" : 5,
    "t_pause_long_min" : 15,
    "n_pomodori" : 4}


filename_record_file = "record_file.txt"


weekdays = {
    "2" : "Monday",
    "3" : "Tuesday",
    "4" : "Wednesday",
    "5" : "Thursday",
    "6" : "Friday",
    "7" : "Saturday",
    "1" : "Sunday"}


# This function is used to retrieve a Python3 dictionary stored as a .json file (copied from monxeana).
def get_dict_from_json(input_pathstring_json_file):
    with open(input_pathstring_json_file, "r") as json_input_file:
        ret_dict = json.load(json_input_file)
    return ret_dict


# This function is used to save a Python3 dictionary as a .json file (copied from monxeana).
def write_dict_to_json(output_pathstring_json_file, save_dict):
    with open(output_pathstring_json_file, "w") as json_output_file:
        json.dump(save_dict, json_output_file, indent=4)
    return


# This function is used to ask the user for his/her pomodoro parameters if not specified upon program call.
def ask_for_pomodoro_parameters():

    # defining default
    pomodoro_parameters = default_pomodoro_parameters.copy()

    # asking for user input
    print(f"pomodoro.py: Please enter your pomodoro parameters:")
    for parameter in [*pomodoro_parameters]:
        user_input = input(f"\t{parameter} (default is {default_pomodoro_parameters[parameter]}): ")
        if user_input == "":
            continue
        else:
            pomodoro_parameters[parameter] = int(user_input)
    print(f"\n")

    # returning pomodoro parameters
    return pomodoro_parameters


# This function is used to convert a datetime.timedelta object to a dictionary containing 
def tdToDict(td:datetime.timedelta) -> dict:
    def __t(t, n):
        if t < n: return (t, 0)
        v = t//n
        return (t -  (v * n), v)
    (s, h) = __t(td.seconds, 3600)
    (s, m) = __t(s, 60)    
    (micS, milS) = __t(td.microseconds, 1000)

    return {
         'days': td.days
        ,'hours': h
        ,'minutes': m
        ,'seconds': s
        ,'milliseconds': milS
        ,'microseconds': micS
    }


# This function is used to write the finished working session to a history/highscore file.
def record_pomodoro_session(
    abspath_record_file,
    record_dict):

    # retrieving current 'record_file' data
    try:
        save_dict = get_dict_from_json(abspath_record_file)
    except:
        save_dict = {}

    # adding the new session
    save_dict.update(record_dict)

    # saving the 'record_dict'
    write_dict_to_json(abspath_record_file, save_dict)

    return




##################################################
### Main Definition
##################################################


# This is the main function of this program. It is used as a pomodoro timer.
def pomodoro(
    t_pomodori_min = default_pomodoro_parameters["t_pomodori_min"], # duration of the work phases in minutes
    t_pause_short_min = default_pomodoro_parameters["t_pause_short_min"], # duration of the short pauses in minutes
    t_pause_long_min = default_pomodoro_parameters["t_pause_long_min"], # duration of the long pauses in minutes
    n_pomodori = default_pomodoro_parameters["n_pomodori"]): # number of work phases required for a long pause

    # preparations
    print(f"pomodoro.py:\n\tt_pomodori_min = {t_pomodori_min} minute(s)\n\tt_pause_short_min = {t_pause_short_min} minute(s)\n\tt_pause_long_min = {t_pause_long_min} minute(s)\n\tn_pomodori = {n_pomodori}\n\n")
    print(f"pomodoro.py:")
    ctr_shifts = 1
    ctr_pauses = 1
    start_date = datetime.datetime.now()
    duration_shifts = datetime.timedelta()
    duration_pauses = datetime.timedelta()


    # main loop that is running until interrupted
    try:
        while True:

            ### pomodoro slice

            # counting up to 't_pomodori_min'
            timestamp_start = datetime.datetime.now()
            manual_pause = False
            while (datetime.datetime.now()-timestamp_start).seconds/60 <= t_pomodori_min and manual_pause == False:
                manual_pause = keyboard.is_pressed("ctrl+q+p")
                temp = datetime.datetime.now() -timestamp_start
                print(f"\tshift #{ctr_shifts}: {tdToDict(temp)['hours']:02d}:{tdToDict(temp)['minutes']:02d}:{tdToDict(temp)['seconds']:02d} h", end="\r")
                time.sleep(0.01)

            # info: time is up
            if manual_pause == False:
                zenity_cmd = "zenity --info --text='wörkse time is up'"
                zenity_return = subprocess.run(zenity_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #stdout = zenity_return.stdout.decode('utf-8')
            #stderr = zenity_return.stderr.decode('utf-8')
            #print(f"stdout: --->{stdout}<---")
            #print(f"stderr: --->{stderr}<---")

            # determining the duration of the shift
            temp = datetime.datetime.now() -timestamp_start
            duration_shifts = duration_shifts +temp
            print(f"\tshift #{ctr_shifts}: {tdToDict(temp)['hours']:02d}:{tdToDict(temp)['minutes']:02d}:{tdToDict(temp)['seconds']:02d} h")
            ctr_shifts += 1

            ### pauses

            # counting up to 't_pause_short_min' and 't_pause_long_min'
            t_pause_min = t_pause_long_min if ctr_pauses % n_pomodori == 0 else t_pause_short_min 
            timestamp_start = datetime.datetime.now()
            manual_work = False
            while (datetime.datetime.now() -timestamp_start).seconds/60 <= t_pause_min and manual_work == False:
                manual_work = keyboard.is_pressed("ctrl+q+w")
                temp = datetime.datetime.now() -timestamp_start
                print(f"\tpause #{ctr_pauses}: {tdToDict(temp)['hours']:02d}:{tdToDict(temp)['minutes']:02d}:{tdToDict(temp)['seconds']:02d} h", end="\r")
                time.sleep(0.01)

            # info: time is up
            if manual_pause == False:
                zenity_cmd = "zenity --info --text='pause time is up'"
                zenity_return = subprocess.run(zenity_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # determining the duration of the pause
            temp = datetime.datetime.now() -timestamp_start
            duration_pauses = duration_pauses +temp
            print(f"\tpause #{ctr_pauses}: {tdToDict(temp)['hours']:02d}:{tdToDict(temp)['minutes']:02d}:{tdToDict(temp)['seconds']:02d} h")
            ctr_pauses +=1

    except KeyboardInterrupt:
        interruptstring = f"\n\n\npomodoro.py: Done! In total you were working for {tdToDict(duration_shifts +duration_pauses)['hours']:02d}:{tdToDict(duration_shifts +duration_pauses)['minutes']:02d}:{tdToDict(duration_shifts +duration_pauses)['seconds']:02d} h straight!\n\t{ctr_shifts-1} shift(s), adding up to {tdToDict(duration_shifts)['hours']:02d}:{tdToDict(duration_shifts)['minutes']:02d}:{tdToDict(duration_shifts)['seconds']:02d} h \n\t{ctr_pauses-1} pause(s), adding up to {tdToDict(duration_pauses)['hours']:02d}:{tdToDict(duration_pauses)['minutes']:02d}:{tdToDict(duration_pauses)['seconds']:02d} h\n\n"
        print(interruptstring)

    record_dict = {
        f"{start_date.strftime('%Y%m%d_%H%M')} ({weekdays[str(start_date.weekday())]})" : {
            "worked" : f"{tdToDict(duration_shifts)['hours']:02d}:{tdToDict(duration_shifts)['minutes']:02d}:{tdToDict(duration_shifts)['seconds']:02d} h",
            "paused" : f"{tdToDict(duration_pauses)['hours']:02d}:{tdToDict(duration_pauses)['minutes']:02d}:{tdToDict(duration_pauses)['seconds']:02d} h"}
        }
    return record_dict





##################################################
### Main Execution
##################################################


# Executing the main program
if __name__ == "__main__":


    # printing text
    print(f"\n\n\n###################################\n### pomodoro.py\n###################################\n\n\n")
    print(f"pomodoro.py: summary\n{docstring1}\n{docstring2}\n{docstring3}\n\n")
    print(f"pomodoro.py: controls\n{docstring4}\n{docstring5}\n{docstring6}\n\n")



    # retrieving the pomodoro parameters
    if len(sys.argv) == 1:
        pomodoro_args = ask_for_pomodoro_parameters()
    elif len(sys.argv) == 5:
        pomodoro_args = default_pomodoro_parameters.copy()
        pomodoro_args["t_pomodori_min"] = int(sys.argv[1])
        pomodoro_args["t_pause_short_min"] = int(sys.argv[2])
        pomodoro_args["t_pause_long_min"] = int(sys.argv[3])
        pomodoro_args["n_pomodori"] = int(sys.argv[4])
    else:
        raise Exception("")
 
    # executing the pomodoro main program
    record_dict = pomodoro(
        t_pomodori_min = pomodoro_args["t_pomodori_min"],
        t_pause_short_min = pomodoro_args["t_pause_short_min"],
        t_pause_long_min = pomodoro_args ["t_pause_long_min"],
        n_pomodori = pomodoro_args["n_pomodori"])

    # using the pomodoro parameters passed upon program call
    h =  int(record_dict[[*record_dict][0]]["worked"][0:2]) 
    m =  int(record_dict[[*record_dict][0]]["worked"][3:5]) 
    s =  int(record_dict[[*record_dict][0]]["worked"][6:8]) 
    if h >= 1:
        print(f"pomodoro.py: You were working for more than one hour; the session was recorded.\n\n")
        record_pomodoro_session(
            abspath_record_file = '/'.join(sys.argv[0].split('/')[0:-1]) +'/' +filename_record_file,
            record_dict = record_dict)
    print("\n")
