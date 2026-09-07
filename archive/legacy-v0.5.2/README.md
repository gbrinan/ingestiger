# IngesTiger — 인제스트타이거

**원본 뭉치를 역추적 가능한 코퍼스로.**
pdf · hwp/hwpx · doc/docx · md · txt · png · pptx · xlsx · csv · wav →
마크다운 변환 → **로컬 정본** → (지시 시) **구글 드라이브 / 선택 DB 미러** → 코퍼스/RAG 적재.

soloforce의 `ingest-crab`(인제스트크랩)을 [paperthin](https://github.com/LilMGenius/paperthin)
철학으로 재설계한 후속 세대입니다. 핵심 전제는 그대로입니다:

> 검색된다는 것은 값이 맞다는 증거가 아니다.
> 진척은 적재 건수가 아니라 **원본까지 되짚을 수 있는 값의 수**다.

## 구성

| 경로 | 내용 |
|---|---|
| [`skills/ingestiger/SKILL.md`](./skills/ingestiger/SKILL.md) | **절차의 정본.** 수직 루프 · 변환 라우팅 표 · 저장 계층 · 게이트 · 검증 |
| [`agent/role-directive.md`](./agent/role-directive.md) | Soloforce2용 역할 지시서 (스킬을 정본으로 참조) |
| [`agent/meta.json`](./agent/meta.json) | 에이전트 메타 + **version(semver) 정본** |
| [`docs/soloforce2-integration.md`](./docs/soloforce2-integration.md) | Soloforce2 연동·버전 고정 가이드 |
| `tasks.md` / `findings.md` / `progress.md` | 파일 기반 플래닝 워크플로 (계획 · 발견 · 로그) |

## 설계 원칙 (paperthin에서)

- **Trust the artifact, not the author** — 배치는 정산(발견=적재+실패+건너뜀+격리+보류),
  역추적 3건, 문서별 스모크 질의가 맞아야 끝난다. 변환기의 성공 종료 코드도, 만든 세션의
  자신감도 증거가 아니다.
- **자기완결 + SSOT** — 스킬 하나만 설치해도 돌아가고, 도구명은 "바뀌면 여기만 고친다"
  표 한 곳, 버전은 meta.json 한 곳에만 산다.
- **negatives-as-corpus** — 실패·건너뜀 목록은 지우지 않는다. 다음 배치의 훈련 데이터다.
- **절제** — 지시 없는 폴더는 열지 않고, 배치 50을 넘기지 않고, 스키마를 만들거나 바꾸지 않는다.

## 저장 파이프라인

```
원본 (읽기 전용)
   │  판별: 확장자가 아니라 매직바이트
   │  변환: kordoc(한국 문서·OCR) / markitdown / faster-whisper(wav)  ← 라우팅 표는 SKILL.md가 정본
   │  품질 게이트: 깨진 글리프·저신뢰 OCR/STT → 격리(quarantine/)
   ▼
로컬 정본  <기준 폴더>/ingestiger/{index.md, updates.md, md/, quarantine/, meta/}
   │           ├ 사람이 폴더만 열어도 무엇이 들어왔는지 보인다 (위키형 색인)
   │           └ 민감 자동 스캔 → 플래그는 보류(사람 판정 대기), 확정은 사람
   ├─ (지시 시) 구글 드라이브 미러 — 정본 구조 그대로 (보류·격리 제외)
   ├─ (지시 시) 선택 DB 미러 — 코퍼스 스키마 (청킹은 적재와 동일 규칙)
   ▼
코퍼스/RAG 적재(구조 청크 우선) → 검증(역추적 3건 + 문서별 스모크 질의) → 보고
```

## 버전

`agent/meta.json`의 `version`이 정본이며 git tag `vX.Y.Z`와 일치합니다.
판정은 크기가 아니라 종류: 수정=patch, 새 능력=minor, 대체 없는 제거=major.
Soloforce2는 태그를 고정(pin)해 가져갑니다 — [연동 가이드](./docs/soloforce2-integration.md).
