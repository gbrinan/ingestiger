# progress.md — 작업 로그 (오래된 것부터)

## 2026-08-30 — 세션 1: 참조 수집 → 설계 → v0.1.0 작성

- paperthin(LilMGenius, v0.17.4) 클론 후 CLAUDE.md·README·docs/invocation.md와
  스킬 28개 SKILL.md 전수를 라인 바이 라인 정독. 결과는 findings.md §1.
- soloforce `config/agents/ingest-crab/`(role-directive.md, meta.json)과
  `config/guides/corpus-gates.md` 전문 확보. 결과는 findings.md §2.
- 멀티포맷 변환 도구·"google wiki skill"(Karpathy LLM-Wiki 패턴)·soloforce2 연동 지점을
  gh api·웹으로 검증 조사. 결과는 findings.md §3~5.
- 설계 결정 D1~D8 확정 (tasks.md).
- 산출물 작성:
  - `skills/ingestiger/SKILL.md` — 절차 정본 (Goal/저장 계층/Workflow/라우팅 표/Rules/Verification)
  - `agent/role-directive.md` — ingest-crab 후속 지시서 (절차는 스킬 참조로 위임)
  - `agent/meta.json` — version 0.1.0 도입, supersedes=ingest-crab
  - `README.md`, `docs/soloforce2-integration.md`
- 검증(Phase 5): 콜드리드(shower식) 서브세션 실행 + 정산 규칙 자기점검 → 결과 아래 표.

### 테스트/검증 결과

| 검증 | 기대 | 실제 | 상태 |
|---|---|---|---|
| 콜드리드: 맥락 0 독자가 SKILL.md만으로 루프 실행 가능 | 가능 | 판정 "손질 필요" → 지적 3건+α 반영: "적재" 단일 정의(로컬+코퍼스 성공), 저장소 식별 절차·청킹 규칙을 적재 단계로, 미러 검증 드라이브/DB 분리, 격리=실패 버킷 사유 `격리`, 문서id(원본 해시)/content_hash(변환 해시) 구분, 좌표 `<파일>:<위치>` 일반화, 배치 50 초과=다음 배치 이월, soloforce 판별=corpus-gates.md 존재 | ✅ |
| 정산 규칙 무모순: 발견=적재+실패+건너뜀, 미러 별도 버킷 | 무모순 | 수정 후 Goal(버킷 정의)·Workflow·Verification·출력 형식 4곳 일치. 색인 정합은 "행 증가분=발견 수(상태 열 포함)"로 재정의 | ✅ |
| 도구명 SSOT: 라우팅 표 밖에 도구명 없음 | 표 1곳 | README 다이어그램에 요약 재등장 → "SKILL.md가 정본" 명시로 처리 | ✅ |
| meta.json version = git tag | v0.1.0 | v0.1.0 | ✅ |

## 2026-08-31 — 세션 2: hate → first_nail 실배치 → v0.2.0

- `/hate` 판정: "잘 쓰인 문서 = 작동하는 스킬" 가정에 바깥 진실 0 — first_nail로
  다운로드 폴더 포맷별 대표 14건 실배치 실행.
- 배치 결과(상세 findings.md §6): 발견 14 = 적재 9 + 실패 4 + 건너뜀 1.
  적재 9건 opencrab(chromadb+mongodb), 역추적 3건 적중(35,720개·560,000명·5.0H),
  스모크 질의 3/3 top-1. 로컬 정본 `Documents\ingestiger-corpus\ingestiger\`.
- 베스트 프랙티스 리서치(GitHub·웹, URL 검증): LlamaIndex 멱등성, docling confidence,
  구조 청킹, 골든 질문 평가, whisper 신뢰도, Presidio PII 레인, 변환기 버전 조건.
- SKILL.md v0.2.0 클린 재작성(부풀리기 아닌 접어 넣기): 정산 5버킷(+격리·보류),
  매직바이트 판별, 품질 게이트, 멱등성 규칙, 문서별 스모크 질의(축별 확인),
  STT 신뢰도 게이트·mm:ss 좌표, 구조 청크 우선, 라우팅 표 kordoc 우선 재편,
  드라이브 미러 도구 행·레거시 doc 행 신설. meta.json 0.2.0 (새 능력 = minor).
- 미해결 3건(CMap pdf 복구 / 레거시 doc 체인 / 한국형 PII 스택)은 별도 리서치로 진행.

### 세션 2 검증 결과

| 검증 | 기대 | 실제 | 상태 |
|---|---|---|---|
| 실배치 정산 | 합 일치 | 14 = 9+4+1 | ✅ |
| 역추적 3건 | 원본 좌표 도달 | hwpx 제2조 표 · csv 7행 · pptx 슬라이드1 | ✅ |
| 스모크 질의 | top-k 적중 | 3/3 top-1 (하이브리드) — BM25 단독 축은 인덱스 0 발견 | ✅ |
| 민감 게이트 | 실데이터 발화 | 가맹점키·지급액 xlsx → 건너뜀 처리 | ✅ |
| v0.2.0 정산 무모순 | 5버킷 정의·Workflow·Verification·출력 형식 일치 | 일치 | ✅ |

## 재부팅 체크 (5문항 — 새 세션이 여기서 이어받을 때)

1. **북극성은?** tasks.md 첫 절. ingest-crab → 인제스트타이거 재설계 + Soloforce2 연동.
2. **지금 단계는?** tasks.md "현재 단계" 참조.
3. **정본이 어디인가?** 절차=skills/ingestiger/SKILL.md, 버전=agent/meta.json,
   발견=findings.md, 결정=tasks.md 결정 기록.
4. **하지 말아야 할 것은?** 게이트 재서술(corpus-gates.md 참조), soloforce2 쪽 직접 수정,
   스키마 생성·변경, 태그 없는 복사.
5. **다음 행동은?** tasks.md의 첫 번째 미체크 항목.
