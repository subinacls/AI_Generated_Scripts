"""
This function takes two parameters:

namespace (optional): the name of the OpenShift namespace to view deploymentconfigs in. 
If not provided, the current project will be used. dc_name (optional): the name of the 
specific deploymentconfig to view. If not provided, the user will be prompted to select one.
The function first checks if a specific deploymentconfig was provided. If not, it prompts 
the user to select one from a list of all deploymentconfigs in the specified namespace. 
Once a deploymentconfig has been selected, the function retrieves the deploymentconfig's 
specification in JSON format using oc get dc and pipes the output to jq to extract and 
display only the .spec section.

You can use this function by calling it with the appropriate parameters, like this:

  view_deploymentconfig myproject mydeploymentconfig

This will display the .spec section of the mydeploymentconfig deploymentconfig in the myproject project. If no deploymentconfig is provided, the function will prompt the user to select one from a list of all deploymentconfigs in the project. Example output might look like this:

EXAMPLE:
$ view_deploymentconfig myproject
No DeploymentConfig provided. Please select one from the list below:
1. deploymentconfig-1
2. deploymentconfig-2
Enter the number of the DeploymentConfig to view: 2
{
  "replicas": 3,
  "selector": {
    "app": "myapp"
  },
  "strategy": {
    "rollingParams": {
      "intervalSeconds": 1,
      "maxSurge": "25%",
      "maxUnavailable": "25%"
    },
    "type": "Rolling"
  },
  "template": {
    "metadata": {
      "labels": {
        "app": "myapp"
      }
    },
    "spec": {
      "containers": [
        {
          "image": "myimage:latest",
          "imagePullPolicy": "Always",
          "name": "myapp",
          "ports": [
            {
              "containerPort": 8080,
              "protocol": "TCP"
            }
          ],
          "resources": {},
          "terminationMessagePath": "/dev/termination-log",
          "terminationMessagePolicy": "File"
        }
      ],
      "dnsPolicy": "ClusterFirst",
      "restartPolicy": "Always",
      "schedulerName": "default-scheduler",
      "securityContext": {},
      "terminationGracePeriodSeconds": 30
    }
  }
}
"""

function view_deploymentconfig() {
  local namespace=${1:-$(oc project -q)}
  local dc_name=$2

  if [ -z "$dc_name" ]; then
    # If no DeploymentConfig name was provided, prompt the user to select one
    echo "No DeploymentConfig provided. Please select one from the list below:"
    oc get dc -n $namespace --no-headers | awk '{print NR ". " $1}'
    read -p "Enter the number of the DeploymentConfig to view: " selection
    dc_name=$(oc get dc -n $namespace --no-headers | awk -v sel="$selection" 'NR==sel{print $1}')
    if [ -z "$dc_name" ]; then
      echo "Invalid selection."
      return 1
    fi
  fi

  oc get dc $dc_name -n $namespace -o json | jq '.spec'
}; #view_deploymentconfig myproject mydeploymentconfig
