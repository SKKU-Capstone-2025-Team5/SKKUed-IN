import csv, random
from pathlib import Path
#사용자 더미 데이터 생성하기
N_USERS = 250   # 200~300 사이로? 일단은, 원하면 늘리고...잘 모르곘
RANDOM_SEED = 42

MAJORS = [
    "Computer Science","Software Engineering","Statistics","Data Science",
    "Industrial Engineering","Economics","Design","Mathematics","AI","Information Systems"
]

SKILLS = [
    "Python","Java","C++","SQL","R","NLP","CV","ML","DL","ETL",
    "React","Node.js","Express","Spring","Django","Flask",
    "Docker","Kubernetes","AWS","GCP",
    "Pandas","NumPy","Sklearn","TensorFlow","PyTorch",
    "Figma","UI/UX","Illustrator","Stata","Optimization","OR-Tools",
]

INTERESTS = [
    "Backend","Frontend","Full-Stack","Cloud","DevOps","Security",
    "AI","NLP","Computer Vision","Recommender","Analytics","BI",
    "Finance","Fintech","Econometrics","Operations","Hackathon","Startup",
]

def make_user(i: int):
    uid = f"u{i:03d}"
    name = f"User{i:03d}"
    major = random.choice(MAJORS)
    skills = ";".join(sorted(random.sample(SKILLS, k=random.randint(3,6))))
    interests = ";".join(sorted(random.sample(INTERESTS, k=random.randint(3,6))))
    if major in ["Statistics","Data Science","Mathematics","AI"]:
        if "ML" not in skills and random.random()<0.5: skills += ";ML"
        if "AI" not in interests and random.random()<0.5: interests += ";AI"
    return [uid, name, major, skills, interests]

if __name__ == "__main__":
    random.seed(RANDOM_SEED)
    root = Path(__file__).resolve().parent
    data = root / "data"
    data.mkdir(exist_ok=True)
    out = data / "users.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user_id","name","major","skills","interests"])
        for i in range(1, N_USERS+1):
            w.writerow(make_user(i))
    print(f"[OK] generated {N_USERS} users -> {out}")