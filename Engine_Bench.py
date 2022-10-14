import matplotlib.pyplot as plt
import numpy as np

import serial
import pygame as pg
import math
import json
import time

from multiprocessing import Process, Manager

caution_temp = 60


def plot(x_time: list, y_RPM: list, y_voltage: list, new_value):
    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(x_time, y_RPM, 'r-')
    plt.xlabel('Seconds Since Start')
    plt.ylabel('RPM')
    plt.title('Generated Data')
    plt.draw()

    while 1:
        if new_value.value == 1:
            line1.set_ydata(y_RPM)
            line1.set_xdata(x_time)
            plt.ylim([0, 6500])
            if len(x_time) == 0 or x_time[-1] < 100:
                plt.xlim([0, 100])
            else:
                plt.xlim([x_time[-1] - 100, x_time[-1]])
            plt.draw()
            plt.pause(0.02)

            new_value.value = 0

    plt.ioff()
    plt.show()


def plot_engine_curve(x_time: list, y_RPM: list, y_voltage: list, new_value):
    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(y_voltage, y_RPM, ':')
    plt.xlabel('Voltage')
    plt.ylabel('RPM')
    plt.title('Engine Curve')
    plt.draw()

    while 1:
        if new_value.value == 1:
            usable_index = [i for i in range(1, len(y_voltage)) if y_voltage[i] > y_voltage[i-1]]
            usable_RPM = [y_RPM[i] for i in usable_index]
            usable_voltage = [y_voltage[i] for i in usable_index]

            line1.set_ydata(usable_RPM)
            line1.set_xdata(usable_voltage)
            plt.ylim([0, 6500])
            plt.xlim([0, 25])

            plt.draw()
            plt.pause(0.02)

            new_value.value = 0

    plt.ioff()
    plt.show()


