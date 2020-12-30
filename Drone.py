"""
The following code controls the drone based on commands sent from the piano.
It also records/saves the videos.
Author: Kenny Blake
Version: 3.0
"""
from pyardrone import ARDrone
import cv2
from datetime import datetime
from time import sleep
import threading
import os
import logging
import NoFrameRecieved

class Drone():
    def __init__(self):
        self.d = ARDrone()                      #The ARDrone object. 
        self.vidInitState = False               #If the CV2 VideoWriter object has been started, and is ready to store video data. 
        self.recording = False                  #If the CV2 VideoWriter object is currently storing video data. 
        self.flying = False                     #If the drone is flying or not.
        self.commands = ["d", "u", "tl", 
        "tr", "b", "f", "l", "r"]               #The commands for the drone randomizer
        self.counter = 0                        #The counter for the emergency key

        #We use multithreading to record the video. This is the thread that starts the video.
        self.videoThread = threading.Thread(name = "droneVideoAction", target = self.droneVideoAction, daemon=False)

    """
    Gets the command being sent by the drone script, and, if applicable, the speed.
    Sends the command to the drone, or starts recording the video/inits the video if needed.
    """
    def droneCommand(self, data:str):
        command = data[0]                       #The command that correlates to the key that was pressed. Can be found in the ____keys dictionaries found in the constructor of Piano.
        amount = data[1]                        #The amount, if not 0, that the key wants it's command to do. For Example, this would move the drone left 0.3x.

        #The Takeoff/Land command
        if command == "t":
            if not self.flying:
                self.d.navdata_ready.wait()
                print(self.d.navdata)
                self.d.takeoff()
                self.flying = True
            else:
                self.d.land()
                self.flying = False

        #The Record Command: Starts/Stops the record functionality
        elif command == "R":
            #if the drone is not flying(1)
            if not self.flying:

                #(1)however it was already recording and I just forgot to hit stop recording
                if self.recording:
                    self.droneVideoAction()
                    self.videoThread.join()

                #(1)and I haven't started flying it yet/it's not flying anymore
                else:
                    logging.error("Drone must be flying in order to record video!")

            #if the drone is flying
            else:
                if not self.videoThread.is_alive():
                    self.videoThread.start()
                else:
                    self.droneVideoAction()
                
        #The Hover command: Stops all movement of the drone
        elif command == "h":
            self.d.hover()  

        #The Down command: Moves the drone down the specified amount
        elif command == "d": 
            self.d.move(down = amount)
        
        #The Up command: Moves the drone up the specified amount
        elif command == "u":
            self.d.move(up = amount)

        #The Turn Left command: Turns the drone left the specified amount
        elif command == "tl":
            self.d.move(ccw = amount)

        #The Turn Right command: Turns the drone right the specified amount
        elif command == "tr":
            self.d.move(cw = amount)

        #The Backwards command: Moves the drone backwards the specified amount
        elif command == "b":
            self.d.move(backward=amount)

        #The Forwards command: Moves the drone forwards the specified amount
        elif command == "f":
            self.d.move(forward = amount)

        #The Move Left command: Moves the drone left the specified amount
        elif command == "l":
            self.d.move(left = amount)
        
        #The Move right command: Moves the drone right the specified amount
        elif command == "r":
            self.d.move(right = amount)

        #The Emergency Command: If pressed three times, kills the drone entirely.
        elif command == "E":
            
            #If the key has been hit 3 times
            if self.counter >= 3:
                
                #Sends the emergency command
                self.d.emergency()

                #we want to record the emergency, so waits 3 seconds, then closes it.
                sleep(3)
                self.droneVideoAction()
            
            #If the key hasn't been hit 3 times.
            else:
                self.counter += 1

    """
    Calls upon the drone to send video, 
    """
    def droneVideoAction(self):
        
        #if we are not currently recording yet
        if not self.recording:
            
            #readies the video on the drone
            print("waiting for drone video!")
            self.d.video_ready.wait()
            print("video ready!")

            #sets up the cv2 VideoWriter
            frame = self.d.video_client.frame
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            date_time = datetime.now().strftime("%m-%d-%Y -- %H-%M-%S")
            self.fullFileName = f"{os.getcwd()}{os.path.sep}videos{os.path.sep}{date_time}.avi"
            self.videoWriter = cv2.VideoWriter(self.fullFileName, fourcc, 20, (frame.shape[1], frame.shape[0]))

            #sets the drone object to be in recording mode.
            self.recording = True
        
        #if we are currently recording
        else:
            self.recording = False

        #while the drone object is in recording mode:
        while self.recording:
            
            #the frame recieved from the drone
            cF = self.d.video_client.frame

            #if the frame exists
            if cF is not None:
                
                #shows the frame
                cv2.imshow("current droneFrame", cF)
                
                #OpenCV Requires this. So just pretend it isn't here.
                if cv2.waitKey(10) == ord('q'):
                    break

                #writes it.
                self.videoWriter.write(cF)
                
            #if there is no frame recieved from the drone, log an error.
            else:
                self.d.land()
                self.flying = False
                n = NoFrameRecieved
                raise n

        """
        Closes the video writer and writes it to the file,
        Closes all windows for cv2
        Joins the video thread to the main thread.
        """
        logging.info(f"Video is now closed. Written to: {self.fullFileName}")
        self.videoWriter.release()
        self.recording = False
        cv2.destroyAllWindows()


            


