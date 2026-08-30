# sniff.py — 매직바이트 형식 판별 (SKILL.md Workflow 1단계의 실행체)
# 사용: uv run python scripts/sniff.py <파일...>
# 출력: <실제형식>|<확장자일치 OK/MISMATCH>|<파일경로>  (한 줄씩)
# 종료코드: 위장 파일이 하나라도 있으면 1
import sys, os

SIGS = [
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "ole2"),      # doc/xls/ppt/hwp5 공통 컨테이너
    (b"%PDF-", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"PK\x03\x04", "zip"),                              # docx/xlsx/pptx/hwpx 공통
    (b"RIFF", "riff"),                                   # wav
    (b"\xff\xd8\xff", "jpg"),
]
# zip 계열은 내부 항목으로 세분
ZIP_HINTS = [(b"word/", "docx"), (b"xl/", "xlsx"), (b"ppt/", "pptx"),
             (b"Contents/section0.xml", "hwpx"), (b"mimetypeapplication/hwp", "hwpx")]
# ole2 계열 세분 (HWP 5.x는 "HWP Document File" 스트림)
TEXT_HINTS = [(b"MIME-Version", "mhtml"), (b"<?xml", "xml"), (b"{\\rtf", "rtf")]

EXT_OK = {  # 실제형식 -> 허용 확장자
    "pdf": {"pdf"}, "png": {"png"}, "jpg": {"jpg", "jpeg"},
    "docx": {"docx"}, "xlsx": {"xlsx"}, "pptx": {"pptx"}, "hwpx": {"hwpx"},
    "ole2-hwp": {"hwp"}, "ole2": {"doc", "xls", "ppt", "hwp"},
    "wav": {"wav"}, "text": {"md", "txt", "csv"}, "mhtml": {"mht", "mhtml"},
    "xml": {"xml"}, "rtf": {"rtf"}, "zip": {"zip"},
}

def sniff(path):
    with open(path, "rb") as f:
        head = f.read(4096)
    for sig, kind in SIGS:
        if head.startswith(sig):
            if kind == "zip":
                for hint, sub in ZIP_HINTS:
                    if hint in head or hint in _more(path):
                        return sub
                return "zip"
            if kind == "riff":
                return "wav" if head[8:12] == b"WAVE" else "riff"
            if kind == "ole2":
                return "ole2-hwp" if b"HWP Document" in _more(path) else "ole2"
            return kind
    for hint, kind in TEXT_HINTS:
        if hint in head[:256]:
            return kind
    try:
        head.decode("utf-8")
        return "text"
    except UnicodeDecodeError:
        return "unknown"

def _more(path):
    with open(path, "rb") as f:
        return f.read(65536)

def main(argv):
    bad = 0
    for p in argv:
        if not os.path.isfile(p):
            print(f"MISS|파일 없음|{p}"); bad += 1; continue
        kind = sniff(p)
        ext = os.path.splitext(p)[1].lstrip(".").lower()
        ok = ext in EXT_OK.get(kind, set())
        if not ok:
            bad += 1
        print(f"{kind}|{'OK' if ok else 'MISMATCH:확장자=' + ext}|{p}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
