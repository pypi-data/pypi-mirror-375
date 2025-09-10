#!/usr/bin/python3
import sys
import argparse
import yaml
import pyflowapi


def main(argv):
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--config", "-c", type=str, required=False,
                           default="pyflowapi-server.yaml",
                           help="Configuration file")

    args = argparser.parse_args(argv)

    with open(args.config, "r") as f:
        d = f.read()
        config = yaml.safe_load(d)

    server = pyflowapi.server.Server(config)
    server.run()


if __name__ == "__main__":
    main(sys.argv[1:])
