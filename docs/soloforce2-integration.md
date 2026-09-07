# 기본 실행 + Soloforce2 연동 설계

결정: 처리 엔진과 데이터 계약은 하나로 유지하고, 실행·권한·저장 연결만 호스트 어댑터로 바꾼다. 기본 실행도 로컬 + Google Drive를 지원한다. Soloforce2는 직원 위임·도구 연결·진행/승인 UI를 제공한다. RAG/BM25/임베딩은 이 경로의 의존성이 아니다.

설계 단계다. Soloforce2 코드, OAuth 설정, 실제 Drive 파일은 변경하지 않았다. 아래 새 도구/API/경로는 모두 제안이며 기존 기능과 구별한다.

## 읽은 코드와 확인 범위

2026-09-07, 로컬 checkout `/Users/anank/Documents/ChatGPT/Soloforce2/repo`, origin `https://github.com/gbrinan/soloforce2.git`, HEAD `153a3db85ebd431c3afae186920bddaa3ffb79d9`. 일반 네트워크에서는 DNS 실패했으나, 2026-09-07 승인된 네트워크 경로에서 `git ls-remote https://github.com/gbrinan/soloforce2.git HEAD`를 재실행해 원격 HEAD가 위 로컬 HEAD와 일치함을 확인했다. 조사 대상 src/packages/tools/config의 tracked 변경도 없었다. 기존 미추적 사용자 설정은 읽거나 수정하지 않았다. 저장소 전체 정독이 아닌 연동 경로 중심 코드 조사다.

| 실제 코드 | 확인한 동작 | 설계에 미치는 영향 |
|---|---|---|
| src/agent-registry.ts:8, 141, 184, 255 | WorkerAgentDef, runtime/권한/MCP 설정, config/agents/<id>/meta.json 자동 발견, 역할을 history/agents/<id>/wiki에 시드/재동기화 | 역할 파일만 복사하면 끝이 아님. 메타 필드와 배포 경로/갱신 충돌 검증 필요 |
| src/adapters/index.ts:1; types.ts:9 | claude-code/codex-cli/antigravity-cli 레지스트리, execute(config, taskId, prompt, options), 미지정 adapter 폴백 | 호스트별 계약 시험 필요. 설치되어 있다는 이유로 같은 도구 지원을 가정하지 않음 |
| src/agent.ts:190; src/adapters/codex-cli.ts:74 | 도구 권한을 SafeFS 도구로 매핑, Codex 격리 설정에서 safefs 등록 | 추가 MCP가 모든 런타임에 자동 연결된다는 가정 금지 |
| src/server/mcp-registry.ts:232 | 할당된 서버만 해석, allow/approval 분류 | Wiki MCP를 등록·할당하되 런타임별 실제 주입 검증 |
| src/mcp/safefs-server.ts:762 | DelegateTask는 ACK 반환 후 task-notification으로 결과 전달, taskId/after/cwd 등 | 배치 처리를 비동기 작업으로 연결. ACK를 처리 완료로 간주하지 않음 |
| src/server/worker-pty.ts:107 | 해당 PTY 경로는 어댑터 레지스트리에 연결되지 않았다는 주석 | 파일 존재만으로 운영 실행 경로라고 판단하지 않음 |
| src/server/google-readonly-provider.ts:12 | drive.readonly scope | Drive 출력용 쓰기 provider/연결 권한 추가 필요 |
| src/server/google-readonly-routes.ts:41 | Drive import가 corpus.import로 연결되고 corpus 미설정이면 실패 | 다운로드/권한검사를 공통 source provider로 분리하고 Wiki import 별도 연결 |
| src/mcp/apps-ai-server.ts: AI_TOOLS | 앱별 명시 도구 목록/게이팅과 HTTP 프록시 | Wiki 결과를 context packet으로 전달. 기존 앱 기능을 전부 자동 실행하지 않음 |

코드 근거는 위 commit의 경로/줄 기준이다. 원격 HEAD 일치는 이번 확인 시점 기준이며 향후 갱신 후 다시 대조해야 한다.

## 공통 구조

```text
             기본 호스트                    Soloforce2
        CLI + 현재 대화의 LLM         직원 등록 + Job + 실행 adapter
                   \                      /
                 HostBridge (신규 계약)
        identity / scope / task / capabilities / receipts
                            |
                  IngesTiger 공통 코어
             가져오기 → 분해하기 → 저장하기
                |          |           |
           source reader  LLM 호출    검증 / 정본 변경
           Kordoc 등      호스트 위임    |
                             LocalStore + durable outbox
                                         |
                                    DriveStore
                                         |
                            같은 판의 원격 snapshot
```

공통 코어는 Soloforce2 내부 모듈을 import하지 않는다. 우선 기존 Python 스크립트를 파일 요청/응답 프로토콜로 감싼다. 향후 구현 언어 변경에도 스키마/오류/판 계약을 유지한다. 기본 호스트에 위임 기능이 없으면 현재 대화가 LLM 작업을 순차 수행한다. Drive 쓰기 능력이 없으면 로컬 작업 후 drive_pending을 반환하며 완전 저장을 주장하지 않는다.

