import dataclasses as dc


@dc.dataclass(unsafe_hash=True)
class UserSignupRequestDto:
    id: str
    password: str
    gisu: str
    ban: str
    imgUrl: str

    def set_url(self, imgUrl):
        self.imgUrl = imgUrl