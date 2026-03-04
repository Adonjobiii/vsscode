import time
import threading
import random
import sys

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Tkinter is required to run this program.")
    sys.exit(1)

from collections import defaultdict
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# --- Add matplotlib imports for graph ---
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Correct answers for all original questions
CORRECT_ANSWERS = {
    "Logical": {
        1: 'c', 2: 'c', 3: 'a', 4: 'd', 5: 'd', 6: 'a', 7: 'a', 8: 'b', 9: 'd', 10: 'c',
        11: 'c', 12: 'a', 13: 'c', 14: 'b', 15: 'b', 16: 'd', 17: 'c', 18: 'a', 19: 'c', 20: 'a',
        21: 'b', 22: 'b', 23: 'c', 24: 'b', 25: 'a'
    },
    "Critical": {
        1: 'b', 2: 'b', 3: 'a', 4: 'b', 5: 'b', 6: 'c', 7: 'b', 8: 'b', 9: 'c', 10: 'c',
        11: 'c', 12: 'b', 13: 'b', 14: 'a', 15: 'b', 16: 'b', 17: 'c', 18: 'c', 19: 'a', 20: 'b',
        21: 'c', 22: 'b', 23: 'b', 24: 'a', 25: 'b'
    },
    "Creative": {
        1: 'b', 2: 'c', 3: 'c', 4: 'b', 5: 'b', 6: 'c', 7: 'b', 8: 'b', 9: 'b', 10: 'b',
        11: 'b', 12: 'b', 13: 'b', 14: 'b', 15: 'b', 16: 'b', 17: 'b', 18: 'b', 19: 'b', 20: 'c',
        21: 'a', 22: 'b', 23: 'b', 24: 'b', 25: 'b'
    },
    "Abstract": {
        1: 'a', 2: 'd', 3: 'a', 4: 'd', 5: 'b', 6: 'b', 7: 'b', 8: 'b', 9: 'a', 10: 'b',
        11: 'd', 12: 'c', 13: 'a', 14: 'b', 15: 'b', 16: 'c', 17: 'c', 18: 'b', 19: 'b', 20: 'b',
        21: 'b', 22: 'a', 23: 'a', 24: 'a', 25: 'c'
    },
    "Algorithmic": {
        1: 'c', 2: 'a', 3: 'd', 4: 'c', 5: 'c', 6: 'b', 7: 'c', 8: 'b', 9: 'c', 10: 'a',
        11: 'c', 12: 'a', 13: 'b', 14: 'a', 15: 'c', 16: 'c', 17: 'b', 18: 'a', 19: 'd', 20: 'c',
        21: 'c', 22: 'a', 23: 'c', 24: 'b', 25: 'd'
    },
    "Computational": {
        1: 'b', 2: 'c', 3: 'a', 4: 'b', 5: 'a', 6: 'b', 7: 'a', 8: 'b', 9: 'c', 10: 'b',
        11: 'd', 12: 'd', 13: 'c', 14: 'b', 15: 'b', 16: 'b', 17: 'b', 18: 'b', 19: 'b', 20: 'c',
        21: 'd', 22: 'a', 23: 'b', 24: 'a', 25: 'b'
    },
    "System": {
        1: 'b', 2: 'b', 3: 'b', 4: 'b', 5: 'c', 6: 'b', 7: 'b', 8: 'c', 9: 'b', 10: 'b',
        11: 'c', 12: 'c', 13: 'b', 14: 'b', 15: 'b', 16: 'b', 17: 'b', 18: 'a', 19: 'b', 20: 'b',
        21: 'b', 22: 'b', 23: 'b', 24: 'b', 25: 'b'
    }
}

