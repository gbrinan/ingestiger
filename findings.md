# findings.md — 조사·발견 기록

> 발견 즉시 기록한다. 근거(파일·커밋·URL)를 함께 남긴다. 조사일: 2026-08-30.

## 1. paperthin 라인 바이 라인 정독 (LilMGenius/paperthin, v0.17.4, 스킬 28개 전수)

### 1-1. 철학 (CLAUDE.md Philosophy 절, 5원칙 — 원문 근거)

1. **Trust the artifact, not the author.** 스킬은 "그 자리에 없던 사람에게 작업이 참으로
   읽히게" 만들기 위해 존재한다. 만든 사람의 세션 내 판단은 최악의 심판이므로, 스킬은
   (a) 지금 참인 것으로부터 작업을 재도출하거나 (b) 바깥 눈을 들여와 검증한다.
2. **Generic examples, not instances.** 내구 문서의 예시는 항상 일반형(`(#123, @handle)`).
   실제 PR 번호·SHA는 시간이 지나면 "현재 사실"로 오독되는 잔여물이 된다.
3. **SSOT + 자기완결 스킬.** 하나의 사실은 한 곳에 살고 나머지는 참조한다. 그러나 스킬은
   홀로 설치되어도 돌아가야 하므로 자기가 필요한 런타임 규칙은 인라인으로 담는다.
   SSOT는 "사실"의 드리프트를 막고, 자기완결은 "스킬"의 이동성을 보장한다 — 서로 다른 층위.
4. **Restraint(절제).** 진짜로 개선되는 것만 바꾼다. "개선할 것이 없으면 아무것도 바꾸지
   않는 패스"가 정상 결과다. 적은 슬롭(잡음·중복·패딩)이지, 추가 자체가 아니다.
5. **Recursive.** 모든 스킬은 스킬을 만들 때도 쓸 수 있을 만큼 일반적이어서,
   스킬로 스킬을 유지보수한다. 그 루프가 곧 제품이다.

### 1-2. 구조 (Layout)

- `skills/<perspective>/<name>/SKILL.md` — 플러그인 안의 유일한 내구적 분류축은
  **perspective**, 그리고 그것은 **cardinality × time** 두 직교축이다:
  - `depth/` 하나의 산출물·지금 (다듬기·검증) — 19개
  - `breadth/` 여러 곳·지금 (하나의 진실 정합) — 2개
  - `coil/` 한 프로젝트·반복 사이 (배움의 운반) — 6개
  - `mesh/` 여러 시점·라운드 사이 (독립 시각의 수렴) — 1개
- 분류는 "스킬이 무엇을 호출하나"가 아니라 "트리거·산출이 미치는 범위"로 한다.
- 이름 규칙: 반사신경을 부르는 실제 단어(shower, sip) 또는 촘촘한 압축(re0, ssotize).
  낯선 이가 이름만 보고 절반은 추측 가능해야 한다. 모델 브랜드 명명 금지 — 메커니즘은
  어떤 모델보다 오래 살아야 한다.

### 1-3. SKILL.md 해부학 (모든 스킬 공통)

```
---
name: <kebab-name>            # 디렉터리·호출명과 일치
description: "<트리거가 풍부한 한 줄>"
# disable-model-invocation: true   ← 사용자 호출 전용일 때만
---
<한 줄: 이 스킬이 하는 일>
## Goal / ## Workflow(번호 단계) / ## Rules(제약) / ## Verification(끝내기 전 확인+보고)
```

- **호출 구분**: 기본은 model-invoked. 사용자 호출 전용은 (a) 트리거가 인간의 의도적 행위
  (커밋·푸시·배포)이거나 (b) 손 닿는 곳에 있는 것만으로 에이전트를 편향시키는 경우뿐
  (hate=철거 편향, feynman=만성 자기의심, debloat=과압축…). 사용자 호출 스킬은
  다른 사용자 호출 스킬을 자동으로 부를 수 없다.
- **스킬 간 참조**: `/skill` 식 산문 호출("Run the `/re0` skill")로만. 폴더 간 딥링크 금지.

### 1-4. 공유 규약 3종 (여러 스킬에 인라인 복제, CLAUDE.md가 지도)

- **edit-safety**: 대상 존재를 확인하고 없으면 MISS 보고(조용한 no-op 금지), 유니코드
  안전 편집, 위치 대상은 발생 건별 치환(일괄 스윕 금지), 큰 구조 이동은 스크립트로.
- **negatives-as-corpus**: "잘라냄"은 아카이브 이동이지 삭제가 아니다. 실패한 가지는 자산.
- **commit-economy**: 커밋 메시지는 내구적 인수인계 사실만, diff가 증명하는 것은 쓰지 않음.

