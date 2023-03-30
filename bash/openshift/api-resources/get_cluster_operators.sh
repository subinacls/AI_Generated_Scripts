"""
This function uses the oc command-line tool to retrieve a list of all ClusterOperators in the current OpenShift cluster. It does not take any parameters.

You can use this function by calling it like this:

  get_cluster_operators

This will output a table of information about all ClusterOperators in the current OpenShift cluster. You can customize the output by using various flags with the oc get clusteroperators command, such as -o wide to include additional information about each operator.
"""

function get_cluster_operators() {
  oc get clusteroperators
}; #get_cluster_operators
