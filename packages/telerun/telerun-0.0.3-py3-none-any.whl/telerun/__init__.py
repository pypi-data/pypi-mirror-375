#!/usr/bin/env python3

import argparse
from functools import partial
from pathlib import Path
import urllib
import urllib.parse
import urllib.request
import ssl
import os
import json
import traceback
import time
import base64
import sys
from datetime import datetime
import textwrap
import tarfile
import io
import socket  # for socket.timeout exception
import errno  # for errno.ECONNRESET exception
import dataclasses as dc
import certifi

print_err = partial(print, file=sys.stderr)


@dc.dataclass
class Conf:
    username: str
    token: str
    url: str = "https://telerun.accelerated-computing.io"
    cert: str | None = None

    # This network_timeout only covers non-blocking operations on the socket; for example, this will cover
    # connection establishment timeouts (including SSL verification/cert exchange);
    # but this will not necessary cover the I/O over slow networks, since if the data are arriving (but slow),
    # the socket will not timeout.
    network_timeout: float = 60  # seconds
    retry_backoff_factor: float = 1
    version: str = "0.1.3"
    poll_interval = 0.25  # seconds
    job_id_digits = 7  # minimum number of digits to display for job IDs

    script_file: Path = dc.field(
        default_factory=lambda: Path(os.path.realpath(__file__))
    )

    platforms: set[str] = dc.field(
        default_factory=lambda: {
            "x86_64",
            "cuda",
        }
    )

    filename_platforms: dict[str, str] = dc.field(
        default_factory=lambda: {
            "cpp": "x86_64",
            "cu": "cuda",
        }
    )

    @staticmethod
    def mock():
        return Conf("", "")

    @property
    def script_dir(self):
        return self.script_file.parent

    def render_job(self, job_id):
        return str(job_id).zfill(self.job_id_digits)

    def at_least_version(self, compat_version: str):
        curr_parts = [int(part) for part in self.version.split(".")]
        try:
            compat_parts = [int(part) for part in compat_version.split(".")]
            return compat_parts <= curr_parts
        except ValueError:
            return False

    @property
    def ctx(self) -> "Context":
        return Context(self)

    @staticmethod
    def default_conf_path() -> Path:
        return Path.home() / ".telerun.json"

    @staticmethod
    def from_file(conf: str | None):
        for file in [conf, Conf.default_conf_path(), Path(__file__) / "telerun.json"]:
            if file is None:
                continue
            try:
                with open(file) as fd:
                    config = json.load(fd)
                    for i in ("username", "token"):
                        if i not in config:
                            print_err(f"{i} not in config file {file}")
                            exit(1)
                    return Conf(**config)

            except FileNotFoundError:
                pass
        print_err("Could not find config file")
        exit(1)

    def get_out_dir(self, out: str | None, job_id):
        return (
            Path.cwd() / "telerun-out" / self.render_job(job_id)
            if out is None
            else Path(out)
        )


