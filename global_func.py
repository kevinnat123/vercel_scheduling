class CustomError(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))