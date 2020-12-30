"""
The following code captures input from the MIDI Keyboard, and sends it to the drone script. 
as well as displays the keyboard, captures audio input. 
Author: Kenny Blake
Version: 4.0
"""
import pygame
import pygame.midi
from datetime import datetime
from time import time, sleep
import os
from Drone import Drone
import random
from midiutil import MIDIFile

class Piano: 
    def __init__(self):
        pygame.init()                                                               #Initializes pygame
        pygame.midi.init()                                                          #Initializes pygame midi

        self.startTime = time()                                                     #The time the program began, for the sake of the midi file
        self.MyMidi = MIDIFile(1)                                                   #The MIDIFile writer object
        self.midi_output = pygame.midi.Output(pygame.midi.get_default_output_id())    #The Output Device of the pygame midi object.
        self.midiInput = pygame.midi.Input(pygame.midi.get_default_input_id())                                       #The Input Device of the pygame midi object.

       
        self.drone = Drone()                                                        #The Drone Object, this is what this class communicates with. 

        self.pianoImg = pygame.image.load('60key.png')                              #The picture of the 60 key piano
        pygame.display.set_caption("MIDI piano input")                              #Sets the title of the pygame window
        l = 200                                                                     #The lower pixel bound. This is the Y-Value of the whiteKeyPressed.png/whiteKeyReleased.png images.    
        u= 170                                                                      #The upper pixel bound. This is the X-Value of the blackKeyPressed.png/blackKeyReleased.png images.
        self.blackKeyReleased = pygame.image.load('blackKeyReleased.png')           #The blackKeyReleased image
        self.whiteKeyReleased = pygame.image.load('whiteKeyReleased.png')           #The whiteKeyReleased image
        self.blackKeyPressed = pygame.image.load('blackKeyPressed.png')             #The blackKeyPressed image
        self.whiteKeyPressed = pygame.image.load('whiteKeyPressed.png')             #The whiteKeyPressed image
        self.clock = pygame.time.Clock()                                            #The fps of the game
        self.display = pygame.display.set_mode(self.pianoImg.get_rect().size)       #The Display object, where pygame draws everything.
        self.running = True                                                         #If the game is running
        self.pianoTime = 0                                                          #The BPM of the tempo
        self.MyMidi.addTempo(0, self.pianoTime, 60)                                 #Adds the tempo to the Midi file
        
        self.font = pygame.font.get_default_font()                                  #Sets the font of text that will be displayed in the pygame window
        self.font = pygame.font.Font(self.font, 20)                                 #Finalizes the fonts object, adds size, makes it usable         
                                                         

       #The White Keys on the keyboard, in ascending order. Contains where the whiteKeyPressed/whiteKeyReleased images should be displayed, as well as the command/amount that goes with it.
        self.whiteKeys = {
        36: (33 , l, "t", 0),                                                                                               #The Takeoff/Land key
        38: (69, l, "h", 0),                                                                                                #The Hover key
        40: (117, l, "d", .8333334), 41: (164, l, "d", .66666666), 43: (212, l, "d", .3333333),                             #The Down white Keys
        45: (260, l, "u", .1666667), 47: (307, l, "u", .5), 48: (354, l, "u", .66666666), 50: (400, l, "u", 1),             #The Up white Keys
        52: (447, l, "tl", .833333), 53: (494, l, "tl", .666666), 55: (541, l, "tl", .33333),                               #The Turn left white keys
        57: (588, l, "tr", .1666667), 59: (635, l, "tr", 3/6), 60: (672, l, "tr", 4/6), 62: (718, l, "tr", 1),              #The Turn Right white keys
        64: (766, l, "b", 5/6), 65: (813, l, "b", 4/6), 67: (860, l, "b", 2/6),                                             #The Backwards white Keys   
        69: (897, l, "f", 1/6), 71: (944, l, "f", .5), 72: (981, l, "f", 4/6), 74: (1038, l, "f", 1),                       #The Forward white keys
        76: (1085, l, "l", 5/6), 77: (1132, l, "l", 4/6), 79: (1179, l, "l", 2/6),                                          #The MOVE left white keys
        81: (1216, l, "r", 1/6), 83: (1260, l, "r", .5), 84: (1304, l, "r", 4/6), 86: (1358, l, "r", 1),                    #The MOVE right white keys
        88: (1402, l, "E"),                                                                                                 #The EMERGENCY KEY(press 3x to activate)
        89: (1446, l, "F", 0),                                                                                              #The Flip Key (Non-Functional)
        91: (1514, l, "d", random.random()), 93: (1548, l, "r", random.random()), 95: (1602, l, "tr", random.random()),     #The Randomizer white keys 
        96: (1651, l, "FC", 0)                                                                                              #The Find computer key (non-functional)
        }                                                                                            
        


        #The Black Keys on the keyboard, in ascending order. Contains where the whiteKeyPressed/whiteKeyReleased images should be displayed, as well as the command/amount that goes with it.
        self.blackKeys = {
        37: (45, u, "R", 0),                                                                                                #The Record key
        39: (90, u, "d", 1), 42: (180, u, "d", .5), 44: (225, u, "d", .1666667),                                            #The Down black keys
        46: (280, u, "u", .3333333), 49: (370, u, "u", .8333334),                                                           #The Up black keys
        51: (425, u, "tl", 1), 54: (505, u, "tl", .5), 56: (565, u, "tl", .166667),                                         #The Turn left black keys
        58: (605, u, "tr", 2/6), 61: (695, u, "tr", 5/6),                                                                   #The Turn right black keys
        63: (740, u, "b", 1), 66: (830, u, "b", 3/6), 68: (875, u, "b", 1/6),                                               #The Backwards black keys
        70: (925, u, "f", 2/6), 73: (1020, u, "f", 5/6),                                                                    #The Forward black keys
        75: (1065, u, "l", 1), 78: (1155, u, "l", .5), 80: (1200, u, "l", 1/6),                                             #The MOVE left black keys
        82: (1245, u, "r", 2/6), 85: (1335, u, "r", 5/6),                                                                   #The MOVE right black keys
        87: (1380, u, "R2", random.random()), 90: (1490, u, "u", random.random()), 92: (1535, u, "l", random.random()), 94: (1580, u, "tl", random.random()) #The Random black keys
        }
        



        
    """
    Adds the keys to the midi file
    
    keyPressed: The Key that was pressed
    timeStamp: When the key was pressed
    """
    def addKeyToMidi(self, keyPressed, timeStamp):
        self.MyMidi.addNote(0, 0, keyPressed, timeStamp, 1, 100)
    

    """
    Displays the base piano image
    """
    def displayPiano(self):
        self.display.blit(self.pianoImg, (0,0))
        pygame.display.update()


    """
    Gets the key pressed, as well as the actuation value of that key.
    Adds the proper ___keyPressed/___keyReleased images in their proper spots.
    Sends the data over to the drone. 

    keyPressed: The key that was pressed
    val: The actuation value, so 144 if the key is being pressed, 128 if the key was released.
    """
    def midiAction(self, keyPressed, val):

        if keyPressed in self.whiteKeys.keys():

            data = self.whiteKeys.get(keyPressed)
            if val == 144:

                self.display.blit(self.whiteKeyPressed, tuple(data[0:2]))
                timeStamp = time() - self.startTime

                self.addKeyToMidi(keyPressed, timeStamp)

                self.drone.droneCommand(data[2:4])

            if val == 128:
                self.display.blit(self.whiteKeyReleased, tuple(data[0:2]))


        elif keyPressed in self.blackKeys.keys():

            data = self.blackKeys.get(keyPressed)
            if val == 144:

                self.display.blit(self.blackKeyPressed, tuple(data[0:2]))
                timeStamp = time() - self.startTime

                self.addKeyToMidi(keyPressed, timeStamp)

                self.drone.droneCommand(data[2:4]) #Where the command is sent to the drone

            elif val == 128:
                self.display.blit(self.blackKeyReleased, tuple(data[0:2]))
            
        else:
            print(f"{keyPressed} Not found!")


    """
    The main function of this program. Gets midi inputs, displays the piano. 
    """
    def run(self):
        self.displayPiano()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.quitPiano()
            if self.midiInput.poll():
                inpt = self.midiInput.read(1)
                keyPressed= inpt[0][0][1]
                val = inpt[0][0][0]
                self.midiAction(keyPressed, val)
            pygame.display.update()
        self.midiInput.close()


    """
    Writes the midi file to memory, saves it. Quits the pygame window. 
    Exits the python program, shuts the program down. 
    """
    def quitPiano(self):
        t = datetime.now()
        tC = time()
        cwd = os.getcwd()
        fil = f"{cwd}/midis/{t.strftime('%m%d%Y')}{tC}.mid"
        with open(fil, "wb") as output_file:
            self.MyMidi.writeFile(output_file)
            print(f"written to {fil}")
        output_file.close()
        if self.drone.videoThread.is_alive():
            self.drone.videoThread.join()
        exit()
        pygame.quit()
        