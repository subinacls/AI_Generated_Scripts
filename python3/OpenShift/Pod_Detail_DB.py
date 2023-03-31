import json
import os
import subprocess

class PodDB:
    def __init__(self, namespace):
        self.namespace = namespace
        self.pods = {}
        self.update()

    def update(self):
        # Run the "oc get pods" command with the "-o json" flag to get the JSON output
        output = subprocess.check_output(['oc', 'get', 'pods', '-n', self.namespace, '-o', 'json'])
        pods_json = json.loads(output)

        # Parse the JSON data and store it in the "pods" dictionary
        for pod in pods_json['items']:
            name = pod['metadata']['name']
            self.pods[name] = pod

    def search(self, query):
        # Search for a pod with a matching name
        if query in self.pods:
            return self.pods[query]

        # Search for a pod with a matching label
        for pod in self.pods.values():
            labels = pod['metadata'].get('labels', {})
            if query in labels.values():
                return pod

        return None

    def dump(self, filename):
        # Dump the contents of the "pods" dictionary to a file
        with open(filename, 'w') as f:
            json.dump(self.pods, f)

    def load(self, filename):
        # Load the contents of the "pods" dictionary from a file
        if os.path.isfile(filename):
            with open(filename) as f:
                self.pods = json.load(f)
        else:
            self.pods = {}

# Example usage
pod_db = PodDB('myproject')
pod_db.update()
pod_db.dump('pods.json')
pod = pod_db.search('mypod')
print(json.dumps(pod, indent=4))
