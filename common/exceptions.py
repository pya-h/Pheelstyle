

class WaitAssholeException(Exception):
    def __init__(self, time_remaining):
        self.time_remaining = time_remaining

    def fa(self):
        return f"لطفا برای ارسال ایمیل بعدی {self.time_remaining} ثانیه صبر کنید. "

    def __str__(self):
        return f"Please wait {self.time_remaining} seconds for sending next email."
