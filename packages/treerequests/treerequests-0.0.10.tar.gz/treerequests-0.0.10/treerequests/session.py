from typing import Optional, Tuple, Any, Callable
import copy
import time
import random
from threading import Lock

from .useragents import newagent
from .logger import create_logger


class AlreadyVisitedError(Exception):
    pass


class RedirectionError(Exception):
    pass


def smarttrim(src):
    # turns " \v i am a   \a \n \n \a test  \a " to "i am a test"

    return " ".join(
        src.translate(str.maketrans("\t\n\r\a\v\f\v", "       ", "")).split()
    )


def newbrowser(browser: Optional[str | Callable]) -> dict:
    if browser is None:
        return {}

    if isinstance(browser, Callable):
        return browser()

    import browser_cookie3

    return getattr(browser_cookie3, browser)()


def _ua(user_agent):
    if isinstance(user_agent, str):
        return [user_agent]
    return user_agent


def get_cookiejar_init(lib):
    try:
        return lib.cookies.RequestsCookieJar
    except Exception:
        pass
    try:
        return lib.cookies.Cookies
    except Exception:
        pass
    raise Exception("Couldn't find type for cookie jar")


def Session(
    lib,
    session,
    tree,
    alreadyvisitederror=None,
    requesterror=None,
    redirectionerror=None,
    **kwargs,
):
    orig_tree = tree
    cookie_obj_init = get_cookiejar_init(lib)

    class ret_obj(session):
        def get_settings(
            self, settings: dict, dest: Optional[dict] = None, remove: bool = True
        ) -> dict:
            passed = False
            if settings.get("__treerequests_passed"):
                settings.pop("__treerequests_passed")
                passed = True

            user_agent = settings.get("user_agent", -1)
            browser = settings.get("browser", -1)
            logger = settings.get("logger", -1)
            if dest is None:
                dest = {}

            for i in self._settings.keys():
                val = settings.get(i, self._settings[i])

                if i == "headers" or i == "cookies" or i == "proxies":
                    if dest.get(i) is None:
                        dest[i] = {}
                    dest[i].update(val)
                else:
                    dest[i] = val

                if remove:
                    settings.pop(i, None)

            if not passed:
                if user_agent != -1:
                    dest["headers"].update(
                        {"User-Agent": newagent(*_ua(dest["user_agent"]))}
                    )
                if browser is not None and browser != -1:
                    dest["cookies"] = cookie_obj_init(dest["cookies"])
                    dest["cookies"].update(newbrowser(dest["browser"]))
                if logger != -1:
                    dest["_logger"] = create_logger(logger)
            return dest

        def _settings_update(self):
            self.proxies.update(self["proxies"])
            self["proxies"] = {}
            self.headers.update(self["headers"])
            self["headers"] = {}
            self.cookies.update(self["cookies"])
            self["cookies"] = {}

        def set_settings(self, settings: dict, remove=True):
            self.get_settings(settings, dest=self._settings, remove=remove)
            self._settings_update()

        def __getitem__(self, key):
            return self._settings[key]

        def new_user_agent(self):
            self.headers.update({"User-Agent": newagent(*_ua(self["user_agent"]))})

        def new_browser(self):
            self.cookies.update(newbrowser(self["browser"]))

        def __setitem__(self, item, value):
            x = self._settings[item]
            self._settings[item] = value
            if type(x) is type(value) and x != value:
                if item == "user_agent":
                    self.new_user_agent()
                if item == "browser":
                    self.new_browser()
                if item == "logger":
                    self._settings["_logger"] = create_logger(value)

        def __init__(self, **settings):
            self._settings = {
                "proxies": {},
                "headers": {},
                "cookies": {},
                "timeout": 30,
                "verify": True,
                "allow_redirects": False,
                "redirects": False,
                "retries": 2,
                "retry_wait": 5,
                "force_retry": False,
                "wait": 0,
                "wait_random": 0,
                "trim": False,
                "user_agent": [
                    ("desktop", "windows", ("firefox", "chrome")),
                ],
                "raise": True,
                "browser": None,
                "visited": False,
                "logger": None,
                "_logger": None,  # compiled .logger
            }
            self.get_settings(settings, dest=self._settings)
            self.visited = set()
            self._lock = Lock()

            super().__init__(**settings)

            self._settings_update()

            self.new_user_agent()
            self.new_browser()

        def new(self, independent=False, **settings):
            r = type(self)(**settings)
            r.headers = copy.copy(self.headers)
            r.cookies = copy.copy(self.cookies)
            r.proxies = copy.copy(self.proxies)

            if independent:
                r.visited = copy.copy(self.visited)
                if r["_logger"] == self["_logger"]:
                    r["_logger"] = None
                    r["logger"] = None
            else:
                r._lock = self._lock
            return r

        def req_try(
            self,
            url: str,
            method: str,
            settings: dict,
            kwargs: dict,
            retry: bool = False,
        ):
            if not retry:
                if settings["wait"] != 0:
                    time.sleep(settings["wait"])
                if settings["wait_random"] != 0:
                    time.sleep(random.random() * settings["wait_random"])

            visited = settings["visited"]
            if (not retry and visited) or settings["_logger"] is not None:
                with self._lock:
                    if not retry and visited:
                        self.visited.add(url)
                    if settings["_logger"] is not None:
                        settings["_logger"](method, url, retry)

            return self.request(
                method,
                url,
                verify=settings["verify"],
                allow_redirects=settings["allow_redirects"],
                timeout=settings["timeout"],
                proxies=settings["proxies"],
                headers=settings["headers"],
                cookies=settings["cookies"],
                **kwargs,
            )

        def req(self, url: str, method: str = "get", **settings):
            settings = self.get_settings(kwargs)

            tries = settings["retries"]
            retry_wait = settings["retry_wait"]
            if settings["visited"]:
                with self._lock:
                    if url in self.visited:
                        if alreadyvisitederror is not None:
                            raise alreadyvisitederror(url)
                        else:
                            raise AlreadyVisitedError(url)

            instant_end_code = [400, 401, 402, 403, 404, 410, 412, 414, 421, 505]

            i = 0
            while True:
                resp = None
                try:
                    resp = self.req_try(url, method, settings, kwargs, retry=(i != 0))
                except (
                    lib.ConnectTimeout,
                    lib.ConnectionError,
                    lib.ReadTimeout,
                    lib.exceptions.ChunkedEncodingError,
                ) as e:
                    if i > tries:
                        if requesterror:
                            raise requesterror()
                        else:
                            raise e

                    ok = False
                else:
                    ok = resp.ok

                if ok:
                    if (
                        not settings["redirects"]
                        and resp.status_code >= 300
                        and resp.status_code < 400
                    ):
                        if redirectionerror:
                            raise redirectionerror()
                        else:
                            raise RedirectionError()

                    return resp

                if (
                    resp is not None
                    and not settings["force_retry"]
                    and resp.status_code in instant_end_code
                ) or i > tries:
                    if settings["raise"]:
                        try:
                            resp.raise_for_status()
                        except Exception as e:
                            if requesterror:
                                raise requesterror()
                            else:
                                raise e

                    return resp

                i += 1
                if retry_wait != 0:
                    time.sleep(retry_wait)

        def get(self, url: str, **settings):
            return self.req(url, method="get", **settings)

        def post(self, url: str, **settings):
            return self.req(url, method="post", **settings)

        def head(self, url: str, **settings):
            return self.req(url, method="head", **settings)

        def put(self, url: str, **settings):
            return self.req(url, method="put", **settings)

        def delete(self, url: str, **settings):
            return self.req(url, method="delete", **settings)

        def options(self, url: str, **settings):
            return self.req(url, method="options", **settings)

        def patch(self, url: str, **settings):
            return self.req(url, method="patch", **settings)

        def html(
            self,
            url: str,
            response: bool = False,
            tree: Callable = None,
            method: str = "get",
            **settings,
        ) -> Any | Tuple[Any, Any]:
            settings = self.get_settings(settings)
            settings["__treerequests_passed"] = True

            resp = self.req(url, method=method, **settings)

            text = resp.text
            if settings["trim"]:
                text = smarttrim(text)

            if tree is None:
                tree = orig_tree
            r = tree(text, url)

            return (r, resp) if response else r

        def delete_html(
            self,
            url: str,
            response: bool = False,
            tree: Callable = None,
            **settings,
        ) -> Any | Tuple[Any, Any]:
            return self.html(
                url, response=response, tree=tree, method="delete", **settings
            )

        def put_html(
            self,
            url: str,
            response: bool = False,
            tree: Callable = None,
            **settings,
        ) -> Any | Tuple[Any, Any]:
            return self.html(
                url, response=response, tree=tree, method="put", **settings
            )

        def patch_html(
            self,
            url: str,
            response: bool = False,
            tree: Callable = None,
            **settings,
        ) -> Any | Tuple[Any, Any]:
            return self.html(
                url, response=response, tree=tree, method="patch", **settings
            )

        def post_html(
            self,
            url: str,
            response: bool = False,
            tree: Callable = None,
            **settings,
        ) -> Any | Tuple[Any, Any]:
            return self.html(
                url, response=response, tree=tree, method="post", **settings
            )

        def get_html(
            self,
            url: str,
            response: bool = False,
            tree: Callable = None,
            **settings,
        ) -> Any | Tuple[Any, Any]:
            return self.html(
                url, response=response, tree=tree, method="get", **settings
            )

        def json(
            self, url: str, response: bool = False, method="get", **settings
        ) -> dict | Tuple[dict, Any]:
            resp = self.req(url, method=method, **settings)
            r = resp.json()
            return (r, resp) if response else r

        def get_json(
            self, url: str, response: bool = False, **settings
        ) -> dict | Tuple[dict, Any]:
            return self.json(url, response=response, method="get", **settings)

        def post_json(
            self, url: str, response: bool = False, **settings
        ) -> dict | Tuple[dict, Any]:
            return self.json(url, response=response, method="post", **settings)

        def delete_json(
            self, url: str, response: bool = False, **settings
        ) -> dict | Tuple[dict, Any]:
            return self.json(url, response=response, method="delete", **settings)

        def put_json(
            self, url: str, response: bool = False, **settings
        ) -> dict | Tuple[dict, Any]:
            return self.json(url, response=response, method="put", **settings)

        def patch_json(
            self, url: str, response: bool = False, **settings
        ) -> dict | Tuple[dict, Any]:
            return self.json(url, response=response, method="patch", **settings)

    return ret_obj(**kwargs)
