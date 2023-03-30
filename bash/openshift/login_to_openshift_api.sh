function login_to_openshift_api() {
  local USERNAME="${1:-myusername}";
  local PASSWORD="${2:-mycoolpasssword}";
  local APILOCATION="${3:-api.openshift.com:443}";
  local NAMESPACE="${4:-defaultnamespace}";
  # Authenticate with OpenShift API using provided credentials;
  oc login --username=$username --password=$PASSWORD $APILOCATION;
  # Set the active namespace;
  oc project $NAMESPACE;
};# login_to_openshift_api testuser testpasswd https://api.localhost.local:8443 mytestnamespace;

login_to_openshift_api testuser testpasswd https://api.localhost.local:8443 mytestnamespace
