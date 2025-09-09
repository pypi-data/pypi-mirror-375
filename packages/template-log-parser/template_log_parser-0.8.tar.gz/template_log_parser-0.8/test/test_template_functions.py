import unittest

from template_log_parser.templates.template_functions import compile_templates
from template_log_parser.templates.definitions import SimpleTemplate

from test.resources import logger

base_templates = [
    ["{this} is a {template} with a search string for types event_a", "event_a", "is a"],
    ["this is a {template} without a search string for types event_b", "event_b"],
]

class TestTemplateFunctions(unittest.TestCase):
    """Defines a class to test functions associated with templates"""

    def test_compile_templates(self):
        """Assert compile_templates return the correct types, and behaves correctly for search string criteria"""

        logger.info("Checking compile_templates()")

        logger.info("Checking search_string_criteria='copy'")
        # Copy
        compiled_templates_copy = compile_templates(templates=base_templates, search_string_criteria='copy')
        # Pair items for testing
        paired_list_copy = zip(compiled_templates_copy, base_templates)
        for item in paired_list_copy:
            compiled = item[0]
            self.assertIsInstance(compiled, SimpleTemplate)
            base = item[1]
            compiled_template_string = compiled.template.format

            # Base string matches Parser.format, compiled template string
            self.assertEqual(compiled_template_string, base[0])
            # Search string in base string along with compiled template string
            self.assertTrue(compiled.search_string in base[0])
            self.assertTrue(compiled.search_string in compiled_template_string)

            # Ensure copy
            if len(base) < 3:
                self.assertEqual(base[1], compiled.search_string)

        logger.info("search_string_criteria='copy' OK")

        logger.info("Checking search_string_criteria='find'")
        # Find

        compiled_templates_find = compile_templates(templates=base_templates, search_string_criteria='find')
        # Pair items for testing
        paired_list_find = zip(compiled_templates_find, base_templates)
        for item in paired_list_find:
            compiled = item[0]
            self.assertIsInstance(compiled, SimpleTemplate)
            base = item[1]
            compiled_template_string = compiled.template.format

            # Base string matches Parser.format, compiled template string
            self.assertEqual(compiled_template_string, base[0])
            # Search string in base string along with compiled template string
            self.assertTrue(compiled.search_string in base[0])
            self.assertTrue(compiled.search_string in compiled_template_string)

        logger.info("search_string_criteria='find' OK")