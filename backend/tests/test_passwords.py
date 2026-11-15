"""Password hashing. No database is used."""

from app.services.passwords import hash_password, verify_password

PASSWORD = "correct horse battery staple"


def test_hash_does_not_contain_the_password():
    assert PASSWORD not in hash_password(PASSWORD)


def test_hash_uses_argon2id():
    assert hash_password(PASSWORD).startswith("$argon2id$")


def test_same_password_gives_a_different_hash_each_time():
    assert hash_password(PASSWORD) != hash_password(PASSWORD)


def test_correct_password_is_accepted():
    assert verify_password(PASSWORD, hash_password(PASSWORD))


def test_wrong_password_is_rejected():
    assert not verify_password("wrong password", hash_password(PASSWORD))


def test_password_check_is_case_sensitive():
    assert not verify_password(PASSWORD.upper(), hash_password(PASSWORD))


def test_text_that_is_not_a_hash_is_rejected():
    assert not verify_password(PASSWORD, "not a hash")


def test_empty_hash_is_rejected():
    assert not verify_password(PASSWORD, "")
