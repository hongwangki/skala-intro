import re
from password import check_password

quit_pattern = re.compile(r'^!quit$')

# 1️⃣ 비밀번호 인증 단계
while True:
    pwd = input("비밀번호를 입력하세요 (!quit 입력 시 종료): ")

    if quit_pattern.match(pwd):
        print("프로그램을 종료합니다.")
        exit()

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

    if quit_pattern.match(text):
        print("에코 프로그램을 종료합니다.")
        break

    print("입력한 문장:", text)
