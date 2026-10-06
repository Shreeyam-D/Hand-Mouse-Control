import cv2
import math
import time
import pyautogui
import mediapipe as mp


# ============================================================
# PYAutoGUI SETTINGS
# ============================================================

screen_width, screen_height = pyautogui.size()

pyautogui.PAUSE = 0.01


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("ERROR: Camera could not be opened.")

    exit()


# ============================================================
# VARIABLES
# ============================================================

previous_x = 0
previous_y = 0

smooth_x = 0
smooth_y = 0

smoothing = 0.50


# Click control
last_click_time = 0
click_cooldown = 0.5


# Right click control
last_right_click_time = 0
right_click_cooldown = 0.7


# Scroll
previous_scroll_y = None


# ============================================================
# DISTANCE FUNCTION
# ============================================================

def distance(x1, y1, x2, y2):

    return math.hypot(
        x2 - x1,
        y2 - y1
    )


# ============================================================
# FINGER DETECTION
# ============================================================

def get_finger_states(hand):

    landmarks = hand.landmark

    index_up = landmarks[8].y < landmarks[6].y

    middle_up = landmarks[12].y < landmarks[10].y

    ring_up = landmarks[16].y < landmarks[14].y

    pinky_up = landmarks[20].y < landmarks[18].y

    return (
        index_up,
        middle_up,
        ring_up,
        pinky_up
    )


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:

        print("Camera frame could not be read.")

        break


    # Mirror camera
    frame = cv2.flip(frame, 1)

    frame_height, frame_width, _ = frame.shape


    # ========================================================
    # MEDIAPIPE
    # ========================================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)


    # Default gesture
    gesture = "NO HAND"


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]

        landmarks = hand.landmark


        # Draw hand
        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # ====================================================
        # INDEX FINGER TIP
        # ====================================================

        index = landmarks[8]

        index_x = int(index.x * frame_width)
        index_y = int(index.y * frame_height)


        # ====================================================
        # THUMB TIP
        # ====================================================

        thumb = landmarks[4]

        thumb_x = int(thumb.x * frame_width)
        thumb_y = int(thumb.y * frame_height)


        # ====================================================
        # MIDDLE FINGER TIP
        # ====================================================

        middle = landmarks[12]

        middle_x = int(middle.x * frame_width)
        middle_y = int(middle.y * frame_height)


        # ====================================================
        # DRAW POINTS
        # ====================================================

        cv2.circle(
            frame,
            (index_x, index_y),
            10,
            (255, 0, 255),
            -1
        )

        cv2.circle(
            frame,
            (thumb_x, thumb_y),
            10,
            (255, 0, 255),
            -1
        )

        cv2.circle(
            frame,
            (middle_x, middle_y),
            10,
            (255, 0, 255),
            -1
        )


        # ====================================================
        # FINGER STATES
        # ====================================================

        (
            index_up,
            middle_up,
            ring_up,
            pinky_up
        ) = get_finger_states(hand)


        # ====================================================
        # PINCH DISTANCE
        # ====================================================

        pinch_distance = distance(
            index_x,
            index_y,
            thumb_x,
            thumb_y
        )


        # ====================================================
        # GESTURE 1
        # INDEX ONLY = MOVE MOUSE
        # ====================================================

        index_only = (
            index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        )


        if index_only:

            gesture = "MOVE"


            # -----------------------------------------------
            # Convert camera coordinates to screen coordinates
            # -----------------------------------------------

            # Limit movement area so cursor is easier to control

            margin_x = 80
            margin_y = 60

            x = max(
                margin_x,
                min(
                    frame_width - margin_x,
                    index_x
                )
            )

            y = max(
                margin_y,
                min(
                    frame_height - margin_y,
                    index_y
                )
            )


            # Convert to screen coordinates

            target_x = (
                (x - margin_x)
                /
                (frame_width - 2 * margin_x)
                *
                screen_width
            )

            target_y = (
                (y - margin_y)
                /
                (frame_height - 2 * margin_y)
                *
                screen_height
            )


            # -----------------------------------------------
            # SMOOTH CURSOR
            # -----------------------------------------------

            smooth_x = (
                smooth_x * (1 - smoothing)
                +
                target_x * smoothing
            )

            smooth_y = (
                smooth_y * (1 - smoothing)
                +
                target_y * smoothing
            )


            pyautogui.moveTo(
                int(smooth_x),
                int(smooth_y)
            )


        # ====================================================
        # GESTURE 2
        # PINCH = LEFT CLICK
        # ====================================================

        pinch = (
            pinch_distance < 40
        )


        if pinch:

            gesture = "LEFT CLICK"


            current_time = time.time()


            if (
                current_time - last_click_time
                > click_cooldown
            ):

                pyautogui.click()

                last_click_time = current_time


        # ====================================================
        # GESTURE 3
        # INDEX + MIDDLE = RIGHT CLICK
        # ====================================================

        two_fingers = (
            index_up
            and middle_up
            and not ring_up
            and not pinky_up
        )


        if two_fingers:

            gesture = "RIGHT CLICK"


            current_time = time.time()


            if (
                current_time - last_right_click_time
                > right_click_cooldown
            ):

                pyautogui.rightClick()

                last_right_click_time = current_time


        # ====================================================
        # GESTURE 4
        # OPEN HAND = SCROLL MODE
        # ====================================================

        open_hand = (
            index_up
            and middle_up
            and ring_up
            and pinky_up
        )


        if open_hand:

            gesture = "SCROLL"


            # Palm center
            palm_y = int(
                (
                    landmarks[0].y
                    +
                    landmarks[5].y
                    +
                    landmarks[9].y
                    +
                    landmarks[13].y
                    +
                    landmarks[17].y
                )
                / 5
                * frame_height
            )


            if previous_scroll_y is not None:

                movement = (
                    palm_y -
                    previous_scroll_y
                )


                # Scroll sensitivity

                if abs(movement) > 5:

                    scroll_amount = int(
                        -movement / 8
                    )

                    pyautogui.scroll(
                        scroll_amount
                    )


            previous_scroll_y = palm_y


        else:

            previous_scroll_y = None


        # ====================================================
        # GESTURE 5
        # FIST = NEUTRAL
        # ====================================================

        fist = (
            not index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        )


        if fist:

            gesture = "NEUTRAL"


    else:

        previous_scroll_y = None


    # ========================================================
    # UI HEADER
    # ========================================================

    cv2.rectangle(
        frame,
        (0, 0),
        (frame_width, 110),
        (20, 20, 20),
        -1
    )


    cv2.putText(
        frame,
        "HAND MOUSE CONTROLLER",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Gesture: {gesture}",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )


    # ========================================================
    # INSTRUCTIONS
    # ========================================================

    cv2.putText(
        frame,
        "INDEX = MOVE",
        (30, frame_height - 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "PINCH = LEFT CLICK",
        (30, frame_height - 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "TWO FINGERS = RIGHT CLICK",
        (30, frame_height - 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "OPEN HAND = SCROLL",
        (30, frame_height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Hand Mouse Controller",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

hands.close()