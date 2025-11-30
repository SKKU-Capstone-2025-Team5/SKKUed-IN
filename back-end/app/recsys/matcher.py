# app/recsys/matcher.py
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Iterable, Sequence
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

def _tok(s: str) -> str:
    if pd.isna(s):
        return ""
    toks = [t.strip().lower() for t in str(s).replace(",", ";").split(";") if t.strip()]
    return " ".join(toks)

@dataclass
class MatchConfig:
    w_major: float = 0.20
    w_skills: float = 0.60
    w_interests: float = 0.20
    topk: int = 5
    same_person_penalty: float = -1e9

    @classmethod
    def from_values(cls, w_major=None, w_skills=None, w_interests=None, topk=None):
        wm = float(w_major) if w_major is not None else cls.w_major
        ws = float(w_skills) if w_skills is not None else cls.w_skills
        wi = float(w_interests) if w_interests is not None else cls.w_interests
        s = wm + ws + wi
        if s <= 0:
            wm, ws, wi = cls.w_major, cls.w_skills, cls.w_interests
            s = wm + ws + wi
        wm, ws, wi = wm / s, ws / s, wi / s
        tk = int(topk) if topk is not None else cls.topk
        return cls(w_major=wm, w_skills=ws, w_interests=wi, topk=tk)

