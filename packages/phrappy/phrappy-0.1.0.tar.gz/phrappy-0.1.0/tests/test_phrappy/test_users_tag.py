import pytest, secrets, string, random
from random import randint
from phrappy import Phrappy
from phrappy.models import (
    UserCreateDtoLinguist, UserEditDtoLinguist, UserPasswordEditDto
)

def gen_password(n=16):
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]
    pw = [secrets.choice(p) for p in pools]
    pw += [secrets.choice(''.join(pools)) for _ in range(n - 4)]
    random.SystemRandom().shuffle(pw)
    return ''.join(pw)

@pytest.mark.live
@pytest.mark.destructive
def test_user_lifecycle(client: Phrappy):
    name = "Luinguist"
    username = f"{name}_{randint(1000,9999)}"
    password = gen_password()

    new_user = client.user.create_user_v3(
        user_create_dto=UserCreateDtoLinguist(
            userName=username,
            firstName=name,
            lastName="Surname",
            email=f"void@{username.lower()}.example",
            password=password,
            timezone="Europe/Stockholm",
            note="User created automatically for testing purposes.",
        ),
        send_invitation=False,
    )
    try:
        # read and update user
        gottens = client.user.get_user_v3(new_user.uid)
        d = gottens.model_dump()
        for k in ["sourceLocales"]:
            d.pop(k, None)
        client.user.update_user_v3(new_user.uid, UserEditDtoLinguist(**d, sourceLocales=["sv"]))

        # change password and re-login
        new_password = gen_password()
        client.user.update_password(new_user.uid, UserPasswordEditDto(password=new_password))
        new_client = Phrappy.from_creds(username=username, password=new_password)
        me = new_client.authentication.who_am_i()
        assert me and getattr(me, "user", None)
    finally:
        client.user.delete_user(new_user.uid)
