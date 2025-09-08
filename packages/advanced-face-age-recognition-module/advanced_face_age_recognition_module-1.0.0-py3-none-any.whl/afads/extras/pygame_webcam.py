# pygame_webcam.py
import cv2
import numpy as np
import pygame
from afads import AFADS

def cv2_to_surface(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    surf = pygame.image.frombuffer(rgb.tobytes(), (w, h), "RGB")
    return surf

def main():
    pygame.init()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera")
        return
    ret, frame = cap.read()
    if not ret:
        print("No frame from camera")
        return

    h, w = frame.shape[:2]
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("AFADS Pygame Webcam  —  [SPACE]=Assess  [A]=Allow-any  [E]=Allow-18+  [Q]=Quit")

    clock = pygame.time.Clock()
    eng = AFADS()
    result = None
    allow_any = False
    allow_18 = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_SPACE:
                    ok, frame = cap.read()
                    if ok:
                        result = eng.assess(frame, return_dict=True)
                elif event.key == pygame.K_a:
                    if result:
                        allow_any = (result.get("estimated_age",-1.0) >= 0)
                elif event.key == pygame.K_e:
                    if result:
                        allow_18 = (result.get("prob_over_18",0.0) >= 0.85)

        ok, frame = cap.read()
        if not ok: continue

        # overlay text with OpenCV, then blit via pygame
        overlay = frame.copy()
        y = 24
        def put(line, color=(255,255,255)):
            nonlocal y, overlay
            cv2.putText(overlay, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
            y += 24

        put("AFADS Pygame — Space=Assess, A=Allow-any, E=Allow-18+, Q=Quit")
        if result:
            age = result.get("estimated_age",-1.0)
            p18 = result.get("prob_over_18",0.0)
            put(f"Age≈ {age:.1f}" if age>=0 else "Age: —")
            put(f"P(≥18): {p18:.2f}")
        put(f"ALLOW(any): {'YES' if allow_any else 'NO'}", (0,255,0) if allow_any else (0,0,255))
        put(f"ALLOW(18+): {'YES' if allow_18 else 'NO'}", (0,255,0) if allow_18 else (0,0,255))

        surf = cv2_to_surface(overlay)
        screen.blit(surf, (0,0))
        pygame.display.flip()
        clock.tick(30)

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    main()
