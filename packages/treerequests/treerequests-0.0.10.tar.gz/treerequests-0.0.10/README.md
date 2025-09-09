# treerequests

A wrapper around `requests` like libraries, common html parsers, user agents, `browser_cookie3` and `argparse` libraries.

# Installation

    pip install treerequests

# Dependencies

There are no explicit dependencies for this project, libraries will be imported when explicitly called. The possible modules are:

- [browser_cookie3](https://github.com/borisbabic/browser_cookie3)
- [bs4](https://pypi.org/project/beautifulsoup4/)
- [html5_parser](https://github.com/kovidgoyal/html5-parser)
- [selectolax](https://github.com/rushter/selectolax)
- [lxml](https://github.com/lxml/lxml)
- [reliq](https://github.com/TUVIMEN/reliq-python)

# Usage

## Code

```python
import sys, argparse, requests
from treerequests import Session, args_section, args_session, lxml

requests_prefix = "requests"

parser = argparse.ArgumentParser(description="some cli tool")
args_section(
    parser,
    name="requests section"
    noshortargs=True, # disable shortargs
    prefix=requests_prefix # make all arguments start with "--requests-"
)

args = parser.parse_args(sys.argv[1:])
ses = Session(
    requests,
    requests.Session,
    lxml, # default html parser for get_html()
    wait=0.1
)

# update session by parsed arguments
args_session(
    ses,
    args,
    prefix=requests_prefix,
    raise=True, # raise when requests fail
    timeout=12,
    user_agent=[('desktop','linux',('firefox','chrome'))] # user agent will be chosen randomly from linux desktop, firefox or chrome agents
)

tree = ses.get_html("https://www.youtube.com/")
title = tree.xpath('//title/text()')[0]
```

## newagent(*args) and useragents

`useragents` is a dictionary storing user agents in categorized way. Please notify me if you find some of them being blocked by sites.

```python
useragents = {
    "desktop": {
        "windows": {
            "firefox": []
            "chrome": [],
            "opera": [],
            "edge": [],
        },
        "linux": {
            "firefox": [],
            "chrome": [],
            "opera": [],
        },
        "macos": {
            "firefox": [],
            "chrome": [],
            "safari": [],
        },
    },
    "phone": {
        "android": {
            "chrome": [],
            "firefox": [],
        },
        "ios": {
            "safari": [],
            "firefox": [],
            "chrome": [],
        },
    },
    "bot": {
        "google": [],
        "bing": [],
        "yandex": [],
        "duckduckgo": [],
    },
}
```

`newagent` is a function that returns random user agent from `useragents`, if no arguments are passed this happens on the whole `dict`. If only one string argument is specified it gets returned without change.

In other cases arguments restrict amount of choices. If tuples of strings are passed dictionary will be repeatedly accessed by their contents, if final elements is a dictionary then all lists under it are accessed. This can be shortened to passing just strings to get top elements. All arguments represent singular expressions that are concatenated at the end. Passing tuple inside tuple will group results.


`newagent()` choose from all user agents

`newagent('my very special user agent')` return string without change

`newagent( ('desktop',) )` get desktop agent

`newagent( ['desktop'] )` get desktop agent (you can use lists instead of tuples)

`newagent( ('desktop',), ('phone',) )` get desktop or phone agent

`newagent( 'desktop', 'phone' )` get desktop or phone agent (tuples can be dropped)

`newagent( ('desktop', 'linux') )` get desktop linux agent

`newagent( ('desktop', 'linux', 'firefox') )` get agent of firefox from linux on desktop

Get agent from firefox or chrome from windows or linux on desktop, or bots, everything below is equivalent

`newagent( ('desktop', 'linux', 'firefox' ), ('desktop', 'linux', 'chrome' ), ('desktop', 'windows', 'firefox' ), ('desktop', 'windows', 'chrome' ), 'bot' )`

`newagent( ('desktop', ( ( 'linux', 'firefox' ), ( 'linux', 'chrome' ), ( 'windows', 'firefox' ), ( 'windows', 'chrome' ) ) ), 'bot' )`

`newagent( ('desktop', ( ( 'linux', ( 'firefox', 'chrome' ) ), ( 'windows', ( 'firefox', 'chrome' ) ) ) ), 'bot' )`

`newagent( ('desktop', ( 'linux', 'windows' ), ( 'firefox', 'chrome' ) ), 'bot' )`

## HTML parsers

Are defined as functions taking html string and url as arguments, and return objects of parsers, `kwargs` are passed to initialized object.

`parser(text, url, obj=None, **kwargs)`

Currently `bs4`, `html5_parser`, `lxml`, `lexbor`, `modest` and `reliq` parsers are defined.

You can specify `obj` argument to change default class type

```python
from reliq import RQ
from treerequests import reliq, Session
import requests

reliq2 = RQ(cached=True)
ses = Session(requests, requests.Session, lambda x, y: reliq(x,y,obj=reliq2))
```

## Session()

`Session(lib, session, tree, alreadyvisitederror=None, requesterror=None, redirectionerror=None, **settings)` creates and returns object that inherits from `session` argument, `lib` is the module from which `session` is derived, `tree` is a html parser function. You can change raised errors by setting `alreadyvisitederror`, `requesterror`, `redirectionerror`.

Settings are passed by `settings`, and also can be passed to all request methods `get`, `post`, `head`, `get_html`, `get_json` etc. where they don't change settings of their session.

```python
import requests
from treerequests import Session, lxml

ses = Session(requests, requests. Session, lxml, user_agent=("desktop","windows"), wait=2)
resp = ses.get('https://wikipedia.org')
print(resp.status_code)
```

### Settings

`timeout=30` request timeout

`allow_redirects=False` follow redirections

`redirects=False` if set to `False` `RedirectionError()` will be raised if redirection happens

`retries=2`  number of retries attempted in case of failure

`retry_wait=5` waiting time between retries in seconds

`force_retry=False` retry even if failure indicates it can't succeed

`wait=0`  waiting time for each request in seconds

`wait_random=0` random waiting time from 0 to specified value in seconds

`trim=False` trim whitespaces from html before passing to parser in `get_html`

`user_agent=[ ("desktop", "windows", ("firefox", "chrome")) ]` arguments passed to `newagent()` function to get user agent

`raise=True` raise exceptions for failed requests

`browser=None` get cookies from browsers by `browser_cookie3` lib, can be set to string name of function e.g. `browser="firefox"` or a to any function that returns `dict` of cookies without taking arguments.

`visited=False` keep track of visited urls and raise exception if attempt to redownload happens `treerequests.AlreadyVisitedError()` exception is raised.

`logger=None` log events, if set to `str`, `Path` or file object writes events in lines where things are separated by `'\t'`. If set to `list` event tuple is appended. It can be set to arbitrary function that takes single `tuple` argument.

Anything that doesn't match these settings will be directly passed to the original library's function.

You can get settings by treating session like a `dict` like `ses['wait']`, values can be changed in similar fashion `ses['wait'] = 0.8`. Changing values of some settings can implicitly change other settings e.g. `user_agent`.

`get_settings(self, settings: dict, dest: dict = {}, remove: bool = True) -> dict` method can be used to create settings dictionary while removing fields from original dictionary (depends on `remove`).

`set_settings(self, settings: dict, remove: bool = True)` works similar to `get_settings()` but updates the session with settings.

### visited

`visited` field is a `set()` of used urls, that are collected if `visited` setting is `True`.

### new_user_agent()

Changes user agent according to set rules.

### new_browser()

Updates cookies from browser session.

### new()

`new(self, independent=False, **settings)` creates copy of current object, if `independent` is `visited` will become a different object and `logger` will be set to `None`.

### req()

`req(self, url: str, method: str = "get", **settings)`

Makes a request with http method specified by `method`, returns normal response. Should be used instead of `request()`.

### get_html()

`get_html(self, url: str, response: bool = False, tree: Callable = None, **settings)`

Makes a GET request to `url` expecting html and returns parser object. Parser can be changed by setting `tree` to appropriate function.

If `response` is set response object is returned alongside parser.

`post_html()`, `delete_html()`, `put_json()`, `patch_json()` use different http methods according to their naming.

`html()` has optional method `method: str = "get"` that specifies http method used.

```python
import requests
from treerequests import Session, lxml

ses = Session(requests, requests. Session, lxml, user_agent=("desktop","windows"), wait=2)

tree = ses.get_html('https://wikipedia.org')
print(tree.xpath('//title/text()')[0])

tree, resp = ses.get_html('https://wikipedia.org',respose=True)
print(resp.status_code)
print(tree.xpath('//title/text()')[0])
```

### get_json()

`get_json(self, url: str, response: bool = False, **settings) -> dict | Tuple[dict, Any]`

If `response` is set response object is returned alongside parser.

`get_json()`, `post_json()`, `delete_json()`, `put_json()`, `patch_json()` take `url` and `**settings` as arguments and return `dict`, making requests using method according to their naming, while expecting json as output.

`json()` works the same way, but accepts optional parameter `method: str = "get"` to signify http method used for request.

## args_section()

```
args_section(
    parser,
    name: str = "Request settings",
    noshortargs: bool = False,
    prefix: str = "",
    rename: list[Tuple[str, str] | Tuple[str] | str] = [],
)
```

Creates section in `ArgumentParser()` that is `parser`. `prefix` is used only for longargs e.g. `--prefix-wait`.

If `noshortargs` is set no shortargs will be defined.

`rename` is a list of things to remove or rename. If an element of it is a string or tuple with single string then argument gets removed e.g. `rename=['location','L',('wait-random',)]`. To rename an argument element has to be a tuple with 2 strings e.g. `rename=[("wait","delay"),("w","W")]`. If used with `prefix` names renamed should be given without prefix and new name will not include prefix, if you want to keep prefix you'll have to specify it again in new name e.g. `prefix="requests", rename=[("location",'requests-redirect')]`.

```python
import argparse
from treerequests import args_section

parser = argparse.ArgumentParser(description="some cli tool")
args_section(
    parser,
    name="Settings of requests",
    prefix="request",
    noshortargs=True,
    rename=["location",("wait","requests-delay"),("user-agent","ua")] # remove --location, rename --requests-wait to --requests-delay and --requests-user-agent to --ua
)

args = parser.parse_args(sys.argv[1:])
```

`-w, --wait TIME` wait before requests, time follows the `sleep(1)` format of suffixes e.g. `2.8`, `2.8s`, `5m`, `1h`, `1d`

`-W, --wait-random TIME` wait randomly for each request from 0 to TIME

`-r, --retries NUM` number of retries in case of failure

`--retry-wait TIME` waiting time before retrying

`--force-retry` retry even if status code indicates it can't succeed

`-m, --timeout TIME` request timeout

`-k, --insecure` ignore ssl errors

`--user-agent UA` set user agent

`-B, --browser NAME` use cookies extracted from browser e.g. `firefox`, `chromium`, `chrome`, `safari`, `brave`, `opera`, `opera_gx` (requires `browser_cookie3` module)

`-L, --location` Allow for redirections

`--proxies DICT` (where `DICT` is python stringified dictionary) are directly passed to requests library, e.g. `--proxies '{"http":"127.0.0.1:8080","ftp":"0.0.0.0"}'`.

`-H ,--header "Key: Value"` very similar to `curl` `--header` option, can be specified multiple times e.g. `--header 'User: Admin' --header 'Pass: 12345'`. Similar to `curl` `Cookie` header will be parsed like `Cookie: key1=value1; key2=value2` and will be changed to cookies.

`-b, --cookie "Key=Value"` very similar to `curl` `--cookie` option, can be specified multiple times e.g. `--cookie 'auth=8f82ab' --cookie 'PHPSESSID=qw3r8an829'`.

## args_session()

`args_session(session, args, prefix="", rename=[], **settings)` updates `session` settings with `parsearg` values in `args`. `prefix` and `rename` should be the same as was specified for `args_section()`. You can pass additional `settings`, parsed arguments take precedence above previous settings.

```python
import sys, argparse, requests
from treerequests import Session, args_section, args_session, lxml

parser = argparse.ArgumentParser(description="some cli tool")
section_rename = ["location"]
args_section(parser,rename=section_rename)

args = parser.parse_args(sys.argv[1:])
session = Session(requests, requests.Session, lxml)
args_session(session, args, rename=section_rename)

tree = ses.get_html("https://www.youtube.com/")
```

## simple_logger()

`simple_logger(dest: list | str | Path | io.TextIOWrapper | Callable)` creates a simpler version of `logger` setting of `Session` where only urls are logged.

```python
import sys, requests
from treerequests import Session, bs4, simple_logger

s1 = Session(requests, requests.Session, bs4, logger=sys.stdout)
s2 = Session(requests, requests.Session, bs4, logger=simple_logger(sys.stdout))

s1.get('https://youtube.com')
# prints get\thttps://youtube.com\tFalse

s2.get('https://youtube.com')
# prints https://youtube.com
```
