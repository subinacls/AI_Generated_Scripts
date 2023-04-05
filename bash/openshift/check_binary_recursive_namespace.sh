check_binary_recursive_namespace() {
  binary=$1
  for pod in $(kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'); do
    for container in $(kubectl get pods $pod -o jsonpath='{range .spec.containers[*]}{.name}{"\n"}{end}'); do
      output=$(kubectl exec -it $pod -c $container -- type $binary 2>&1)
      if [[ $output == *"not found"* ]]; then
        echo -e "\033[1;31m$pod : $container - FAIL\033[0m"
      else
        echo -e "\033[1;32m$pod : $container - PASS\033[0m"
      fi
    done
  done
}; # check_binary_recursive_namespace openssl
