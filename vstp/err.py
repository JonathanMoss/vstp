"""Custom exceptions"""


class MissingPartFile(Exception):
    """Exception raised where the required BPLAN file extracts are missing

    Attributes:
        file_name -- the missing file which caused the error
        message -- explanation of the error

    """

    def __init__(self, file_name):
        """Initialisation"""

        self.file_name = file_name
        self.message = f'The {self.file_name} file cannot be found'
        super().__init__(self.message)


class BadViaList(Exception):
    """Exception raised where a non-list is passed as a keyword argument

    Attributes:
        message -- explanation of the error

    """

    def __init__(self):
        """Initialisation"""

        self.message = f'TIPLOCs expected as a list for VIA'
        super().__init__(self.message)


class BadAvoidList(Exception):
    """Exception raised where a non-list is passed as a keyword argument

    Attributes:
        message -- explanation of the error

    """

    def __init__(self):
        """Initialisation"""

        self.message = f'TIPLOCs expected as a list for AVOID'
        super().__init__(self.message)


class BadTiplocError(Exception):
    """Exception raised where the TIPLOC passed is not valid

    Attributes:
        tiploc -- the tiploc being validated
        message -- explanation of the error
    """

    def __init__(self, tiploc):
        """Initialisation"""

        self.tiploc = tiploc
        self.message = f'{self.tiploc} is not a valid TIPLOC'
        super().__init__(self.message)
