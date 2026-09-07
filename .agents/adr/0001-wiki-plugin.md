# LLM Wiki를 단일 스킬 플러그인으로 배포

상태: 제안. 네 활용 목적은 같은 사실을 읽는 모드이므로 별도 사실 저장소나 네 개의 중복 스킬로 나누지 않는다.

[참고 ADR](https://github.com/mattpocock/skills/blob/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md)의 명시적 skill 경로 목록과 배포/초안 구분을 채택한다. 초기에는 `skills/ingestiger/` 하나만 승격한다. 초안/은퇴 파일은 `skills/` 밖에 둔다. 원본 사실, 런타임 Wiki, 개인 테스트 자료는 배포 패키지에 포함하지 않는다.

Claude 플러그인의 `skills` 배열은 명시 경로만 선언한다. 별도 Codex 네이티브 manifest는 이 제안의 범위에 넣지 않는다. 참고 ADR의 Codex 제약은 그 문서의 검증 당시 관찰이며 현재 런타임을 직접 시험한 결론은 아니다. 범용 skill 폴더 설치는 유지한다. symlink나 수동 중복 스킬 디렉터리로 배포 집합을 만들지 않는다.

역할 지시서의 상대 경로는 원본 트리 배치와 함께 보존한다. 호스트 배포를 위해 내용을 복제·재서술하지 않는다. 버전 정본은 Claude manifest, 에이전트 메타는 검사로 동기화되는 파생 배포물로 정한다. 향후 manifest 생성 작업을 자동화할 수 있다.
