class NotIntegratedYetException(Exception):
    """Exception raised when Trajectory is not integrated yet"""

    def __init__(self, path):
        super().__init__("Trajectory not integrated yet")
