# verguard.py — meta.json version과 git tag 일치 가드 (배포 전 실행)
# 사용: uv run python scripts/verguard.py   (레포 루트에서)
# 종료코드: 불일치 시 1
import json, subprocess, sys

def main():
    v = json.load(open("agent/meta.json", encoding="utf-8"))["version"]
    tag = subprocess.run(["git", "describe", "--tags", "--abbrev=0"],
                         capture_output=True, text=True).stdout.strip()
    ok = tag == f"v{v}"
    print(f"meta.json {v} / 최신 태그 {tag} -> {'일치' if ok else '불일치'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