class UserMatcher:
    def __init__(self, users_df: pd.DataFrame, cfg: MatchConfig = MatchConfig()):
        self.cfg = cfg
        self.users = users_df.copy()
        for col in ["major", "skills", "interests"]:
            self.users[col] = self.users[col].apply(_tok)

        corpus = (
            self.users["major"] + " " + self.users["skills"] + " " + self.users["interests"]
        ).fillna("")

        # TF-IDF (유니/바이그램, 흔함/희귀 토큰 컷, 서브리니어 TF)
        self.vec = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.9,
            sublinear_tf=True,
            norm="l2",
        )
        self.X_all = self.vec.fit_transform(corpus)

        # 필드별 벡터
        self.X_major = self.vec.transform(self.users["major"])
        self.X_skills = self.vec.transform(self.users["skills"])
        self.X_interests = self.vec.transform(self.users["interests"])

        # 정규화(코사인 유사도 기반)
        self.U_major = normalize(self.X_major)
        self.U_skills = normalize(self.X_skills)
        self.U_interests = normalize(self.X_interests)

        # 가중 합 임베딩
        self._rebuild_U()

        self.users = self.users.reset_index(drop=True)
        self.idx_by_id = {int(uid): i for i, uid in enumerate(self.users["user_id"])}

    # ---- 내부 유틸 ----
    def _rebuild_U(self):
        self.U = (
            self.cfg.w_major * self.U_major
            + self.cfg.w_skills * self.U_skills
            + self.cfg.w_interests * self.U_interests
        )
        self.U = normalize(self.U)

    def _sim_fields(self, i: int, j: int) -> Tuple[float, float, float]:
        """각 필드별 코사인 유사도 (major, skills, interests)."""
        mj = float((self.U_major[i] @ self.U_major[j].T).toarray()[0, 0])
        sk = float((self.U_skills[i] @ self.U_skills[j].T).toarray()[0, 0])
        it = float((self.U_interests[i] @ self.U_interests[j].T).toarray()[0, 0])
        return mj, sk, it

    # ---- 학습(1): 수락/거절 이력 기반 ----
    def learn_from_history(
        self,
        target_user_id: int,
        interactions: List[Tuple[int, int, int]],
        # (target_user_id, other_user_id, label)  label: +1(ACCEPTED) / -1(REJECTED)
        min_events: int = 2,
        floor: float = 1e-3,
    ) -> Dict[str, float]:
        """
        타겟 유저의 팀 수락/거절 기록으로 필드 가중치를 재추정.
        아이디어: (수락 평균 유사도 - 거절 평균 유사도)를 필드별로 계산 후 정규화.
        학습 데이터가 부족하면 기존 가중치 유지.
        """
        if target_user_id not in self.idx_by_id:
            return {
                "w_major": self.cfg.w_major,
                "w_skills": self.cfg.w_skills,
                "w_interests": self.cfg.w_interests,
            }

        pos_mj = pos_sk = pos_it = 0.0
        neg_mj = neg_sk = neg_it = 0.0
        pos_cnt = neg_cnt = 0

        i = self.idx_by_id[target_user_id]

        for _, other_uid, label in interactions:
            j = self.idx_by_id.get(int(other_uid))
            if j is None:
                continue
            mj, sk, it = self._sim_fields(i, j)
            if label > 0:
                pos_mj += mj; pos_sk += sk; pos_it += it; pos_cnt += 1
            elif label < 0:
                neg_mj += mj; neg_sk += sk; neg_it += it; neg_cnt += 1

        if (pos_cnt + neg_cnt) < min_events:
            return {
                "w_major": self.cfg.w_major,
                "w_skills": self.cfg.w_skills,
                "w_interests": self.cfg.w_interests,
            }

        pos_mj /= max(1, pos_cnt)
        pos_sk /= max(1, pos_cnt)
        pos_it /= max(1, pos_cnt)
        neg_mj = (neg_mj / max(1, neg_cnt)) if neg_cnt else 0.0
        neg_sk = (neg_sk / max(1, neg_cnt)) if neg_cnt else 0.0
        neg_it = (neg_it / max(1, neg_cnt)) if neg_cnt else 0.0

        d_mj = max(pos_mj - neg_mj, 0.0) + floor
        d_sk = max(pos_sk - neg_sk, 0.0) + floor
        d_it = max(pos_it - neg_it, 0.0) + floor

        s = d_mj + d_sk + d_it
        w_major = d_mj / s
        w_skills = d_sk / s
        w_interests = d_it / s

        self.cfg.w_major, self.cfg.w_skills, self.cfg.w_interests = w_major, w_skills, w_interests
        self._rebuild_U()

        return {"w_major": w_major, "w_skills": w_skills, "w_interests": w_interests}

    # ---- 학습(2): 기존 코드 호환용 API ----
    def learn_weights(
        self,
        pos_pairs: Sequence[Tuple[int, int]],
        neg_pairs: Sequence[Tuple[int, int]],
        steps: int = 100,   # (미사용; 시그니처 호환용)
        lr: float = 0.1,    # (미사용; 시그니처 호환용)
        verbose: bool = False,
        floor: float = 1e-3,
        min_events: int = 2,
    ) -> Dict[str, float]:
        """
        (userA, userB) 쌍 리스트로 들어오는 기존 호출과 100% 호환.
        내부적으로는 위의 heuristic(평균 유사도 차이)으로 가중치를 갱신.
        """
        # 평균 유사도 계산
        def avg_sims(pairs: Iterable[Tuple[int, int]]):
            tot_mj = tot_sk = tot_it = 0.0
            cnt = 0
            for a, b in pairs:
                ia = self.idx_by_id.get(int(a))
                ib = self.idx_by_id.get(int(b))
                if ia is None or ib is None:
                    continue
                mj, sk, it = self._sim_fields(ia, ib)
                tot_mj += mj; tot_sk += sk; tot_it += it
                cnt += 1
            if cnt == 0:
                return 0.0, 0.0, 0.0, 0
            return tot_mj / cnt, tot_sk / cnt, tot_it / cnt, cnt

        pos_mj, pos_sk, pos_it, pc = avg_sims(pos_pairs)
        neg_mj, neg_sk, neg_it, nc = avg_sims(neg_pairs)

        if (pc + nc) < min_events:
            if verbose:
                print("[learn_weights] not enough events; keep old weights.")
            return {
                "w_major": self.cfg.w_major,
                "w_skills": self.cfg.w_skills,
                "w_interests": self.cfg.w_interests,
            }

        d_mj = max(pos_mj - neg_mj, 0.0) + floor
        d_sk = max(pos_sk - neg_sk, 0.0) + floor
        d_it = max(pos_it - neg_it, 0.0) + floor

        s = d_mj + d_sk + d_it
        w_major = d_mj / s
        w_skills = d_sk / s
        w_interests = d_it / s

        self.cfg.w_major, self.cfg.w_skills, self.cfg.w_interests = w_major, w_skills, w_interests
        self._rebuild_U()

        if verbose:
            print(f"[learn_weights] -> w_major={w_major:.3f}, w_skills={w_skills:.3f}, w_interests={w_interests:.3f}")

        return {"w_major": w_major, "w_skills": w_skills, "w_interests": w_interests}

    # ---- 추천 ----
    def topk_for(self, user_id: int, topk: Optional[int] = None) -> List[Dict]:
        if user_id not in self.idx_by_id:
            raise ValueError(f"user_id '{user_id}' not found")
        k = topk or self.cfg.topk
        i = self.idx_by_id[user_id]
        sims = (self.U[i] @ self.U.T).toarray().ravel()
        sims[i] = self.cfg.same_person_penalty
        order = np.argsort(-sims)[:k]
        out = []
        for j in order:
            row = self.users.iloc[j]
            out.append({
                "user_id": int(row["user_id"]),
                "name": row.get("name", ""),
                "major": row.get("major", ""),
                "skills": row.get("skills", ""),
                "interests": row.get("interests", ""),
                "similarity": round(float(sims[j]), 4),
            })
        return out

def load_users_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")