# qualgate.py — 변환 품질 게이트 (SKILL.md Workflow 2단계의 실행체)
# 사용: uv run python scripts/qualgate.py <변환된 md 파일...>
# 판정: PASS | QUARANTINE(사유)  — 종료코드: 격리가 하나라도 있으면 1
# 검사: 깨진 글리프·두부·대체문자 비율, 한글 문서의 한글 소실, 오류 문자열, 본문 빈약
import sys, re, os

TOFU = set("■□�⬛")          # ■ □ � ⬛
ERR_PAT = re.compile(r"#REF!|#VALUE!|#NAME\?")
NN_RUN = re.compile(r"(?:\bn{2,6}\b[\s:·+/,]*){4,}")  # 'nn nn nnnn' 연쇄 (CMap 손상 증상)

def judge(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    body = re.sub(r"\s+", "", text)
    if len(body) < 20:
        return "QUARANTINE(본문 20자 미만)"
    tofu_ratio = sum(c in TOFU for c in body) / len(body)
    if tofu_ratio > 0.02:
        return f"QUARANTINE(두부/대체문자 {tofu_ratio:.1%})"
    if NN_RUN.search(text):
        return "QUARANTINE(nn 연쇄 — CMap 손상 증상)"
    if ERR_PAT.search(text):
        return "QUARANTINE(스프레드시트 오류 문자열)"
    hangul = sum("가" <= c <= "힣" for c in body)
    ascii_alpha = sum(c.isascii() and c.isalpha() for c in body)
    # 한글 파일명·한글 표제인데 본문 한글이 사실상 0이면 소실 의심
    name_has_hangul = any("가" <= c <= "힣" for c in os.path.basename(path))
    if name_has_hangul and hangul < 5 and ascii_alpha > 50:
        return "QUARANTINE(한글 소실 의심 — 파일명은 한글, 본문 한글 <5자)"
    return "PASS"

def main(argv):
    bad = 0
    for p in argv:
        v = judge(p)
        if v != "PASS":
            bad += 1
        print(f"{v}|{p}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
