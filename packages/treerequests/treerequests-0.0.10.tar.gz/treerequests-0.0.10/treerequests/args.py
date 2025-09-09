from typing import Optional, Tuple
import argparse
import re
import ast


def conv_curl_header_to_requests(src):
    r = re.search(r"^\s*([A-Za-z0-9_-]+)\s*:(.*)$", src)
    if r is None:
        return None
    return {r[1]: r[2].strip()}


def conv_curl_cookie_to_requests(src):
    r = re.search(r"^\s*([A-Za-z0-9_-]+)\s*=(.*)$", src)
    if r is None:
        return None
    return {r[1]: r[2].strip()}


def valid_header(src):
    r = conv_curl_header_to_requests(src)
    if r is None:
        raise argparse.ArgumentTypeError('Invalid header "{}"'.format(src))
    return r


def valid_cookie(src):
    r = conv_curl_cookie_to_requests(src)
    if r is None:
        raise argparse.ArgumentTypeError('Invalid cookie "{}"'.format(src))
    return r


def valid_browser(browser):
    import browser_cookie3

    try:
        return getattr(browser_cookie3, browser)
    except AttributeError:
        raise argparse.ArgumentTypeError('no such browser "{}"'.format(browser))


def valid_time(time):
    time = time.strip()

    suffix = time[-1:]
    weight = 1
    if not suffix.isdigit():
        time = time[:-1]
        match suffix:
            case "s":
                weight = 1
            case "m":
                weight = 60
            case "h":
                weight = 3600
            case "d":
                weight = 24 * 3600
            case _:
                raise argparse.ArgumentTypeError(
                    'incorrect time format "{}"'.format(time)
                )
    try:
        num = float(time)
    except ValueError:
        raise argparse.ArgumentTypeError('incorrect time format "{}"'.format(time))

    if num < 0:
        raise argparse.ArgumentTypeError('incorrect time format "{}"'.format(time))

    return num * weight


def arg_name(name, rename: list[Tuple[str]]) -> Optional[Tuple[str, bool]]:
    if name is None:
        return
    for i in rename:
        l = len(i)
        if l < 1 or l > 2:
            assert 0

        if i[0] != name:
            continue

        if l == 1:
            return
        else:
            return i[1], True
    return name, False


def args_longarg(arg: str, prefix: str, rename: list[Tuple[str]]):
    if (r := arg_name(arg, rename)) is None:
        return
    longarg = "--"
    if r[1]:
        return longarg + r[0]
    if len(prefix) > 0:
        longarg += prefix + "-"
    longarg += r[0]
    return longarg


def args_shortarg(
    shortarg: Optional[str], noshortargs: Optional[list[str]], rename: list[Tuple[str]]
) -> Optional[str]:
    if noshortargs:
        return
    if (r := arg_name(shortarg, rename)) is None:
        return
    return "-" + r[0]


def rename_normalize(rename):
    for i, j in enumerate(rename):
        if isinstance(j, str):
            val = j.lstrip("-")
            rename[i] = (val,)
        else:
            rename[i] = tuple([k.lstrip("-") for k in j])