def dashboard(x_time: list, y_RPM: list, y_voltage: list, new_value):

    serial_speed = 1000000
    serial_port = '/dev/cu.usbmodem1301'
    ser = serial.Serial(serial_port, serial_speed, timeout=1)

    current_RPM = 0
    current_voltage = 0
    current_temp = [0, 0, 0, 0, 0, 0]
    MAX_RPM = 0

    pg.init()

    font = pg.font.Font('freesansbold.ttf', 32)
    font_2 = pg.font.Font('freesansbold.ttf', 22)
    font_3 = pg.font.Font('freesansbold.ttf', 32)
    font_4 = pg.font.Font('freesansbold.ttf', 38)
    font_5 = pg.font.Font('freesansbold.ttf', 15)
    font_6 = pg.font.Font('freesansbold.ttf', 13)


    screen = pg.display.set_mode([500, 500])
    pg.display.set_caption('LL6 Prototype Tachometer')

    start_time = time.time()

    running = True
    while running:

        # Get serial input
        data = ser.readline().decode()
        if data:
            try:
                d = [float(i) for i in data.split(',')]
                current_RPM = d[0]
                current_voltage = d[1]

                if len(d) > 2:
                    current_temp = d[2:]

                MAX_RPM = max(MAX_RPM, current_RPM)

                # Add data to history
                x_time.append(time.time() - start_time)
                y_RPM.append(current_RPM)
                y_voltage.append(current_voltage)

                new_value.value = 1
            except:
                print(data)
                print("Communication Error, Invalid Data Received")

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((0, 0, 0))

        pg.draw.circle(screen, (210, 216, 214), (250, 250), 250)
        pg.draw.circle(screen, (0, 0, 0), (250, 250), 248)
        pg.draw.circle(screen, (210, 216, 214), (250, 250), 245)
        # Draw Redline
        pg.draw.arc(screen, (255, 0, 27), (0, 0, 500, 500),
                    math.radians(269 - (5500 * 0.06)), math.radians(270 - (5000 * 0.06)), 100)
        pg.draw.circle(screen, (67, 91, 188), (250, 250), 155)
        pg.draw.circle(screen, (0, 0, 0), (250, 250), 150)

        dial_pos = 0
        deg = 90

        # Draw center words
        text = font.render(str(int(current_RPM)), True, (210, 216, 214))
        textRect = text.get_rect()
        textRect.center = (250, 220)
        screen.blit(text, textRect)

        text = font_2.render("Max: " + str(int(MAX_RPM)), True, (210, 216, 214))
        textRect = text.get_rect()
        textRect.center = (250, 250)
        screen.blit(text, textRect)

        text = font_2.render(f'{current_voltage} V', True, (210, 216, 214))
        textRect = text.get_rect()
        textRect.center = (250, 280)
        screen.blit(text, textRect)

        avg_temp = round(sum(current_temp) / len(current_temp), 1)
        if avg_temp >= caution_temp:
            text = font_2.render(f'{avg_temp} C', True, (255, 0, 0))
        else:
            text = font_2.render(f'{avg_temp} C', True, (210, 216, 214))
        textRect = text.get_rect()
        textRect.center = (250, 310)
        screen.blit(text, textRect)

        # Show split temperature
        temp_split_coordinate = [210, 330]
        for index, t in enumerate(current_temp):
            if t >= caution_temp:
                text = font_6.render(f'#{index + 1}: {t} C', True, (255, 0, 0))
            else:
                text = font_6.render(f'#{index + 1}: {t} C', True, (210, 216, 214))
            textRect = text.get_rect()
            textRect.center = tuple(temp_split_coordinate)
            screen.blit(text, textRect)

            if index % 2 == 0:
                temp_split_coordinate[0] = 290
            else:
                temp_split_coordinate[0] = 210
                temp_split_coordinate[1] += 20

        needle = current_RPM * 0.06

        # Draw Needle
        pg.draw.arc(screen, (236, 66, 69), (0 + dial_pos, 0 + dial_pos, 500 - dial_pos, 500 - dial_pos),
                    math.radians(270 - needle), math.radians(270), 50)

        # Draw marks
        marks = [1000, 2000, 3000, 4000, 5000, 6000]
        for m in marks:
            needle = m * 0.06
            pg.draw.arc(screen, (67, 91, 188), (0 + dial_pos, 0 + dial_pos, 500 - dial_pos, 500 - dial_pos),
                        math.radians(269 - needle), math.radians(270 - needle), 50)
            needle = (m - 500) * 0.06
            pg.draw.arc(screen, (67, 91, 188), (0 + dial_pos, 0 + dial_pos, 500 - dial_pos, 500 - dial_pos),
                        math.radians(269 - needle), math.radians(270 - needle), 50)

        for m in [0] + marks[:-1]:
            word_rad = math.radians(m * 0.06 + 90)
            word_loc = (180 * math.cos(word_rad) + 250, 180 * math.sin(word_rad) + 250)

            text = font_4.render(str(int(m / 1000)), True, (210, 216, 214))
            textRect = text.get_rect()
            textRect.center = word_loc
            screen.blit(text, textRect)

            text = font_3.render(str(int(m / 1000)), True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = word_loc
            screen.blit(text, textRect)

        # Draw RPM multiplier
        text = font_5.render('x1000', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (290, 420)
        screen.blit(text, textRect)
        text = font_5.render('r/min', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (290, 435)
        screen.blit(text, textRect)

        # Draw Max Reach
        pg.draw.arc(screen, (209, 142, 246), (0 + dial_pos, 0 + dial_pos, 500 - dial_pos, 500 - dial_pos),
                    math.radians(269 - (MAX_RPM * 0.06)), math.radians(270 - (MAX_RPM * 0.06)), 50)

        pg.display.flip()

    pg.quit()

if __name__ == '__main__':
    manager = Manager()

    x_time = manager.list()
    y_RPM = manager.list()
    y_voltage = manager.list()
    new_data = manager.Value('i', 0)
    new_data.value = 0

    p = Process(target=dashboard, args=(x_time, y_RPM, y_voltage, new_data,))
    p2 = Process(target=plot, args=(x_time, y_RPM, y_voltage, new_data,))

    p.start()
    p2.start()

    p.join()
    p2.join()