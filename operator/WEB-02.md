# WEB-02 운영 메모

- 실제 플래그: `BUBU{sort_order_leaks_secrets}`
- 웹앱에는 이 값을 `FLAG` 환경변수로 주입하고, CTFd에는 동일한 값을 Static flag로 등록합니다.
- 참가자 ZIP의 `flag.txt`에 있는 `BUBU{fake_flag}`는 형식 예시입니다.
- 점수와 공개 URL: 운영진 확정 필요
- 상태: GitHub에 소스·ZIP·운영 문서·풀이 스크립트 준비. 서버 배포와 CTFd 등록은 아직 하지 않았습니다.

## 의도된 풀이

1. 부스 페이지에서 정렬 기준을 바꾸고 네트워크 요청 `GET /api/booths?sort=...`를 확인합니다.
2. `sort` 값이 SQL의 `ORDER BY` 식에 들어갑니다. API는 공개 부스 정보만 반환하며, 계산된 SQL 식의 값·비밀 데이터·자세한 SQL 오류는 보여주지 않습니다. 참·거짓에 따라 달라지는 부스 순서가 관찰 가능한 단서입니다.
3. 예를 들어 아래 식을 `sort` 값으로 URL 인코딩해 보냅니다. 참이면 첫 부스 ID가 `1`, 거짓이면 `6`이 됩니다.

   ```sql
   CASE WHEN (SELECT unicode(substr(value,1,1)) FROM staff_secrets WHERE name='event_flag') > 70 THEN id ELSE -id END
   ```

4. 비교 위치와 문자 코드를 바꿔 각 글자를 알아냅니다. 출력 가능한 ASCII 코드(32~126)를 순서대로 대입하거나 이진 탐색할 수 있고, `substr` 결과가 빈 문자열인지 비교해 길이를 알아낼 수 있습니다.
5. 테이블 이름을 모르는 경우 `sqlite_master`의 `name`을 같은 방식으로 한 글자씩 추출할 수 있습니다. 얻은 플래그를 CTFd에 제출합니다.

로컬 검증 스크립트: `python3 operator/WEB-02-solve.py --method linear` (순차 대입), `--method binary` (이진 탐색).

## 힌트

1. 정렬 버튼이 서버에 보내는 요청을 개발자 도구에서 살펴보세요.
2. `ORDER BY`에는 컬럼 이름뿐 아니라 조건에 따라 값이 바뀌는 식도 들어갈 수 있습니다.
3. 데이터가 직접 보이지 않아도 정렬 결과가 달라지는지 비교해 보세요.