# All original questions from the uploaded files
QUESTIONS = {
    "Logical": [
        {"id": 1, "q": "The sequence is 4, 8, 12, 16, ... What is the 15th term?", "options": {"a": "56", "b": "60", "c": "64", "d": "68"}},
        {"id": 2, "q": "All laptops are devices. Some devices are tablets. Which conclusion must logically hold true?", "options": {"a": "All devices are laptops", "b": "Some tablets are laptops", "c": "Some tablets are devices", "d": "Some devices are not laptops"}},
        {"id": 3, "q": "A person walks 15 m east, 10 m north, then 15 m west. Where is he relative to the start?", "options": {"a": "10 m north", "b": "10 m south", "c": "5 m west", "d": "Back at start"}},
        {"id": 4, "q": "Which number does not fit the pattern (divisible by both 2 and 3)? 6, 12, 18, 24, 36", "options": {"a": "6", "b": "12", "c": "18", "d": "36"}},
        {"id": 5, "q": "The sequence is 7, 14, 28, 112. What is the missing number?", "options": {"a": "40", "b": "42", "c": "48", "d": "56"}},
        {"id": 6, "q": "The series is A1, C3, E5, G7, ... What is the 6th term?", "options": {"a": "K11", "b": "I9", "c": "H9", "d": "J10"}},
        {"id": 7, "q": "The series is 11, 21, 31, 41, ... What is the 12th term?", "options": {"a": "120", "b": "121", "c": "122", "d": "123"}},
        {"id": 8, "q": "IF MARKET → LZQJDS, then STREET →?", "options": {"a": "RSQDDS", "b": "RSRDDS", "c": "RSPDDS", "d": "RSPDDT"}},
        {"id": 9, "q": "A clock shows 6:00. What is the angle between hands?", "options": {"a": "90°", "b": "120°", "c": "150°", "d": "180°"}},
        {"id": 10, "q": "Choose the odd one out: Python, Java, SQL, C#, Swift", "options": {"a": "Python", "b": "Java", "c": "SQL", "d": "Swift"}},
        {"id": 11, "q": "If 2=4, 3=9, 4=16, 5=25 then 6=?", "options": {"a": "30", "b": "35", "c": "36", "d": "40"}},
        {"id": 12, "q": "10 workers take 10 days for a job. How many days for 20 workers?", "options": {"a": "5", "b": "10", "c": "20", "d": "2"}},
        {"id": 13, "q": "Which number does not follow the symmetry pattern? 21212, 45454, 89889, 56565", "options": {"a": "21212", "b": "45454", "c": "89889", "d": "56565"}},
        {"id": 14, "q": "A person walks 12 m north, 9 m east, 3 m south. Shortest distance from start?", "options": {"a": "12", "b": "15", "c": "10.8", "d": "18"}},
        {"id": 15, "q": "In a queue, John is 8th from front and 12th from back. How many in queue?", "options": {"a": "18", "b": "19", "c": "20", "d": "21"}},
        {"id": 16, "q": "All coders are learners. Some learners are teachers. Which conclusion is valid?", "options": {"a": "Some coders are teachers", "b": "All learners are coders", "c": "Both follow", "d": "Neither follows"}},
        {"id": 17, "q": "Find the missing term: B, E, I, N, T, ...?", "options": {"a": "U", "b": "V", "c": "Z", "d": "Y"}},
        {"id": 18, "q": "Five rooms in a row. Blue left of Yellow. Red not next to Blue. Green between Blue & Yellow. White at an end. Where is Red?", "options": {"a": "1st", "b": "2nd", "c": "3rd", "d": "Cannot be determined"}},
        {"id": 19, "q": "A man says: \"I have twice as many sisters as brothers.\" His sister says: \"I have same number of brothers as sisters.\" How many siblings?", "options": {"a": "4 brothers, 2 sisters", "b": "3 brothers, 3 sisters", "c": "2 brothers, 4 sisters", "d": "2 brothers, 3 sisters"}},
        {"id": 20, "q": "IF WORD → XPSF, then ROAD → ?", "options": {"a": "SPBE", "b": "SPAD", "c": "RPBD", "d": "SPBD"}},
        {"id": 21, "q": "If PAPER = OZODQ then TABLE =?", "options": {"a": "SZAKD", "b": "SZBKD", "c": "SZAKC", "d": "SZBKC"}},
        {"id": 22, "q": "Remove vowels from COMPUTER. What is the 3rd letter from right?", "options": {"a": "P", "b": "T", "c": "R", "d": "M"}},
        {"id": 23, "q": "A is 5 years younger than B. B is 2 years older than C. Sum of ages = 45 What is A's age?", "options": {"a": "12", "b": "13", "c": "14", "d": "15"}},
        {"id": 24, "q": "A number series follows rule: n²+1. If 2=3, 3=8, 4=15, what is 7?", "options": {"a": "47", "b": "48", "c": "49", "d": "50"}},
        {"id": 25, "q": "A code uses reverse + shift by 2 rule. If CAT → VYR, then DOG → ?", "options": {"a": "WLT", "b": "WLR", "c": "WKT", "d": "XLT"}}
    ],
    "Critical": [
        {"id": 1, "q": "If all teachers are educated, and some educated people are not teachers, which statement must be true?", "options": {"a": "All educated are teachers", "b": "Some educated are not teachers", "c": "Some teachers are not educated", "d": "None of these"}},
        {"id": 2, "q": "Why do doctors wash their hands before surgery?", "options": {"a": "Tradition in hospitals", "b": "To reduce risk of infection", "c": "To save time", "d": "To make patients feel comfortable"}},
        {"id": 3, "q": "You see smoke coming out of a building. What is the most reasonable assumption?", "options": {"a": "The building is on fire", "b": "Someone is cooking", "c": "There is dust in the air", "d": "Smoke always means fire"}},
        {"id": 4, "q": "A man reads every day but never buys books. What could explain this?", "options": {"a": "He doesn't like reading", "b": "He borrows books from a library", "c": "He reads without understanding", "d": "He only reads newspapers"}},
        {"id": 5, "q": "Which of these is an opinion, not a fact?", "options": {"a": "Water boils at 100°C", "b": "Reading books makes you smarter", "c": "The sun rises in the east", "d": "Humans need oxygen to live"}},
        {"id": 6, "q": "If a road is wet, which conclusion is most logical?", "options": {"a": "It rained recently", "b": "Someone washed the road", "c": "Both A and B are possible", "d": "The road is broken"}},
        {"id": 7, "q": "A man claims he can predict tomorrow's weather perfectly every day. How can we test this claim scientifically?", "options": {"a": "Believe him immediately", "b": "Observe his predictions over several days", "c": "Ask his friends", "d": "Read a weather book"}},
        {"id": 8, "q": "A shopkeeper says a product is \"50% off\", but the price is higher than before. What explains this?", "options": {"a": "It's a real discount", "b": "The shopkeeper increased the original price before discount", "c": "The product is free", "d": "The sign is a mistake"}},
        {"id": 9, "q": "Which of these arguments is the weakest?", "options": {"a": "Exercise improves health; therefore, people should exercise.", "b": "Studying leads to better grades; therefore, students should study.", "c": "Drinking water prevents hunger; therefore, don't eat food.", "d": "Wearing seatbelts saves lives; therefore, always wear them."}},
        {"id": 10, "q": "You hear a strange noise in your computer. What is the most logical next step?", "options": {"a": "Hit the computer", "b": "Restart the system", "c": "Check for loose hardware or fan issues", "d": "Throw it away"}},
        {"id": 11, "q": "A scientist finds evidence supporting his theory. Which action avoids bias?", "options": {"a": "Ignore contradictory evidence", "b": "Only publish supporting data", "c": "Test and consider all evidence", "d": "Ask friends for opinions"}},
        {"id": 12, "q": "A coin lands heads 5 times in a row. What is the best conclusion?", "options": {"a": "The next toss will definitely be heads", "b": "The coin is biased or it's coincidence", "c": "Tossing guarantees equal heads and tails every time", "d": "The coin will land tails next"}},
        {"id": 13, "q": "A person always drives recklessly but claims they are safe. This is an example of:", "options": {"a": "Logical reasoning", "b": "Contradiction", "c": "Deductive proof", "d": "Strong evidence"}},
        {"id": 14, "q": "A company claims its medicine works for everyone, but no tests are done. This claim lacks:", "options": {"a": "Evidence", "b": "Assumptions", "c": "Opinions", "d": "Theories"}},
        {"id": 15, "q": "A student is absent often but gets high marks. The best inference is:", "options": {"a": "Attendance is necessary for marks", "b": "The student studies outside class", "c": "The student is cheating", "d": "Teachers grade randomly"}},
        {"id": 16, "q": "A politician says: \"Crime has reduced since I became mayor.\" Which question tests this claim?", "options": {"a": "Do you like being mayor?", "b": "Has crime reduced due to other factors?", "c": "How many voters support you?", "d": "Did the population decrease?"}},
        {"id": 17, "q": "Every successful startup had strong leadership. Which conclusion is correct?", "options": {"a": "Leadership guarantees success", "b": "Some failed startups had weak leadership", "c": "Strong leadership is one factor in success", "d": "Startups fail without leadership"}},
        {"id": 18, "q": "A study shows drinking tea daily is linked to better memory. Best interpretation?", "options": {"a": "Tea directly improves memory", "b": "People with better memory like tea", "c": "Correlation doesn't prove cause", "d": "Tea is the only factor"}},
        {"id": 19, "q": "A school has 90% pass rate. Which critical question matters most?", "options": {"a": "Are the exams too easy?", "b": "Do students enjoy exams?", "c": "Who teaches in that school?", "d": "What is the school's theme color?"}},
        {"id": 20, "q": "Which is a flawed argument?", "options": {"a": "If it rains, roads are wet. It is raining, so roads are wet.", "b": "All computers need power. This device needs power, so it's a computer.", "c": "Eating vegetables improves health, so eat vegetables.", "d": "Practice improves coding skills."}},
        {"id": 21, "q": "A person believes \"All new technologies are harmful.\" This is an example of:", "options": {"a": "Open-minded reasoning", "b": "Critical thinking", "c": "Overgeneralization", "d": "Cause-effect reasoning"}},
        {"id": 22, "q": "A company advertises: \"Our product is best because no one complained.\" This is:", "options": {"a": "Strong evidence", "b": "Appeal to ignorance", "c": "Deductive logic", "d": "Causal reasoning"}},
        {"id": 23, "q": "A friend says: \"If you don't invest in my idea, you'll regret it forever.\" This is:", "options": {"a": "Logical reasoning", "b": "Emotional manipulation (fear appeal)", "c": "Sound argument", "d": "Critical thinking"}},
        {"id": 24, "q": "A student argues: \"I failed because the exam was unfair, not because I didn't study.\" This is:", "options": {"a": "Shifting blame (fallacy)", "b": "Valid critical reasoning", "c": "Scientific proof", "d": "Empirical evidence"}},
        {"id": 25, "q": "Which of the following best illustrates confirmation bias?", "options": {"a": "Reading both positive and negative reviews", "b": "Searching only for evidence that supports your opinion", "c": "Ignoring irrelevant details", "d": "Testing all hypotheses equally"}}
    ],
    "Creative": [
        {"id": 1, "q": "Which of the following is an example of creative thinking?", "options": {"a": "Memorizing a formula", "b": "Solving a math problem in a new way", "c": "Copying someone's notes", "d": "Repeating learned steps"}},
        {"id": 2, "q": "You have a box, a candle, matches, and thumbtacks. How can you fix the candle to the wall without dripping wax?", "options": {"a": "Stick the candle to the wall", "b": "Melt wax and glue it", "c": "Use the box as a candle holder and tack it to the wall", "d": "Hold the candle with hand"}},
        {"id": 3, "q": "If cars never existed, which innovative alternative might evolve for transport?", "options": {"a": "Horses only", "b": "Rocket backpacks", "c": "AI-powered flying carpets or smart vehicles", "d": "None"}},
        {"id": 4, "q": "Which book title is the most creative for Artificial Intelligence?", "options": {"a": "AI Basics", "b": "Thinking Machines", "c": "Computer Science Notes", "d": "Robots and Humans"}},
        {"id": 5, "q": "Which option demonstrates \"thinking outside the box\"?", "options": {"a": "Using the same method repeatedly", "b": "Finding multiple different solutions to a problem", "c": "Giving up on a problem", "d": "Memorizing solutions"}},
        {"id": 6, "q": "If pens were never invented, which alternative would people imagine for writing?", "options": {"a": "Speaking words loudly", "b": "Drawing in the sand", "c": "Using sticks dipped in ink or digital stylus", "d": "None"}},
        {"id": 7, "q": "Which of these is an example of combining ideas?", "options": {"a": "Sleeping instead of working", "b": "A phone that is also a camera and music player", "c": "A broken laptop", "d": "A chair without a seat"}},
        {"id": 8, "q": "A city has too much traffic. Which solution shows creative thinking?", "options": {"a": "Build more roads only", "b": "Introduce flying taxis or underground walkways", "c": "Ban all cars forever", "d": "Do nothing"}},
        {"id": 9, "q": "A company designs a backpack students love. Which approach is creative?", "options": {"a": "Copy an existing design", "b": "Ask students for new features they want", "c": "Make only larger bags", "d": "Add random patterns"}},
        {"id": 10, "q": "Which is a sign of creativity?", "options": {"a": "Sticking to one method", "b": "Generating many different ideas for a single problem", "c": "Memorizing known answers", "d": "Refusing to take risks"}},
        {"id": 11, "q": "Which invention best shows combining unrelated fields?", "options": {"a": "A normal bicycle", "b": "A smartwatch that tracks heartbeat and calls emergency services", "c": "A car without wheels", "d": "A simple calendar"}},
        {"id": 12, "q": "You need to keep a drink cool without a fridge. Which solution is creative?", "options": {"a": "Leave it under the sun", "b": "Wrap it in a wet cloth and place it in the breeze", "c": "Drink it warm", "d": "Pour it on ice cream"}},
        {"id": 13, "q": "A game designer wants a new mobile game. Which idea shows creativity?", "options": {"a": "Copying a popular game", "b": "Mixing puzzles with music beats", "c": "Releasing the same version again", "d": "Using existing graphics only"}},
        {"id": 14, "q": "Which is the most creative use for an empty glass jar?", "options": {"a": "Throw it away", "b": "Use as a pencil holder, light jar, or mini plant pot", "c": "Keep it empty", "d": "Smash it"}},
        {"id": 15, "q": "A teacher asks students to design a future school. Which design is creative?", "options": {"a": "Draws current building", "b": "Imagines floating classrooms with AI assistants", "c": "Copies another design", "d": "Leaves the page blank"}},
        {"id": 16, "q": "A city faces power cuts. Which sustainable plan is creative?", "options": {"a": "Use diesel generators", "b": "Switch to solar-powered smart grids with storage batteries", "c": "Cut power for half the city", "d": "Increase bills to reduce usage"}},
        {"id": 17, "q": "Which product is an example of creative innovation?", "options": {"a": "A smartphone with a bigger screen", "b": "A foldable phone that becomes a tablet", "c": "A wired telephone", "d": "A calculator"}},
        {"id": 18, "q": "You design a chair that never tips over. Which feature is unique?", "options": {"a": "Normal four legs", "b": "Self-balancing gyroscope technology", "c": "A flat board", "d": "A chair without legs"}},
        {"id": 19, "q": "A community has excess rainwater flooding roads. Which solution is creative?", "options": {"a": "Build more drains", "b": "Collect rainwater in rooftop tanks for reuse", "c": "Do nothing", "d": "Make the ground concrete"}},
        {"id": 20, "q": "Which approach is NOT creative thinking?", "options": {"a": "Brainstorming freely", "b": "Asking \"What if\" questions", "c": "Copying old solutions blindly", "d": "Combining ideas from different areas"}},
        {"id": 21, "q": "A startup builds a bicycle + laptop stand for remote workers. This is:", "options": {"a": "Innovation through combination", "b": "Old thinking", "c": "Useless complexity", "d": "Predictable invention"}},
        {"id": 22, "q": "A student builds a robot that paints murals based on music beats. This thinking is:", "options": {"a": "Repetitive", "b": "Creative cross-domain thinking", "c": "Copy-paste", "d": "Memorization"}},
        {"id": 23, "q": "A group brainstorms to save office paper. Which idea is most creative?", "options": {"a": "Print on both sides", "b": "Share files digitally with voice-to-text reports", "c": "Throw away less", "d": "Ban printers"}},
        {"id": 24, "q": "Which project best demonstrates creative CS-based design thinking?", "options": {"a": "Building a static webpage", "b": "Designing AI-driven smart homes", "c": "Copying open-source code blindly", "d": "Using outdated technology"}},
        {"id": 25, "q": "A new app integrates AR for education and VR for therapy. This is an example of:", "options": {"a": "Unoriginal work", "b": "Multi-domain creative innovation", "c": "Purely entertainment", "d": "Non-creative reuse"}}
    ],
    "Abstract": [
        {"id": 1, "q": "What comes next in the pattern AAA?", "options": {"a": "B", "b": "C", "c": "D", "d": "E"}},
        {"id": 2, "q": "Which shape is the odd one out?", "options": {"a": "Circle", "b": "Triangle", "c": "Square", "d": "Cube"}},
        {"id": 3, "q": "If \"@\" = 1, \"#\"=2, \"$\"=3, then what does \"@#@$\" represent?", "options": {"a": "1213", "b": "1321", "c": "1231", "d": "1312"}},
        {"id": 4, "q": "Complete the pattern: 2, 4, 8, 16, ?", "options": {"a": "18", "b": "24", "c": "30", "d": "32"}},
        {"id": 5, "q": "Which figure is a correct rotation of ↑→↓?", "options": {"a": "↓↑→", "b": "→↓↑", "c": "→↑↓", "d": "↑↓→"}},
        {"id": 6, "q": "Which figure completes the analogy: Square: 4 sides :: Pentagon: ?", "options": {"a": "3 sides", "b": "5 sides", "c": "6 sides", "d": "7 sides"}},
        {"id": 7, "q": "Which of these best represents abstraction in mathematics?", "options": {"a": "Solving only one example", "b": "Generalizing patterns into formulas", "c": "Memorizing random numbers", "d": "Listing observations without rules"}},
        {"id": 8, "q": "Find the missing shape:", "options": {"a": "", "b": "", "c": "", "d": ""}},
        {"id": 9, "q": "Which number does not belong in the group? 3, 5, 9, 17, 33, 65, 129, 257, 513", "options": {"a": "9", "b": "33", "c": "513", "d": "65"}},
        {"id": 10, "q": "If \"\" is mirrored horizontally, which is the correct image?", "options": {"a": "", "b": "<◆>", "c": "", "d": "↔"}},
        {"id": 11, "q": "Which figure completes the sequence?", "options": {"a": "", "b": "", "c": "", "d": "▲"}},
        {"id": 12, "q": "A cube has faces A, B, C, D, E, F. If A opposite D, and B opposite E, which is opposite C?", "options": {"a": "A", "b": "B", "c": "F", "d": "D"}},
        {"id": 13, "q": "Which option generalizes: 2+4=6, 4+6=10, 6+8=14?", "options": {"a": "n+(n+2)", "b": "n x 2", "c": "n²", "d": "Fibonacci rule"}},
        {"id": 14, "q": "In a number pattern, each term is double the previous minus 1. If first is 3, what is the 4th?", "options": {"a": "11", "b": "13", "c": "15", "d": "17"}},
        {"id": 15, "q": "Which figure matches abstraction of a cycle?", "options": {"a": "Random dots", "b": "A circular loop", "c": "A square grid", "d": "A line segment"}},
        {"id": 16, "q": "If A=2, a=4, O=6, what sequence does A represent?", "options": {"a": "246", "b": "864", "c": "248", "d": "426"}},
        {"id": 17, "q": "A diagram with 3 overlapping circles labeled A, B, C has the intersection shaded. Which concept is shown?", "options": {"a": "Symmetry", "b": "Hierarchy", "c": "Set Intersection", "d": "Difference"}},
        {"id": 18, "q": "Find the missing step:→→→?", "options": {"a": "..", "b": "....", "c": "", "d": "..."}},
        {"id": 19, "q": "A figure is rotated 90° clockwise three times. Final orientation is?", "options": {"a": "Same as original", "b": "90° clockwise", "c": "180°", "d": "270°"}},
        {"id": 20, "q": "A folded paper has one hole. When unfolded it shows 4 holes. How many layers were folded?", "options": {"a": "1", "b": "2", "c": "4", "d": "8"}},
        {"id": 21, "q": "A series is generated by n²+n. What is the 6th term?", "options": {"a": "36", "b": "42", "c": "48", "d": "56"}},
        {"id": 22, "q": "A matrix has rows shifting one place forward each time. If row 1 is 1,2,3→ row 2 is 2,3,4 row 3 is?", "options": {"a": "3,4,5", "b": "4,5,6", "c": "5,6,7", "d": "6,7,8"}},
        {"id": 23, "q": "Which best describes abstraction in computer science?", "options": {"a": "Ignoring unimportant details", "b": "Adding unnecessary complexity", "c": "Memorizing code", "d": "Writing everything literally"}},
        {"id": 24, "q": "A puzzle uses only shapes but rules are hidden. Which skill is applied to solve?", "options": {"a": "Abstraction", "b": "Random guessing", "c": "Blind memorization", "d": "Direct calculation"}},
        {"id": 25, "q": "A recursive figure doubles its size at each step. At step 5, starting with 1 block, how many blocks?", "options": {"a": "8", "b": "16", "c": "32", "d": "64"}}
    ],
    "Algorithmic": [
        {"id": 1, "q": "Start at 3, multiply by 2, add 4, subtract 1. What is the result?", "options": {"a": "9", "b": "10", "c": "11", "d": "12"}},
        {"id": 2, "q": "Which option best represents an algorithm to find the largest of three numbers?", "options": {"a": "Compare first two, then compare the larger with the third", "b": "Add all numbers", "c": "Subtract smallest from largest", "d": "Multiply all and divide by 2"}},
        {"id": 3, "q": "Which of the following best defines an algorithm?", "options": {"a": "A list of random instructions", "b": "A single equation", "c": "A sequence of unorganized data", "d": "A step-by-step procedure for solving a problem"}},
        {"id": 4, "q": "What must an algorithm always have?", "options": {"a": "Visual output", "b": "An infinite loop", "c": "A clear input and output", "d": "At least 10 steps"}},
        {"id": 5, "q": "Arrange steps for making tea: Pour water, Add tea leaves, Boil water, Add sugar/milk.", "options": {"a": "1→2→3→4", "b": "1 3→2→4", "c": "3 1→2→4", "d": "2 1→4→3"}},
        {"id": 6, "q": "Which everyday task best represents an algorithm?", "options": {"a": "Random shopping", "b": "Following a cooking recipe", "c": "Talking to a friend", "d": "Reading a novel"}},
        {"id": 7, "q": "Which of these is NOT a property of an algorithm?", "options": {"a": "Finiteness", "b": "Definiteness", "c": "Ambiguity", "d": "Efficiency"}},
        {"id": 8, "q": "What is the primary benefit of using a sorting algorithm?", "options": {"a": "To find the mean", "b": "To organize data for faster searching", "c": "To shuffle data", "d": "To delete data"}},
        {"id": 9, "q": "Which statement is true about algorithms and flowcharts?", "options": {"a": "Flowcharts are more efficient", "b": "Algorithms are more visual", "c": "Flowcharts are a visual representation of algorithms", "d": "Algorithms do not need a starting point"}},
        {"id": 10, "q": "To find if a number is even, you use the modulo operator (%). What is the condition?", "options": {"a": "number % 2 == 0", "b": "number / 2 == 0", "c": "number % 2 != 0", "d": "number * 2 == 0"}},
        {"id": 11, "q": "To find if a year is a leap year, you divide by 4. What is the logic?", "options": {"a": "If year % 4 != 0", "b": "If year / 4 == 0", "c": "If year % 4 == 0", "d": "If year * 4 == 0"}},
        {"id": 12, "q": "Which is an example of a brute-force algorithm?", "options": {"a": "Checking every single password to crack a lock", "b": "Using a smart key to open a door", "c": "Guessing the password with clues", "d": "Asking the owner for the password"}},
        {"id": 13, "q": "Which search algorithm is fastest on a sorted list?", "options": {"a": "Linear search", "b": "Binary search", "c": "Sequential search", "d": "Random check"}},
        {"id": 14, "q": "To find a book in a library, you search row by row. This is a:", "options": {"a": "Linear search", "b": "Binary search", "c": "Brute-force approach", "d": "Divide and conquer"}},
        {"id": 15, "q": "What is the key idea of a divide and conquer algorithm?", "options": {"a": "Solving the problem all at once", "b": "Breaking a problem into small, independent subproblems", "c": "Trying every possible solution", "d": "Repeating the same step over and over"}},
        {"id": 16, "q": "You are looking for the number 8 in a sorted list [1, 2, 4, 8, 16]. Which is faster?", "options": {"a": "Linear search", "b": "Random check", "c": "Binary search", "d": "Multiply all and check"}},
        {"id": 17, "q": "Which algorithm prints even numbers 1-10?", "options": {"a": "for i=1 to 10: if i%2!=0 print i", "b": "For i=1 to 10: if i%2==0 print i", "c": "Print only odd numbers", "d": "While i>10 print i"}},
        {"id": 18, "q": "What is the time complexity of checking all n elements one by one?", "options": {"a": "O(n)", "b": "0(1)", "c": "O(n²)", "d": "O(log n)"}},
        {"id": 19, "q": "A flowchart takes x, checks if x>10: if true subtract 2 else add 3. If x=9 what happens?", "options": {"a": "Subtract 2-7", "b": "Add 3→12", "c": "Add 3 then subtract 2", "d": "Add 3 12→ end"}},
        {"id": 20, "q": "To find the maximum of n numbers, what must you track?", "options": {"a": "A string", "b": "A counter", "c": "Largest number so far", "d": "A list of all numbers"}},
        {"id": 21, "q": "Which algorithm strategy tries every possibility to ensure correctness?", "options": {"a": "Divide and conquer", "b": "Greedy approach", "c": "Brute force", "d": "Dynamic programming"}},
        {"id": 22, "q": "Which algorithm design technique breaks a problem into overlapping subproblems?", "options": {"a": "Dynamic programming", "b": "Divide and conquer", "c": "Brute force", "d": "Greedy approach"}},
        {"id": 23, "q": "What's the best way to sort an unsorted list quickly?", "options": {"a": "Linear search", "b": "Bubble sort", "c": "Quick sort", "d": "Brute force"}},
        {"id": 24, "q": "A greedy algorithm always selects the best choice at each step. This leads to:", "options": {"a": "Optimal solution", "b": "Sub-optimal solution", "c": "Random solution", "d": "No solution"}},
        {"id": 25, "q": "Which of these is a property of a recursive algorithm?", "options": {"a": "It solves the entire problem in one step", "b": "It has no base case", "c": "It uses an iterative loop", "d": "It calls itself"}},
    ],
    "Computational": [
        {"id": 1, "q": "You need a to-do list for study. Which option best represents an algorithm?", "options": {"a": "Writing random thoughts", "b": "Listing step-by-step actions", "c": "Reading without planning", "d": "Skipping tasks"}},
        {"id": 2, "q": "A recipe says: \"Boil water → Add tea → Add sugar → Stir → Serve.\" This is an example of:", "options": {"a": "Random activity", "b": "Storytelling", "c": "Step-by-step procedure", "d": "Guesswork"}},
        {"id": 3, "q": "Which shows pattern recognition?", "options": {"a": "Plants grow faster in sunlight", "b": "Watching a movie", "c": "Reading a novel", "d": "Changing ringtone"}},
        {"id": 4, "q": "In a biology experiment, you repeat the process with 5 samples. What computational concept is this?", "options": {"a": "Abstraction", "b": "Repetition (loop)", "c": "Sorting", "d": "Debugging"}},
        {"id": 5, "q": "A fruit-sorting machine separates ripe and unripe fruits by color. Which concept is used?", "options": {"a": "Pattern recognition", "b": "Random guessing", "c": "Sorting randomly", "d": "Naming fruits"}},
        {"id": 6, "q": "When you summarize only important steps in solving a math problem, this is:", "options": {"a": "Guessing", "b": "Abstraction", "c": "Memorization", "d": "Visualization"}},
        {"id": 7, "q": "Which of these is an example of decomposition?", "options": {"a": "Breaking a computer into parts: CPU, memory, I/O", "b": "Memorizing facts", "c": "Random guessing", "d": "Ignoring details"}},
        {"id": 8, "q": "You observe mosquitoes breed in stagnant water. You create a plan to clean standing water. This shows:", "options": {"a": "Brute force", "b": "Pattern recognition and abstraction", "c": "Random behavior", "d": "Linear thinking"}},
        {"id": 9, "q": "Which task most requires computational thinking?", "options": {"a": "Writing a letter", "b": "Drawing a picture", "c": "Designing a new app", "d": "Reading a book"}},
        {"id": 10, "q": "A chess player analyzes a position by breaking it into smaller parts (pieces, squares). This is an example of:", "options": {"a": "Pattern recognition", "b": "Decomposition", "c": "Algorithmic thinking", "d": "Abstraction"}},
        {"id": 11, "q": "A car's GPS finds the shortest route. It applies:", "options": {"a": "Random choice", "b": "Greedy algorithm", "c": "Sorting", "d": "Optimization algorithm"}},
        {"id": 12, "q": "A spreadsheet automatically calculates a sum after you enter numbers. This is a form of:", "options": {"a": "Random action", "b": "Manual task", "c": "Algorithmic thinking", "d": "Automated computation"}},
        {"id": 13, "q": "Which is an example of debugging?", "options": {"a": "Writing new code", "b": "Planning a project", "c": "Finding and fixing an error in a program", "d": "Reading documentation"}},
        {"id": 14, "q": "Which is a good example of a data structure?", "options": {"a": "A random list of words", "b": "A list of groceries", "c": "A list of items sorted alphabetically", "d": "A bunch of unrelated files"}},
        {"id": 15, "q": "A machine learning model identifies cats in photos. This is based on:", "options": {"a": "Random guessing", "b": "Pattern recognition", "c": "Linear search", "d": "Brute force"}},
        {"id": 16, "q": "What is the purpose of an algorithm in computational thinking?", "options": {"a": "To create randomness", "b": "To provide a step-by-step solution", "c": "To increase complexity", "d": "To make problems harder"}},
        {"id": 17, "q": "Which is a good example of abstraction?", "options": {"a": "A detailed drawing of a car engine", "b": "A simple drawing of a car", "c": "A full-scale model of a car", "d": "A list of all car parts"}},
        {"id": 18, "q": "A doctor's diagnostic flow: \"If fever>101°F → Check infection → If yes, suggest antibiotic.\" This is an example of:", "options": {"a": "Guessing", "b": "Algorithm with conditionals", "c": "Random choice", "d": "Storytelling"}},
        {"id": 19, "q": "Testing blood samples Group A→B→C for 5 patients is applying:", "options": {"a": "Debugging", "b": "Looping through a list", "c": "Filtering data", "d": "None"}},
        {"id": 20, "q": "A decision tree: If answer=No, go left; If Yes, go right. This logic is:", "options": {"a": "Guessing", "b": "Sequential flow", "c": "Binary decision making", "d": "Random choice"}},
        {"id": 21, "q": "You plan alternate study days for biology and programming, with weekly review. This shows:", "options": {"a": "Poor management", "b": "Scheduling algorithm", "c": "Random habit", "d": "Memorization"}},
        {"id": 22, "q": "Which concept is used when filtering large data sets to show only relevant fields?", "options": {"a": "Sorting", "b": "Abstraction", "c": "Decomposition", "d": "Filtering"}},
        {"id": 23, "q": "A student designs a simulation to predict weather using past data. This applies:", "options": {"a": "Pattern recognition", "b": "Abstraction", "c": "Randomization", "d": "Guessing"}},
        {"id": 24, "q": "Which step in computational thinking is MOST related to reusing existing code libraries?", "options": {"a": "Abstraction", "b": "Pattern recognition", "c": "Decomposition", "d": "Debugging"}},
        {"id": 25, "q": "A smart fridge detects items and creates a shopping list. Which concept is dominant?", "options": {"a": "Sorting", "b": "Pattern recognition", "c": "Random sampling", "d": "Guessing"}},
    ],
    "System": [
        {"id": 1, "q": "In a network, a failure in one server slows others. This shows:", "options": {"a": "Independent components", "b": "System interdependence", "c": "Isolated processing", "d": "Single-point failure"}},
        {"id": 2, "q": "Which best describes a \"system\"?", "options": {"a": "A collection of interrelated parts", "b": "A single isolated process", "c": "A standalone device", "d": "A single line of code"}},
        {"id": 3, "q": "A software system made of modules communicating with each other is an example of:", "options": {"a": "Linear thinking", "b": "Modular interconnected design", "c": "Random architecture", "d": "Unrelated components"}},
        {"id": 4, "q": "Which of these is a feedback loop?", "options": {"a": "A program running once", "b": "A thermostat adjusting temperature", "c": "A keyboard sending input", "d": "Storing static data"}},
        {"id": 5, "q": "Which is NOT a property of systems?", "options": {"a": "Interaction between parts", "b": "Emergent behavior", "c": "Components working in isolation", "d": "Interdependence"}},
        {"id": 6, "q": "A change in database schema affects APIs and frontends. This shows:", "options": {"a": "No relationship", "b": "Ripple effect", "c": "Perfect isolation", "d": "Independent coding"}},
        {"id": 7, "q": "Which of these is an open system in computing?", "options": {"a": "Program without input/output", "b": "Operating system interacting with users/hardware", "c": "Encrypted closed file", "d": "Fixed circuit board"}},
        {"id": 8, "q": "When improving performance, a CS student must analyze:", "options": {"a": "Only hardware", "b": "Only software", "c": "Interaction of all parts", "d": "Ignore environment"}},
        {"id": 9, "q": "A positive feedback loop typically leads to:", "options": {"a": "Stability", "b": "Exponential growth or decline", "c": "No change", "d": "Isolation"}},
        {"id": 10, "q": "Which best describes an emergent property of a system?", "options": {"a": "A property of a single component", "b": "A property that arises from interactions between components", "c": "A property that is pre-coded", "d": "A property that is a result of random chance"}},
        {"id": 11, "q": "A car's braking system is connected to the gas pedal. This is an example of:", "options": {"a": "A single component", "b": "A linear process", "c": "An interconnected system", "d": "A random process"}},
        {"id": 12, "q": "When a small change in one part of a system causes a large effect elsewhere, this is called:", "options": {"a": "Predictable outcome", "b": "Isolated effect", "c": "Leverage point", "d": "Random noise"}},
        {"id": 13, "q": "Which best describes a sub-system?", "options": {"a": "A system without inputs", "b": "A smaller system that is part of a larger one", "c": "A single component", "d": "A system that is isolated"}},
        {"id": 14, "q": "A supply chain is a good example of a system because:", "options": {"a": "It has no components", "b": "It has interdependent parts like suppliers, manufacturers, and customers", "c": "It is a linear process", "d": "It has no feedback loops"}},
        {"id": 15, "q": "When designing a new feature for a social media app, a developer considers how it will affect user engagement, server load, and privacy. This is an example of:", "options": {"a": "Linear thinking", "b": "System thinking", "c": "Isolated development", "d": "Brute force"}},
        {"id": 16, "q": "An AI model generates biased content due to bias in its training data. This shows:", "options": {"a": "Feedback loop amplification", "b": "System interdependence", "c": "Static execution", "d": "Linear data handling"}},
        {"id": 17, "q": "Which cybersecurity question reflects systems thinking?", "options": {"a": "How fast to patch a server?", "b": "How do vulnerabilities affect the network?", "c": "Which theme color to use?", "d": "What is storage limit?"}},
        {"id": 18, "q": "A student claims optimizing one function improves the system. Which principle challenges this?", "options": {"a": "Sub-optimization may not improve whole", "b": "Isolated optimization improves all", "c": "Optimizing one guarantees full gain", "d": "Systems unaffected by parts"}},
        {"id": 19, "q": "A failure spreads from one microservice to others. This is called:", "options": {"a": "System resilience", "b": "Cascading failure", "c": "Linear failure", "d": "Closed feedback"}},
        {"id": 20, "q": "Which scenario shows dynamic system behavior?", "options": {"a": "Static web page", "b": "Weather model updating real-time", "c": "Hardcoded function", "d": "Manual yearly update"}},
        {"id": 21, "q": "Designing software that self-heals after failure is:", "options": {"a": "Static response", "b": "System adaptability/resilience", "c": "Closed system design", "d": "Manual error handling"}},
        {"id": 22, "q": "In supply chains, a shortage in raw materials affects production globally. This reflects:", "options": {"a": "Isolated systems", "b": "Global interdependence", "c": "Random effect", "d": "Local-only failure"}},
        {"id": 23, "q": "Which best explains \"holistic analysis\" in system thinking?", "options": {"a": "Looking only at one part", "b": "Considering interactions of all parts", "c": "Ignoring environment", "d": "Testing modules separately"}},
    ],
}

