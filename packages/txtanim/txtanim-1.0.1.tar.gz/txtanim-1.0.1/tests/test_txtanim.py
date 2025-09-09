"""
Test file for txtanim library.

This file demonstrates how to use all the animations in txtanim
with examples and explanations.
"""

import time
import txtanim  # Import the library

# --------------------------------------------
# 1️⃣ Typewriter Animation
# --------------------------------------------
print("Typewriter Animation:")
txtanim.typewriter("Hello World!", speed=0.05, color="cyan")
time.sleep(1)  # Pause for 1 second between animations

# Reverse Typewriter
print("\nReverse Typewriter:")
txtanim.typewriter("Deleting Text...", speed=0.05, reverse=True, color="red")
time.sleep(1)

# --------------------------------------------
# 2️⃣ Blink Animation
# --------------------------------------------
print("\nBlink Animation:")
txtanim.blink("BLINKING TEXT", cycles=3, speed=0.3, color="yellow")
time.sleep(1)

# --------------------------------------------
# 3️⃣ Pulse Animation
# --------------------------------------------
print("\nPulse Animation:")
txtanim.pulse("PULSING TEXT", cycles=3, speed=0.2, color="green")
time.sleep(1)

# --------------------------------------------
# 4️⃣ Spinner Animation
# --------------------------------------------
print("\nSpinner Animation:")
txtanim.spinner(cycles=10, speed=0.1, color="magenta")
time.sleep(1)

# --------------------------------------------
# 5️⃣ Loading Dots Animation
# --------------------------------------------
print("\nLoading Dots Animation:")
txtanim.loading_dots("Saving", cycles=5, speed=0.3, color="blue", symbol=".")
time.sleep(1)

# --------------------------------------------
# 6️⃣ TQDM-style Progress Bar
# --------------------------------------------
print("\nProgress Bar Animation:")
txtanim.progress_bar(total=20, prefix="Downloading", color="cyan", delay=0.05)
time.sleep(1)

# --------------------------------------------
# Test Complete
# --------------------------------------------
print("\nAll animations tested successfully!")