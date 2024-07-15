# BadFox!!

# Battle plan:
# 1. Open video
# 2. Extract frames
# 3. Compress to 40x7 characters (maybe do this by hand?)
# 4. Map text to pixels (white = character, black = no character)
# 5. Edit text onto base image
# 6. Save as video
# 7. Done!

import cv2
from PIL import ImageFont, ImageDraw, Image
import sys
import numpy as np
import ffmpeg

TWEET_TEXT: list[str] = [
    "We are working on writing the newsletter but  ",
    "we will not be able to release until at least ",
    "few days after the update to GameMaker LTS    ",
    "is released (this month)                      ",
    "                                              ",
    "By the way, a couple friends have been able to",
    "play through the unfinished Chapter 4. They   ",
    "enjoyed it.                                   ",
]

FONT_PATH: str = "assets/Chirp.ttf"

THRESHOLD: int = 127

TEXT_X: int = 35
TEXT_Y: int = 239

FONT = ImageFont.truetype(FONT_PATH, 51)


# Saves the video as a series of images
def save_frames() -> list:
    frames = []
    capture = cv2.VideoCapture("assets/badapple_video.avi")

    ok, image = capture.read()
    while ok:
        # Crunch the video down to proper B&W with a threshold
        frames.append(cv2.threshold(image, THRESHOLD, 255, cv2.THRESH_BINARY)[1])
        ok, image = capture.read()

    capture.release()

    return frames


# Creates a frame of the video
def create_frame(frame, video):
    with Image.open("assets/TF_Tweet_notext.png") as img_pil:
        draw = ImageDraw.Draw(img_pil)

        for rows in range(8):
            text_x = TEXT_X

            for cols in range(46):
                # If a pixel is white, the text is white (255, 255, 255, 255)
                # Otherwise, it's the same color as the bg (22, 32, 42, 255)
                COLOR = (
                    (255, 255, 255, 255)
                    if (frame[rows][cols][0] == 255)
                    else (22, 32, 42, 255)
                )

                draw.text(
                    (text_x, TEXT_Y + (rows * 48)),
                    TWEET_TEXT[rows][cols],
                    font=FONT,
                    fill=COLOR,
                )

                text_x += FONT.getlength(TWEET_TEXT[rows][cols])

        video.write(cv2.cvtColor(np.array(img_pil), cv2.COLOR_BGR2RGB))


# Creates the final video
def create_video() -> None:
    frames = save_frames()
    count = 0

    NUM_OF_FRAMES = len(frames)
    BAR_FRAMES = ["│", "╱", "─", "╲"]

    LOADING_BAR_STR = "{0}/{1} frames... {2}"

    vidwriter = cv2.VideoWriter(
        "out/audioless_output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, (1170, 845)
    )

    print("BAD FOX!!\n")
    for frame in frames:
        create_frame(frame, vidwriter)

        sys.stdout.write(
            LOADING_BAR_STR.format(count, NUM_OF_FRAMES, BAR_FRAMES[count % 4])
        )
        sys.stdout.flush()

        # Set cursor back to line start
        sys.stdout.write("\b" * len(LOADING_BAR_STR))

        count += 1

    vidwriter.release()


def add_audio() -> None:
    video_file = ffmpeg.input("out/audioless_output.mp4")
    audio_file = ffmpeg.input("assets/badapple_audio.aac")

    out = ffmpeg.output(
        video_file, audio_file, "out/BadFox.mp4", vcodec="copy", acodec="copy"
    )
    out.run()


def run() -> None:
    create_video()
    add_audio()


run()
