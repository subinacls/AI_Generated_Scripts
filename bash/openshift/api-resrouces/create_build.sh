"""
This function takes two parameters:

project: the name of the OpenShift project to create the build in
source_url: the URL of the source code repository to build
The function uses the oc command-line tool to create a new build in the specified project, using the specified source URL. Note that this function assumes you have already logged in to OpenShift and selected the appropriate project.

You can use this function by calling it with the appropriate parameters, like this:

create_build myproject https://github.com/myuser/myapp.git

"""

function create_build() {
  local project=$1
  local source_url=$2

  oc new-build $source_url -n $project
}; # create_build myproject https://github.com/myuser/myapp.git
