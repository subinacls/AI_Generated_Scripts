function create_deployment() {
  local project=$1
  local dc_name=$2
  local image=$3

  oc new-app $image --name=$dc_name -n $project
}
