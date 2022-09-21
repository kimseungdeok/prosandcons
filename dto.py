import dataclasses as dc


@dc.dataclass(unsafe_hash=True)
class UserSignupRequestDto:
    id: str
    password: str
    gisu: str
    ban: str
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