def args_section(
    parser,
    name: str = "Request settings",
    noshortargs: bool = False,
    rename: list[Tuple[str, str] | Tuple[str] | str] = [],
    prefix: str = "",
):
    section = parser.add_argument_group(name)

    rename_normalize(rename)

    def add(shortarg, longarg, help, **kwargs):
        shortarg = args_shortarg(shortarg, noshortargs, rename)
        longarg = args_longarg(longarg, prefix, rename)

        if shortarg is None and longarg is None:
            return

        r = shortarg if shortarg is not None else longarg

        help = help.replace("{.}", r)

        a = [i for i in (shortarg, longarg) if i is not None]
        section.add_argument(*a, default=None, help=help, **kwargs)

    add(
        "w",
        "wait",
        "Sets waiting time for each request",
        metavar="TIME",
        type=valid_time,
    )
    add(
        "W",
        "wait-random",
        "Sets random waiting time for each request to be from 0 to TIME",
        metavar="TIME",
        type=valid_time,
    )
    add(
        "r",
        "retries",
        "Sets number of retries for failed request to NUM",
        metavar="NUM",
        type=int,
    )
    add(
        None,
        "retry-wait",
        "Sets interval between each retry",
        metavar="TIME",
        type=valid_time,
    )
    add(
        None,
        "force-retry",
        "Retry no matter the error",
        action="store_true",
    )
    add(
        "m",
        "timeout",
        "Sets request timeout",
        metavar="TIME",
        type=valid_time,
    )
    add(
        "k",
        "insecure",
        "Ignore ssl errors",
        action="store_false",
    )
    add(
        "L",
        "location",
        "Allow for redirections, can be dangerous if credentials are passed in headers",
        action="store_true",
    )
    add(
        "A",
        "user-agent",
        "Sets custom user agent",
        metavar="UA",
        type=str,
    )
    add(
        "x",
        "proxies",
        'Set requests proxies dictionary, e.g. {.} \'{"http":"127.0.0.1:8080","ftp":"0.0.0.0"}\'',
        metavar="DICT",
        type=lambda x: dict(ast.literal_eval(x)),
    )
    add(
        "H",
        "header",
        "Set curl style header, can be used multiple times e.g. {.} 'User: Admin' {.} 'Pass: 12345'",
        metavar="HEADER",
        type=valid_header,
        action="append",
    )
    add(
        "b",
        "cookie",
        "Set curl style cookie, can be used multiple times e.g. {.} 'auth=8f82ab' {.} 'PHPSESSID=qw3r8an829'",
        metavar="COOKIE",
        type=valid_cookie,
        action="append",
    )
    add(
        "B",
        "browser",
        "Get cookies from specified browser e.g. {.} firefox",
        metavar="BROWSER",
        type=valid_browser,
    )

    return section


def finish_cookies(cookies):
    ret = {}
    if cookies is None:
        return ret
    for i in cookies:
        ret.update(i)
    return ret


def finish_headers(headers, cookies):
    ret = {}
    if headers is None:
        return ret

    for i in headers:
        ret.update(i)

    cookie = list(
        filter(lambda x: x is not None, map(lambda x: x.get("Cookie"), headers))
    )
    if len(cookie) == 0:
        return ret
    cookie = cookie[0]

    ret.pop("Cookie")
    for i in cookie.split(";"):
        pair = i.split("=")
        name = pair[0].strip()
        val = None
        if len(pair) > 1:
            val = pair[1].strip()
        cookies.update({name: val})
    return ret


def args_session(
    session,
    args,
    prefix: str = "",
    rename: list[Tuple[str, str] | Tuple[str] | str] = [],
    **settings,
):
    prefix = prefix.replace("-", "_")
    rename_normalize(rename)

    def argval(name: str):
        if (r := arg_name(name, rename)) is None:
            return
        name = r[0]
        if not r[1] and len(prefix) > 0 and len(name) > 1:
            return getattr(args, prefix + "_" + name)
        else:
            return getattr(args, name)

    cookies = finish_cookies(argval("cookie"))
    headers = finish_headers(argval("header"), cookies)

    settings["headers"] = headers
    settings["cookies"] = cookies

    def setarg(longarg: str, shortarg: str = None, dest: str = None):
        name = longarg
        if (value := argval(name)) is None:
            if (value := argval(shortarg)) is None:
                return

        if dest is not None:
            name = dest
        settings[name] = value

    setarg("timeout")
    setarg("proxies")
    setarg("insecure", dest="verify")
    setarg("location", dest="allow_redirects")
    setarg("retries")
    setarg("retry_wait")
    setarg("force_retry")
    setarg("wait")
    setarg("wait_random")
    setarg("user_agent")
    setarg("browser")

    session.set_settings(settings, remove=False)
