"""Custom exceptions"""


class MissingPartFile(Exception):
    """Exception raised where the required BPLAN file extracts are missing

    Attributes:
        file_name -- the missing file which caused the error
        message -- explanation of the error

    """

    def __init__(self, file_name):

        self.file_name = file_name
        self.message = f'The {self.file_name} file cannot be found'
        super().__init__(self.message)
