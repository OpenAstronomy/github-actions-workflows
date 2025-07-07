# /// script
# requires-python = "==3.12"
# dependencies = [
#     "pyyaml==6.0.2",
# ]
# ///
import json
import os
import sys

import yaml

GITHUB_ENV = os.getenv("GITHUB_ENV")
if GITHUB_ENV is None:
    raise ValueError("GITHUB_ENV not set. Must be run inside GitHub Actions.")

DELIMITER = "EOF"


def set_env(env):

    env = yaml.load(env, Loader=yaml.BaseLoader)
    print(json.dumps(env, indent=2))

    if not isinstance(env, dict):
        title = "`env` must be mapping"
        message = f"`env` must be mapping of env variables to values, got type {type(env)}"
        print(f"::error title={title}::{message}")
        exit(1)

    for k, v in env.items():

        if not isinstance(v, str):
            title = "`env` values must be strings"
            message = f"`env` values must be strings, but value of {k} has type {type(v)}"
            print(f"::error title={title}::{message}")
            exit(1)

        v = v.split("\n")

        with open(GITHUB_ENV, "a") as f:
            if len(v) == 1:
                f.write(f"{k}={v[0]}\n")
            else:
                for line in v:
                    assert line.strip() != DELIMITER
                f.write(f"{k}<<{DELIMITER}\n")
                for line in v:
                    f.write(f"{line}\n")
                f.write(f"{DELIMITER}\n")

        print(f"{k} written to GITHUB_ENV")


if __name__ == "__main__":
    set_env(sys.argv[1])
