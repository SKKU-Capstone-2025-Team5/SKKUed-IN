from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

@dataclass
class MatchConfig:
    w_major: float = 0.2
    w_skills: float = 0.55
    w_interests: float = 0.25
    topk: int = 5
    same_person_penalty: float = -1e9

def _tok(s: str) -> str:
    if pd.isna(s): return ""
    toks = [t.strip().lower() for t in str(s).replace(",", ";").split(";") if t.strip()]
    return " ".join(toks)

class UserMatcher:
    def __init__(self, users_df: pd.DataFrame, cfg: MatchConfig = MatchConfig()):
        self.cfg = cfg
        self.users = users_df.copy()
        for col in ["major","skills","interests"]:
            self.users[col] = self.users[col].apply(_tok)

        corpus = (self.users["major"]+" "+self.users["skills"]+" "+self.users["interests"]).fillna("")
        self.vec = TfidfVectorizer()
        self.X_all = self.vec.fit_transform(corpus)

        self.X_major     = self.vec.transform(self.users["major"])
        self.X_skills    = self.vec.transform(self.users["skills"])
        self.X_interests = self.vec.transform(self.users["interests"])

        self.U = self.cfg.w_major*self.X_major + self.cfg.w_skills*self.X_skills + self.cfg.w_interests*self.X_interests
        self.U = normalize(self.U)
        self.users = self.users.reset_index(drop=True)
        self.idx_by_id = {uid:i for i, uid in enumerate(self.users["user_id"])}

    def topk_for(self, user_id: str, topk: int | None = None) -> List[Dict]:
        if user_id not in self.idx_by_id:
            raise ValueError(f"user_id '{user_id}' not found")
        k = topk or self.cfg.topk
        i = self.idx_by_id[user_id]
        sims = (self.U[i] @ self.U.T).toarray().ravel() #
        sims[i] = self.cfg.same_person_penalty
        order = np.argsort(-sims)[:k]
        out = []
        for j in order:
            row = self.users.iloc[j]
            out.append({
                "user_id": row["user_id"],
                "name": row["name"],
                "major": row["major"],
                "skills": row["skills"],
                "interests": row["interests"],
                "similarity": round(float(sims[j]), 4),
            })
        return out

def load_users_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")