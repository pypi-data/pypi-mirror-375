"""
Define errors that may be raised by xdoctest
"""


class MalformedDocstr(Exception):
    """
    Exception raised when the docstring itself does not conform to the expected
    style (e.g. google / numpy).
    """


class ExistingEventLoopError(Exception):
    """
    Exception raised when the docstring uses a top level await and the test is
    already running in an event loop.
    """


class DoctestParseError(Exception):
    """
    Exception raised when doctest code has an error.
    """
    def __init__(self, msg, string=None, info=None, orig_ex=None):
        """
        Args:
            msg (str): error message
            string (str | None): the string that failed
            info (Any | None): extra information
            orig_ex (Exception | None): The underlying exceptoin
        """
        super(DoctestParseError, self).__init__(msg)
        self.msg = msg
        self.string = string
        self.info = info
        self.orig_ex = orig_ex


class ExitTestException(Exception):
    pass


class IncompleteParseError(SyntaxError):
    """
    Used when something goes wrong in the xdoctest parser
    """

try:
    import _pytest
    import _pytest.outcomes
except ImportError:  # nocover
    # Define dummy skipped exception if pytest is not available
    class _pytest:  # type: ignore
        class outcomes:
            class Skipped(Exception):
                pass