class Context:
    def __init__(self, conf: Conf) -> None:
        self.conf = conf
        self.ssl_ctx = (
            ssl.create_default_context(cafile=certifi.where())
            if conf.cert is None
            else ssl.create_default_context(cadata=conf.cert)
        )

    def request(
        self,
        method,
        path,
        params,
        *,
        body=None,
        use_auth=False,
        use_version=True,
        disable_retry=False,
    ):
        assert path.startswith("/")
        params = dict(params)
        if use_version:
            params["v"] = self.conf.version
        if use_auth:
            params["username"] = self.conf.username
            params["token"] = self.conf.token
        url = f"{self.conf.url}{path}"

        if len(params) > 0:
            url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"

        if body is not None:
            body = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, method=method, data=body)
        if body is not None:
            req.add_header("Content-Type", "application/json")

        # Connect to server.
        retry_cnt = 0
        while True:
            try:
                with urllib.request.urlopen(
                    req, context=self.ssl_ctx, timeout=self.conf.network_timeout
                ) as response:
                    return json.load(response)
            except urllib.error.URLError as e:
                # Retry on timeout, connection reset, connection refused;
                # Terminate immediately with a user-friendly message on SSL errors;
                # Otherwise, raise the error.
                do_retry = False
                if isinstance(e.reason, socket.timeout):
                    print_err("Failed to connect to server (timeout), retrying...")
                    do_retry = True
                elif (
                    isinstance(e.reason, OSError) and e.reason.errno == errno.ECONNRESET
                ):
                    # Handle "Connection reset by peer" error.
                    print_err(
                        "Failed to connect to server (broken connection), retrying..."
                    )
                    do_retry = True
                elif isinstance(e.reason, ConnectionRefusedError):
                    print_err(
                        "Failed to connect to server (connection refused), retrying..."
                    )
                    do_retry = True
                elif isinstance(e.reason, ssl.SSLError):
                    print_err(
                        f"Failed to connect to server, SSL error: {e.reason}; Is your certificate valid?"
                    )
                    exit(
                        0
                    )  # exit with 0 to avoid spamming the user with error messages

                # Retry if needed, otherwise raise the error.
                if do_retry and not disable_retry:
                    retry_cnt += 1
                    time.sleep((int)(self.conf.retry_backoff_factor * (2**retry_cnt)))
                else:
                    raise e

    def request_version(ctx):
        return ctx.request("GET", "/api/version", {}, use_version=False)

    def check_version(ctx):
        response = ctx.request_version()
        if response["latest_user"] != ctx.conf.version:
            supported = ctx.conf.at_least_version(response["compat_user"])
            if supported:
                print_err(
                    f"A new Telerun client version is available (version {response['latest_user']})"
                )
            else:
                print_err(
                    f"Version {ctx.conf.version} of the Telerun client is no longer supported",
                )
            print_err(
                "\nTo update, pull the latest commit from the Telerun repository\n",
            )
            # # Work in progress:
            # print(
            #     "\n"
            #     f"To update to version {response['latest_user']}, run:\n"
            #     "\n"
            #     "    python3 telerun.py update\n",
            #     "\n",
            #     end="",
            #     file=sys.stderr,
            # )
            if not supported:
                exit(1)

    def cancel_pending(ctx, job_id):
        try:
            response = ctx.request(
                "POST", "/api/cancel", {"job_id": job_id}, use_auth=True
            )
            assert response["success"] is True
            return "success"
        except urllib.error.HTTPError as e:
            if e.code == 400:
                response_json = json.load(e)
                if response_json.get("error") in {"not_found", "already_executing"}:
                    return response_json["error"]
            raise

    def get_job_spec(ctx, args, *, cond):
        if args.latest and args.job_id is not None:
            print_err("Arguments '--latest' and '<job_id>' are mutually exclusive")
            exit(1)

        if args.latest:
            response = ctx.request("GET", "/api/jobs", {}, use_auth=True)
            assert response["success"] is True
            jobs = response["jobs"]
            jobs = [job for job in jobs if cond(job)]
            if not jobs:
                return None
            return jobs[-1]
        elif args.job_id is not None:
            return args.job_id
        else:
            print_err("Missing argument '<job_id>' or '--latest'")
            exit(1)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %I:%M %p")


