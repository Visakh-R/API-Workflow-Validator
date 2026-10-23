import unittest
from lexer import tokenize
from parser import parse
from semantic import validate_semantics

class ValidatorTests(unittest.TestCase):
    def validate(self, source):
        return validate_semantics(parse(tokenize(source)))

    def test_valid_workflow(self):
        source = """WORKFLOW Demo {
REQUEST LOGIN
SAVE token FROM LOGIN.access_token
REQUEST GET_PROFILE USING token
REQUEST LOGOUT USING token
}"""
        self.assertEqual(self.validate(source), [])

    def test_auth_before_login(self):
        source = """WORKFLOW Demo {
REQUEST GET_PROFILE
}"""
        errors = self.validate(source)
        self.assertTrue(any("requires authentication" in e for e in errors))

    def test_undefined_variable(self):
        source = """WORKFLOW Demo {
REQUEST LOGIN
REQUEST GET_PROFILE USING missing
}"""
        errors = self.validate(source)
        self.assertTrue(any("used before it is defined" in e for e in errors))

    def test_unknown_operation(self):
        source = """WORKFLOW Demo {
REQUEST FLY_TO_MOON
}"""
        errors = self.validate(source)
        self.assertTrue(any("unknown API operation" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
