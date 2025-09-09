"""
Entry Point
===========

This module defines the en-/decryption process and implements it as a CLI. 

"""

import base64
import os
import sys
from pathlib import Path
from typing import Final, TypeAlias

import click
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from platformdirs import user_data_path


# ─── typing ─────────────────────────────────────────────────────────────────────── ✦ ─
#
PathLike: TypeAlias = os.PathLike


# ─── constants ──────────────────────────────────────────────────────────────────── ✦ ─
#
DATA_DIR: Final[Path] = (
    user_data_path(__package__.split(".")[-1], "hyletic", ensure_exists=True)
    or Path("~/.cryptex").expanduser()
)
ENCRYPTION_DIR: Final[Path] = Path(DATA_DIR, "encrypted")
DECRYPTION_DIR: Final[Path] = Path(DATA_DIR, "decrypted")

for directory in [DATA_DIR, ENCRYPTION_DIR, DECRYPTION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ─── helpers ────────────────────────────────────────────────────────────────────── ✦ ─
#
def generate_key(password: bytes, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """
    Generate an encryption key from a password.

    Parameters
    ----------
    password : str
        The password from which to derive the key.
    salt : bytes, optional
        The salt used to generate the key. If the parameter is left
        unspecified, this function generates and uses a new salt
        on-the-fly.

    Returns
    -------
    A tuple that contains the newly generated key and salt, in that order.

    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=1_200_000
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key, salt


# ─── command-line interface ─────────────────────────────────────────────────────── ✦ ─
#
@click.group()
def cli():
    """Secrecy - A command-line utility for encrypting and decrypting files."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False)
@click.option("--password", "-p", help="Encryption password")
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (defaults to DATA_DIR/encrypted/filename.crypt)",
)
@click.option(
    "--print-only",
    "-P",
    is_flag=True,
    default=False,
    help="Output encrypted data to stdout without prompting to save",
)
def encrypt(
    file: str | PathLike | None = None,
    password: str | None = None,
    output: str | PathLike | None = None,
    print_only: bool = False
) -> None: 
    """Encrypt a file using a password.

    Parameters
    ----------
    file : str | PathLike, optional
        A string or path-like object representing the location of the
        target file. If not provided, reads from stdin.
    password : str, optional
        The string of UTF-8-encoded characters used to encrypt the file.
    output : str | PathLike, optional
        A string or path-like object representing the location to which
        this function writes the target file's encrypted contents.
    print_only : bool
        A boolean value that determines whether this function writes the
        encrypted contents to disk or outputs them to stdout. Defaults to
        ``False``.

    Returns
    -------
    Nothing.

    """
    if not password:
        password = click.prompt(
            "Enter encryption password", hide_input=True, confirmation_prompt=True
        )

    password_bytes = password.encode()

    key, salt = generate_key(password_bytes)
    f = Fernet(key)

    # Read the input data.
    if file:
        # Read from file
        with open(file, "r") as input_file:
            data = input_file.read()
        input_name = file.stem
    else:
        # Read from `stdin`.
        if sys.stdin.isatty():
            click.echo("Reading from stdin (press Ctrl+D when done):")
        data = sys.stdin.read()
        input_name = "stdin"

    token = f.encrypt(data.encode())

    if print_only:
        # Output to stdout (binary data)
        sys.stdout.buffer.write(salt + token)
        return

    if output:
        if isinstance(output, str):
            output = (
                Path(output).expanduser() if output.startswith("~")
                else Path(output)
            )
    else:
        if not file and not sys.stdin.isatty():
            sys.stdout.buffer.write(salt + token)
            return
        elif sys.stdout.isatty():
            if click.confirm("Would you like to save the encrypted data to a file?", default=True):
                suggested_path = ENCRYPTION_DIR / f"{input_name}.crypt"
                path_prompt = (
                    "Where? (Enter an absolute path, or press enter to use\n"
                    f"the Cryptex data directory: {suggested_path})"
                )
                output_str = click.prompt(
                    path_prompt, default=str(suggested_path), show_default=False
                )
                output = Path(output_str).expanduser()
            else:
                sys.stdout.buffer.write(salt + token)
                return
        else:
            sys.stdout.buffer.write(salt + token)
            return

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and not click.confirm(
            f"File `{output}` already exists. Do you want to overwrite it?"
        ):
            click.echo("Operation cancelled.")
            return

        with open(output, "wb") as of:
            of.write(salt + token)

        source_desc = str(file) if file else "stdin"
        click.echo(f"Encrypted {source_desc} successfully.")
        click.echo(f"Saved output to {output.resolve()}")
    except Exception as e:
        click.echo(f"Error saving file: {e}", err=True)
        return


@cli.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False)
@click.option("--password", "-p", help="Decryption password")
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (used only if user chooses to save)",
)
@click.option(
    "--print-only",
    "-P",
    is_flag=True,
    default=False,
    help="Print decrypted content to console without prompting to save",
)
def decrypt(
    file: str | PathLike | None = None,
    password: str = None,
    output: str | PathLike | None = None,
    print_only: bool = False
) -> None:
    """
    Decrypt an encrypted file using a password.

    Parameters
    ----------
    file : str | PathLike, optional
        A string or path-like object representing the location of the
        file to be decrypted. If not provided, reads from stdin.
    password : str
        The string of UTF-8-encoded characters used to decrypt the file.
    output : str | PathLike, optional
        A string or path-like object representing the location to which
        this function saves the target file's decrypted contents. Defaults
        to the value of this module's ``DECRYPTION_DIR`` constant.
    print_only : bool
        A boolean value that determines whether this function writes the
        target file's decrypted contents to disk or simply streams them to
        ``stdout``. Defaults to ``False``.

    Returns
    -------
    Nothing.

    """

    if not password:
        password: str = click.prompt("Enter decryption password", hide_input=True)

    password_bytes: bytes = password.encode()

    try:
        if file:
            with open(file, "rb") as input_file:
                salt = input_file.read(16)
                encrypted_data = input_file.read()
            input_name = file.stem
        else:
            if sys.stdin.isatty():
                click.echo("Reading encrypted data from stdin...")
            encrypted_bytes = sys.stdin.buffer.read()
            salt = encrypted_bytes[:16]
            encrypted_data = encrypted_bytes[16:]
            input_name = "stdin"

        key, _ = generate_key(password_bytes, salt)
        f = Fernet(key)

        decrypted_data = f.decrypt(encrypted_data)
        decoded_text = decrypted_data.decode()

        click.echo("\n==================== DECRYPTED DATA ====================\n")
        click.echo(decoded_text)
        click.echo("\n========================================================\n")

        if print_only:
            return

        if click.confirm("Would you like to save this output to disk?", default=True):
            if not output:
                suggested_path = DECRYPTION_DIR / f"{input_name}_decrypted.txt"
                path_prompt = (
                    "Where? (Enter an absolute path, or press enter to use\n"
                    f"the Cryptex data directory: {suggested_path})"
                )
                output_str = click.prompt(
                    path_prompt, default=str(suggested_path), show_default=False
                )
                output = Path(output_str).expanduser()

            try:
                output.parent.mkdir(parents=True, exist_ok=True)
                if output.exists() and not click.confirm(
                    f"File `{output}` already exists. Do you want to overwrite it?"
                ):
                    click.echo("Operation cancelled.")
                    return

                with open(output, "w") as of:
                    of.write(decoded_text)

                click.echo(f"✓ Wrote decrypted data to `{output.resolve()}`.")
            except Exception as e:
                click.echo(f"Error saving file: {e}", err=True)
                return

    except Exception as e:
        click.echo(f"Error decrypting file: {e}", err=True)
        click.echo(
            "This could be due to an incorrect password or corrupted file.", err=True
        )
        sys.exit(1)


if __name__ == "__main__":
    cli()
