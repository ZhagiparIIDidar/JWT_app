from shemas import SUser
from utils import hash_password

sergei = SUser(
    username="Sergei", password=hash_password("qwerty"), email="sergei@mail.com"
)
den = SUser(username="a", password=hash_password("a"), email="den@mail.com")
demo_db: dict[str, SUser] = {
    sergei.username: sergei,
    den.username: den,
}
