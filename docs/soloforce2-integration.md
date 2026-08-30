# Soloforce2 연동 가이드

인제스트타이거를 gbrinan/soloforce2에 붙이는 절차. 확인 기준일: 2026-08-30 (soloforce2 main).

## 연동 지점 (soloforce2의 기존 규약)

| soloforce2 표면 | 이 레포의 원천 | 방법 |
|---|---|---|
| `config/agents/ingestiger/meta.json` | `agent/meta.json` | 그대로 복사 |
| `config/agents/ingestiger/role-directive.md` | `agent/role-directive.md` | 그대로 복사 |
| `config/agents/ingestiger/skills/SKILL.md` | `skills/ingestiger/SKILL.md` | 그대로 복사 (role-directive가 "skills/ingestiger/SKILL.md"로 참조하므로 상대 경로 유지) |
| `history/skills/index.md` (스킬-알바 라우팅 표) | — | 1행 추가: `ingestiger \| 다포맷 원본을 코퍼스로 적재 \| ingestiger \| 인제스트, 적재, 코퍼스, RAG, hwp, pdf` |

`ingest-crab`은 당분간 나란히 두고, 인제스트타이거가 배치 3회 이상 게이트를 통과하면
ingest-crab을 은퇴시킨다 (paperthin negatives-as-corpus: 삭제가 아니라 보존 — 폴더는
남기고 라우팅 표에서만 뺀다).

## 버전 관리 (이 레포가 정본)

soloforce2에는 에이전트 버전 규약이 없다 (meta.json에 version 필드 없음, CHANGELOG 없음).
따라서:

1. **정본**: 이 레포 `agent/meta.json`의 `version` + 같은 값의 git tag `vX.Y.Z`.
2. **고정(pin)**: soloforce2로 복사할 때는 반드시 태그 시점의 파일을 쓰고,
   soloforce2 쪽 meta.json의 `version`·`source` 필드를 그대로 유지한다 —
   soloforce2 안에서 어떤 판이 돌고 있는지 meta.json만 열어도 알 수 있다.
3. **갱신**: 이 레포에서 수정 → 태그 → soloforce2에 재복사. soloforce2 쪽에서 직접
   고치지 않는다 (고치면 갈라진다 — 급하면 여기에 먼저 반영하고 태그 후 복사).
4. **판정 기준**: 수정=patch, 새 능력(포맷·적재처 추가)=minor, 대체 없는 제거=major.

## 복사 명령 (로컬 작업본 기준)

soloforce2 로컬 체크아웃이 `C:\Users\user\Documents\soloforce2`일 때:

```bash
cd /c/Users/user/Documents/soloforce2
mkdir -p config/agents/ingestiger/skills
V=v0.1.0  # 고정할 태그
git -C /path/to/ingestiger checkout $V
cp /path/to/ingestiger/agent/meta.json            config/agents/ingestiger/meta.json
cp /path/to/ingestiger/agent/role-directive.md     config/agents/ingestiger/role-directive.md
cp /path/to/ingestiger/skills/ingestiger/SKILL.md  config/agents/ingestiger/skills/SKILL.md
```

복사 후 확인: `config/agents/ingestiger/meta.json`의 `version`이 의도한 태그와 같은가.

## 의존 문서 (soloforce2 쪽에 이미 있어야 하는 것)

- `config/guides/corpus-gates.md` — 공통 게이트 (v1에서 승계 필요 시 soloforce에서 복사)
- `config/guides/output-saving.md`, `config/guides/report-style.md` — 산출물·문체 규칙
- 코퍼스 저장소 MCP와 변환기 MCP 배선 (`config/mcp-base.json`) — 도구 라우팅 표는
  SKILL.md가 정본이므로 서버 이름이 다르면 SKILL.md 표만 고친 patch를 태그한다
