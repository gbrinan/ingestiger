# tasks.md — 인제스트타이거(IngesTiger) 재설계

> 파일 기반 플래닝 워크플로(ahastudio/til `ai/file-based-planning-workflow.md`)를 따른다.
> 이 파일은 "무엇을 하는가"만 담는다. 발견은 `findings.md`, 작업 로그는 `progress.md`.

## 북극성 (North Star)

soloforce의 `ingest-crab` 에이전트를 **paperthin 철학**(Trust the artifact, not the author /
모든 스킬은 제거한다 / 자기완결 / 절제)으로 재설계하여, pdf·hwp·doc·md·txt·png·pptx·xlsx·csv·wav를
**로컬 저장 → 구글 드라이브 또는 선택 DB 저장** 파이프라인으로 코퍼스/RAG에 적재하는
**인제스트타이거** 스킬을 만들고, Soloforce2의 ingestiger로 버전 관리하며 연동한다.

## 현재 단계

Phase 6 — 배포·연동 (진행 중: push·태그까지 완료, Soloforce2 반영은 다음 세션)

## 단계

- [x] **Phase 1 — 참조 수집**
  - [x] paperthin 전체 스킬 28개 라인 바이 라인 정독 (CLAUDE.md, README, invocation.md 포함)
  - [x] soloforce `config/agents/ingest-crab/role-directive.md`, `meta.json` 원본 확보
  - [x] soloforce `config/guides/corpus-gates.md` 전문 확보
  - [x] TIL 파일 기반 플래닝 워크플로 확보 (이 레포 구조의 근거)
- [x] **Phase 2 — 리서치**
  - [x] 멀티포맷 변환 도구 조사 (markitdown, docling, unstructured, opendataloader, HWP 계열, whisper 계열)
  - [x] "google wiki skill" 계열 최신 레포 확인 (Karpathy LLM-Wiki 패턴)
  - [x] Soloforce2 연동 지점(디렉터리·버전 규약) 파악
- [x] **Phase 3 — 설계**
  - [x] paperthin 철학 → 인제스트타이거 설계 원칙 도출 (findings.md에 기록)
  - [x] 저장 파이프라인 확정: 로컬(정본) → 미러(구글 드라이브 | 선택 DB), 도구 폴더에서 확인 가능
  - [x] 포맷별 변환 라우팅 표 확정 (findings.md)
- [x] **Phase 4 — 스킬 작성**
  - [x] `skills/ingestiger/SKILL.md` (paperthin 해부학: Goal/Workflow/Rules/Verification)
  - [x] `agent/role-directive.md` (인제스트타이거 역할 지시서 — ingest-crab 후속)
  - [x] `agent/meta.json` (id=ingestiger, 이름=인제스트타이거, version 필드 도입)
  - [x] `README.md` (사람용 정문)
- [x] **Phase 5 — 검증**
  - [x] 콜드리드(shower식): 판정 "손질 필요" → 지적 반영 후 정산·색인·미러 검증 정합 (progress.md 표)
  - [x] 정산 게이트 자기검증: 발견 = 적재 + 실패 + 건너뜀 규칙이 스킬 안에서 모순 없는가
- [ ] **Phase 6 — 배포·연동**
  - [x] Soloforce2 연동 가이드(`docs/soloforce2-integration.md`) 작성 — 버전 고정 방식 포함
  - [ ] main에 커밋·push, v0.1.0 태그
  - [ ] Soloforce2 로컬(`C:\Users\user\Documents\soloforce2`)에 config/agents/ingestiger 반영 (다음 세션)

## 결정 기록

- **D1** 레포 구조는 TIL 3-파일 패턴(tasks/findings/progress)을 루트에 둔다.
- **D2** 스킬 문서 언어는 한국어 — ingest-crab 원본과 Soloforce2 지시서 관례를 따른다.
  단, paperthin detool 원칙에 따라 도구명은 "바뀌면 여기만 고친다" 표 한 곳에만 고정.
- **D3** 이름: ingest-crab → **ingestiger / 인제스트타이거**. paperthin 명명 규칙
  ("이름은 반사신경을 부른다, 낯선 이가 절반은 추측 가능해야")에 맞는 압축 합성어.
- **D4** 버전 관리: `agent/meta.json`의 `version`(semver)이 정본, git tag `vX.Y.Z`와 일치.
  Soloforce2에는 version 필드 관례가 없으므로 **이 레포가 버전의 유일한 출처**가 된다.
  판정 기준은 paperthin과 동일 — 크기가 아니라 종류(수정=patch, 새 능력=minor, 대체 없는 제거=major).
- **D5** 저장 계층: 로컬이 항상 정본(1차), 구글 드라이브/선택 DB는 미러(2차).
  ingest-crab의 "로컬 기본, 지시로만 변경" 원칙 계승. 미러 실패는 적재 실패가 아니라 미러 실패로 따로 센다.
- **D6** 변환 도구 라우팅: 문서·이미지·표는 문서 변환기(docling 계열), HWP/HWPX는 한국 문서
  변환기(kordoc), 음성은 오프라인 STT(faster-whisper). 정본 표는 SKILL.md 한 곳에만 둔다.
- **D7** 코퍼스는 검색 인덱스에만 넣지 않고 **위키형 색인**(Karpathy LLM-Wiki 패턴: index.md +
  갱신 로그)을 로컬 정본 폴더에 함께 유지한다 — 사람이 폴더만 열어도 무엇이 들어왔는지 보인다.
- **D8** corpus-gates.md(공통 게이트)는 재서술하지 않고 참조한다 — 그 문서 자체가 중복 금지를
  명시한다. 단, 이 레포는 soloforce 밖에서도 살아야 하므로(스킬 자기완결) SKILL.md에는
  게이트의 **이름과 한 줄 요지**만 싣고, soloforce 안에서는 원문이 우선함을 명시한다.

## 미해결 질문

- Q1 (해결): 선택 DB 기본 후보 — supabase `corpus` 스키마(ingest-crab 계승)를 기본 옵션으로 유지.
  다른 DB는 호출자가 적재처 표에 행을 추가하는 방식으로 확장 (스킬은 표만 정의).
- Q2 (해결): Soloforce2 수용 구조 = `config/agents/ingestiger/` (meta+role-directive),
  스킬 본문은 `history/skills/` 풀에 등록. 상세는 docs/soloforce2-integration.md.

## 오류 기록

- E1: 작업 세션의 Write 도구가 워크트리에 훅 스크립트 부재로 오류 → 본 저장소의
  `.claude/hooks/moai/`를 워크트리로 복사해 훅을 복구. 이후 훅의 정상 동작(프로젝트 밖 쓰기
  차단)에 따라 staging→cp 패턴으로 작성.