def submit_handler(args):
    # # Work in progress:
    # if args.async_ and args.out is not None:
    #     print("Arguments '--out' and '--async' are mutually exclusive", file=sys.stderr)
    #     print("To get the output of an asynchronous job, use 'telerun.py get-output <job_id>'", file=sys.stderr)
    #     exit(1)
    conf = Conf.from_file(args.conf)
    ctx = conf.ctx
    ctx.check_version()

    if args.platform is None:
        for k, v in conf.filename_platforms.items():
            if args.file.endswith(k):
                platform = v
                break
        else:
            if args.file.endswith(".tar"):
                platform = "cuda"
            else:
                supported_filenames = ", ".join(
                    f"'*.{ext}'" for ext in conf.filename_platforms.keys()
                )
                supported_platforms = ", ".join(
                    repr(platform) for platform in conf.platforms
                )
                print_err(
                    f"Could not infer platform from filename {os.path.basename(args.file)!r}\n"
                    f"Supported filenames: {supported_filenames}\n"
                    "\n"
                    "You can also specify the platform explicitly with '--platform'\n"
                    f"Supported platforms: {supported_platforms}",
                )
                exit(1)
    elif args.platform not in conf.platforms:
        print_err(
            f"Unsupported platform {args.platform!r}\n"
            f"Supported platforms: {', '.join(repr(platform) for platform in conf.platforms)}",
            file=sys.stderr,
        )
        exit(1)
    else:
        platform = args.platform

    is_tarball = args.file.endswith(".tar")
    if is_tarball:
        # If source is a tarball, read as binary and encode here.
        with open(args.file, "rb") as fb:
            source = base64.b64encode(fb.read()).decode("utf-8")
    else:
        # Read as a text file.
        with open(args.file, "r") as f:
            source = f.read()

    options = {
        "args": args.args,
        "generate_asm": args.asm,
        "tarball": is_tarball,
    }

    submit_query_args = {}
    if args.force:
        submit_query_args["override_pending"] = "1"

    try:
        submit_response = ctx.request(
            "POST",
            "/api/submit",
            submit_query_args,
            body={
                "platform": platform,
                "source": source,
                "options": options,
            },
            use_auth=True,
        )
    except urllib.error.HTTPError as e:
        try:
            body = e.fp.read().decode()
            response_json = json.loads(body)
            if response_json.get("error") == "pending_job":
                print_err(
                    "You already have a pending job. Pass '--force' if you want to replace it",
                )
            else:
                print_err(f"Got msg {response_json}")

        except json.JSONDecodeError:
            print_err(f"Got msg {e.msg} {body}")
        except Exception:
            print(f"Failed with code {e.code} {e.msg}")
        exit(1)
        raise
    except urllib.error.URLError as e:
        raise

    assert submit_response["success"] is True
    job_id = submit_response["job_id"]

    print()
    print(f"{timestamp()}    submitted job {conf.render_job(job_id)}")
    print()

    # if args.async_:
    #     return

    out_dir = conf.get_out_dir(args.out, job_id)

    milestones_specs = {
        "compile_claim": "compiling",
        "compile_complete": "compiled successfully",
        "execute_claim": "executing",
        "execute_complete": "completed successfully",
        "compile_fail": "compilation failed",
        "execute_fail": "execution failed",
    }

    log_milestone_specs = {
        "compile_output": {"msg": "compile output", "key": "compile_log"},
        "execute_output": {"msg": "output", "key": "execute_log"},
    }

    compile_all = ["compile_claim", "compile_output", "compile_complete"]

    state_histories = {
        ("compile", False, None): [],
        ("compile", True, None): ["compile_claim"],
        ("execute", False, None): compile_all,
        ("execute", True, None): compile_all + ["execute_claim"],
        ("complete", False, "success"): compile_all
        + ["execute_claim", "execute_output", "execute_complete"],
        ("complete", False, "compile_fail"): [
            "compile_claim",
            "compile_output",
            "compile_fail",
        ],
        ("complete", False, "execute_fail"): compile_all
        + ["execute_claim", "execute_output", "execute_fail"],
    }

    def check_deleted(payload):
        if payload is None:
            print(f"{timestamp()}    job {conf.render_job(job_id)} deleted by server")
            print()
            exit(1)

    milestones_seen = set()

    try:
        while True:
            time.sleep(conf.poll_interval)
            status_response = ctx.request(
                "GET", "/api/status", {"job_id": job_id}, use_auth=True
            )
            assert status_response["success"] is True
            status = status_response["status"]
            check_deleted(status)

            # download and extract the output archive before printing the completion message so
            # that the user doesn't accidentally CTRL+C out of the script before we've saved all
            # the output
            if status["curr_phase"] == "complete":
                # Get result tarball.
                output_archive_response = ctx.request(
                    "GET",
                    "/api/output",
                    {"job_id": job_id, "keys": "output_tar_gz"},
                    use_auth=True,
                )
                assert output_archive_response["success"] is True
                check_deleted(output_archive_response["output"])
                output_archive_base64 = output_archive_response["output"].get(
                    "output_tar_gz"
                )
                if output_archive_base64 is not None:
                    output_archive = base64.b64decode(output_archive_base64)
                    os.makedirs(out_dir, exist_ok=True)
                    with io.BytesIO(output_archive) as output_archive_f:
                        with tarfile.open(fileobj=output_archive_f) as tar:
                            tar.extractall(out_dir, filter="data")

                # Get asm/sass if requested.
                if args.asm and (platform == "x86_64" or platform == "cuda"):
                    output_asm_response = ctx.request(
                        "GET",
                        "/api/output",
                        {"job_id": job_id, "keys": "compiled_asm_sass"},
                        use_auth=True,
                    )
                    assert output_asm_response["success"] is True
                    output_asm = output_asm_response["output"].get("compiled_asm_sass")
                    if output_asm is not None:
                        os.makedirs(out_dir, exist_ok=True)
                        with open(os.path.join(out_dir, "asm-sass.txt"), "w") as f:
                            f.write(output_asm)

                # Get ptx if requested.
                if args.asm and platform == "cuda":
                    output_asm_response = ctx.request(
                        "GET",
                        "/api/output",
                        {"job_id": job_id, "keys": "compiled_ptx"},
                        use_auth=True,
                    )
                    assert output_asm_response["success"] is True
                    output_asm = output_asm_response["output"].get("compiled_ptx")
                    if output_asm is not None:
                        os.makedirs(out_dir, exist_ok=True)
                        with open(os.path.join(out_dir, "asm-ptx.txt"), "w") as f:
                            f.write(output_asm)

            curr_state = (
                status["curr_phase"],
                status["claimed"],
                status["completion_status"],
            )
            for milestone in state_histories[curr_state]:
                if milestone in milestones_seen:
                    continue
                milestones_seen.add(milestone)
                if milestone in milestones_specs:
                    print(f"{timestamp()}    {milestones_specs[milestone]}")
                    print()
                elif milestone in log_milestone_specs:
                    key = log_milestone_specs[milestone]["key"]
                    log_response = ctx.request(
                        "GET",
                        "/api/output",
                        {"job_id": job_id, "keys": key},
                        use_auth=True,
                    )
                    assert log_response["success"] is True
                    check_deleted(log_response["output"])
                    milestone_log = log_response["output"][key]
                    if milestone_log is None:
                        milestone_log = ""
                    os.makedirs(out_dir, exist_ok=True)
                    with open(
                        os.path.join(out_dir, key.replace("_", "-")) + ".txt", "w"
                    ) as f:
                        f.write(milestone_log)
                    if milestone_log.strip():
                        print(
                            f"{timestamp()}    {log_milestone_specs[milestone]['msg']}:"
                        )
                        print()
                        print(
                            textwrap.indent(milestone_log, "    "),
                            end="" if milestone_log.endswith("\n") else "\n",
                        )
                        print()
                else:
                    assert False

            if status["curr_phase"] == "complete":
                completion_status = status["completion_status"]
                if completion_status != "success":
                    exit(1)
                break

    except KeyboardInterrupt:
        cancel_result = ctx.cancel_pending(job_id)
        if cancel_result != "success":
            print(f"{timestamp()}    detached from job")
            print()

            # # Work in progress:
            # print(f"Job {render_job(job_id)} is already executing and will run to completion")
            # print()
            # print("To track its progress, run:")
            # print()
            # print("    python3 telerun.py list-jobs")
            # print()
            # print("To get its output when it completes, run:")
            # print()
            # print(f"    python3 telerun.py get-output {job_id}")
            # print()
        else:
            print(f"{timestamp()}    cancelled job")
            print()
        exit(130)


