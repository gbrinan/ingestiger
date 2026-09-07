# IngesTiger

많은 문서를 기업·프로젝트별 LLM Wiki로 정리하고, 에이전트가 부서별 업무 니즈와 근거를 빠르게 찾도록 하는 스킬입니다.

사실과 요구사항은 한 정본에 두고, 부서·도메인·공통 과제·활용 목적별 목차에서 참조합니다. 새 문서가 들어오면 출처와 변경 영향을 비교해 기존 지식에 반영합니다.

여러 기업의 비슷한 업무도 허용된 접근 범위 안에서 패턴별로 묶어 읽습니다. 각 기업의 세부 조건과 근거는 유지합니다. Wiki와 별도로 [ASCII ERD와 짧은 구성 요약](skills/ingestiger/references/structure.md)을 만듭니다.

현재는 **개편 제안판**입니다. 실행 지침과 데이터 계약, 플러그인 폴더 구성을 제공합니다. 대량 자동 변환, 갱신 엔진, 다중 사용자 권한관리의 구현 완료를 뜻하지 않습니다.

- [개편 제안과 구현 순서](docs/proposal.md)
- [역할 지시서](agent/role-directive.md)
- [실행 스킬](skills/ingestiger/SKILL.md)
- [기존 연동에서 전환하기](docs/soloforce2-integration.md)
- [구조 결정](.agents/adr/0001-wiki-plugin.md)

저장 대상은 로컬 + Google Drive다. [두 저장소 계약](skills/ingestiger/references/storage.md)과 [기본 실행/Soloforce2 연동 설계](docs/soloforce2-integration.md)를 제공한다. Drive 쓰기·동기화와 호스트 통합은 아직 설계 단계다.

## 사용 예

“이 문서 묶음을 A기업 B프로젝트의 Wiki로 정리하고, 디자인·마케팅의 공통 니즈를 보여줘.”

“이 피드백을 기존 니즈에 대조해 변경안을 만들고, 교육과 서비스 명세에 미치는 영향을 알려줘.”

“이 프로젝트의 SCM 요구사항과 원문 근거만 읽어 일반 에이전트용 맥락을 만들어줘.”

## 설치 범위

플러그인 선언은 `.claude-plugin/plugin.json`에 있으며 `skills/ingestiger`만 노출합니다. 범용 스킬 설치에서는 해당 폴더를 `references/`와 함께 복사합니다. Claude Code 실제 설치 검증은 아직 수행하지 않았습니다. 원격 저장소에 이 제안판을 올리기 전에는 GitHub 설치가 새 판을 제공하지 않습니다.

실제 기업의 원본과 Wiki는 플러그인 저장소 밖의 지정 작업공간에 저장합니다.

## 스크립트와 LLM

[실행 분담](skills/ingestiger/references/execution.md) · [운영 명령](skills/ingestiger/references/runbook.md): XLSX 구조 추출·LLM 요청 준비·응답 검증·후보 목차 생성을 스크립트로 실행한다. 니즈 의미 분석은 호스트 LLM을 사용한다. Graphify는 설계 참고이며 아직 연동하지 않았다.

[Golden sample 시작 절차](skills/ingestiger/references/golden-samples.md): 이미지는 원본과 최소 정보만 보관하고 필요할 때 참조한다.

[대용량 발표자료 처리](skills/ingestiger/references/large-decks.md): Keynote/PPTX 컨테이너·매체 구성을 먼저 확인하고 슬라이드 단위로 읽는다.
