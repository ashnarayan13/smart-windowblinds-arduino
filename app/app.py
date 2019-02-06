from flask import Flask, flash, redirect, render_template, request, session, abort
import sensor_calcs
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, os.path, glob

app = Flask(__name__)


# 0 - STOP
# 1 - UP
# 2 - DOWN
# 3 - OPEN
# 4 - CLOSE
# 5 - RESET-DOWN
# 6 - RESET-UP
class StateMachine:
    state = 0
    prox_counter = 0
    prev_state = 0
    s_path = ""
    prox_on = 0


@app.route('/')
def hello_world():
    control = StateMachine.state
    # =====
    if StateMachine.state == 3:
        StateMachine.prev_state = 3
        print ("PREV STATE IS = {}".format(StateMachine.prev_state))
    if StateMachine.prev_state == 3:
        StateMachine.state = 0
        StateMachine.prev_state = 0
        print ("STATE IS = {}".format(StateMachine.state))
    # =====
    # =====
    if StateMachine.state == 4:
        StateMachine.prev_state = 4
        print ("PREV STATE IS = {}".format(StateMachine.prev_state))
    if StateMachine.prev_state == 4:
        StateMachine.state = 0
        StateMachine.prev_state = 0
        print ("STATE IS = {}".format(StateMachine.state))
    # =====
    # =====
    if StateMachine.state == 5:
        StateMachine.prev_state = 5
        print ("PREV STATE IS = {}".format(StateMachine.prev_state))
    elif StateMachine.state == 6:
        StateMachine.prev_state = 6
        print ("PREV STATE IS = {}".format(StateMachine.prev_state))

    if StateMachine.prev_state == 5 or StateMachine.prev_state == 6:
        StateMachine.state = 0
        StateMachine.prev_state = 0
        print ("STATE IS = {}".format(StateMachine.state))
    # =====
    return render_template('index.html', out_command=control)


@app.route("/proximity/")
def proximity():
    prox = request.args.get('prox')
    # =======================================
    # POLICY 1: PROXIMITY
    # Condition: User detected near the window
    # =======================================
    # if 10 measurements are < 20
    # than change state to MOVE UP
    #
    u_PROX_COUNT_MAX = 3
    u_prox = int(float(prox))
    # Increment counter
    if u_prox < 20:
        StateMachine.prox_counter += 1
        print ("(PROX) SM PROX COUNTER = {}".format(StateMachine.prox_counter))
    else:
        StateMachine.prox_counter = 0
        StateMachine.prox_on = 1
        StateMachine.state = 4
        print ("(PROX RESET) SM PROX COUNTER = {}".format(StateMachine.prox_counter))

    # Check Action is needed
    if StateMachine.prox_counter > u_PROX_COUNT_MAX:
        print ("(PROX) STATE IS = {}".format(StateMachine.state))
        if StateMachine.state != 5 or StateMachine.state != 6:  # if not RESET
            StateMachine.prox_on = 1
            StateMachine.state = 3   # than OPEN
    # =======================================

    return render_template('prox.html', prox=prox)


@app.route("/microphone/")
def microphone():
    mic = request.args.get('mic')
    # =======================================
    # POLICY 2: CLAPS (MICROPHONE)
    # Condition: User claps
    # =======================================
    # - if first clap detected than change state to OPEN (3)
    # - if second clap detected than change state to CLOSE (4)
    # PRECONDITIONS: STOP (0) or DOWN (2)

    u_MIC_MAX = 100
    u_mic = int(float(mic))
    # Check Action is needed
    if u_mic > u_MIC_MAX:
        StateMachine.state = 3
        # If we detecting second clap or need to close blinds
        if StateMachine.state == 3 and StateMachine.prev_state == 3:
            StateMachine.state = 4
            StateMachine.prev_state = 0
        StateMachine.prev_state = 3
    return render_template('microphone.html', mic=mic)


@app.route("/data/")
def data():
    temp = request.args.get('temp')
    hum  = request.args.get('hum')
    uv   = request.args.get('uv')
    lum  = request.args.get('lum')
    ir   = request.args.get('ir')
    #lum = "3.000"
    #ir = "12.00"
    #prox = request.args.get('prox')
    # =======================================
    # FEATURE 1: DUMP DATA
    # to csv file (append)
    # =======================================
    with open('sensors_data.csv', mode='a') as sensors_data_file:
        sensors_data = csv.writer(sensors_data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sensors_data.writerow([float(temp), float(hum), float(uv), float(lum), float(ir)])
        print ("LOG: temp = {}, hum = {}, uv = {}, lum = {}, ir = {}".format(float(temp), float(hum), float(uv), float(lum), float(ir)))

    # TRUE - Open
    # FALSE - Close
    # sensor_calcs.calculate_movement();

    # DRAW DIAGRAM
    df = pd.read_csv("sensors_data.csv", names=["Temperature", "Humidity", "UV", "Luminance", "IR level"])
    #df = df.tail(12)
    df = df[-12:]
    df.plot()
    plt.legend(loc='best')
    # GET NAME (count files)
    path = "static/images/plot/"
    pngCounter = len(glob.glob1(path, "*.png"))
    cur_num = pngCounter + 1
    path = path + str(cur_num) + ".png"
    plt.savefig(path)
    serv_path = "http://10.25.12.154/static/images/plot/" + str(cur_num) + ".png"
    StateMachine.s_path = serv_path

    # PROXIMITY CHECK
    #print ("(PROX) STATE IS {}".format(StateMachine.prox_on))
    if StateMachine.prox_on == 1:
        StateMachine.state = 0
        StateMachine.prox_on = 0
    #print ("(PROX) STATE IS {}".format(StateMachine.prox_on))

    # ====================
    # POLICY 2: IR Sensor
    # ====================
    #act = sensor_calcs.justBasic(ir, lum)
    #if act:
    #    StateMachine.state = 3
    #else:
    #    StateMachine.state = 4



    return render_template('data.html', temp=temp, hum=hum, uv=uv)


@app.route('/user/', defaults={'command': ''}, methods=['GET'])
def user(command):
    if request.method == 'GET':
        command = request.args.get('command', '')

    if command == '':
        command = str(StateMachine.state)
    else:
        # User decides to change mode manually
        StateMachine.state = int(command)

    # Pretty text (command description)
    command_name = ""
    if command == '0':
        command_name = "STOP"
    elif command == '1':
        command_name = "MOVE UP"
    elif command == '2':
        command_name = "MOVE DOWN"
    elif command == '3':
        command_name = "OPEN"
    elif command == '4':
        command_name = "CLOSE"
    elif command == '5':
        command_name = "RESET-DOWN"
    elif command == '6':
        command_name = "RESET-UP"
    else:
        command_name = "UNKNOWN = {}".format(command)

    return render_template('user.html', command=command_name, sp=StateMachine.s_path)


if __name__ == '__main__':
    app.run()

