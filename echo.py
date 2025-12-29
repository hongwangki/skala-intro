import re
import sys
import string

# local password check function (replaces password.py)
def check_password(pwd: str) -> bool:
    if not pwd or len(pwd) < 6:
        return False
    has_alpha = any(c.isalpha() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    has_special = any(c in string.punctuation for c in pwd)
    return has_alpha and has_digit and has_special

quit_pattern = re.compile(r'^!quit$')

exit_pattern = re.compile(r'^exit$')
# 1️⃣ 비밀번호 인증 단계
while True:
    pwd = input("비밀번호를 입력하세요 (!quit 입력 시 종료): ")

    if quit_pattern.match(pwd) or exit_pattern.match(pwd):
        print("프로그램을 종료합니다.")
        sys.exit()
    if check_password(pwd):
        print("비밀번호 인증 성공!\n")
        break
    else:
        print("비밀번호 조건을 만족하지 않습니다.")
        print("- 알파벳 포함")
        print("- 숫자 포함")
        print("- 특수문자 포함")
        print("- 최소 6자리 이상\n")

# 2️⃣ 에코 프로그램
while True:
    text = input("문장을 입력하세요 (!quit 입력 시 종료): ")

    if quit_pattern.match(text) or exit_pattern.match(text):
        print("에코 프로그램을 종료합니다.")
        break

    print("입력한 문장:", text)
