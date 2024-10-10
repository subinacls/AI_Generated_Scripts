#!/bin/bash

# Function to show the logs of the wg-easy container
show_docker_wg_easy_logs() {
    docker logs wg-easy
}

# Function to start the Docker container
start_docker_wg_easy() {
    docker logs $(docker run --detach \
        --name wg-easy \
        --env UI_TRAFFIC_STATS=true \
        --env UI_CHART_TYPE=1 \
        --env ENABLE_PROMETHEUS_METRICS=true \
        --env PROMETHEUS_METRICS_PASSWORD='BCRYPTHASHERE' \
        --env LANG=en \
        --env WG_HOST=YOURIPADDRESSHERE \
        --env PASSWORD_HASH='BCRYPTHASHHERE' \
        --env PORT=51821 \
        --env WG_PORT=51820 \
        --volume ~/.wg-easy:/etc/wireguard \
        --publish 51820:51820/udp \
        --publish 51821:51821/tcp \
        --cap-add NET_ADMIN \
        --cap-add SYS_MODULE \
        --sysctl 'net.ipv4.conf.all.src_valid_mark=1' \
        --sysctl 'net.ipv4.ip_forward=1' \
        --restart unless-stopped \
        ghcr.io/wg-easy/wg-easy
    )
}

# Function to stop the Docker container
stop_docker_wg_easy() {
    docker stop wg-easy
    docker rm wg-easy
}

# Check command line argument to start or stop the container
if [ "$1" == "start" ]; then
    start_docker_wg_easy
    echo "wg-easy container started."
elif [ "$1" == "stop" ]; then
    stop_docker_wg_easy
    echo "wg-easy container stopped and removed."
elif [ "$1" == "logs" ]; then
    echo "showing wg-easy logs."
    show_docker_wg_easy_logs
else
    echo "Usage: $0 {start|stop|logs}"
fi