## 공통 호출 계약: 신규 설계

모든 요청은 `schema_version, request_id, workspace_id, org_id, project_id, operation, payload_ref, expected_revision`을 가진다. principal과 허용 범위는 요청문에서 신뢰하지 않고 서버/호스트의 인증 문맥에서 결합한다. 본문 전체 대신 승인된 artifact 참조와 해시를 전달한다.

결과는 `request_id, task_id, stage, state, artifact_refs, coverage, validation, local_revision, drive_revision, sync_state, errors`다. LLM 문장이나 작업 완료 메시지만으로 저장 성공을 결정하지 않는다. receipt는 실제 저장/검증 함수가 생성한다.

| 신규 기능명 | 역할 | 쓰기 경계 |
|---|---|---|
| wiki.capabilities | 형식/도구/읽기/쓰기/위임 가능 상태 | 읽기. configured와 검증된 기능 구별 |
| wiki.ingest | 범위 확정 원본 등록과 읽기용 표현 확보 | 승인된 원본 저장·배치 생성 |
| wiki.prepare | 처리 단위와 LLM 요청 생성 | 작업판만 |
| wiki.submit | 응답 스키마·인용 검사, 의미 검토 상태 기록 | 후보만 |
| wiki.commit | 승인 범위/의미 검토/expected revision 검증 후 정본 반영 | 단일 writer·정본 전환 |
| wiki.read | 목차/패턴/ID로 필요한 지식과 근거 packet 반환 | 접근 범위 제한 읽기 |
| wiki.sync | 지정된 판의 로컬→Drive 전달/재개 | 연결된 folderId만, 공개 권한 변경 없음 |
| wiki.status | 단계·보류·실패·저장 판 조회 | 읽기 |

위 이름은 새 API/MCP 설계다. 일반 CLI와 Soloforce2 MCP wrapper는 같은 operation을 호출한다. SafeBash만 가능한 환경에서는 제한된 명령 wrapper로 같은 JSON 계약을 사용한다. 임의 셸 명령이나 Drive credential을 모델에 넘기지 않는다.

## Soloforce2에 필요한 변경

### 1. 설치와 에이전트 등록

IngesTiger 배포 bundle은 원형으로 버전별 보관한다. Soloforce2용 installer가 `config/agents/ingestiger/meta.json`과 역할 진입문을 생성한다. 원본 역할은 bundle에만 두고 생성 진입문은 bundle 버전/경로를 참조한다. 기존 상대 링크를 history wiki 위치에서 그대로 해석하면 깨지므로 설치 root를 검증해 진입 경로를 생성해야 한다.

meta 필드는 실제 WorkerAgentDef로 매핑한다. 회사 자료 root와 자기 산출물만 read/writePaths에 배정하고 Python/Kordoc wrapper에 필요한 실행 권한만 추가한다. Bash 기본 미부여 상태에서 설명만 추가해 파서 실행을 기대하지 않는다. 기존 사용자 편집 역할이 있으면 무조건 덮어쓰지 않고 충돌과 이전판을 보존한다.

### 2. 도구 연결과 런타임

`src/server/mcp-registry.ts`에 Wiki MCP를 등록하고 해당 직원에 할당하는 설치 경로가 필요하다. `src/agent.ts`, `src/adapters/codex-cli.ts` 등 실제 실행 경로에서 MCP가 주입되는지 확인한다. 현재 Codex의 safefs 등록만으로 추가 서버 지원을 보장하지 않는다. 우선 제한된 SafeBash wrapper 경로도 제공하되 두 경로의 결과 계약을 동일하게 시험한다.

Kordoc은 HWP/HWPX의 기본 source adapter다. 호스트에서 실행 가능한 경로/버전 확인 후 사용하며 등록만으로 실파일 변환 성공을 보고하지 않는다. Graphify 연결은 선택 사항이며 첫 통합의 의존성으로 넣지 않는다.

### 3. 직원 위임과 결과 회수

마이크루가 IngesTiger 작업을 위임하면 ACK의 job/task ID를 공통 batch ID와 연결한다. 원문 묶음마다 prepare → LLM response → 검증으로 진행하고 job cancel/timeout 때 이월 단위를 남긴다. 세션 재실행은 검증된 요청 해시로 재사용 여부를 결정한다.

컨설팅·교육·서비스 제작·일반 에이전트는 위임 설명이나 전체 원본 대신 wiki.read의 scope-filtered packet을 받는다. 앱별 도구는 필요한 산출물 제작 단계에서 선택한다. 광고 게시·메일 발송·최종 주문 같은 외부 실행 권한은 지식 전달에 따라 생기지 않는다.

### 4. Drive 읽기 경로 분리와 쓰기 추가

