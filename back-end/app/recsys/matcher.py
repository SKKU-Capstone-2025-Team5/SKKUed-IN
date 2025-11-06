from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

@dataclass


#class MatchConfig:
    #w_major: float = 0.2
    #w_skills: float = 0.55
    #w_interests: float = 0.25
    #topk: int = 5
    #same_person_penalty: float = -1e9

#skill비중을 조금 . 더주고, 관심사 비중을 약간 낮추는게 팀매칭에선 안정적일 것이라 생각. 가중치 고정했는데, 이거 자동학습은 조금 더 생각해봐야할듯해서.
class MatchConfig:
    w_major: float = 0.20
    w_skills: float = 0.60
    w_interests: float = 0.20
    topk: int = 5
    same_person_penalty: float = -1e9
    @classmethod
    def from_values(cls, w_major=None, w_skills=None, w_interests=None, topk=None):
        # 입력이 None이면 기본값 사용, 합이 0이거나 음수면 냅둠
        wm = float(w_major) if w_major is not None else cls.w_major
        ws = float(w_skills) if w_skills is not None else cls.w_skills
        wi = float(w_interests) if w_interests is not None else cls.w_interests
        s = wm + ws + wi
        if s <= 0:
            wm, ws, wi = cls.w_major, cls.w_skills, cls.w_interests
            s = wm + ws + wi
        # 합 1로 정규화하기
        wm, ws, wi = wm/s, ws/s, wi/s
        tk = int(topk) if topk is not None else cls.topk
        return cls(w_major=wm, w_skills=ws, w_interests=wi, topk=tk)

def _tok(s: str) -> str:
    if pd.isna(s): return ""
    toks = [t.strip().lower() for t in str(s).replace(",", ";").split(";") if t.strip()]
    return " ".join(toks)
#--------------------



#--------------------
class UserMatcher:
    def __init__(self, users_df: pd.DataFrame, cfg: MatchConfig = MatchConfig()):
        self.cfg = cfg
        self.users = users_df.copy()
        for col in ["major","skills","interests"]:
            self.users[col] = self.users[col].apply(_tok)

        corpus = (self.users["major"]+" "+self.users["skills"]+" "+self.users["interests"]).fillna("")
        #self.vec = TfidfVectorizer()
        self.vec = TfidfVectorizer(
            ngram_range=(1, 2),   # uni+bigram
            min_df=2,             # 너무 희귀한 토큰 cut
            max_df=0.9,           # 너무 흔한 토큰 cut
            sublinear_tf=True,    # tf를 1+log(tf)로 눌러 과대평가 방지
            norm="l2",            # l2노름이 보통 코사인 유사도랑 상성관계라 이게 정베
        )
        self.X_all = self.vec.fit_transform(corpus)

        self.X_major     = self.vec.transform(self.users["major"])
        self.X_skills    = self.vec.transform(self.users["skills"])
        self.X_interests = self.vec.transform(self.users["interests"])

        self.U = self.cfg.w_major*self.X_major + self.cfg.w_skills*self.X_skills + self.cfg.w_interests*self.X_interests
        self.U = normalize(self.U)
        self.users = self.users.reset_index(drop=True)
        self.idx_by_id = {uid:i for i, uid in enumerate(self.users["user_id"])}

    def topk_for(self, user_id: int, topk: int | None = None) -> List[Dict]:
        if user_id not in self.idx_by_id:
            raise ValueError(f"user_id '{user_id}' not found")
        #--------------------







        #--------------------
        k = topk or self.cfg.topk
        i = self.idx_by_id[user_id]
        sims = (self.U[i] @ self.U.T).toarray().ravel() #
        sims[i] = self.cfg.same_person_penalty
        order = np.argsort(-sims)[:k]
        out = []
        for j in order:
            row = self.users.iloc[j]
            out.append({
                "user_id": int(row["user_id"]), # Ensure user_id is int
                "name": row["name"],
                "major": row["major"],
                "skills": row["skills"],
                "interests": row["interests"],
                "similarity": round(float(sims[j]), 4),
            })
        return out

def load_users_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")
