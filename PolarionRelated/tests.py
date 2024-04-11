import re


if __name__ == '__main__':
    email1 = "example@gmail.com"
    if re.match(r"[\w_%+-]+@[\w.-]+\.[a-zA-Z]{2,4}", email1):
        print("Valid email")
    else:
        print("Invalid email")
