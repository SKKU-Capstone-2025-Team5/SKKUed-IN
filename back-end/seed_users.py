# seed_users.py
import requests
import random

BASE_URL = "http://127.0.0.1:8000/api/v1/auth/register"

MAJORS = [
    "Statistics", "Computer Science", "Industrial Engineering",
    "Mechanical Engineering", "Artificial Intelligence",
    "Business Administration", "Economics"
]

SKILL_POOL = [
    "Python", "R", "C++", "React", "Django", "FastAPI",
    "TensorFlow", "PyTorch", "SQL", "Git", "Recsys", "DevOps",
]

INTEREST_POOL = [
    "AI", "ML", "Deep Learning", "NLP", "Optimization",
    "Web", "Hackathon", "Open Source", "Vision", "Big Data"
]


def random_skills():
    return random.sample(SKILL_POOL, random.randint(1, 4))


def random_interests():
    return random.sample(INTEREST_POOL, random.randint(1, 3))


def generate_seed_users(n=20):
    users = []
    for i in range(n):
        email = f"seed{i:03}@skku.edu"
        user = {
            "email": email,
            "full_name": f"Seed User {i:03}",
            "major": random.choice(MAJORS),
            "age": str(random.randint(20, 26)),
            "phone_number": f"010-{i:03}-{i:04}",
            "introduction": f"Hello, I am Seed User {i}.",
            "profile_image_url": "/images/basic_profile.png",
            "skills": random_skills(),
            "interests": random_interests(),
            "phone_number_public": True,
            "age_public": True,
            "password": "Password123!",     # 로그인용 비번!!
        }
        users.append(user)
    return users


def register_user(user: dict):
    resp = requests.post(BASE_URL, json=user)
    try:
        data = resp.json()
    except:
        data = resp.text
    print("REGISTER:", user["email"], resp.status_code, data)


def main():
    seed_users = generate_seed_users(20)
    for u in seed_users:
        register_user(u)


if __name__ == "__main__":
    main()