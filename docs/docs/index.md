# Description

System to store application configuration

## Motivation

To support a release system that can store references to various application artifacts we need a config system that can store environment variables needed by a specific application (i.e. what is put into `.env` file). Specifically, we want to make the configurations immutable so once they are refered to from a release system they won't change.


## Features

* Uses AWS Parameter Store as a storage layer for parameters
* Enforces each parameter needs to be assigned to an application identifier (`app-name`), an environment identifier (`env`) and a integer version (`ver-number`)
* Once parameters are written with such combination of identifiers `acme-config` prevents from overwriting them.
* Allows to retreive parameters for a given combination of (`app-name`, `env` and `ver-number`) and stores it in a local file in `.env` file format convenient for editing.
* Allows to set parameters from `.env` file specified at a file path.

## Example usage

Requires setup of a default AWS profile e.g. via `aws sso login`. Can be specified via `AWS_PROFILE` env var.

## To set

    ac set -app-name acme-config -env dev -ver-number 1 --params-path .env

## To fetch

    ac fetch -app-name acme-config -env dev -ver-number 1