### 1-5. 스킬별 핵심 (28개 전수 — 각 스킬의 하중을 받는 규칙)

**depth/**
- `re0` 산출물을 "첫 클린 버전"으로 재작성. 변경 이력이 아니라 "지금 참인 것"으로 변환.
  찾을 게 없으면 아무것도 바꾸지 않는다.
- `readchk` 지시를 딴 말로 재진술→맥락과 대조→해소되면 침묵 진행, 진짜 갈림길 하나만 질문.
- `aim` 데이터가 얇은 요청과 함께 오면: 다 읽고→의도를 "확인만 하면 되는 제안"으로.
  질문으로 돌려주면 실패.
- `modelchk` 실행 전 2좌표(모델 티어 fast/standard/frontier × 추론 노력 glance~exhaustive)
  권고. 라우팅 권한 없음, 검증은 티어로 대체 불가.
- `hate` (사용자 호출) 계획을 죽일 단 하나의 하중 반론 + 그것을 검증할 가장 싼 실험
  `{root, first_nail}`. 체크리스트 반환 금지.
- `macrothink` (사용자 호출) 세션의 미끼를 벗긴 재진술로 2~5개 신선한 읽기 팬아웃,
  발산 먼저 보고. 수렴은 안심일 뿐 증명이 아니다.
- `feynman` (사용자 호출) 방금 내린 결정을 맥락 없는 비평가가 압박 — 근거를 먼저 주지
  않고, 얕은 답엔 더 좁은 질문. 설명 못 한 갭은 유효한 결과.
- `autobahn` 위험 인접 범위를 실행 전에 도려내고(CARVE), 안전한 나머지를 깨끗한 프롬프트만
  본 새 서브에이전트가 전속력으로(RUN), 제외는 원장(LEDGER)으로 가시화. 회피가 아니라 제거.
- `reorder` (사용자 호출) 나열의 순서를 하나의 명명 가능한 원칙으로 재정렬. 이동만, 개서 금지.
- `detool` 내구 문서에서 우연한 스택 명사를 메커니즘 언어로. 단 출처 기록·런북·도구가
  주어인 주장은 구체명 유지. "역할 판별이 편집보다 먼저".
- `dedash` (사용자 호출) 사용자 지정 범위에서 em-dash류를 문법 역할별로 건별 치환.
- `debloat` (사용자 호출) 하중을 받는 주장 하나도 잃지 않고 밀도만 압축. 중복은 ssotize로,
  드리프트는 re0로 넘긴다 — 압축은 압축만.
- `shower` 맥락 0의 서브세션에 산출물 내용만 건네 콜드리드. 불일치는 전부 독자 탓이 아니라
  산출물의 결함. "읽기이지 grep 스윕이 아니다".
- `factchk` 현실 근거 주장을 외부 소스로 양방향 검증(황당한 게 진짜일 수도, 명백한 게
  거짓일 수도). 소스에 못 닿으면 단정 말고 플래그.
- `mandela` 평가·지표·실험의 누수 8패턴 감사(암기, 잘못된 귀무가설, 공유 환각, 동어반복,
  검증자=설계자, 공유 풀 편향, 프레임 주입, 요구 특성). 읽기 전용.
- `sip` 무언가를 만들거나 고친 직후 자동으로: shower→(주장 있으면 factchk / 평가면 mandela)
  →ssotize 감사→(이식성 주장 시 detool)→re0. 스스로 재구현하지 않고 스킬을 호출.
  사용자 호출 스킬은 절대 자동으로 부르지 않는다.
- `re0-git` (사용자 호출) 끝난 커밋의 메시지만 재작성 — 트리는 바이트 동일. 커밋을 만들거나
  권하지 않는다. HEAD는 날짜 갱신, 과거 커밋은 날짜 보존.
- `re0-release` (사용자 호출) 배송 체크리스트 전체를 하나의 의도적 명령으로. 커밋과
  태그+푸시를 별도 확인 두 번으로. 워크플로가 소유한 단계는 절대 손으로 안 한다.
- `re0-merge` (사용자 호출) 기여 랜딩: 추가형 기여는 기본 거절(입증 책임은 추가 쪽),
  저자 크레딧 보존, 수락 시점에 승인, 거절도 논지에 묶인 이유와 함께 — 침묵 클로즈 금지.

**breadth/**
- `ssotize` 흩어진 사실 감사(읽기 전용)→정본 지정→변이 계획 승인 후 통합→나머지는 참조로.
  두 방법으로 재열거해 누락 확인. 신뢰 경계(사적↔공개)를 넘는 통합은 확인 필수.
- `re0-upgrade` (사용자 호출) 설치본을 전체 카탈로그로 수렴 — 이름 변경 은퇴, 미설치 추가,
  기존 갱신, 전부 계획 출력·확인 후. 섀도 설치는 stop-and-report.

**coil/**
- `re0-plan` (사용자 호출) 사이클 케이스북 폴더를 "만드는 동작 안에서" 시딩 — 빈 폴더 금지.
  무게 분류(lightweight=RETRO 한 문단 / full=DESIGN+WORKFLOW+EVIDENCE).
- `re0-loop` FRAME→BUILD→DRIVE→RE0-MEMO→HATE→RE0-WORK→BUILD AGAIN. 진척의 단위는 시간·파일
  수가 아니라 품질 게이트를 통과한 템플릿·재사용 모듈·제거된 안티패턴 수. 실제 표면(브라우저·
  HTTP·CLI)을 몰아본 증거 필수. 바깥 진실이 안 들어오면 랩 중단.
- `re0-memo` 끝난·실패한 사이클에서 교훈 추출. 구체 불만은 위로 일반화해 패턴 가족으로,
  구체 사례는 증거로 아래에. "다음 에이전트가 행동할 수 없으면 아직 교훈이 아니다".
- `re0-work` 통제된 재시작: 계약·스키마·게이트·어휘·실표면 테스트·네거티브 코퍼스만 승계,
  우연한 아키텍처는 복사 금지.
- `catchup` 사람의 잃어버린 맥락을 라이브 상태(파일 mtime, git log, 계획 문서)에서 재구성.
  결정 순서로 구성: Needs you → Changed → New words. 읽기 전용.
- `nba` 라이브 사이클 상태에서 단 하나의 다음 행동. 메뉴는 마비를 재생산한다. 읽기 전용.

**mesh/**
- `prism` (사용자 호출) 한 산출물을 2~5개 독립 렌즈(진짜 구별되는 실패 모드당 1개)로 분해,
  수렴·불일치·"불일치를 해소할 단 하나의 질문" 반환. 평균 금지 — 평균이 이 스킬이 막는 실패.

### 1-6. 인제스트타이거가 paperthin에서 가져갈 설계 원칙

| paperthin 원리 | 인제스트타이거 적용 |
|---|---|
| Trust the artifact, not the author | "검색된다 ≠ 값이 맞다"(ingest-crab 계승) — 진척은 적재 건수가 아니라 **원본까지 역추적 가능한 값의 수** |
| 모든 스킬은 제거한다 | 인제스트는 추가 작업이지만 게이트는 제거형: 미상 보존, 민감 건너뜀, 실패 목록 그대로 — 날조·부풀림 제거 |
| 자기완결 + SSOT | SKILL.md 홀로 이동 가능(게이트 요지 인라인), 도구명은 "바뀌면 여기만" 표 1곳, 버전은 meta.json 1곳 |
| Generic examples | 지시서 예시는 `<파일>:<시트>:<행>` 일반형만 |
| edit-safety | 원본 읽기 전용, 산출물만 생성, 조용한 누락 금지(MISS=실패 버킷) |
| negatives-as-corpus | 실패·건너뜀 목록은 원장에 보존 — 삭제 금지, 다음 배치의 훈련 데이터 |
| Verification 절 필수 | 배치 종료 = 정산 일치 + 역추적 3건 + 색인 갱신 확인을 스킬 안에 명문화 |
| 절제 | 배치 상한 50, 지시 없는 폴더 안 연다, 스키마를 만들거나 바꾸지 않는다 |

## 2. ingest-crab 원본 분석 (gbrinan/soloforce, config/agents/ingest-crab/)

- **정체성**: "내부 검색 코퍼스 적재 담당", 팀=지식관리팀, permLevel=normal, meta.json에
  version 필드 없음.
- **완료 게이트**: 검색됨≠맞음. 진척 = 원본까지 되짚을 수 있는 값의 수.
  정산 버킷: **발견 = 적재 + 실패 + 건너뜀**.
- **수직 루프**(배치당 ≤50): 수집→변환→적재→검증→보고. "현재 도구" 표(변환=kordoc MCP,
  적재/검증=opencrab MCP)와 루프를 분리 — "도구가 바뀌면 표만 고친다".
- **적재 대상 표**: 로컬(기본) / supabase(공유 의도 지시 시, jarvis `corpus` 스키마,
  `config/corpus/0001_corpus_schema.sql`이 유일 기준) / both(로컬 먼저→미러).
- **고객사 자료 절대 금지** — 단일 테넌트 그래프라 사후 격리 불가.
- **공통 게이트는 corpus-gates.md 참조** (재서술 금지 — 실제로 갈라진 전례가 문서에 기록됨).
- content_hash=변환 후 md의 sha256, chunk=문단 단위 500~1000자. 스키마 생성·변경 금지.

### corpus-gates.md 공통 게이트 요지 (원문은 soloforce config/guides/corpus-gates.md)

1. 정산 일치(발견=처리+비처리, 버킷은 지시서가 명시) 2. 역추적 3건(값→원본 좌표)
3. 미상은 `미상`으로(공백·추측 금지) / 하드 룰: 원본 읽기 전용, 날조 금지, 근거·확실도,
   게이트 약화 금지, 3회 실패 시 격리 후 다음으로 / 민감 판정: "의도치 않은 사람에게 보이면
   누가 손해 보나" — 해당하면 내용 옮기지 않고 경로만 보고.

## 3. 멀티포맷 변환 도구 리서치 (2026-08-30 gh api·웹 검증)

| 도구 | 버전(확인일 기준) | 담당 포맷 | 비고 |
|---|---|---|---|
| docling (docling-project) | v2.123.1 (2026-08-28) | pdf, doc/docx, pptx, xlsx, csv, md, html, png(OCR: tesseract/rapidocr `kor`), wav(asr extra) | 표·레이아웃 최강, MIT, pip, Windows OK. **HWP 미지원** |
| markitdown (microsoft) | v0.1.7 (2026-07-29) | 위 대부분 + zip/epub | 얇고 빠른 폴백. 오디오는 온라인 STT라 한국어 오프라인엔 부적합 |
| kordoc (chrisryugj) | v4.12.0 (2026-08-29) | **hwp, hwpx**(+pdf·docx·xlsx) → md | npm CLI+MCP, MIT. ingest-crab이 이미 사용 — 재통합 비용 0 |
| faster-whisper (SYSTRAN) | v1.2.1 | **wav** → text (`language="ko"`) | CTranslate2 int8, CPU 가능, 오프라인 |
| opendataloader-pdf | v2.5.5 (2026-08-25) | (선택) 난이도 높은 스캔 PDF | 한컴 후원, 2026 오픈소스 PDF 벤치마크 1위 |
| unstructured | 0.27.5 | (비채택) | Windows 시스템 의존성 무겁고 md가 아닌 element 모델 |

**최소 툴체인 = 3개**: docling + kordoc + faster-whisper. (선택 4번째: opendataloader-pdf)

## 4. "google wiki skill" — Karpathy LLM-Wiki 패턴 (2026)

쿼리별 RAG 대신 **한 번 컴파일해 두는 상호링크 마크다운 위키**(index + 갱신 로그)를
에이전트가 유지하는 패턴. 확인된 레포:
- kfchou/wiki-skills (180★, 2026-07) / toolboxmd/karpathy-wiki (103★, 2026-08-28)
- praneybehl/llm-wiki-plugin (95★) / 6eanut/llm-wiki (43★)
- 참고: google-gemini/gemini-skills(3.9k★)와 anthropics/skills에는 위키/코퍼스 인제스트
  스킬 없음. anthropics/skills 규약 확인: frontmatter는 `name`+`description` 둘뿐.

**적용(D7)**: 로컬 정본 폴더에 `index.md`(문서별 1행: 제목·출처 경로·해시·적재일·적재처)와
`updates.md`(배치별 갱신 로그)를 유지 — soloforce의 wiki-memory 개념과도 접합.

## 5. Soloforce2 연동 지점 (gbrinan/soloforce2, main, 2026-08-30 확인)

- 에이전트 규약: `config/agents/{id}/meta.json + role-directive.md` (v1과 동일).
  현재 ingest-crab이 동일하게 존재. **"ingestiger" 문자열은 아직 없음** — 신규 도입.
- 스킬 풀: `history/skills/` (부팅 시 `prompts/sub-agents/*.md`에서 1회 시딩,
  `src/server/skills.ts` ensureSkillsSeeded, 라우팅 `index.md` 표: 스킬-알바|설명|owner|키워드).
- 버전 규약 부재(meta.json version 없음, CHANGELOG 없음) → **이 레포가 버전 정본**(D4).
  soloforce2의 `.re0/iteration/{semver-slug}/` 관례와는 별개.
- 로컬 작업본: `C:\Users\user\Documents\soloforce2` (브랜치 v0-final = 원격 main).
