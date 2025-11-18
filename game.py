# 1. Installation Requirements:
# pip install opencv-contrib-python
# pip install cvzone 
# pip install pyautogui

#conda activate gesture_env
#pip install opencv-contrib-python cvzone mediapipe pyautogui
#python game.py

import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time

# --- Configuration ---
# Set the detection confidence for the hand tracking (higher is stricter)
DETECTION_CONFIDENCE = 0.7 
# API key is not needed for computer vision tasks

# Initialize the HandDetector
detector = HandDetector(detectionCon=DETECTION_CONFIDENCE, maxHands=1)

# Initialize the video capture (webcam)
# Adjust the index (0, 1, 2...) if you have multiple cameras
cap = cv2.VideoCapture(0)
cap.set(3, 640) # Set frame width
cap.set(4, 480) # Set frame height

print("Gesture Controller Ready. Press 'q' to quit.")
time.sleep(1) # Give a moment for the user to switch to the game window

# State variables to manage key presses cleanly
current_action = "STOP"

# Function to handle key presses and state changes
def perform_action(new_action, key_to_press=None, key_to_release=None):
    global current_action
    
    # Only perform the action if it's different from the current state
    if new_action != current_action:
        # 1. Stop any currently pressed key
        if current_action == "GAS":
            pyautogui.keyUp("right")
        elif current_action == "BRAKE":
            pyautogui.keyUp("left")
            
        # 2. Perform the new action
        if key_to_press:
            pyautogui.keyDown(key_to_press)
            
        # 3. Update the state
        current_action = new_action

def release_all():
    global current_action
    if current_action != "STOP":
        pyautogui.keyUp("right")
        pyautogui.keyUp("left")
        current_action = "STOP"


try:
    while True:
        # 1. Read the frame from the camera
        success, img = cap.read()
        if not success:
            print("Failed to capture image from camera.")
            break
            
        # 2. Flip the image for a more natural mirror view (user's right hand looks like a right hand)
        img = cv2.flip(img, 1)

        # 3. Find hands in the image
        # draw=False stops CVZone from drawing the landmarks, as we'll draw our own feedback
        hands, img = detector.findHands(img, draw=False)
        
        # Default text feedback
        feedback_text = "Place Hand In View"
        feedback_color = (0, 0, 255) # Red

        if hands:
            hand = hands[0]
            # Detect which fingers are up
            # fingers list: [Thumb, Index, Middle, Ring, Pinky] (1=Up, 0=Down)
            fingers = detector.fingersUp(hand)
            totalFingers = fingers.count(1)
            
            # Get the center point of the hand for placing the action text
            center_x, center_y = hand['center']
            
            # --- Gesture Control Logic ---
            
            # Gesture 1: GAS / Accelerate (5 fingers up - Open Palm)
            if totalFingers == 5:
                perform_action("GAS", key_to_press="right")
                feedback_text = "ACCELERATE (Gas)!"
                feedback_color = (0, 255, 0) # Green

            # Gesture 2: BRAKE / Reverse (1 finger up - Index Finger)
            elif totalFingers == 1:
                perform_action("BRAKE", key_to_press="left")
                feedback_text = "BRAKE / REVERSE!"
                feedback_color = (255, 0, 0) # Blue
                
            # Gesture 3: STOP (0 fingers up - Fist, or any other unclear gesture)
            else:
                release_all()
                feedback_text = f"STOP (Fingers: {totalFingers})"
                feedback_color = (0, 255, 255) # Yellow
            
            # Display the action feedback prominently
            cv2.putText(img, feedback_text, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, feedback_color, 3)

        else:
            # No hand detected, ensure keys are released
            release_all()
            cv2.putText(img, feedback_text, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, feedback_color, 3)


        # 4. Display the camera feed
        cv2.imshow('Hill Climb Gesture Controller', img)
        
        # 5. Wait for key press (1ms). Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # 6. Clean up: Release all keys and resources when the loop finishes
    release_all()
    cap.release()
    cv2.destroyAllWindows()
    print("Gesture controller shut down.")