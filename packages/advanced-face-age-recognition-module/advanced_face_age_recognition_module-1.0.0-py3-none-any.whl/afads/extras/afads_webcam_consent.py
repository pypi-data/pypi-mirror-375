# afads_webcam_consent.py
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from afads import AFADS

CONSENT_TEXT = (
    "AFADS needs access to your camera to estimate age on-device.\n\n"
    "No images will be uploaded or stored by default.\n\n"
    "Do you consent to enable the camera now?"
)

def ask_consent():
    root = tk.Tk()
    root.withdraw()
    ok = messagebox.askokcancel("Camera Consent", CONSENT_TEXT, icon='question')
    root.destroy()
    return ok

def draw_overlay(frame, text_lines, box=(10,10)):
    x, y = box
    for i, line in enumerate(text_lines):
        cv2.putText(frame, line, (x, y + 24*i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

def main():
    if not ask_consent():
        print("Consent declined. Exiting.")
        return

    eng = AFADS()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    print("Press [SPACE] to assess current frame, [Q] to quit.")
    result = None

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        # Live hint overlay
        lines = ["AFADS Webcam (Space=Assess, Q=Quit)"]
        if result is not None:
            age = result.get("estimated_age",-1.0)
            p18 = result.get("prob_over_18",0.0)
            lines += [f"Age≈ {age:.1f}" if age>=0 else "Age: —", f"P(≥18): {p18:.2f}"]
        draw_overlay(frame, lines)

        cv2.imshow("AFADS", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord(' '):
            # run assessment on current frame
            result = eng.assess(frame, return_dict=True)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
