import dataclasses as dc


@dc.dataclass(unsafe_hash=True)
class UserSignupRequestDto:
    id: str
    password: str
    gisu: str
    ban: str
    imgUrl: str
    name: str

    def set_url(self, imgUrl):
        self.imgUrl = imgUrl


@dc.dataclass(unsafe_hash=True)
class ProsRequestDto:
    first: str
    second: str
    third: str
    fourth: str
    fifth: str


@dc.dataclass(unsafe_hash=True)
class ConsRequestDto:
    first: str
    second: str
    third: str
    fourth: str
    fifth: str


@dc.dataclass(unsafe_hash=True)
class UserResponseDto:
    uuid: str
    ban: int
    name: str
    imgUrl: str
    first_pro: str
    second_pro: str
    first_con: str
    second_con: str

    def set_img_url(self,url):
        self.imgUrl = url

    def set_pros(self, first, second):
        self.first_pro = first
        self.second_pro = second

    def set_cons(self, first, second):
        self.first_con = first
        self.second_con = second


@dc.dataclass(unsafe_hash=True)
class UserDetailResponseDto:
    first_pro: str
    second_pro: str
    third_pro: str
    fourth_pro: str
    fifth_pro: str
    first_con: str
    second_con: str
    third_con: str
    fourth_con: str
    fifth_con: str

    # Default Constructor
    def __init__(self):
        return

    def set_pros(self, first, second, third, fourth, fifth):
        self.first_pro = first
        self.second_pro = second
        self.third_pro = third
        self.fourth_pro = fourth
        self.fifth_pro = fifth

    def set_cons(self, first, second, third, fourth, fifth):
        self.first_con = first
        self.second_con = second
        self.third_con = third
        self.fourth_con = fourth
        self.fifth_con = fifth


