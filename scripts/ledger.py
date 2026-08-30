# ledger.py — 정산·색인 정합 기계 검증 (SKILL.md Verification 1·3의 실행체)
# 사용: uv run python scripts/ledger.py <코퍼스 기준 폴더의 ingestiger 디렉터리> --found N
# 검사: index.md 상태 열 합계 == 발견 N, 적재 행마다 md/ 파일 실재, 격리 행마다 quarantine/ 실재
# 종료코드: 불일치 시 1 (배치 미완 판정)
import sys, os, re

STATES = ["적재", "실패", "건너뜀", "격리", "보류"]

def main(argv):
    base = argv[0]
    found = int(argv[argv.index("--found") + 1]) if "--found" in argv else None
    idx = os.path.join(base, "index.md")
    rows = []
    for line in open(idx, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("제목", "---") or cells[0].startswith("-"):
            continue
        rows.append(cells)
    counts = {s: 0 for s in STATES}
    problems = []
    md_files = set(os.listdir(os.path.join(base, "md"))) if os.path.isdir(os.path.join(base, "md")) else set()
    q_files = " ".join(os.listdir(os.path.join(base, "quarantine"))) if os.path.isdir(os.path.join(base, "quarantine")) else ""
    for cells in rows:
        title, status = cells[0], cells[-1]
        state = next((s for s in STATES if status.startswith(s)), None)
        if state is None:
            problems.append(f"상태 판독 불가: {title} -> {status[:30]}")
            continue
        counts[state] += 1
        if state == "적재" and not any(title.split("(")[0][:8] in f or title[:8] in f for f in md_files):
            problems.append(f"적재인데 md/ 파일 미발견: {title}")
        if state == "격리" and title[:8] not in q_files:
            problems.append(f"격리인데 quarantine/ 파일 미발견: {title}")
    total = sum(counts.values())
    line = " + ".join(f"{s} {counts[s]}" for s in STATES)
    print(f"정산: 발견 {total} = {line}")
    if found is not None and total != found:
        problems.append(f"발견 기대 {found} != 색인 합계 {total}")
    if not os.path.isfile(os.path.join(base, "updates.md")):
        problems.append("updates.md 없음")
    if problems:
        print("판정: 미완")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("판정: 정산 일치, 색인 정합")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
