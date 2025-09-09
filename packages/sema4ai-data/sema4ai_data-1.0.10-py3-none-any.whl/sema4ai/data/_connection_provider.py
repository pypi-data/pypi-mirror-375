"""
The code below could be better. It's a bit too over engineered for what it does
-- it's this way mostly due to historical reasons as initially it was per DataSource and
it was then extracted, so, it could be simplified in the future....
"""
import os
import typing
from typing import Optional, TypedDict

if typing.TYPE_CHECKING:
    from sema4ai.actions._action_context import DataContext

    from sema4ai.data._data_server_connection import DataServerConnection


class _BaseInternalConnectionProvider:
    _connection: Optional["DataServerConnection"] = None

    @property
    def _http_url(self) -> str:
        raise NotImplementedError()

    @property
    def _http_user(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    def _http_password(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    def _mysql_host(self) -> str:
        raise NotImplementedError()

    @property
    def _mysql_port(self) -> int:
        raise NotImplementedError()

    @property
    def _mysql_user(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    def _mysql_password(self) -> Optional[str]:
        raise NotImplementedError()

    @property
    def datasource_name(self) -> str:
        raise NotImplementedError()

    def connection(self) -> "DataServerConnection":
        if self._connection is None:
            from sema4ai.data._data_server_connection import DataServerConnection

            self._connection = DataServerConnection(
                self._http_url,
                self._http_user,
                self._http_password,
                self._mysql_host,
                self._mysql_port,
                self._mysql_user,
                self._mysql_password,
            )

        return self._connection


class HttpDict(TypedDict):
    url: str
    user: str
    password: str


class MysqlDict(TypedDict):
    host: str
    port: int
    user: str
    password: str


class _EnvVarInfoTypeDict(TypedDict):
    http: HttpDict
    mysql: MysqlDict


class _ConnectionProviderFromDataContextOrEnvVar(_BaseInternalConnectionProvider):
    """
    Internal API to wrap a datasource which is passed encrypted.
    """

    _env_var_info: Optional[_EnvVarInfoTypeDict] = None

    def __init__(self, data_context: Optional["DataContext"], path: str):
        """
        Args:
            data_context: The data context.
            path: the path of the data required inside of the data context
                (a '/' splitted path, for instance: 'datasources/my_datasource')
        """
        import json

        self._data_context = data_context
        self._paths = path.split("/")
        env_var_info = os.environ.get("SEMA4AI_DATA_SERVER_INFO")
        if env_var_info:
            self._env_var_info = json.loads(env_var_info)
        else:
            self._env_var_info = None

    def _get_dict_in_data_context(self) -> dict:
        if self._data_context is None:
            return {}

        from robocorp import log

        with log.suppress():
            if self._data_context is None:
                raise RuntimeError("Data context is not available.")

            dct = self._data_context.value

            v = None
            for path in self._paths:
                if not isinstance(dct, dict):
                    dct = None  # Remove from context
                    raise RuntimeError(
                        f"Unable to get path: {self._paths} in data context (expected dict to get {path!r} from)."
                    )
                try:
                    dct = v = dct[path]
                except KeyError:
                    dct = None  # Remove from context
                    raise RuntimeError(
                        f"Unable to get path: {self._paths} in data context (current path: {path!r})."
                    )

            dct = None  # Remove from context
            if v is None:
                raise RuntimeError(
                    f"Error. Path ({self._paths}) invalid for the data context."
                )

            if not isinstance(v, dict):
                del v
                raise RuntimeError(
                    f"Error. Path ({self._paths}) did not map to a dict in the data context."
                )

            return v

    def _get_env_var_info(self) -> Optional[_EnvVarInfoTypeDict]:
        if self._env_var_info is not None:
            return self._env_var_info

        import json

        info = os.environ.get("SEMA4AI_DATA_SERVER_INFO")
        if info:
            self._env_var_info = json.loads(info)
            return self._env_var_info

        return None

    def _get_from_dict(self, path: str) -> typing.Any:
        from robocorp import log

        with log.suppress():
            paths = path.split("/")
            try:
                found = self._get_dict_in_data_context()
                for path in paths:
                    found = found[path]
                return found
            except KeyError:
                info = os.environ.get("SEMA4AI_DATA_SERVER_INFO")
                if info:
                    env_var_info = self._get_env_var_info()
                    if env_var_info:
                        found = typing.cast(dict, env_var_info)
                        try:
                            for path in paths:
                                found = found[path]
                            return found
                        except Exception:
                            pass
                raise RuntimeError(
                    f"Error. Unable to get: {path} (not available in SEMA4AI_DATA_SERVER_INFO env var nor in data context)."
                )

    @property
    def _http_url(self) -> str:
        """
        Provides the actual url wrapped in this class.
        """
        from robocorp import log

        with log.suppress():
            return self._get_from_dict("http/url")

    @property
    def _http_user(self) -> Optional[str]:
        """
        Provides the actual user wrapped in this class.
        """
        from robocorp import log

        with log.suppress():
            try:
                return self._get_from_dict("http/user")
            except Exception:
                return None  # Not mandatory

    @property
    def _http_password(self) -> Optional[str]:
        """
        Provides the actual password wrapped in this class.
        """
        from robocorp import log

        with log.suppress():
            try:
                return self._get_from_dict("http/password")
            except Exception:
                return None  # Not mandatory

    @property
    def _mysql_host(self) -> str:
        from robocorp import log

        with log.suppress():
            return self._get_from_dict("mysql/host")

    @property
    def _mysql_port(self) -> int:
        from robocorp import log

        with log.suppress():
            return self._get_from_dict("mysql/port")

    @property
    def _mysql_user(self) -> Optional[str]:
        from robocorp import log

        with log.suppress():
            return self._get_from_dict("mysql/user")

    @property
    def _mysql_password(self) -> Optional[str]:
        from robocorp import log

        with log.suppress():
            return self._get_from_dict("mysql/password")


class _ConnectionProviderFromDict(_BaseInternalConnectionProvider):
    """
    Internal API to wrap a datasource which is not passed encrypted.
    """

    def __init__(self, value: dict):
        """
        Args:
            value: A dict with the values meant to be wrapped in this class.
        """

        http = value.get("http")
        mysql = value.get("mysql")

        if http is not None:
            self.__http_url = http.get("url")
            self.__http_user = http.get("user")
            self.__http_password = http.get("password")

        if mysql is not None:
            self.__mysql_host = mysql.get("host")
            self.__mysql_port = mysql.get("port")
            self.__mysql_user = mysql.get("user")
            self.__mysql_password = mysql.get("password")

        if self.__http_password is not None:
            from robocorp import log

            log.hide_from_output(self.__http_password)
            log.hide_from_output(repr(self.__http_password))

        if self.__mysql_password is not None:
            from robocorp import log

            log.hide_from_output(self.__mysql_password)
            log.hide_from_output(repr(self.__mysql_password))

    @property
    def _http_url(self) -> str:
        return self.__http_url

    @property
    def _http_user(self) -> Optional[str]:
        return self.__http_user

    @property
    def _http_password(self) -> Optional[str]:
        return self.__http_password

    @property
    def _mysql_host(self) -> str:
        return self.__mysql_host

    @property
    def _mysql_port(self) -> int:
        return self.__mysql_port

    @property
    def _mysql_user(self) -> Optional[str]:
        return self.__mysql_user

    @property
    def _mysql_password(self) -> Optional[str]:
        return self.__mysql_password
