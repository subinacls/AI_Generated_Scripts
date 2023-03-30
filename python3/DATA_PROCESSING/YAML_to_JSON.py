#!/usr/bin/env python3
import sys
import yaml
import json

class YamlToJsonConverter:
    def __init__(self):
        pass

    def convert(self, input_stream, output_stream):
        try:
            yaml_data = yaml.safe_load(input_stream)
            json_data = json.dumps(yaml_data, indent=2)
            output_stream.write(json_data)
        except Exception as e:
            print(f"Error converting YAML to JSON: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    if sys.stdin.isatty():
        print("Usage: python3 <yaml-file> | python3 yaml_to_json.py")
        sys.exit(1)

    converter = YamlToJsonConverter()
    converter.convert(sys.stdin, sys.stdout)

"""
You can use this class by piping YAML input to it through the command line, like this:

  python3 yaml_to_json.py < input.yaml > output.json

Alternatively, you can use it with a YAML file:

  python3 yaml_to_json.py input.yaml > output.json

In both cases, the class reads from stdin and writes to stdout.
"""
