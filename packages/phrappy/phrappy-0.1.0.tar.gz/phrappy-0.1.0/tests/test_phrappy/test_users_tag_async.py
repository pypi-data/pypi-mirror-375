import pytest, secrets, string, random
from random import randint
from phrappy import AsyncPhrappy
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
@pytest.mark.asyncio
async def test_user_lifecycle(aclient: AsyncPhrappy):
    name = "Luinguist"
    username = f"{name}_{randint(1000,9999)}"
    password = gen_password()

    new_user = await aclient.user.create_user_v3(
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
        gottens = await aclient.user.get_user_v3(new_user.uid)
        d = gottens.model_dump()
        for k in ["sourceLocales"]:
            d.pop(k, None)
        await aclient.user.update_user_v3(new_user.uid, UserEditDtoLinguist(**d, sourceLocales=["sv"]))

        new_password = gen_password()
        await aclient.user.update_password(new_user.uid, UserPasswordEditDto(password=new_password))
        new_client = await AsyncPhrappy.from_creds(username=username, password=new_password)
        try:
            me = await new_client.authentication.who_am_i()
            assert me and getattr(me, "user", None)
        finally:
            await new_client.aclose()
    finally:
        await aclient.user.delete_user(new_user.uid)
