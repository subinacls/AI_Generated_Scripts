"""
This function, named openshift_describe, allows you to interact with the OpenShift API to fetch and display pod and container details using the oc describe command. The function can work with or without input arguments for the pod and container names. It is designed to provide an interactive way to select and view the desired information.

Here's a detailed explanation of the function and how to use it:

If no arguments are provided, the function lists all available pods in the current namespace and asks the user to enter a pod number or type 'ALL' to select all pods.

If the user selects a specific pod, the function lists all available containers within that pod and asks the user to enter a container number or type 'ALL' to select all containers.

If the user provides a pod name and/or container name as input arguments, the function uses those arguments as the selected pod and container, respectively.

Based on the user's selections, the function calls the oc describe command to fetch and display the requested information:

If the user selects a specific pod and container, the function displays the description of the selected container in the selected pod.
If the user selects a specific pod and 'ALL' for containers, the function displays the description of all containers within the selected pod.
If the user selects 'ALL' for pods and a specific container, the function displays the description of the specified container for all pods (assuming the container name exists in each pod).
If the user selects 'ALL' for both pods and containers, the function displays the description of all pods in the current namespace.
To use the function, you can either add the script to your .bashrc or .bash_profile file or run the script directly in your terminal session. Once the function is available, you can call it using:

bash
Copy code
openshift_describe [pod_name] [container_name]
Where pod_name and container_name are optional arguments. If you don't provide any arguments, the function will guide you through an interactive selection process.

For example:

bash
Copy code
# Interactive mode without any arguments
openshift_describe_container

# Specify a pod and container name directly
openshift_describe_container my-pod my-container

# Specify a pod name and select container interactively
openshift_describe_container my-pod

# Specify a container name and select pod interactively
openshift_describe_container "" my-container
"""

function openshift_describe_container() {
  local pod_name="$1"
  local container_name="$2"
  local selected_pod=""
  local selected_container=""

  if [[ -z "$pod_name" ]]; then
    echo "Pods:"
    local pods=($(oc get pods -o jsonpath='{.items[*].metadata.name}'))
    local index=0
    for pod in "${pods[@]}"; do
      echo "$index) $pod"
      ((index++))
    done
    echo "Enter the pod number or type 'ALL':"
    read input
    if [[ "$input" == "ALL" ]]; then
      selected_pod="ALL"
    else
      selected_pod="${pods[$input]}"
    fi
  else
    selected_pod="$pod_name"
  fi

  if [[ -z "$container_name" ]]; then
    echo "Containers in $selected_pod:"
    local containers=($(oc get pods "$selected_pod" -o jsonpath='{.spec.containers[*].name}'))
    local index=0
    for container in "${containers[@]}"; do
      echo "$index) $container"
      ((index++))
    done
    echo "Enter the container number or type 'ALL':"
    read input
    if [[ "$input" == "ALL" ]]; then
      selected_container="ALL"
    else
      selected_container="${containers[$input]}"
    fi
  else
    selected_container="$container_name"
  fi

  if [[ "$selected_pod" == "ALL" ]]; then
    if [[ "$selected_container" == "ALL" ]]; then
      oc describe pods
    else
      for pod in "${pods[@]}"; do
        echo "=============================="
        echo "Pod: $pod - Container: $selected_container"
        echo "=============================="
        oc describe pod "$pod" -c "$selected_container"
      done
    fi
  else
    if [[ "$selected_container" == "ALL" ]]; then
      for container in "${containers[@]}"; do
        echo "=============================="
        echo "Pod: $selected_pod - Container: $container"
        echo "=============================="
        oc describe pod "$selected_pod" -c "$container"
      done
    else
      oc describe pod "$selected_pod" -c "$selected_container"
    fi
  fi
}; # openshift_describe_container my-pod my-container

