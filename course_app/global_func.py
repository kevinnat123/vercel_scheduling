class CustomError(Exception):
    """
    CustomError adalah exception khusus yang dapat menyimpan detail kesalahan dalam bentuk dictionary.

    Ini berguna untuk menangani error secara terstruktur, terutama saat kamu ingin melempar pesan
    kompleks seperti error validasi, error API, atau pesan yang bisa dikembalikan ke frontend.

    Attributes:
        error_dict (dict): Dictionary yang berisi detail error.

    Example:
        raise CustomError({'message': 'Username tidak boleh kosong', 'field': 'username'})

    Catching:
        try:
            ...
        except CustomError as e:
            print(e.error_dict['message'])  # Mengakses pesan kesalahan
    """
    
    def __init__(self, error_dict):
        """
        Inisialisasi CustomError dengan dictionary berisi informasi kesalahan.

        Args:
            error_dict (dict): Dictionary error, misalnya {'message': 'Field kosong'}
        """
        self.error_dict = error_dict
        super().__init__(str(error_dict))