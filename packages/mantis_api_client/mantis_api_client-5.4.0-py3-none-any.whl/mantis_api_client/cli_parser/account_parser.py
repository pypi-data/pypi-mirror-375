# -*- coding: utf-8 -*-
import argparse
import getpass
import os
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from typing import Any
from typing import List
from urllib.parse import parse_qs
from urllib.parse import urlparse

import requests
from mantis_authz import jwt
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree

import mantis_api_client
import mantis_api_client.dataset_api as dataset_api
import mantis_api_client.scenario_api as scenario_api
from mantis_api_client import user_api
from mantis_api_client.config import mantis_api_client_config
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored


class Version:
    def __init__(self, str_vers: str) -> None:
        try:
            self.major, self.minor, self.patch = str_vers.split(".", 2)
        except Exception as e:
            raise Exception(
                "Bad version format for '{}': 'X.Y.Z' expected. Error: {}".format(
                    str_vers, e
                )
            )


#
# 'status' related functions
#
def status_handler(args: Any) -> None:  # noqa: C901
    """Get platform status."""

    exit_code = 0

    client_version = mantis_api_client.__version__
    client_vers = Version(str_vers=client_version)
    client_fullversion = mantis_api_client.__fullversion__
    print(
        f"[+] mantis_api_client version: {client_version} ({client_fullversion})".format(
            client_version
        )
    )

    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if active_profile_domain:
        print(f"[+] Authenticated to {active_profile_domain}")
    else:
        print(
            colored(
                "[+] Not authenticated, you need to execute 'mantis account login'",
                "red",
            )
        )
        sys.exit(1)
    print("[+] APIs status")

    # Dataset API
    print("  [+] Dataset API")
    print("    [+] address: {}".format(mantis_api_client_config.dataset_api_url))
    try:
        dataset_api_version = dataset_api.get_version()
        dataset_vers = Version(str_vers=dataset_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(dataset_api_version))
        if dataset_vers.major != client_vers.major:
            exit_code = 1
            print(
                "    [-] "
                + colored(
                    "Error: Dataset API major version ({}) mismatchs with mantis_api_client major version ({})".format(
                        dataset_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # Scenario API
    print("  [+] Scenario API")
    print("    [+] address: {}".format(mantis_api_client_config.scenario_api_url))
    try:
        scenario_api_version = scenario_api.get_version()
        scenario_vers = Version(str_vers=scenario_api_version)
        cyber_range_version = scenario_api.get_cyberrange_version()
    except requests.exceptions.ConnectionError:
        exit_code = 1
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(scenario_api_version))
        print("    [+] Cyber Range version: {}".format(cyber_range_version))
        if scenario_vers.major != client_vers.major:
            exit_code = 1
            print(
                "    [-] "
                + colored(
                    "Error: Scenario API major version ({}) mismatchs with mantis_api_client major version ({})".format(
                        scenario_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # User API
    print("  [+] Backoffice API")
    print("    [+] address: {}".format(mantis_api_client_config.user_api_url))
    try:
        user_api_version = user_api.get_version()
        user_vers = Version(str_vers=user_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(user_api_version))
        if user_vers.major != client_vers.major:
            exit_code = 1
            print(
                "    [-] "
                + colored(
                    "Error: User API major version ({}) mismatchs with mantis_api_client major version ({})".format(
                        user_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    if exit_code != 0:
        sys.exit(exit_code)


#
# 'info' related functions
#
def info_handler(args: Any) -> None:  # noqa: C901
    """Get personal info."""

    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if not active_profile_domain:
        print("[+] Not authenticated")
        return

    console = Console(highlight=False)
    rprint = console.print
    active_tokens = get_oidc_client().get_active_tokens()
    access_token = jwt.get_unverified_claims(active_tokens["access_token"])
    id_token = jwt.get_unverified_claims(active_tokens["id_token"])

    sub_orgs = user_api.fetch_current_seats()
    sub_membership: dict[str, list[dict]] = {}
    sub_default_ws = get_oidc_client().get_default_workspace()
    # Handle case where the user pertains to an organization
    if sub_orgs:
        sub_wss = user_api.fetch_current_workspaces()
        for sub_org in sub_orgs:
            sub_org_wss: list[dict] = []
            sub_membership[sub_org["name"]] = sub_org_wss
            for sub_ws in sub_wss:
                if sub_org["id"] == sub_ws["organization_id"]:
                    sub_org_wss.append(sub_ws)

    sorted_scopes = ", ".join(sorted(access_token["scope"].split()))

    print(f"[+] Connected to {active_profile_domain}")
    print(f"  [+] Username: {id_token['preferred_username']}")
    print(f"  [+] Email: {id_token.get('email', 'N/A')}")
    if sub_orgs:

        def hl_activated_ws(ws: dict) -> str:
            if ws["id"] == sub_default_ws:
                return f"[bold]{ws['name']}[/bold]"
            return ws["name"]

        rprint(
            r"  \[+] Organization membership: {}".format(
                ", ".join(
                    "{} ({})".format(
                        org,
                        ", ".join(map(hl_activated_ws, org_wss)),
                    )
                    for org, org_wss in sub_membership.items()
                )
            )
        )
    print(f"  [+] Scopes: {sorted_scopes}")


#
# 'login_handler' handler
#
def login_handler(args: Any) -> None:
    oidc_client = get_oidc_client()
    # Parameters
    oidc_domain = args.domain
    username = args.username
    if args.password_stdin:
        password = sys.stdin.read().rstrip()
    elif args.password_fd:
        with os.fdopen(args.password_fd) as f:
            password = f.read().rstrip()
    elif args.password_file:
        password = args.password_file.read_text().rstrip()
    elif args.username:
        password = getpass.getpass()
    else:
        password = None

    scope = " ".join(
        [
            "openid",
            "offline_access",
            "groups",
            "profile",
            "email",
            "scenario:run",
        ]
    )
    redirect_uri = mantis_api_client_config.oidc.redirect_uri
    redirect_auto = redirect_uri.startswith("http")
    code_placeholder: List[str] = []
    if redirect_auto:
        thread = _init_create_callback_request_handler_thread(code_placeholder)
        thread.start()
    if username and password:
        token = oidc_client.token(
            oidc_domain, username, password, redirect_uri=redirect_uri, scope=scope
        )
    else:
        auth_url = oidc_client.auth_url(
            oidc_domain,
            redirect_uri=redirect_uri,
            scope=scope,
        )
        if shutil.which("xdg-open") is not None:
            subprocess.run(["xdg-open", auth_url])
            print(f"A web browser should have been opened for {oidc_domain!r}")
        else:
            print(
                f"Open this URL in a web browser in order to create an access token for M&NTIS:\n\n{auth_url}\n"
            )

        if redirect_auto:
            timeout = mantis_api_client_config.oidc.redirect_url_timeout
            print(f"Waiting callback for {timeout}s")
            thread.join(timeout)
            if thread.is_alive():
                print("Timeout exceeded, exiting")
                print("Access NOT granted")
                exit(1)
            code = code_placeholder[0]
        else:
            code = input("Paste the code displayed in the webpage: ")
        token = get_oidc_client().token(
            oidc_domain,
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
        )
    print("Access granted")
    oidc_client.configure_profile(oidc_domain, token["refresh_token"])

    # Handle case where the user does not pertain to an organization
    subject_workspaces = user_api.fetch_current_workspaces()
    subject_organizations = user_api.fetch_current_seats()
    subject_orgs_wss = [
        (sub_org, sub_ws)
        for sub_org in subject_organizations
        for sub_ws in subject_workspaces
        if sub_ws["organization_id"] == sub_org["id"]
    ]
    selected_idx: int | None = None
    if args.workspace:
        for i, (_, ws) in enumerate(subject_orgs_wss):
            if args.workspace == ws["id"]:
                selected_idx = i
    console = Console()
    if selected_idx is None:
        match len(subject_orgs_wss):
            case 0:
                return
            case 1:
                selected_idx = 0
            case _:
                i = 1
                root = Tree(":file_folder:[yellow]Workspace memberships")
                for org in subject_organizations:
                    org_branch = root.add(f"Organization [magenta]{org['name']}")
                    for ws in subject_workspaces:
                        if ws["organization_id"] != org["id"]:
                            continue
                        org_branch.add(rf"[bold green]{i}[/bold green]. {ws['name']}")
                        i += 1
                console.print(root)
                selected_idx = (
                    int(
                        Prompt.ask(
                            "Select a default workspace",
                            choices=[str(k + 1) for k in range(len(subject_orgs_wss))],
                        )
                    )
                    - 1
                )
    selected_ws = subject_orgs_wss[selected_idx][1]
    console.print(f"Workspace [b green]{selected_ws['name']}[/b green] activated")

    oidc_client.configure_profile(
        oidc_domain, token["refresh_token"], selected_ws["id"]
    )


#
# 'logout_handler' handler
#
def logout_handler(args: Any) -> None:
    get_oidc_client().configure_profile(None)


def _init_create_callback_request_handler_thread(code_placeholder: list) -> Thread:
    class CallbackHTTPRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            query = urlparse(self.path).query
            if "error" in query:
                self.send_response(404)
            else:
                code = parse_qs(query)["code"][0]
                code_placeholder.append(code)
                self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                "<script>window.close()</script> Authorization {}. You may close this window.\r\n".format(
                    "failed" if "error" in query else "succeeded"
                ).encode()
            )

        def log_request(*args, **kwargs):
            # do nothing
            pass

    def serve_one_redirect_callback() -> None:
        with HTTPServer(
            (
                mantis_api_client_config.oidc.redirect_url.host,
                mantis_api_client_config.oidc.redirect_url.port,
            ),
            CallbackHTTPRequestHandler,
        ) as server:
            server.handle_request()

    return Thread(target=serve_one_redirect_callback, daemon=True)


def add_account_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # -------------------
    # --- login options
    # -------------------

    parser_account = subparsers.add_parser(
        "account",
        help="Authentication actions for M&NTIS CLI.",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_account = parser_account.add_subparsers()

    # 'status' command
    parser_status = subparsers_account.add_parser(
        "status",
        help="Get platform status",
        formatter_class=root_parser.formatter_class,
    )
    parser_status.set_defaults(func=status_handler)

    # 'info' command
    parser_info = subparsers_account.add_parser(
        "info", help="Get personal info", formatter_class=root_parser.formatter_class
    )
    parser_info.set_defaults(func=info_handler)

    parser_login = subparsers_account.add_parser(
        "login",
        help="Log into a M&ntis account",
        formatter_class=root_parser.formatter_class,
    )
    parser_login.add_argument(
        "--domain",
        help="The M&ntis cluster SSO domain (default: %(default)s)",
        default="mantis-platform.io",
    )
    parser_login.add_argument(
        "--username",
        "-u",
        help="Your M&ntis cluster SSO username",
    )
    parser_login_mex_group = parser_login.add_mutually_exclusive_group()
    parser_login_mex_group.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read your M&ntis cluster SSO password from stdin",
    )
    parser_login_mex_group.add_argument(
        "--password-fd",
        type=int,
        help="Read your M&ntis cluster SSO password from a descriptor",
    )
    parser_login_mex_group.add_argument(
        "--password-file",
        type=Path,
        help="Read your M&ntis cluster SSO password from a file",
    )
    parser_login.add_argument(
        "-w",
        "--workspace",
        help="Pass the workspace that will be used as default for workspace-aware commands",
    )
    parser_login.set_defaults(func=login_handler)

    # -------------------
    # --- logout options
    # -------------------

    parser_logout = subparsers_account.add_parser(
        "logout",
        help="Log out from your M&ntis account",
        formatter_class=root_parser.formatter_class,
    )
    parser_logout.set_defaults(func=logout_handler)

    parser_account.set_defaults(func=lambda _: parser_account.print_help())
