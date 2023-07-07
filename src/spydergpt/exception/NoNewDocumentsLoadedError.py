class NoNewDocumentsLoadedError(Exception):
    """The NoNewDocumentsLoadedError class is used to raise an exception when
    no new documents were loaded during a data processing operation. It
    provides a descriptive message of the error to help identify the issue.
    The error code is also provided to help identify the issue."""

    # error code to the exception to help identify the issue.
    error_code = "NO_NEW_DOCUMENTS"

    def __init__(
        self,
        message: str = "No new documents were loaded during data processing.",
    ) -> None:
        """initializes the NoNewDocumentsLoadedError class with a descriptive
        message of the error. It calls the constructor of the base
        class (Exception) with the error message.

        Args:
            message (str): descriptive message of the error
        """
        # Call the constructor of the base class (Exception)
        # with the error message
        super().__init__(message)

    def __str__(self):
        """returns a string representation of the exception.

        Returns:
            str: string representation of the exception
        """
        return super().__str__()

    def __repr__(self):
        """returns a string representation of the exception that can be used
        to recreate the object.

        Returns:
            str: string representation of the exception
        """
        return f'{self.__class__.__name__}("{self.args}")'