def cancel_handler(args):
    conf = Conf.from_file(args.conf)
    ctx = conf.ctx
    ctx.check_version()

    def is_cancellable(job):
        if job["curr_phase"] == "complete":
            return False
        if job["curr_phase"] == "execute":
            return job["curr_phase_claimed_at"] is None
        return True

    job = ctx.get_job_spec(args, cond=is_cancellable)
    if job is None:
        print("No pending jobs to cancel")
        return
    job_id = job["job_id"]

    cancel_result = ctx.cancel_pending(job_id)
    if cancel_result == "success":
        print(f"Cancelled job {conf.render_job(job_id)}")
    elif cancel_result == "not_found":
        print(f"Job {conf.render_job(job_id)} not found")
    elif cancel_result == "already_executing":
        print(
            f"Job {conf.render_job(job_id)} is already executing and will run to completion"
        )


def version_handler(args):
    conf = Conf.from_file(args.conf)
    ctx = conf.ctx
    ctx.check_version()

    print("Telerun client version:   " + conf.version)
    if hasattr(args, "offline") and args.offline:
        return

    response = ctx.request_version()
    print(f"Latest supported version: {response['compat_user']}")
    print(f"Latest available version: {response['latest_user']}")
    if not conf.at_least_version(response["latest_user"]):
        print()
        print("To update, pull the latest version from the Telerun repository")
        print()


