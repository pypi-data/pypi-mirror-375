import configparser
import os

import click

from edos.settings import conf


def configure(
    token,
    aws_access_key,
    aws_secret_key,
    swarmpit_token,
    fakturoid_token,
    clockify_token,
):
    conf.DIGITAL_OCEAN_CONFIG = {"token": token}
    conf.AWS_CONFIG = {
        "aws_access_key": aws_access_key,
        "aws_secret_key": aws_secret_key,
    }
    conf.SWARMPIT_CONFIG = {"token": swarmpit_token}
    conf.INVOICE_CONFIG = {
        "faturoid_api_key": fakturoid_token,
        "clockify_api_key": clockify_token,
    }


def get_do_token() -> str:
    previous_token = conf.DIGITAL_OCEAN_CONFIG.get("token", "")
    click.echo(
        (
            "This tool needs your DigitalOcean API token for:\n"
            "    - Creating databases\n"
            "\n"
            "You can get your access token at:\n"
            "    https://cloud.digitalocean.com/settings/api/tokens"
        )
    )
    if previous_token:
        click.echo((f"Your current token: {previous_token}\n" "(Enter empty string to use your current token)"))
    token = ""
    while not token:
        token = click.prompt(
            click.style("Your DO token", fg="yellow"),
            default=previous_token,
            show_default=False,
            type=str,
        )
    return token


def get_aws_keys() -> tuple[str, str]:
    previous_aws_access_key = conf.AWS_CONFIG.get("aws_access_key", "")
    previous_aws_secret_key = conf.AWS_CONFIG.get("aws_secret_key", "")
    click.echo(("This tool needs your AWS AccessKey and SecretKey for:\n" "    - Creating spaces"))
    if previous_aws_access_key:
        click.echo(
            (f"Your current access_key: {previous_aws_access_key}\n" "(Enter empty string to use your current token)")
        )
    aws_access_key = ""
    while not aws_access_key:
        aws_access_key = click.prompt(
            click.style("Your AWS access key", fg="yellow"),
            default=previous_aws_access_key,
            show_default=False,
            type=str,
        )
    if previous_aws_secret_key:
        click.echo(
            (f"Your current secret_key: {previous_aws_secret_key}\n" "(Enter empty string to use your current token)")
        )
    aws_secret_key = ""
    while not aws_secret_key:
        aws_secret_key = click.prompt(
            click.style("Your AWS secret key", fg="yellow"),
            default=previous_aws_secret_key,
            show_default=False,
            type=str,
        )
    return aws_access_key, aws_secret_key


def get_swarmpit_token() -> str:
    previous_token = conf.SWARMPIT_CONFIG.get("token", "")
    click.echo(
        (
            "This tool needs your Swarmpit bearer API token for:\n"
            "    - Getting stats services (memory and reservation)\n"
            "\n"
            "You can get your access token at:\n"
            "    https://swarmpit.doc.endevel.cz/#/account-settings "
            "      or in our Lastpass\n"
            "(paste without Bearer keyword)"
        )
    )
    if previous_token:
        click.echo((f"Your current token: {previous_token}\n" "(Enter empty string to use your current token)"))
    token = ""
    while not token:
        token = click.prompt(
            click.style("Your Swarmpit token", fg="yellow"),
            default=previous_token,
            show_default=False,
            type=str,
        )
    return token


def prompt_function(prompt_message: str, previous_token: str) -> str:
    if previous_token:
        click.echo((f"Your current token: {previous_token}\n" "(Enter empty string to use your current token)"))
    token = ""
    while not token:
        token = click.prompt(
            click.style(prompt_message, fg="yellow"),
            default=previous_token,
            show_default=False,
            type=str,
        )
    return token


def get_fakturoid_information() -> tuple[str, str, str]:
    click.echo(
        "For generating invoices, this tool needs your:\n"
        "    - Fakturoid API key\n"
        "    - Fakturoid account email\n"
        "    - Fakturoid account slug (when you log-in, you see "
        'the slug in the url, "stepanbinko" for example)\n'
    )
    api_key = prompt_function("Your Fakturoid API key", conf.INVOICE_CONFIG.get("fakturoid_api_key", ""))
    account_email = prompt_function(
        "Your Fakturoid account email",
        conf.INVOICE_CONFIG.get("fakturoid_account_email", ""),
    )
    account_slug = prompt_function(
        "Your Fakturoid account slug",
        conf.INVOICE_CONFIG.get("fakturoid_account_slug", ""),
    )
    return api_key, account_email, account_slug


def get_clockify_token() -> str:
    previous_token = conf.INVOICE_CONFIG.get("clockify_api_key", "")
    click.echo("For generating invoices, this tool needs your clockify API key:\n")
    if previous_token:
        click.echo((f"Your current token: {previous_token}\n" "(Enter empty string to use your current token)"))
    token = ""
    while not token:
        token = click.prompt(
            click.style("Your clockify token", fg="yellow"),
            default=previous_token,
            show_default=False,
            type=str,
        )
    return token


def configure_interactive():
    click.echo(click.style("Welcome to the EDOS configuration tool", bold=True))

    click.echo()

    config_file = configparser.ConfigParser()
    config_file.add_section("DO")
    token = get_do_token()
    config_file.set("DO", "token", token)

    click.echo()

    config_file.add_section("AWS")
    aws_access_key, aws_secret_key = get_aws_keys()
    config_file.set("AWS", "aws_access_key", aws_access_key)
    config_file.set("AWS", "aws_secret_key", aws_secret_key)

    click.echo()

    config_file.add_section("SWARMPIT")
    token = get_swarmpit_token()
    config_file.set("SWARMPIT", "token", token)

    click.echo()
    config_file.add_section("INVOICE")
    (
        fakturoid_api_key,
        fakturoid_account_email,
        fakturoid_account_slug,
    ) = get_fakturoid_information()
    clockify_token = get_clockify_token()
    config_file.set("INVOICE", "fakturoid_api_key", fakturoid_api_key)
    config_file.set("INVOICE", "fakturoid_account_email", fakturoid_account_email)
    config_file.set("INVOICE", "fakturoid_account_slug", fakturoid_account_slug)
    config_file.set("INVOICE", "clockify_api_key", clockify_token)

    click.echo(f"Writing configuration file: {conf.CONFIG_PATH}")
    os.makedirs(conf.USER_DIR.user_config_dir, exist_ok=True)
    with open(conf.CONFIG_PATH, "w") as git_configfile:
        config_file.write(git_configfile)
    conf.reload()

    click.echo(click.style(">> Done <<", fg="green"))
