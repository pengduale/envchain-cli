"""Tests for envchain.crypto."""

import pytest
from cryptography.exceptions import InvalidTag

from envchain.crypto import encrypt, decrypt


def test_encrypt_returns_string():
    token = encrypt("hello", "passphrase")
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_decrypt_roundtrip():
    secret = "MY_SECRET_VALUE_123"
    passphrase = "correct-horse-battery-staple"
    token = encrypt(secret, passphrase)
    assert decrypt(token, passphrase) == secret


def test_different_encryptions_produce_different_tokens():
    """Each call should produce a unique ciphertext (random salt + nonce)."""
    t1 = encrypt("value", "pass")
    t2 = encrypt("value", "pass")
    assert t1 != t2


def test_wrong_passphrase_raises():
    token = encrypt("secret", "right-pass")
    with pytest.raises(InvalidTag):
        decrypt(token, "wrong-pass")


def test_tampered_ciphertext_raises():
    token = encrypt("secret", "pass")
    tampered = token[:-4] + "AAAA"
    with pytest.raises(Exception):
        decrypt(tampered, "pass")
