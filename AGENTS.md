# IngesTiger 기여 지침

역할은 [역할 지시서](agent/role-directive.md), 실행 절차는 [스킬](skills/ingestiger/SKILL.md), 데이터 의미는 [계약](skills/ingestiger/references/contracts.md)이 관리한다. 사용자 안내는 README에 둔다. 현재 개발 상태와 미검증 범위는 [제안서](docs/proposal.md)를 읽는다.

`skills/`에는 배포할 스킬만 둔다. 런타임 참조는 각 스킬 폴더 내부에 묶는다. `archive/`는 과거 증거이며 현재 실행 지침이 아니다. 실제 기업 자료, 추출물, 테스트 결과는 이 저장소 바깥에서 관리한다.

변경은 하나의 사실을 여러 곳에 복사하지 않고 그 정본에서 시작한다. 자동 생성 뷰는 다시 생성한다. 플러그인 버전 정본은 `.claude-plugin/plugin.json`이며 `agent/meta.json`은 배포 메타데이터 뷰다. 배포 전 `python3 scripts/validate_layout.py`를 실행한다.
