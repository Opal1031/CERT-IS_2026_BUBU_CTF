# WEB-02 · 행사 부스 정렬기

정답과 풀이: 운영진용 [`operator/WEB-02.md`](../operator/WEB-02.md)

## 웹앱 배포

- 이 폴더의 `Dockerfile`로 빌드합니다. 실행 시 실제 플래그를 `FLAG` 환경변수로 주입합니다.
- 컨테이너 내부 포트: `3000` · 상태 확인: `GET /healthz` → `ok`
- `compose.yaml`은 로컬 테스트용으로 `127.0.0.1:3002`에 연결됩니다. 대회에서는 참가자가 접속할 공개 주소를 연결해야 합니다.

로컬 확인:

```sh
FLAG='BUBU{example_only}' docker compose up --build -d
curl -fsS http://127.0.0.1:3002/healthz
FLAG='BUBU{example_only}' docker compose down
```

## CTFd 등록

- 문제명: `행사 부스 정렬기` · 분야: `Web` · 유형: `Standard`
- 점수: 운영진 확정 필요
- 문제 설명:

  > 행사 안내 사이트의 부스 목록에는 정렬 기능이 있습니다. 운영진이 숨겨 둔 플래그를 찾아보세요.
  >
  > 플래그 형식: `BUBU{...}`

- 참가자 파일: `handout/WEB-02.zip` 하나
- 정답: 서버의 `FLAG`와 동일한 실제 값을 Static flag로 등록합니다. ZIP의 `flag.txt`는 형식 예시입니다.
- Connection Info: 운영진이 배정한 웹 인스턴스 공개 URL
