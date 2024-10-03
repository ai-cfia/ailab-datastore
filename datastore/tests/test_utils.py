import os
import unittest

class EnvironmentVariableError(Exception):
    pass

class Test_Utils(unittest.TestCase):
    
    def test_secrets(self):
        NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")
        if not NACHET_SCHEMA:
            raise EnvironmentVariableError("NACHET_SCHEMA is not set")
        NACHET_DB_URL = os.getenv("NACHET_DB_URL") 
        if not NACHET_DB_URL:
            raise EnvironmentVariableError("NACHET_DB_URL is not set")
