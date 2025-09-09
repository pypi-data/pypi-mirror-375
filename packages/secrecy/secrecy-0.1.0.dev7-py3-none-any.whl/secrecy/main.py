"""
Entry Point
===========

This module defines the en-/decryption process and implements it as a CLI.

"""

import base64
import io
import os
import sys
from pathlib import Path
from typing import Final, TypeAlias, Iterator

import click
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from platformdirs import user_data_path

try:
    from . import __version__
except ImportError:
    __version__ = "0.1.0dev7"


# ─── typing ─────────────────────────────────────────────────────────────────────── ✦ ─
#
PathLike: TypeAlias = os.PathLike


# ─── constants ──────────────────────────────────────────────────────────────────── ✦ ─
#
DATA_DIR: Final[Path] = user_data_path(
    __package__.split(".")[-1], "hyletic", ensure_exists=True
)
ENCRYPTION_DIR: Final[Path] = Path(DATA_DIR, "encrypted")
DECRYPTION_DIR: Final[Path] = Path(DATA_DIR, "decrypted")

# Streaming constants
CHUNK_SIZE: Final[int] = 64 * 1024  # 64KB chunks

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


def read_chunks(file_obj, chunk_size: int = CHUNK_SIZE) -> Iterator[bytes]:
    """
    Read data in chunks from a file object.

    Parameters
    ----------
    file_obj
        File object to read from
    chunk_size : int
        Size of each chunk in bytes

    Yields
    ------
    bytes
        Chunks of data from the file
    """
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk


def encrypt_stream(
    input_stream, output_stream, fernet_cipher: Fernet, salt: bytes
) -> None:
    """
    Encrypt data from input stream and write to output stream in chunks.

    Parameters
    ----------
    input_stream
        Input stream to read from
    output_stream
        Output stream to write to
    fernet_cipher : Fernet
        Initialized Fernet cipher
    salt : bytes
        Salt to prepend to output
    """
    # Write the salt first.
    output_stream.write(salt)
    output_stream.flush()

    # Process data in chunks.
    buffer = b""
    for chunk in read_chunks(input_stream):
        buffer += chunk
        # Process complete lines/records when possible
        if b"\n" in buffer or len(buffer) >= CHUNK_SIZE:
            encrypted_chunk = fernet_cipher.encrypt(buffer)
            # Write length prefix for each encrypted chunk
            length = len(encrypted_chunk).to_bytes(4, "big")
            output_stream.write(length + encrypted_chunk)
            output_stream.flush()
            buffer = b""

    # Process remaining buffer.
    if buffer:
        encrypted_chunk = fernet_cipher.encrypt(buffer)
        length = len(encrypted_chunk).to_bytes(4, "big")
        output_stream.write(length + encrypted_chunk)
        output_stream.flush()


def decrypt_stream(input_stream, output_stream, fernet_cipher: Fernet) -> None:
    """
    Decrypt data from input stream and write to output stream in chunks.

    Parameters
    ----------
    input_stream
        Input stream to read from
    output_stream
        Output stream to write to
    fernet_cipher : Fernet
        Initialized Fernet cipher
    """
    while True:
        # Read length of the prefix.
        length_bytes = input_stream.read(4)
        if not length_bytes or len(length_bytes) < 4:
            break

        chunk_length = int.from_bytes(length_bytes, "big")
        encrypted_chunk = input_stream.read(chunk_length)

        if len(encrypted_chunk) < chunk_length:
            break

        decrypted_chunk = fernet_cipher.decrypt(encrypted_chunk)
        output_stream.write(decrypted_chunk)
        output_stream.flush()


# ─── command-line interface ─────────────────────────────────────────────────────── ✦ ─
#
@click.group()
@click.version_option(
    __version__,
    "--version",
    "-V",
    prog_name="Secrecy",
)
def cli():
    """A symmetric encryption utility."""
    pass