# --- 1. Prepare the Dataset for ML Model ---
# This dataset is used to train the model to make predictions.
# We map quiz scores to career paths.
# Each row represents a hypothetical student's scores across 7 categories.
# The scores are normalized (0 to 1).
# The target variable `y_labels` maps to a recommended course.

# Features: Logical, Critical, Creative, Abstract, Algorithmic, Computational, System
X_data_train = np.array([
    # CSE Sub-streams
    [0.70, 0.60, 0.50, 0.60, 0.75, 0.70, 0.60], # AI/ML
    [0.70, 0.70, 0.50, 0.60, 0.70, 0.70, 0.75], # Cybersecurity
    [0.75, 0.60, 0.50, 0.60, 0.70, 0.75, 0.60], # Data Science
    # ECE Sub-streams
    [0.65, 0.70, 0.55, 0.60, 0.60, 0.70, 0.75], # Embedded Systems
    [0.70, 0.70, 0.55, 0.70, 0.60, 0.65, 0.70], # VLSI Design
    [0.65, 0.70, 0.55, 0.60, 0.60, 0.65, 0.75], # Telecommunication
    # Mechanical Engineering Sub-streams
    [0.65, 0.70, 0.80, 0.65, 0.55, 0.60, 0.75], # Automobile Engineering
    [0.65, 0.70, 0.60, 0.65, 0.65, 0.70, 0.75], # Robotics/Automation
    [0.65, 0.75, 0.60, 0.70, 0.55, 0.60, 0.75], # Thermal Engineering
    # Civil Engineering Sub-streams
    [0.60, 0.75, 0.55, 0.60, 0.50, 0.55, 0.85], # Structural Engineering
    [0.60, 0.70, 0.60, 0.60, 0.50, 0.55, 0.80], # Environmental Engineering
    [0.65, 0.70, 0.55, 0.60, 0.50, 0.55, 0.80], # Transportation Engineering
    # IT Sub-streams
    [0.70, 0.65, 0.55, 0.55, 0.70, 0.80, 0.70], # Cloud Computing
    [0.70, 0.65, 0.65, 0.55, 0.70, 0.75, 0.65], # Web Development
    [0.70, 0.70, 0.55, 0.55, 0.70, 0.75, 0.75], # IT Infrastructure
    # Biotechnology / Bioinformatics Sub-streams
    [0.70, 0.70, 0.65, 0.70, 0.55, 0.75, 0.60], # Bioinformatics
    [0.60, 0.70, 0.70, 0.75, 0.55, 0.70, 0.60], # Genetic Engineering
    [0.60, 0.75, 0.65, 0.70, 0.55, 0.70, 0.60]  # Pharmaceutical Biotechnology
])

