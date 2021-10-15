numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def check_email(email):
    if "@" in email:
        try:
            name, mail = email.split("@")
        except ValueError:
            return False
        if "." in mail and len(name) > 1 and not name.isdigit() and not name[0].isdigit():
            try:
                mail = mail.split(".")
            except ValueError:
                return False
            for num in numbers:
                for m in mail:
                    if num in m:
                        return False
            return True
    return False


def check_password(psw):
    if len(psw) > 4:
        if not psw.isdigit():
            num_in_psw = False
            for num in numbers:
                if num in psw:
                    num_in_psw = True
            if not num_in_psw:
                return False

            return True
    return False
