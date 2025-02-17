import os
import argparse
import logging

from dotenv import dotenv_values

from .aws_parameter_store import (
    fetch_parameters,
    set_parameters,
    set_default_version,
    get_default_version,
)


logger = logging.getLogger(__name__)


def save_fetched_parameters(parameters, app_name, env, ver_number):
    """
    Save fetched parameters to a file.
    This function takes a dictionary of parameters and saves them to a file
    named using the provided application name, environment, and version number.
    Each parameter is written in the format `key=value`.

    Parameters:
        parameters (dict): A dictionary containing the parameters to be saved.
        app_name (str): The name of the application.
        env (str): The environment (e.g., 'dev', 'prod').
        ver_number (str): The version number of the application.
    Returns:
        None
    """

    logger.info(parameters)
    with open(f"{app_name}.{env}.{ver_number}.env", "w") as f:
        for key, value in parameters.items():
            f.write(f"{key}={value}\n")
    logger.info(f"Parameters saved to {app_name}.{env}.{ver_number}.env")


def load_params(params_path):
    return dotenv_values(params_path)


def add_main_arguments(parser):
    parser.add_argument("-app-name", required=True, type=str, help="Application name")
    parser.add_argument("-env", required=True, type=str, help="Environment")
    parser.add_argument("-ver-number", required=True, type=int, help="Version number")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ac", description="System to store application configuration"
    )
    subparsers = parser.add_subparsers(dest="command")

    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Fetch parameters",
        description="Fetch parameters from AWS AWS Parameter Store, print them to stdout, and save them to a file in CWD",
    )
    add_main_arguments(fetch_parser)

    set_parser = subparsers.add_parser(
        "set",
        help="Set parameters",
        description="Set parameters in AWS Parameter Store from a .evn file under the provided path",
    )
    add_main_arguments(set_parser)
    set_parser.add_argument(
        "--params-path", required=True, help="Path to .evn file to set as parameters"
    )

    set_version_parser = subparsers.add_parser(
        "set-version",
        help="Set version",
        description="Set default version number to use for (app-name, env) combination",
    )
    add_main_arguments(set_version_parser)

    get_version_parser = subparsers.add_parser(
        "get-version",
        help="Get version",
        description="Get default version number for (app-name, env) combination",
    )
    get_version_parser.add_argument(
        "-app-name", required=True, type=str, help="Application name"
    )
    get_version_parser.add_argument("-env", required=True, type=str, help="Environment")

    return parser.parse_args()


def main_logic(args):
    if args.command == "fetch":
        parameters = fetch_parameters(args.app_name, args.env, args.ver_number)
        save_fetched_parameters(parameters, args.app_name, args.env, args.ver_number)
    elif args.command == "set":
        params_dict = load_params(args.params_path)
        set_parameters(args.app_name, args.env, args.ver_number, params_dict)
        logger.info("Parameters set successfully")
    elif args.command == "set-version":
        set_default_version(args.app_name, args.env, args.ver_number)
        logger.info("Default version set successfully")
    elif args.command == "get-version":
        version = get_default_version(args.app_name, args.env)
        logger.info(
            f"Default version for `{args.app_name}` in `{args.env}` is `{version}`"
        )
        print(version)


def main():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO)
    args = parse_args()
    main_logic(args)


if __name__ == "__main__":
    main()
