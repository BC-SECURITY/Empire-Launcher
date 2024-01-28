#! /bin/bash

if [ "$EUID" -eq 0 ]; then
  echo "This script should not be run as root."
  exit 1
fi

if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: docker is not installed. Please install docker and try again.' >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo 'Error: docker compose is not installed. Please install docker compose and try again.' >&2
    exit 1
fi

if ! [ -x "$(command -v wget)" ]; then
  echo 'Error: wget is not installed. Please install wget and try again.' >&2
  exit 1
fi

if [ -d ~/.empire ]; then
  if [ "$1" == "--update" ]; then
    echo "Update flag provided. Removing existing ~/.empire directory."
    rm -rf ~/.empire
  else
    echo "Error: ~/.empire already exists. Please run with --update to overwrite it." >&2
    exit 1
  fi
fi

mkdir -p ~/.empire
mkdir -p ~/.empire/app-data

echo "Copying files to ~/.empire"

wget -O ~/.empire/docker-compose.yaml https://raw.githubusercontent.com/BC-SECURITY/Empire-Launcher/main/docker-compose.yaml
wget -O ~/.empire/app-data/server-config.yaml https://raw.githubusercontent.com/BC-SECURITY/Empire-Launcher/main/server-config.yaml
wget -O ~/.empire/empire-bin.py https://raw.githubusercontent.com/BC-SECURITY/Empire-Launcher/main/empire-bin.py

sudo ln -s ~/.empire/empire-bin.py /usr/local/bin/empire
sudo chmod 755 /usr/local/bin/empire
