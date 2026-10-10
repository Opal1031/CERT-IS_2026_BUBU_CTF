# WEB-01 운영 메모

- 실제 플래그: `BUBU{client_side_gate_is_open}`
- 웹앱에는 이 값을 `FLAG` 환경변수로 주입하고, CTFd에는 동일한 값을 Static flag로 등록합니다.
- `flag.txt`의 `BUBU{fake_flag}`는 참가자용 형식 예시입니다.
- 점수와 공개 URL: 운영진 확정 필요
- 상태: GitHub에 소스·ZIP·운영 문서 준비. 서버 배포와 CTFd 등록은 아직 하지 않았습니다.

## 의도된 풀이

1. 기본 `member` 역할로 운영진 공지를 열면 접근이 거부됩니다.
2. 브라우저 Console에서 `portalSession.role = 'admin'`으로 바꾼 뒤 공지를 다시 엽니다.
3. 서버가 요청의 `role`을 신뢰해 플래그를 반환합니다. 같은 요청을 직접 보내는 풀이도 유효합니다.

## 힌트

1. 공지 버튼의 동작을 브라우저 개발자 도구에서 확인해 보세요.
2. Console에서 `portalSession.role`을 `admin`으로 바꿔 보세요.