# The target variable `y_labels` maps to a recommended course.
y_labels_train = np.array([
    0, 0, 0,  # CSE
    1, 1, 1,  # ECE
    2, 2, 2,  # Mechanical
    3, 3, 3,  # Civil
    4, 4, 4,  # IT
    5, 5, 5   # Biotechnology
])

# --- 2. Train the Random Forest Model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_data_train, y_labels_train)

# --- Timer Module Class Definitions ---
class TotalTimer:
    """Manages the countdown timer for the entire quiz."""
    def __init__(self, root, timer_label, total_minutes, callback):
        self.root = root
        self.timer_label = timer_label
        self.total_seconds = total_minutes * 60
        self.callback = callback
        self.running = False
        self.timer_id = None

    def start_timer(self):
        """Starts the timer from the total duration."""
        self.running = True
        self.update_timer()

    def stop_timer(self):
        """Stops the timer and cancels any pending updates."""
        if self.running and self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.running = False

    def update_timer(self):
        """Updates the timer display and triggers the callback on timeout."""
        if not self.running:
            return

        mins, secs = divmod(self.total_seconds, 60)
        hours, mins = divmod(mins, 60)
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        self.timer_label.config(text=f"Time Remaining: {time_str}")

        if self.total_seconds <= 0:
            self.stop_timer()
            self.callback()  # End the test
            return

        self.total_seconds -= 1
        self.timer_id = self.root.after(1000, self.update_timer)


