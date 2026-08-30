# piiscan.py — 민감 자동 스캔의 정규식 레이어 (SKILL.md Workflow 3단계의 실행체)
# 사용: uv run python scripts/piiscan.py <md 파일...>
# 판정: CLEAN | HOLD(범주: 스니펫) — 종료코드: HOLD가 하나라도 있으면 1
# 원칙(references/recovery-chains.md §C): 체크섬은 신뢰도 '가산'만 — 형식 일치면 일단 HOLD.
#   플래그는 보류까지만, 확정 판정은 사람이 한다.
# NER 레이어(presidio + KoELECTRA)는 설치된 환경에서 이 스크립트 뒤에 추가로 돈다.
import sys, re

RULES = [
    ("주민등록번호", re.compile(r"\b\d{2}[01]\d[0-3]\d[-\s]?[1-8]\d{6}\b")),
    ("외국인등록번호", re.compile(r"\b\d{2}[01]\d[0-3]\d[-\s]?[5-8]\d{6}\b")),
    ("사업자등록번호", re.compile(r"\b\d{3}-\d{2}-\d{5}\b")),
    ("법인등록번호", re.compile(r"\b\d{6}-\d{7}\b")),
    ("휴대전화", re.compile(r"\b01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}\b")),
    ("유선전화", re.compile(r"\b0(?:2|3[1-3]|4[1-4]|5[1-5]|6[1-4]|70)[-.\s]?\d{3,4}[-.\s]?\d{4}\b")),
    ("카드번호", re.compile(r"\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b")),
    ("이메일", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")),
]
# 문맥 게이트 규칙: 문맥어 ±40자 안의 숫자열만 히트 (계좌는 전국 공통 형식이 없다)
CONTEXT_RULES = [
    ("계좌추정", ["계좌", "입금", "예금주", "국민", "신한", "우리", "하나", "농협", "기업",
                 "카카오뱅크", "토스뱅크"], re.compile(r"\d{2,6}(?:[-\s]?\d{2,6}){1,3}")),
    ("지급·정산", ["지급액", "계좌지급", "정산예정액", "가맹점키", "가맹점명"],
     re.compile(r"[\w가-힣_]{2,}")),
]

def scan(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    hits = []
    for name, pat in RULES:
        for m in list(pat.finditer(text))[:3]:
            hits.append((name, m.group()[:24]))
    for name, ctx_words, pat in CONTEXT_RULES:
        for w in ctx_words:
            i = text.find(w)
            if i >= 0:
                seg = text[max(0, i - 40): i + 40]
                m = pat.search(seg.replace(w, "", 1))
                if m:
                    hits.append((name, f"{w}≈{m.group()[:20]}"))
                    break
    return hits

def main(argv):
    bad = 0
    for p in argv:
        hits = scan(p)
        if hits:
            bad += 1
            cats = "; ".join(f"{n}:{s}" for n, s in hits[:5])
            print(f"HOLD({cats})|{p}")
        else:
            print(f"CLEAN|{p}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
