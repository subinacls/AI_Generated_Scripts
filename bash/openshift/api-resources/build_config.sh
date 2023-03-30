"""
This function takes four parameters:

project: the name of the OpenShift project to create the build config in
bc_name: the name to give the build config object
source_type: the type of source code repository to use (e.g. git, binary, etc.)
source_url: the URL of the source code repository to use
The function uses the oc command-line tool to create a new build config in the specified project, using the specified source type, source URL, and build config name. Note that this function assumes you have already logged in to OpenShift and selected the appropriate project.

You can use this function by calling it with the appropriate parameters, like this:

  create_build_config myproject mybuildconfig git https://github.com/myuser/myapp.git

This will create a new build config in the myproject project, using the source code from
  https://github.com/myuser/myapp.git repository
and the git source type. The build config will be named mybuildconfig.

"""

function create_build_config() {
  local project=$1
  local bc_name=$2
  local source_type=$3
  local source_url=$4

  oc new-build-config $source_type $source_url --name=$bc_name -n $project
}; #create_build_config myproject mybuildconfig git https://github.com/myuser/myapp.git