class QuestionTimer:
    """Manages a per-question countdown timer."""
    def __init__(self, root, timer_label, callback):
        self.root = root
        self.timer_label = timer_label
        self.timer_seconds = 60
        self.callback = callback
        self.running = False
        self.timer_id = None

    def start_timer(self):
        """Starts the timer from 60 seconds."""
        self.timer_seconds = 60
        self.running = True
        self.update_timer()

    def stop_timer(self):
        """Stops the timer and cancels any pending updates."""
        if self.running and self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.running = False

    def update_timer(self):
        """Updates the timer display and triggers the callback on timeout."""
        if not self.running:
            return
        
        self.timer_label.config(text=f"Time left: {self.timer_seconds}s")
        
        if self.timer_seconds <= 0:
            self.stop_timer()
            self.callback()  # Execute the callback function
            return
            
        self.timer_seconds -= 1
        self.timer_id = self.root.after(1000, self.update_timer)

# --- Color palette from the design ---
COLOR_BG_DARK = "#2c3e50"
COLOR_BG_NAV = "#34495e"
COLOR_BG_CONTENT = "#ecf0f1"
COLOR_TIMER = "#c0392b"
COLOR_UNANSWERED = "#e74c3c"
COLOR_ANSWERED = "#27ae60"
COLOR_REVIEW = "#f1c40f"
COLOR_CURRENT_Q_NAV = "#3498db"
COLOR_BUTTON_TEXT = "white"