@cli.command()
@click.argument(
    "file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False
)
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
@click.option(
    "--stream",
    "-s",
    is_flag=True,
    default=False,
    help="Enable streaming mode for large files or continuous input",
)
@click.option(
    "--overwrite",
    "-ov",
    is_flag=True,
    default=False,
    help="Overwrite output file if it exists",
)
def encrypt(
    file: str | PathLike | None = None,
    password: str | None = None,
    output: str | PathLike | None = None,
    print_only: bool = False,
    stream: bool = False,
    overwrite: bool = False,
) -> None:
    """Encrypt a file using a password."""

    if not password:
        # Prompt for a password when interactive mode is invoked without the `-p` flag.
        if not sys.stdin.isatty():
            click.echo(
                "Error: Password required in non-interactive mode. Use -p option.",
                err=True,
            )
            sys.exit(1)
        password = click.prompt(
            "Enter encryption password", hide_input=True, confirmation_prompt=True
        )

    password_bytes = password.encode()
    key, salt = generate_key(password_bytes)
    f = Fernet(key)

    # Determine the input source.
    if file:
        input_stream = open(file, "rb")
        input_name = file.stem
    else:
        input_stream = sys.stdin.buffer
        input_name = "stdin"
        # Automatically enable streaming for `stdin` if it is not a TTY.
        if not sys.stdin.isatty():
            stream = True

    try:
        # Handle streaming mode.
        if stream or (not file and not sys.stdin.isatty()):
            try:
                if output:
                    if isinstance(output, str):
                        output = (
                            Path(output).expanduser()
                            if output.startswith("~")
                            else Path(output)
                        )
                    output.parent.mkdir(parents=True, exist_ok=True)

                    # Check if the file exists and handle overwrite logic.
                    if output.exists() and not overwrite:
                        if sys.stdin.isatty():
                            if not click.confirm(
                                f"File `{output}` already exists. Do you want to overwrite it?"
                            ):
                                click.echo("Operation cancelled.", err=True)
                                sys.exit(1)
                        else:
                            click.echo(
                                f"Error: Output file '{output}' already exists. "
                                "Use --overwrite to force overwriting.",
                                err=True,
                            )
                            sys.exit(1)

                    with open(output, "wb") as output_stream:
                        encrypt_stream(input_stream, output_stream, f, salt)
                    click.echo(
                        f"✓ Encrypted {input_name} to {output.resolve()}", err=True
                    )
                else:
                    encrypt_stream(input_stream, sys.stdout.buffer, f, salt)
            except KeyboardInterrupt:
                click.echo("\nEncryption cancelled.", err=True)
                sys.exit(0)
            return

        if file:
            data = input_stream.read().decode()
        else:
            if sys.stdin.isatty():
                click.echo("Reading from stdin (press Ctrl+D when done):")
            try:
                data = sys.stdin.read()
            except (EOFError, KeyboardInterrupt):
                click.echo("\nInput cancelled.", err=True)
                sys.exit(0)

        token = f.encrypt(data.encode())

        if print_only:
            sys.stdout.buffer.write(salt + token)
            return

        if output:
            if isinstance(output, str):
                output = (
                    Path(output).expanduser()
                    if output.startswith("~")
                    else Path(output)
                )
        else:
            if not file and not sys.stdin.isatty():
                sys.stdout.buffer.write(salt + token)
                return
            elif sys.stdout.isatty():
                if click.confirm(
                    "Would you like to save the encrypted data to a file?", default=True
                ):
                    suggested_path = ENCRYPTION_DIR / f"{input_name}.crypt"
                    path_prompt = (
                        "Where? (Enter an absolute path, or press enter to use "
                        f"the Secrecy data directory: {suggested_path})"
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

            # Check if file exists and handle overwrite logic
            if output.exists() and not overwrite:
                if sys.stdin.isatty():
                    if not click.confirm(
                        f"File `{output}` already exists. Do you want to overwrite it?"
                    ):
                        click.echo("Operation cancelled.", err=True)
                        sys.exit(1)
                else:
                    click.echo(
                        f"Error: Output file '{output}' already exists. "
                        "Use --overwrite to force overwriting.",
                        err=True,
                    )
                    sys.exit(1)

            with open(output, "wb") as of:
                of.write(salt + token)

            source_desc = str(file) if file else "stdin"
            click.echo(f"Encrypted {source_desc} successfully.")
            click.echo(f"Saved output to {output.resolve()}")
        except Exception as e:
            click.echo(f"Error saving file: {e}", err=True)
            return

    finally:
        if file and hasattr(input_stream, "close"):
            input_stream.close()


@cli.command()
@click.argument(
    "file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False
)
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
@click.option(
    "--stream",
    "-s",
    is_flag=True,
    default=False,
    help="Enable streaming mode for large files or continuous input",
)
@click.option(
    "--overwrite",
    "-ov",
    is_flag=True,
    default=False,
    help="Overwrite output file if it exists",
)
def decrypt(
    file: str | PathLike | None = None,
    password: str = None,
    output: str | PathLike | None = None,
    print_only: bool = False,
    stream: bool = False,
    overwrite: bool = False,
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
    stream : bool
        Enable streaming mode for processing large files or continuous input.
    overwrite : bool
        Overwrite output file if it exists.

    Returns
    -------
    Nothing.

    """

    if not password:
        if not sys.stdin.isatty():
            click.echo(
                "Error: Password required in non-interactive mode. Use -p option.",
                err=True,
            )
            sys.exit(1)
        password: str = click.prompt("Enter decryption password", hide_input=True)

    password_bytes: bytes = password.encode()

    try:
        if file:
            input_stream = open(file, "rb")
            input_name = file.stem
        else:
            input_stream = sys.stdin.buffer
            input_name = "stdin"
            # Auto-enable streaming for stdin when not a TTY
            if not sys.stdin.isatty():
                stream = True

        salt = input_stream.read(16)
        if len(salt) < 16:
            raise ValueError("Invalid encrypted file: missing or incomplete salt")

        key, _ = generate_key(password_bytes, salt)
        f = Fernet(key)

        # Peek at the next 4 bytes to see if it's a valid length prefix.
        peek_data = input_stream.read(4)
        if len(peek_data) == 4:
            # Check if this looks like a length prefix
            potential_length = int.from_bytes(peek_data, "big")
            is_streaming_format = 1 <= potential_length <= 1024 * 1024  # 1MB per chunk

            # Reset to the position after the salt if the input is not streaming.
            if not is_streaming_format and hasattr(input_stream, "seek"):
                input_stream.seek(16)
            elif not is_streaming_format:
                # For non-seekable streams, prepend the peek data.
                remaining_data = input_stream.read()
                input_stream = io.BytesIO(peek_data + remaining_data)
        else:
            is_streaming_format = False
            if peek_data and hasattr(input_stream, "seek"):
                input_stream.seek(16)
            elif peek_data:
                remaining_data = input_stream.read()
                input_stream = io.BytesIO(peek_data + remaining_data)

        # Handle streaming mode or streaming format files.
        if stream or is_streaming_format:
            try:
                if output:
                    if isinstance(output, str):
                        output = (
                            Path(output).expanduser()
                            if output.startswith("~")
                            else Path(output)
                        )
                    output.parent.mkdir(parents=True, exist_ok=True)

                    # Check if the file exists; handle overwrite logic.
                    if output.exists() and not overwrite:
                        if sys.stdin.isatty():
                            if not click.confirm(
                                f"File `{output}` already exists. Do you want to overwrite it?"
                            ):
                                click.echo("Operation cancelled.", err=True)
                                sys.exit(1)
                        else:
                            click.echo(
                                f"Error: Output file '{output}' already exists. "
                                "Use --overwrite to force overwriting.",
                                err=True,
                            )
                            sys.exit(1)

                    with open(output, "wb") as output_stream:
                        if not is_streaming_format:
                            encrypted_data = input_stream.read()
                            decrypted_data = f.decrypt(encrypted_data)
                            output_stream.write(decrypted_data)
                        else:
                            if peek_data:
                                temp_stream = io.BytesIO(
                                    peek_data + input_stream.read()
                                )
                                decrypt_stream(temp_stream, output_stream, f)
                            else:
                                decrypt_stream(input_stream, output_stream, f)
                    click.echo(
                        f"✓ Decrypted {input_name} to {output.resolve()}", err=True
                    )
                else:
                    if not is_streaming_format:
                        encrypted_data = input_stream.read()
                        decrypted_data = f.decrypt(encrypted_data)
                        sys.stdout.buffer.write(decrypted_data)
                    else:
                        if peek_data:
                            temp_stream = io.BytesIO(peek_data + input_stream.read())
                            decrypt_stream(temp_stream, sys.stdout.buffer, f)
                        else:
                            decrypt_stream(input_stream, sys.stdout.buffer, f)
            except KeyboardInterrupt:
                click.echo("\nDecryption cancelled.", err=True)
                sys.exit(0)
            return

        encrypted_data = input_stream.read()
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
                    "Where? (Enter an absolute path, or press enter to use "
                    f"the Secrecy data directory: {suggested_path})"
                )
                output_str = click.prompt(
                    path_prompt, default=str(suggested_path), show_default=False
                )
                output = Path(output_str).expanduser()

            try:
                output.parent.mkdir(parents=True, exist_ok=True)

                # Check if the file exists; handle overwrite logic.
                if output.exists() and not overwrite:
                    if sys.stdin.isatty():
                        if not click.confirm(
                            f"File `{output}` already exists. Do you want to overwrite it?"
                        ):
                            click.echo("Operation cancelled.", err=True)
                            sys.exit(1)
                    else:
                        click.echo(
                            f"Error: Output file '{output}' already exists. "
                            "Use --overwrite to force overwriting.",
                            err=True,
                        )
                        sys.exit(1)

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

    finally:
        if file and hasattr(input_stream, "close"):
            input_stream.close()


if __name__ == "__main__":
    cli()
