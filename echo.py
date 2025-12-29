# Python 3: 문장을 반복 입력하고 그대로 출력 (!quit 입력 시 종료)

while True:
    s = input("문장을 입력하시오 (!quit 입력 시 종료): ")

    if s == "!quit":
        print("프로그램을 종료합니다.")
        break

    print("입력하신 문장은:", s)
