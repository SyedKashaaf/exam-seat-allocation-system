import csv
import random
import os

random.seed(42)

# generate_data.py sits in the project ROOT; students.csv goes into data/
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# Mixed department courses
COURSES = {
    "BSAI": ["AI3163", "AI3812", "AI2201", "AI1101", "AI3301"],
    "BSCS": ["CS2512", "CS3301", "CS2201", "CS1101", "CS3401"],
    "BSSE": ["SE2523", "SE3201", "SE2101", "SE1201", "SE3301"],
    "BSIT": ["IT2301", "IT1101", "IT3201", "IT2101", "IT3101"],
}

FIRST_NAMES = [
    "Ali", "Ahmed", "Hassan", "Usman", "Bilal", "Hamza", "Zain", "Saad",
    "Omar", "Faisal", "Tariq", "Imran", "Junaid", "Kamran", "Noman",
    "Ayesha", "Fatima", "Zara", "Sana", "Hira", "Maryam", "Nadia",
    "Sara", "Amna", "Rabia", "Kiran", "Iqra", "Mahnoor", "Laiba", "Alina"
]

LAST_NAMES = [
    "Khan", "Ahmed", "Ali", "Hassan", "Malik", "Chaudhry", "Butt",
    "Siddiqui", "Qureshi", "Shah", "Rana", "Mirza", "Baig", "Rizvi",
    "Javed", "Hussain", "Nawaz", "Iqbal", "Raza", "Noor"
]

students = []
roll_counter = {dept: 1 for dept in COURSES}

for dept, courses in COURSES.items():
    for course in courses:
        # 12 students per course per dept
        count = 12
        for _ in range(count):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            roll = f"{dept[:2]}{str(roll_counter[dept]).zfill(3)}"
            roll_counter[dept] += 1
            students.append({"RollNo": roll, "Name": name, "Course": course})

random.shuffle(students)

os.makedirs(DATA_DIR, exist_ok=True)
out_path = os.path.join(DATA_DIR, "students.csv")
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["RollNo", "Name", "Course"])
    writer.writeheader()
    writer.writerows(students)

print(f"Generated {len(students)} students.")
print(f"Saved to: {out_path}")
