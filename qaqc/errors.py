
class NonFatalTestError(Exception):
    """
    The current test failed, but later tests may still run.
    """


class FatalTestError(Exception):
    """
    The current test failed and all remaining tests must be skipped.
    """


class FailedTestCriteriaError(NonFatalTestError):
    """
    Backwards-compatible name for a nonfatal test failure.
    """


class MissingRequiredTestError(Exception):
    """
    Internal error for when a test was missing a previous required test.
    """
