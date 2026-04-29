"""Attach signature commands to the root CLI."""
from envchain.cli_env_signature import register_signature_commands


def attach(cli, get_store):
    register_signature_commands(cli, get_store)
