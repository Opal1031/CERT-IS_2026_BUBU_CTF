# WEB-01 · 관리자 전용 버튼

공용 웹 인스턴스형 문제입니다. 참가자에게는 `handout/WEB-01.zip`을 제공하고, 이 폴더의 서버 코드는 운영진이 별도 인스턴스로 실행합니다.

## 실행 계약

- Docker 빌드 위치: 이 폴더 (`Dockerfile`)
- 컨테이너 내부 포트: TCP `3000`
- 필수 환경변수: `FLAG` (`BUBU{...}` 형식). 실제 정답은 저장소에 넣지 않고 운영 환경에서 주입합니다.
- 상태 확인: `GET /healthz` → `ok`
- 공개 `GET /flag.txt`에는 형식 예시만 있습니다.

로컬 동작 확인용 명령입니다. 예시 플래그는 대회 정답이 아닙니다.

```sh
FLAG='BUBU{example_only}' docker compose up --build -d
curl -fsS http://127.0.0.1:3001/healthz
docker compose down
```

`compose.yaml`은 기본적으로 호스트의 `127.0.0.1:3001`에 연결합니다. 운영 환경에서는 웹 문제에 별도 공개 주소를 연결하고, 필요하면 `WEB_EASY_BIND_IP`와 호스트 포트 매핑을 조정하세요. CTFd와 문제 웹사이트는 서로 다른 호스트명으로 제공하는 것을 권장합니다.

## CTFd 등록 정보

- 분야: `Web`
- 참가자 파일: `handout/WEB-01.zip` 하나 (`README.md`, 가짜 `flag.txt` 포함)
- 정답: 인스턴스에 주입한 `FLAG`와 동일한 Static flag
- Connection Info: 운영진이 배정한 웹 인스턴스 URL

대회 전에는 CTFd 문제를 숨김 상태로 두고, 인스턴스와 파일 다운로드를 참가자 관점에서 확인한 뒤 공개합니다.
