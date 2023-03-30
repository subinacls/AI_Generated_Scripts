"""
This function takes two parameters:

namespace (optional): the name of the OpenShift namespace to view configmaps in. If not provided, the current project will be used.
configmap (optional): the name of the specific configmap to view. If not provided, the user will be prompted to select one.
The function first checks if a specific configmap was provided. If not, it prompts the user to select one from a list of all configmaps in the specified namespace. Once a configmap has been selected, the function retrieves the configmap's data in JSON format using oc get configmap and pipes the output to jq to extract and display only the .data section.

You can use this function by calling it with the appropriate parameters, like this:

  view_configmap myproject myconfigmap

This will display the .data section of the myconfigmap configmap in the myproject project. If no configmap is provided, the function will prompt the user to select one from a list of all configmaps in the project. Example output might look like this:

EXAMPLE OUTPUT:
  $ view_configmap myproject
  No configmap provided. Please select one from the list below:
  1. configmap-1
  2. configmap-2
  Enter the number of the configmap to view: 2
  {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
  }
"""

function view_configmap() {
  local namespace=${1:-$(oc project -q)}
  local configmap=$2

  if [ -z "$configmap" ]; then
    # If no configmap was provided, prompt the user to select one
    echo "No configmap provided. Please select one from the list below:"
    oc get configmaps -n $namespace --no-headers | awk '{print NR ". " $1}'
    read -p "Enter the number of the configmap to view: " selection
    configmap=$(oc get configmaps -n $namespace --no-headers | awk -v sel="$selection" 'NR==sel{print $1}')
    if [ -z "$configmap" ]; then
      echo "Invalid selection."
      return 1
    fi
  fi

  oc get configmap $configmap -n $namespace -o json | jq '.data | .. | . ' | xargs -0 echo -e;
}; # view_configmap myproject myconfigmap
