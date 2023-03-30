"""
This function takes four parameters:

project: the name of the OpenShift project to create the build pipeline in
pipeline_name: the name to give the build pipeline object
bc_name: the name of the build config to use
output_image: the name of the output image for the build pipeline
The function uses the oc command-line tool to create a new build pipeline in the specified project, using the specified build config, output image, and build pipeline name. Note that this function assumes you have already logged in to OpenShift and selected the appropriate project.

You can use this function by calling it with the appropriate parameters, like this:

  create_build_pipeline myproject mypipeline mybuildconfig myoutputimage

This will create a new build pipeline in the myproject project, using the specified build config, output image, and pipeline name.
"""

function create_build_pipeline() {
  local project=$1
  local pipeline_name=$2
  local bc_name=$3
  local output_image=$4

  oc new-build-pipeline $pipeline_name --build-config=$bc_name --output-image=$output_image -n $project
}; #create_build_pipeline myproject mypipeline mybuildconfig myoutputimage