현재 Google readonly provider의 권한/원본 획득 기능을 재사용하되 corpus.import에 붙은 라우트를 그대로 Wiki 엔진으로 사용하지 않는다. 공통 source reader를 분리하고 새로운 Wiki import 라우트를 둔다. 기존 corpus 경로는 기존 소비자를 위해 유지한다.

새 Drive write provider + 목적 폴더 매핑 + outbox/receipt 저장이 필요하다. 기존 readonly 연결은 변경하지 않고 필요한 쓰기 scope를 연결 UI에서 추가 동의받는다. 연결 상태·owner 검사·비밀 저장 구현을 재사용할 수 있지만 쓰기 권한과 단절/재개는 새로 검증한다. 상세 정본/복제/충돌 정책은 [저장 계약](../skills/ingestiger/references/storage.md)이 관리한다.

### 5. 결과 상태와 의미 검증

Job success와 wiki current 승인, Drive sync 완료를 분리해서 UI에 표시한다. 로컬 성공+Drive 실패는 부분완료다. Semantic review는 원문과 후보를 대조한 `supported / contradicted / insufficient` 결과와 검토 근거를 기록한다. 독립 검토자는 구조 검사와 다른 경로로 원문을 읽어야 한다. 같은 모델의 자기 검토만으로 정확성이 보장된다고 주장하지 않는다.

원문 인용을 유지한 채 '사람이 주문'을 '자동 주문'으로 뒤집는 이전 반례는 필수 음성 사례다. 해당 후보가 current에 반영되면 통합 게이트 실패다. 검토가 없으면 후보까지만 저장/복제한다.

## 최소 수직 통합과 게이트

첫 실험은 기존 증권사 D31을 사용한다. 실제 Drive의 비공개 테스트 폴더 하나에 8개 후보와 원문 근거/manifest를 같은 판으로 저장하고 다시 내려받아 비교한다. 전체 기업 자료를 먼저 업로드하지 않는다.

기본 호스트와 Soloforce2에서 동일 입력/해석을 사용해 범위·인용·상태·저장 내용 계약을 비교한다. 자연어 표현의 바이트 일치가 아니라 조건 보존과 판/근거 연결이 기준이다. 이후 다음 장애를 투입한다.

- 의미 반전 후보: 인용이 진짜여도 current 반영 거부/보류.
- Drive 단절/권한 회수/응답 유실: local_saved 유지, 중복 정본 없이 재개.
- 부분 원격 업로드: 원격 reader는 이전 완성판만 읽음.
- 동일 요청 재시도: 후보/동기화 키 중복 방지.
- 다른 기업/다른 folderId 요청: 이름·본문·건수 노출 없이 거부.
- Drive 외부 수정/오래된 base revision: conflict, 자동 last-write-wins 금지.
- 이미지 레퍼런스: 양쪽 바이트 일치, 분석 호출 0.
- HWP: Kordoc 실제 샘플로 본문/표/좌표 검증. CLI 미설치는 명시 보류.

이 테스트를 통과하기 전 '기본도 되고 Soloforce2도 된다'는 구현 완료 표현은 사용하지 않는다. 현재 설계는 양쪽 호스트를 지원하기 위한 변경 목록이며 실제 양쪽 통합·Drive 업로드·OAuth 동의는 수행하지 않았다.

## 원격 재확인에 따른 구현 분할

원격 HEAD 153a3db 기준 검색 범위 src/apps/packages/tools에서 Drive upload endpoint, drive.file scope, Drive sync 상태 구현을 찾지 못했다. GoogleReadonlyProvider의 실제 인터페이스도 metadata/readFile까지만 제공한다. 쓰기 기능이 이미 있다는 전제로 연결하지 않는다.

1. **쓰기 provider와 권한 연결**: 신규 google-drive-write-provider.ts에 목적 폴더 검사, 파일 생성, resumable upload, 원격 읽기 검증을 구현한다. readonly provider를 그대로 유지하고 write capability를 별도로 선언한다. 기존 scope를 조용히 교체하지 않는다.
2. **동기화 장부**: 신규 wiki-sync-store/service에서 revision별 outbox, fileId 매핑, content hash, 시도/다음 재시도/오류, local/Drive 상태를 영속화한다. 프로세스 메모리만으로 동기화를 관리하지 않는다.
3. **호스트 API와 도구**: wiki.sync/status를 공통 코어에 연결하고 Soloforce2의 인증/owner/project 경계에서 감싼다. 계정 연결 UI에는 읽기/쓰기 가능 여부와 목적 폴더, 작업 UI에는 로컬 저장 판/Drive 판/보류 원인을 표시한다.
4. **완료 게이트**: 동일 revision의 실제 업로드→다시 읽기→해시 대조, 응답 유실 재시도, 권한 철회, 중간 종료 복구를 통과해야 한다. 설정 저장 또는 파일 생성 응답만으로 synced를 만들지 않는다.

이 분할은 구현 계획이며 이번 재확인에서는 Soloforce2 원본 코드를 수정하거나 OAuth/Drive 쓰기를 실행하지 않았다.
