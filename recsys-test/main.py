from pathlib import Path
import argparse, json
from matcher import load_users_csv, UserMatcher, MatchConfig

def parse_args():
    p = argparse.ArgumentParser(description="User-User matching recommender")
    p.add_argument("--user_id", help="예: u001 (개별 사용자 추천)")
    p.add_argument("--topk", type=int, default=5)
    p.add_argument("--w_major", type=float, default=0.2)
    p.add_argument("--w_skills", type=float, default=0.55)
    p.add_argument("--w_interests", type=float, default=0.25)
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    root = Path(__file__).resolve().parent
    users_csv = root / "data" / "users.csv"

    if not users_csv.exists():
        print("[INFO] users.csv not found. Run: python generate_users.py")
        exit(1)

    users = load_users_csv(users_csv)
    cfg = MatchConfig(w_major=args.w_major, w_skills=args.w_skills, w_interests=args.w_interests, topk=args.topk)
    matcher = UserMatcher(users, cfg)

    if not args.user_id:
        print("Please provide --user_id (e.g., u001)")
        exit(1)
    recs = matcher.topk_for(args.user_id, args.topk)
    print(json.dumps({"user_id": args.user_id, "matches": recs}, ensure_ascii=False, indent=2))