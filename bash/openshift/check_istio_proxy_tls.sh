function check_istio_proxy_tls() {
  local deployment=$1
  local namespace=$2
  
  # Check if the deployment exists
  if ! oc get deployment $deployment -n $namespace >/dev/null 2>&1; then
    echo "Error: deployment $deployment not found in namespace $namespace"
    return 1
  fi
  
  # Check if Istio sidecar is injected
  local istio_sidecar=$(oc get deployment $deployment -n $namespace -o jsonpath='{.spec.template.metadata.annotations.sidecar\.istio\.io/inject}')
  if [ "$istio_sidecar" != "true" ]; then
    echo "Istio sidecar not injected in deployment $deployment in namespace $namespace"
    return 1
  fi
  
  # Check if TLS or mTLS is configured
  local tls_mode=$(oc get deployment $deployment -n $namespace -o jsonpath='{.spec.template.metadata.annotations.sidecar\.istio\.io/tls\.mode}')
  if [ "$tls_mode" == "istio" ]; then
    echo "Istio proxy is configured for mTLS in deployment $deployment in namespace $namespace"
  elif [ "$tls_mode" == "simple" ]; then
    echo "Istio proxy is configured for TLS in deployment $deployment in namespace $namespace"
  else
    echo "Istio proxy TLS mode not configured in deployment $deployment in namespace $namespace"
    return 1
  fi
}
