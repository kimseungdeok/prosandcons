import dataclasses as dc


@dc.dataclass(unsafe_hash=True)
class UserSignupRequestDto:
    id: str
    password: str
    gisu: str
    ban: int
    imgUrl: str
    name: str


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
    ban: int
    name: str
    imgUrl: str
    first_pro: str
    second_pro: str
    first_con: str
    second_con: str

    def set_pros(self,first,second):
        self.first_pro = first
        self.second_pro = second

    def set_cons(self,first,second):
        self.first_con = first
        self.second_con = second