# --- Quiz Application Class ---
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Test")
        self.root.geometry("1100x600")
        self.root.configure(bg=COLOR_BG_DARK)

        # Instance variables initialized here
        self.question_index = 0
        self.scores = defaultdict(int)
        self.selected_option = tk.StringVar()
        self.questions = []
        self.current_question = None
        self.answers = {}
        self.review_questions = set()
        self.section_question_map = defaultdict(list)
        self.section_order = sorted(list(QUESTIONS.keys()))
        self.section_question_indices = {}
        self.course_map = {
            0: "Computer Science (CSE)",
            1: "Electronics & Communication (ECE)",
            2: "Mechanical Engineering",
            3: "Civil Engineering",
            4: "Information Technology (IT)",
            5: "Biotechnology / Bioinformatics"
        }

        self.total_timer_label = None
        self.total_timer = None
        self.question_timer_label = None
        self.question_timer = None
        self.question_buttons = {}
        self.dropdown_labels = {}
        self.section_content_frames = {}

        self.initialize_test_session()
        self.build_widgets()
        self.show_question()

    def initialize_test_session(self):
        self.questions = []
        self.answers = {}
        self.review_questions = set()
        self.section_question_map = defaultdict(list)
        self.section_question_indices = {}
        self.question_index = 0
        self.scores = defaultdict(int)

        idx = 0
        for section in self.section_order:
            # Randomly select 7 questions from each category
            if len(QUESTIONS[section]) >= 7:
                qs_selected = random.sample(QUESTIONS[section], 7)
            else:
                qs_selected = QUESTIONS[section] # Use all questions if less than 7

            for i, q in enumerate(qs_selected):
                self.questions.append({**q, "category": section})
                self.section_question_map[section].append(q)
                self.section_question_indices[(section, i)] = idx
                idx += 1
        
        # Shuffle the final list of questions to randomize order across sections
        random.shuffle(self.questions)

        # Rebuild the section_question_map and indices based on the new shuffled list
        self.section_question_map = defaultdict(list)
        self.section_question_indices = {}
        for idx, q in enumerate(self.questions):
            section = q['category']
            self.section_question_map[section].append(q)
            i = len(self.section_question_map[section]) - 1
            self.section_question_indices[(section, i)] = idx

    def build_widgets(self):
        # Clear existing widgets for a clean restart
        for widget in self.root.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=250)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.create_navigation_panel()
        self.create_content_panel()

    def create_navigation_panel(self):
        self.nav_frame = tk.Frame(self.main_frame, bg=COLOR_BG_NAV, padx=10, pady=10)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")

        self.total_timer_label = tk.Label(self.nav_frame, text="Time Remaining: 00:00:00", font=("Arial", 16, "bold"), fg=COLOR_TIMER, bg=COLOR_BG_NAV)
        self.total_timer_label.pack(pady=(0, 20))
        
        # Initializing the total timer with 60 minutes
        self.total_timer = TotalTimer(self.root, self.total_timer_label, 60, self.finish_test_auto)
        self.total_timer.start_timer()
        
        self.nav_canvas = tk.Canvas(self.nav_frame, bg=COLOR_BG_NAV, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.nav_frame, orient="vertical", command=self.nav_canvas.yview)
        self.scrollable_frame = tk.Frame(self.nav_canvas, bg=COLOR_BG_NAV)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))
        )

        self.nav_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.nav_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.nav_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        for section in self.section_order:
            header_frame = tk.Frame(self.scrollable_frame, bg=COLOR_BG_NAV)
            header_frame.pack(fill=tk.X, pady=(10, 0), padx=5)

            dropdown_label = tk.Label(header_frame, text=f"▼ {section}", font=("Arial", 12, "bold"), bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT, anchor="w")
            dropdown_label.pack(side=tk.LEFT, padx=5)
            dropdown_label.bind("<Button-1>", lambda event, s=section: self.toggle_dropdown(s))
            self.dropdown_labels[section] = dropdown_label
            
            q_info_label = tk.Label(header_frame, text=f"Questions 1-{len(self.section_question_map[section])}", font=("Arial", 9), fg="lightgray", bg=COLOR_BG_NAV, anchor="w")
            q_info_label.pack(side=tk.LEFT, padx=5)
            
            q_frame = tk.Frame(self.scrollable_frame, bg=COLOR_BG_NAV)
            q_frame.pack(fill=tk.X, padx=5)
            self.section_content_frames[section] = q_frame
            
            for i in range(len(self.section_question_map[section])):
                global_idx = self.section_question_indices.get((section, i))
                if global_idx is not None:
                    btn = tk.Button(q_frame, text=f"{i+1}", width=3, relief=tk.RAISED, fg=COLOR_BUTTON_TEXT)
                    btn.config(command=lambda idx=global_idx: self.goto_question(idx))
                    btn.grid(row=i//5, column=i%5, padx=2, pady=2)
                    self.question_buttons[global_idx] = btn
        
        self.add_legend_item(self.nav_frame, COLOR_CURRENT_Q_NAV, "Current Question")
        self.add_legend_item(self.nav_frame, COLOR_ANSWERED, "Answered")
        self.add_legend_item(self.nav_frame, COLOR_REVIEW, "Marked for Review")
        self.add_legend_item(self.nav_frame, COLOR_UNANSWERED, "Unanswered")

    def create_content_panel(self):
        self.content_frame = tk.Frame(self.main_frame, bg=COLOR_BG_CONTENT)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.topbar = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        self.topbar.pack(fill=tk.X, anchor="n")
        
        self.question_count_label = tk.Label(self.topbar, text="", font=("Arial", 12), bg=COLOR_BG_CONTENT)
        self.question_count_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.question_timer_label = tk.Label(self.topbar, text="Time left: 60s", font=("Arial", 14, "bold"), fg=COLOR_TIMER, bg=COLOR_BG_CONTENT)
        self.question_timer_label.pack(side=tk.LEFT, padx=10, pady=5)
        self.question_timer = QuestionTimer(self.root, self.question_timer_label, self.next_question_auto)
        
        self.finish_button = tk.Button(self.topbar, text="Finish Test", font=("Arial", 12, "bold"), bg=COLOR_UNANSWERED, fg=COLOR_BUTTON_TEXT, command=self.finish_test, relief=tk.FLAT)
        self.finish_button.pack(side=tk.RIGHT, padx=10, pady=5)

        self.question_area = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        self.question_area.pack(pady=(10, 0), fill=tk.BOTH, expand=True)

        self.question_title_label = tk.Label(self.question_area, text="", font=("Arial", 14, "bold"), bg="white")
        self.question_title_label.pack(anchor="w")

        self.question_text_label = tk.Label(self.question_area, text="", font=("Arial", 15), wraplength=700, justify="left", bg="white")
        self.question_text_label.pack(pady=(10, 5), anchor="w")

        self.options_frame = tk.Frame(self.question_area, bg="white")
        self.options_frame.pack(anchor="w", pady=(0, 10), padx=20)
        self.selected_option.set("")
        self.selected_option.trace_add("write", lambda *args: self.save_answer())
        self.option_radiobuttons = []

        self.control_buttons_frame = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        self.control_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.next_button = tk.Button(self.control_buttons_frame, text="Next →", font=("Arial", 12), command=self.next_question_manual, relief=tk.FLAT, bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        self.review_button = tk.Button(self.control_buttons_frame, text="Mark for Review", font=("Arial", 12), command=self.mark_review, relief=tk.FLAT, bg=COLOR_REVIEW, fg="black")
        self.review_button.pack(side=tk.RIGHT, padx=5)

    def add_legend_item(self, parent, color, text):
        frame = tk.Frame(parent, bg=COLOR_BG_NAV)
        frame.pack(fill=tk.X, padx=5, pady=2, anchor="w")
        tk.Label(frame, bg=color, width=2, height=1, relief=tk.SUNKEN).pack(side=tk.LEFT)
        tk.Label(frame, text=text, fg=COLOR_BUTTON_TEXT, bg=COLOR_BG_NAV, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def toggle_dropdown(self, section):
        frame = self.section_content_frames.get(section)
        label = self.dropdown_labels.get(section)
        if frame and label:
            if frame.winfo_ismapped():
                frame.pack_forget()
                label.config(text=f"▶ {section}")
            else:
                frame.pack(fill=tk.X)
                label.config(text=f"▼ {section}")

    def update_nav_panel(self):
        for global_idx, btn in self.question_buttons.items():
            q = self.questions[global_idx]
            key = (q['category'], q['id'])

            if key in self.answers:
                btn.config(bg=COLOR_ANSWERED, fg=COLOR_BUTTON_TEXT)
            elif global_idx in self.review_questions:
                btn.config(bg=COLOR_REVIEW, fg="black")
            else:
                btn.config(bg=COLOR_UNANSWERED, fg=COLOR_BUTTON_TEXT)

            if global_idx == self.question_index:
                btn.config(relief=tk.SUNKEN, bg=COLOR_CURRENT_Q_NAV)
            else:
                btn.config(relief=tk.RAISED)

        if self.question_index in self.review_questions:
            self.review_button.config(text="Unmark Review", bg=COLOR_REVIEW, fg="black")
        else:
            self.review_button.config(text="Mark for Review", bg=COLOR_BG_NAV, fg="white")

    def goto_question(self, global_idx):
        self.question_timer.stop_timer()
        self.question_index = global_idx
        self.show_question()

    def show_question(self):
        if self.question_index >= len(self.questions):
            self.finish_test()
            return

        self.question_timer.stop_timer()
        self.selected_option.set("")
        self.current_question = self.questions[self.question_index]
        q = self.current_question
        
        self.question_count_label.config(text=f"Question {self.question_index + 1} of {len(self.questions)}")
        self.question_title_label.config(text=q['category'])
        self.question_text_label.config(text=q['q'])

        for rb in self.option_radiobuttons:
            rb.destroy()
        self.option_radiobuttons.clear()

        saved_answer = self.answers.get((q['category'], q['id']), "")
        self.selected_option.set(saved_answer)
        
        for opt_key, opt_val in q['options'].items():
            rb = tk.Radiobutton(
                self.options_frame, text=f"{opt_key}) {opt_val}", variable=self.selected_option,
                value=opt_key, font=("Arial", 12), anchor="w", bg="white", activebackground="#bdc3c7",
                selectcolor=COLOR_CURRENT_Q_NAV, indicatoron=0, width=70, relief=tk.FLAT
            )
            rb.pack(anchor="w", pady=2)
            self.option_radiobuttons.append(rb)

        self.question_timer.start_timer()
        self.update_nav_panel()

    def save_answer(self, *args):
        if self.current_question is None:
            return
        
        q = self.current_question
        key = (q['category'], q['id'])
        selected = self.selected_option.get()
        
        if selected:
            self.answers[key] = selected
            
        self.update_nav_panel()
        
    def next_question_manual(self):
        # Stop the timer when the user manually advances
        self.question_timer.stop_timer()
        self.question_index = (self.question_index + 1) % len(self.questions)
        self.show_question()

    def next_question_auto(self):
        # This is called by the timer when it runs out
        self.question_index = (self.question_index + 1) % len(self.questions)
        self.show_question()

    def mark_review(self):
        global_idx = self.question_index
        if global_idx in self.review_questions:
            self.review_questions.remove(global_idx)
        else:
            self.review_questions.add(global_idx)
        self.update_nav_panel()

    def finish_test(self):
        if messagebox.askyesno("Finish Test", "Are you sure you want to finish the test and see your results? You cannot return."):
            self.total_timer.stop_timer()
            self.question_timer.stop_timer()
            self.save_answer()
            self.show_result()

    def finish_test_auto(self):
        self.total_timer.stop_timer()
        self.question_timer.stop_timer()
        self.save_answer()
        messagebox.showinfo("Time's Up!", "Your time has expired. The test will now be submitted.")
        self.show_result()

    def show_result(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        result_frame = tk.Frame(self.main_frame, bg=COLOR_BG_CONTENT)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(result_frame, text="--- TEST COMPLETE ---", font=("Arial", 18, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=10)

        scores = defaultdict(int)
        section_total = defaultdict(int)
        section_answered = defaultdict(int)
        for section, qs in self.section_question_map.items():
            for q in qs:
                section_total[section] += 1
                key = (section, q['id'])
                if key in self.answers:
                    section_answered[section] += 1
                    if self.answers[key] == CORRECT_ANSWERS[section][q['id']]:
                        scores[section] += 1
        
        total_questions_per_category = {cat: len(QUESTIONS[cat]) for cat in QUESTIONS}
        user_scores_array = np.array([scores[cat] / total_questions_per_category[cat] if total_questions_per_category[cat] > 0 else 0 for cat in self.section_order]).reshape(1, -1)

        predicted_course_id = model.predict(user_scores_array)[0]
        confidence = model.predict_proba(user_scores_array).max()
        
        course_map = {
            0: "Computer Science (CSE)",
            1: "Electronics & Communication (ECE)",
            2: "Mechanical Engineering",
            3: "Civil Engineering",
            4: "Information Technology (IT)",
            5: "Biotechnology / Bioinformatics"
        }

        tk.Label(result_frame, text="\n--- Your Scores ---", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack()
        for section in self.section_order:
            # We need to map the section name to the total number of questions for that section in the current quiz instance.
            section_q_count = len(self.section_question_map.get(section, []))
            tk.Label(result_frame, text=f"  {section}: {scores[section]}/{section_q_count}", font=("Arial", 12), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack()
        
        tk.Label(result_frame, text="\n--- RECOMMENDED COURSE ---", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack()
        
        if confidence >= 0.6:
            tk.Label(result_frame, text=f"✅ Based on your results, we recommend: {course_map.get(predicted_course_id, 'No recommendation available.')}", font=("Arial", 14, "bold"), fg=COLOR_ANSWERED, bg=COLOR_BG_CONTENT).pack(pady=10)
            tk.Label(result_frame, text=f"(Confidence: {confidence * 100:.2f}%)", font=("Arial", 10), bg=COLOR_BG_CONTENT, fg="#7f8c8d").pack()
        else:
            tk.Label(result_frame, text=f"⚠️ We are unable to provide a confident recommendation based on your answers. Please consider seeking counseling.", font=("Arial", 12, "bold"), fg=COLOR_REVIEW, bg=COLOR_BG_CONTENT, wraplength=700).pack(pady=10)
            tk.Label(result_frame, text=f"(Confidence: {confidence * 100:.2f}%)", font=("Arial", 10), bg=COLOR_BG_CONTENT, fg="#7f8c8d").pack()
            
        if MATPLOTLIB_AVAILABLE:
            try:
                fig, ax = plt.subplots(figsize=(7, 3))
                sections = self.section_order
                answered = [section_answered[s] for s in sections]
                not_answered = [len(self.section_question_map.get(s, [])) - section_answered[s] for s in sections]
                ax.bar(sections, answered, label='Answered', color=COLOR_ANSWERED)
                ax.bar(sections, not_answered, bottom=answered, label='Not Answered', color=COLOR_UNANSWERED)
                ax.set_ylabel('Questions')
                ax.set_title('Answered vs Not Answered per Section')
                ax.legend()
                plt.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=result_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=20)
            except Exception as ex:
                print(f"Matplotlib Error: {ex}")
                tk.Label(result_frame, text="(Matplotlib not available for chart)", fg="red", bg=COLOR_BG_CONTENT).pack()
        else:
            tk.Label(result_frame, text="(Matplotlib not available for chart)", fg="red", bg=COLOR_BG_CONTENT).pack()

        tk.Button(result_frame, text="Restart Test", font=("Arial", 12), command=self.restart, relief=tk.FLAT).pack(pady=10)

    def restart(self):
        if self.total_timer:
            self.total_timer.stop_timer()
        if self.question_timer:
            self.question_timer.stop_timer()
        
        self.initialize_test_session()
        self.build_widgets()
        self.show_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()