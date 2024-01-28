#!/usr/bin/env python3
import argparse
import http.client
import subprocess
import sys
import time
from os import environ
from pathlib import Path
from textwrap import dedent

VERSION = "0.0.1"


class Style:
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[0m"


DEFAULT_PATH = "~/.empire"
# This is not currently configurable.
# There is hardcoded references to ~/.empire in the docker-compose file.
ENV_PATH = environ.get("EMPIRE_HOME_DIR")

path = Path(ENV_PATH or DEFAULT_PATH).expanduser().resolve()
docker_compose_file = path / "docker-compose.yaml"
server_config_file = path / "app-data" / "server-config.yaml"
dot_env_file = path / ".env"
base_command = ["sudo", "-E", "docker", "compose", "-f", docker_compose_file]
rm_rf = ["rm", "-rf"]


def main():
    if not docker_compose_file.exists():
        printr(f"Docker compose file not found at {docker_compose_file}.")
        exit(1)

    parser = argparse.ArgumentParser(
        description=dedent(
            f"""
        Empire Launcher v{VERSION}
        Docker Compose File: {docker_compose_file}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(help="Available commands")

    parser_up = subparsers.add_parser("up", help="Starts the Empire server and mysql db")
    parser_up.set_defaults(func=empire_up)

    parser_down = subparsers.add_parser("down", help="Stops the Empire server and mysql db")
    parser_down.set_defaults(func=empire_down)

    parser_destroy = subparsers.add_parser("destroy", help="Stops the Empire server and mysql db and removes the data")
    parser_destroy.set_defaults(func=empire_destroy)

    # empire server
    parser_server = subparsers.add_parser("server", help="Server-related commands")
    server_subparsers = parser_server.add_subparsers(help="Server commands")

    # empire server logs
    parser_server_logs = server_subparsers.add_parser("logs", help="Show server logs")
    parser_server_logs.add_argument(
        "-f",
        "--follow",
        action="store_true",
        help="Follow the logs (like tail -f)",
    )
    parser_server_logs.set_defaults(func=empire_server_logs)

    # empire client
    parser_client = subparsers.add_parser("client", help="Client-related commands")
    parser_client.set_defaults(func=empire_client)

    # empire use
    parser_use = subparsers.add_parser("use", help="Change the Empire version")
    parser_use.add_argument("version", help="The version of Empire to use")
    parser_use.set_defaults(func=empire_use)

    # Parse the arguments
    args = parser.parse_args()

    # If no arguments were provided, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args.func(args)


def empire_up(args):
    printg("Starting Empire")
    printg("It may take up to a minute.")

    command = base_command + ["up", "-d"]
    subprocess.run(command, check=True)

    server_config = server_config_file.read_text()
    port = "1337"
    for line in server_config.split("\n"):
        if "port:" in line:
            port = line.split("port: ")[1]

    time.sleep(5)
    for _i in range(60):
        is_running = check_server_status(f"localhost:{port}", "/index.html")
        if is_running:
            printg("Empire is running!")
            printg(f"Starkiller at http://localhost:{port}/index.html")
            exit(0)
        else:
            printg("Empire is still starting...")
            time.sleep(3)

    printr("Empire failed to start.")


def empire_down(args):
    printg("Shutting down Empire...")
    command = base_command + ["down"]
    subprocess.run(command, check=True)
    exit(0)


def empire_destroy(args):
    printg("Are you sure you want to destroy your Empire instance?")
    printg("This will delete all data and cannot be undone.")
    printg("Type 'destroy' to continue.")
    response = input("> ")

    if response != "destroy":
        print("Aborting.")
        exit(0)

    printg("Shutting down containers and destroying volumes...")
    command = base_command + ["down", "--volumes"]
    subprocess.run(command, check=True)

    printg("Clearing app-data directory...")
    command = rm_rf + [str(path / "app-data" / "server")]
    subprocess.run(command, check=True)
    command = rm_rf + [str(path / "app-data" / "client")]
    subprocess.run(command, check=True)
    printg("Cleared app-data directory")

    exit(0)


def empire_server_logs(args):
    if args.follow:
        command = base_command + ["logs", "-f"]
    else:
        command = base_command + ["logs"]

    subprocess.run(command, check=True)


def empire_client(args):
    # todo what if the server isn't using default credentials?
    #  what if i want to connect as a different user?
    # What if the server is running on a different machine, should we still support?
    command = base_command + ["exec", "empire_server", "./ps-empire", "client"]
    subprocess.run(command, check=True)


def empire_use(args):
    printg("Changing Empire version to " + args.version)

    lines = dot_env_file.read_text().splitlines()
    new_tag = args.version
    new_lines = [
        f"SERVER_TAG={new_tag}" if line.startswith("SERVER_TAG=") else line
        for line in lines
    ]
    dot_env_file.write_text("\n".join(new_lines))

    exit(0)


def check_server_status(host, path):
    conn = http.client.HTTPConnection(host)

    try:
        conn.request("GET", path)
        response = conn.getresponse()

        if response.status == 200:
            return True
        else:
            return False
    except Exception:
        return False
    finally:
        conn.close()


def printg(text):
    print(f"{Style.GREEN}{text}{Style.RESET}")


def printr(text):
    print(f"{Style.RED}{text}{Style.RESET}")


if __name__ == "__main__":
    main()