# # Work in progress:
# def update_handler(args):
#     connection = get_connection_config(args)
#     ctx = Context(connection=connection)
#     version_response = request_version(ctx)
#     latest_version = version_response["latest_user"]
#     if latest_version == version and not args.force:
#         print("Already up to date with version " + version)
#         return
#     print("Current version: " + version)
#     print("Available version: " + latest_version)

#     i = 0
#     backup_path = os.path.join(get_script_dir(), "/old-telerun-v{version}.py.backup")
#     while os.path.exists(backup_path):
#         i += 1
#         backup_path = os.path.join(get_script_dir(), "/old-telerun-v{version}-{i}.py")

#     if not args.yes:
#         print()
#         print(f"Update {script_file!r} to version {latest_version}?")
#         print(f"(A backup of the current version will be saved to {backup_path!r})")
#         print("[Y/n] ", end=" ")
#         prompt_response = input().strip().lower()
#         if prompt_response not in {"", "y", "yes"}:
#             print("Cancelled")
#             return
#     # TODO: Strictly speaking there's a race condition here where the user could update to a new
#     # version that's released between the time they check and the time they update. This is probably
#     # fine for now, but it could be fixed by checking the version again after the update.
#     update_response = ctx.request("GET", "/api/update", {"client_type": "user"}, use_version=False)

#     os.rename(script_file, backup_path)
#     print(f"Saved backup of old client to {backup_path!r}")

#     with open(script_file, "w") as f:
#         f.write(update_response["source"])

#     print(f"Successfully updated {script_file!r} to version {latest_version}")

# # Work in progress:
# def list_jobs_handler(args):
#     raise NotImplementedError()

# # Work in progress:
# def get_output_handler(args):
#     raise NotImplementedError()


