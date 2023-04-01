"""
Here's how the function works:

If no podname is specified, the function lists all pods and prompts the user to select one.
If the podname "all" is specified, the function iterates through all pods and calls itself recursively with each podname.
If no container name is specified, the function lists all containers for the selected pod and prompts the user to select one.
If the container name is "names", the function lists only the container names for the selected pod.
Otherwise, the function gets the details for the specified container in the selected pod.
"""

function get_containers() {
    local PODNAME="$1"
    local CONTAINERNAME="$2"
    local CONTAINERS

    if [ -z "$PODNAME" ]; then
        echo "No podname specified, getting list of all pods..."
        PODS=$(oc get pods | awk '{print $1}' | tail -n +2) #oc get pods
        select PODNAME in $PODS; do
            break
        done
        echo "Selected pod: $PODNAME"
    fi

    if [ "$PODNAME" = "all" ]; then
        echo "Iterating all pods..."
        for PODNAME in $(oc get pods | awk '{print $1}' | tail -n +2); do
            get_containers $PODNAME $CONTAINERNAME
        done
        return
    fi

    if [ -z "$CONTAINERNAME" ]; then
        echo "No container name specified, getting list of containers for pod $PODNAME..."
        CONTAINERS=$(oc get pod "$PODNAME" -o json | jq -r '.spec.containers[] | .name');
        select CONTAINERNAME in $CONTAINERS; do
            break
        done
        echo "Selected container: $CONTAINERNAME"
    elif [ "$CONTAINERNAME" = "names" ]; then
        echo "Listing container names for pod $PODNAME..."
        oc get pod "$PODNAME" -o json | jq -r '.spec.containers[] | .name'
        return
    fi

    echo "Getting details for container $CONTAINERNAME in pod $PODNAME..."
    oc get pod "$PODNAME" -o json | jq ".spec.containers[] | select(.name==\"$CONTAINERNAME\")"
}; # get_container_info
