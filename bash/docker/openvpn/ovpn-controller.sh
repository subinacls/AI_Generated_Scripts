#!/bin/bash

# Function to initialize EasyRSA
easyrsa_init() {
  docker run -v $PWD:/etc/openvpn --rm kylemanna/openvpn ovpn_initpki
}

# Function to create a new OpenVPN user
easyrsa_makeuser() {
  local username=$1
  docker run -v $PWD:/etc/openvpn --rm -it kylemanna/openvpn easyrsa build-client-full $username nopass
}

# Function to get the client configuration for a specific user
openvpn_getclient() {
  local username=$1
  docker run -v $PWD:/etc/openvpn --rm kylemanna/openvpn ovpn_getclient $username
}

# Function to generate OpenVPN config with the external IP
openvpn_genconfig() {
  local extIP=$1
  docker run -v $PWD:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u tcp://$extIP:443
  # -e "port-share $extIP 4433"
}

# Function to start OpenVPN
openvpn_start() {
  docker run -v $PWD:/etc/openvpn -d -p 443:1194/tcp --cap-add=NET_ADMIN kylemanna/openvpn --name openvpn
}

# Function to enter bash shell in the OpenVPN container
opevpn_shell() {
  # Get the container ID or name
  local container_name="kylemanna/openvpn"
  local container_id=$(docker ps -qf "ancestor=$container_name")
  # Check if the container is running
  if [ -n "$container_id" ]; then
    echo "Entering shell for OpenVPN container ($container_id)..."
    docker exec -it $container_id /bin/bash
  else
    echo "OpenVPN container is not running."
  fi
}

openvpn_logs() {
  # Get the container ID or name
  local container_name="kylemanna/openvpn"
  local container_id=$(docker ps -qf "ancestor=$container_name")
  # Check if the container is running
  if [ -n "$container_id" ]; then
    echo "Displaying logs for OpenVPN container ($container_id)..."
    docker logs $container_id
  else
    echo "OpenVPN container is not running."
  fi
}

# Check command line arguments for which function to execute
case "$1" in
  init)
    easyrsa_init
    ;;
  makeuser)
    easyrsa_makeuser "$2"
    ;;
  getclient)
    openvpn_getclient "$2"
    ;;
  genconfig)
    openvpn_genconfig "$2"
    ;;
  start)
    openvpn_start
    ;;
  shell)
    opevpn_shell
    ;;
  logs)
    openvpn_logs
    ;;
  *)
    echo "Usage: $0 {init|makeuser|getclient|genconfig|start|shell|logs} [arguments]"
    ;;
esac
