# Empire Launcher

This project is under construction.
I have no idea whether it will be rolled out more broadly or not.


## Usage
Install docker, docker compose, curl, and wget. You should defer to the 
[docker documentation](https://docs.docker.com/engine/install/) for how to install
docker and docker compose, but this might work for you on kali, which I took from
[this page](https://docs.docker.com/engine/install/debian/).
```shell
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  bookwork stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt-get install curl wget
````

Run the 1-liner install
```shell
curl -sSL https://raw.githubusercontent.com/BC-SECURITY/Empire-Launcher/dev/install.sh | bash
```

Type `empire` to see the help menu

`empire up` to start the server!

## Goal

The end goal for this install is that it can be run as a 1-liner with curl.

The script will then take less than a minute to:
* create an ~/.empire directory
* copy a default docker-compose and server-config into it
* add the empire "binary" to the user's path

It will expect the user to already have a few things installed like docker and wget

Then a plethora of commands will be available to the user (Not all of these are implemented)
* `empire` - Prints the help menu
* `empire up` - Starts the Empire server and mysql db
* `empire down` - Stops the Empire server and mysql db
* `empire destroy` - Stops the Empire server and mysql db and removes the data
* `empire server logs` - Prints the logs from the Empire server
* `empire server logs -f` - Prints the logs from the Empire server and mysql db and follows them
* `empire database logs` - Prints the logs from the mysql db
* `empire client` - Starts the Empire client, attached to the running server container
* `empire database dump` - Dumps the mysql database to the host's ~/.empire/app-data directory
* `empire use version 5.8.0` - Changes the version of Empire that is running (by docker tag)
* `empire server attach` - Attaches to the running server container with a bash session

## Bring your own container
This will only work with the 5.8.4 container or higher.
It will only run with the public build of Empire/Starkiller.

If you want to use your own empire container instead of the one from Dockerhub,
you can build it with the following commands. The ssh mounting is useful if you
are wanting to use the sponsors build of starkiller since it requires a github ssh credential.


```shell
git fetch origin
git checkout docker-beta

eval $(ssh-agent)
# This command will be different depending on your ssh key
# ssh-add ~/.ssh/id_rsa
ssh-add ~/.ssh/id_ed25519

docker buildx build --ssh default=$SSH_AUTH_SOCK -t bcsecurity/empire .
```

## Issues
* The first call to `empire` after installing the binary fails. The second call succeeds. Not sure why.
* There is a set list of ports that are bound to the host. You change this list by modifying `~/.empire/docker-compose.yaml`

## Architecture

The docker-compose file creates a Docker volume for the mysql db to persist data between runs.
The docker-compose file binds the empire data directories to the host's ~/.empire/app-data directory.
This allows the user to modify the server-config.yml and other files without having to rebuild the image.
It also allows the files to persist between runs.