def login_handler(args):
    conf_path: Path = Conf.default_conf_path() if args.conf is None else Path(args.auth)
    if conf_path.exists() and not args.force:
        print(
            f"Authentication file {conf_path} already exists\n"
            "Pass '--force' if you want to replace it\n",
            end="",
            file=sys.stderr,
        )
        exit(1)

    if args.username is None:
        print("Enter your Telerun username:")
        print(">>> ", end="")
        username = input()
    else:
        username = args.username

    username = username.strip()
    if args.login_code is None:
        print("Enter your Telerun token:")
        print(">>> ", end="")
        login_code = input()
    else:
        login_code = args.login_code
    login_code = login_code.strip()
    config = {
        "username": username,
        "token": login_code,
    }
    with open(conf_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved authentication config to {conf_path}")


def add_auth_arg(parser):
    parser.add_argument(
        "--conf",
        help=f"Path to config file, will default to {Conf.mock().default_conf_path()}",
    )


def add_out_dir_arg(parser):
    parser.add_argument(
        "--out",
        help="directory to which to write job output (defaults to './telerun-out/<job_id>' in the current working directory)",
    )


def add_job_spec_arg(parser):
    parser.add_argument("job_id", help="the ID of the job", nargs="?")
    parser.add_argument("--latest", action="store_true", help="use the latest job")


def main():
    parser = argparse.ArgumentParser(
        description="Remote Code Execution as a Service", prog="telerun"
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    parser.add_argument(
        "--version",
        action="store_true",
        dest="version_flag",
        help="alias for 'version'",
    )

    submit_parser = subparsers.add_parser("submit", help="submit a job")
    add_auth_arg(submit_parser)
    submit_parser.add_argument(
        "-f", "--force", action="store_true", help="allow overriding pending jobs"
    )
    add_out_dir_arg(submit_parser)
    mock_conf = Conf(username="", token="")
    submit_parser.add_argument(
        "-s",
        "--asm",
        action="store_true",
        help="generate asm/ptx/sass along with execution",
    )
    submit_parser.add_argument(
        "-p",
        "--platform",
        help="platform on which to run the job (default is inferred from filename: {})".format(
            ", ".join(
                [
                    f"'*.{ext}' -> {platform!r}"
                    for ext, platform in mock_conf.filename_platforms.items()
                ]
            )
        ),
        choices=list(mock_conf.platforms),  # type:ignore
    )
    submit_parser.add_argument("file", help="source file to submit")
    submit_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="arguments for your program"
    )

    # # Work in progress:
    # submit_parser.add_argument("--async", action="store_true", dest="async_", help="do not wait for the job to complete")

    submit_parser.set_defaults(func=submit_handler)

    # # Work in progress:
    # cancel_parser = subparsers.add_parser('cancel', help='cancel a job')
    # add_connection_config_arg(cancel_parser)
    # add_auth_arg(cancel_parser)
    # add_job_spec_arg(cancel_parser)
    # cancel_parser.set_defaults(func=cancel_handler)

    # # Work in progress:
    # list_jobs_parser = subparsers.add_parser('list-jobs', help='list all jobs for your user')
    # add_connection_config_arg(list_jobs_parser)
    # add_auth_arg(list_jobs_parser)
    # list_jobs_parser.set_defaults(func=list_jobs_handler)

    # # Work in progress:
    # get_output_parser = subparsers.add_parser('get-output', help='get the output of a job')
    # add_connection_config_arg(get_output_parser)
    # add_auth_arg(get_output_parser)
    # add_out_dir_arg(get_output_parser)
    # add_job_spec_arg(get_output_parser)
    # get_output_parser.set_defaults(func=get_output_handler)

    version_parser = subparsers.add_parser(
        "version", help="print the version of the client and check for updates"
    )
    version_parser.add_argument(
        "--offline", action="store_true", help="do not check for updates"
    )
    version_parser.set_defaults(func=version_handler)

    # # Work in progress:
    # update_parser = subparsers.add_parser('update', help='update the client')
    # add_connection_config_arg(update_parser)
    # update_parser.add_argument("-f", "--force", action="store_true", help="force update even if already up to date")
    # update_parser.add_argument("-y", "--yes", action="store_true", help="do not prompt for confirmation")
    # update_parser.set_defaults(func=update_handler)

    login_parser = subparsers.add_parser("login", help="log in to Telerun")
    login_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force overwriting authentication file even if it already exists",
    )
    login_parser.add_argument(
        "--conf",
        help=f"Location of config file, defaults to {Conf.mock().default_conf_path}",
    )
    login_parser.add_argument(
        "login_code", help="login code (will prompt if not provided)", nargs="?"
    )
    login_parser.add_argument(
        "username", help="username (will prompt if not provided)", nargs="?"
    )
    login_parser.set_defaults(func=login_handler)

    args = parser.parse_args()

    if args.version_flag:
        version_handler(args)
        return

    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    try:
        args.func(args)
    except urllib.error.HTTPError as e:
        traceback.print_exc()
        print(e.read().decode("utf-8"), file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
