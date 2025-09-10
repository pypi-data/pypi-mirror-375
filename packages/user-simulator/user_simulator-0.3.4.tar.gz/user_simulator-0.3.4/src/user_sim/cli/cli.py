import os
import yaml
import sys
import argparse
from argparse import Namespace
from chatbot_connectors import parse_connector_params

def load_yaml_arguments(project_path):
    files = os.listdir(project_path)

    run_file = next((f for f in files if f in ["run.yml", "run.yaml"]), None)

    if not run_file:
        raise FileNotFoundError(f"Couldn't find run.yml file.")

    run_yaml_path = os.path.join(project_path, run_file)

    with open(run_yaml_path, 'r', encoding='utf-8') as f:
        yaml_args = yaml.safe_load(f) or {}

        if "execution_parameters" in yaml_args:
            parameters = yaml_args.pop("execution_parameters") or []
            yaml_args.update({param: True for param in parameters})

    normalized = {}
    for k, v in yaml_args.items():
        normalized[k.replace("-", "_")] = v

    normalized["project_path"] = project_path
    return normalized


def parse_chat_arguments(argv=None) -> Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="User Simulator - Converses with chatbots to test capabilities")

    default_output_dir = "output"
    default_technology = "taskyto"

    parser.add_argument(
        "-rfy",
        "--run-from-yaml",
        dest="run_from_yaml",
        type=str,
        default=None,
        help=(
             "Path to the project folder which contains run.yaml."
             "Runs Sensei with CLI arguments contained in the run.yaml file."
             "Example: --run-from-yaml /path/to/project/folder"
        ),
    )

    parser.add_argument(
        "-ic",
        "--ignore-cache",
        dest="ignore_cache",
        action="store_true",
        help="Cache is ignored during the testing process.",
    )

    parser.add_argument(
        "-t",
        "--technology",
        type=str,
        default=default_technology,
        help=f"Chatbot technology to use (default: {default_technology})",
    )

    parser.add_argument(
        "-cp",
        "--connector-params",
        dest="connector_params",
        type=str,
        help=(
            'Connector parameters as JSON string or key=value pairs separated by commas. '
            'Examples: \'{"base_url": "http://localhost", "port": 8080}\' or '
            '"base_url=http://localhost,port=8080". '
            "Use --list-connector-params <technology> to see required parameters for each connector."
        ),
    )

    parser.add_argument(
        "-pp", "--project-path",
        dest="project_path",
        type=str,
        default=None,
        help="The project path where all testing content is stored for a specific project."
    )

    parser.add_argument(
        "-up", "--user-profile",
        dest="user_profile",
        type=str,
        default=None,
        help="Name of the user profile YAML or the folder containing user profiles to use in the testing process."
    )

    #todo: extract
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=default_output_dir,
        help=f"Output directory for results and profiles (default: {default_output_dir})",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    parser.add_argument(
        "-cc",
        "--clean-cache",
        dest="clean_cache",
        action="store_true",
        help=f"Cache is cleaned after the testing process",
    )

    parser.add_argument(
        "-uc",
        "--update-cache",
        dest="update_cache",
        action="store_true",
        help=f"Cache is updated with new content if previous cache was saved",
    )

    #todo: implement
    parser.add_argument(
        "--list-connector-params",
        dest="list_connector_params",
        type=str,
        metavar="TECHNOLOGY",
        help="List the available parameters for a specific chatbot technology and exit",
    )

    #todo: implement
    parser.add_argument(
        "--list-connectors",
        dest="list_connectors",
        action="store_true",
        help="List all available chatbot connector technologies and exit",
    )

    args, unknown = parser.parse_known_args(argv) # if argv, uses argv arguments

    if args.run_from_yaml:
        # Detect if the user passed other non-default options besides the YAML
        # Define here the "default" values that should NOT be considered as "user passed something extra"
        defaults_guard = {
            "technology": default_technology,
            "output": default_output_dir,
            "connector_params": None,
            "project_path": None,
            "user_profile": None,
            "verbose": False,
            "clean_cache": False,
            "ignore_cache": False,
            "update_cache": False,
            "list_connector_params": None,
            "list_connectors": False,
        }


        non_default_passed = []
        for k, default_v in defaults_guard.items():
            if k == "run_from_yaml":
                continue
            current_v = getattr(args, k, None)
            if current_v != default_v:
                non_default_passed.append(k)

        if non_default_passed or unknown:
            parser.error(
                "No other arguments can be provided when using --run-from-yaml. "
                f"Detected: {', '.join(non_default_passed + unknown)}"
            )

        yaml_args = load_yaml_arguments(args.run_from_yaml)

        # Minimum default values if the YAML does not provide them
        yaml_defaults = {
            "technology": default_technology,
            "connector_params": None,
            "user_profile": None,
            "output": default_output_dir,
            "verbose": False,
            "clean_cache": False,
            "ignore_cache": False,
            "update_cache": False,
        }
        for k, v in yaml_defaults.items():
            yaml_args.setdefault(k, v)

        return argparse.Namespace(**yaml_args)


    # Normal CLI mode: validate required arguments
    required_args = ["technology", "user_profile", "connector_params"]
    missing = [arg for arg in required_args if getattr(args, arg) in (None, "")]
    if missing:
        parser.error(
            "The following arguments are required when not using --run-from-yaml: "
            + ", ".join(missing)
        )

    return args