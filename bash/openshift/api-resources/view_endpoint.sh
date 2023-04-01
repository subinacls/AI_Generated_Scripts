"""
This function takes two parameters:

namespace (optional): the name of the OpenShift namespace to view endpoints in. If not provided, the current project will be used.
endpoint_name (optional): the name of the specific endpoint to view. If not provided, the user will be prompted to select one.
The function first checks if a specific endpoint was provided. If not, it prompts the user to select one from a list of all endpoints in the specified namespace. Once an endpoint has been selected, the function retrieves the endpoint's subsets in JSON format using oc get endpoint and pipes the output to jq to extract and display only the .subsets section.

You can use this function by calling it with the appropriate parameters, like this:

Copy code
view_endpoint myproject myendpoint
This will display the .subsets section of the myendpoint endpoint in the myproject project. If no endpoint is provided, the function will prompt the user to select one from a list of all endpoints in the project. Example output might look like this:

$ view_endpoint myproject
No Endpoint provided. Please select one from the list below:
1. endpoint-1
2. endpoint-2
Enter the number of the Endpoint to view: 2
[
  {
    "addresses": [
      {
        "ip": "10.0.0.1"
      },
      {
        "ip": "10.0.0.2"
      }
    ],
    "ports": [
      {
        "name": "http",
        "port": 8080,
        "protocol": "TCP"
      }
    ]
  }
]
"""function view_endpoint() {
  local namespace=${1:-$(oc project -q)}
  local endpoint_name=$2

  if [ -z "$endpoint_name" ]; then
    # If no endpoint name was provided, prompt the user to select one
    echo "No Endpoint provided. Please select one from the list below:"
    oc get endpoints -n $namespace --no-headers | awk '{print NR ". " $1}'
    read -p "Enter the number of the Endpoint to view: " selection
    endpoint_name=$(oc get endpoints -n $namespace --no-headers | awk -v sel="$selection" 'NR==sel{print $1}')
    if [ -z "$endpoint_name" ]; then
      echo "Invalid selection."
      return 1
    fi
  fi

  oc get endpoint $endpoint_name -n $namespace -o json | jq '.subsets'
}; # view_endpoint myproject myendpoint
