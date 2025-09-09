import unittest

from test.resources import logger, built_in_log_file_types

from template_log_parser.templates.template_functions import compile_templates


class TestLogTypeClasses(unittest.TestCase):
    """Defines a class for tests of LogTypeClasses themselves"""

    def test_modify_templates(self):
        """Test function to determine that modify templates correctly adds prefixes and/or suffixes"""
        logger.info(f"---Checking modify_templates()")
        splitting_item = "-|-|-|-|"
        prefix_base = "Line Start "
        prefix = prefix_base + splitting_item
        suffix_base = " Line End"
        suffix = splitting_item + suffix_base

        for built_in in built_in_log_file_types:
            logger.info(f'Built-In {built_in.name}')
            built_in.modify_templates(prefix=prefix, suffix=suffix)

            # From each simple_template namedtuple, pull its compiled template.format attribute for the base string
            deconstructed_templates = [item.template.format for item in built_in.templates]
            for template in deconstructed_templates:
                # Should result in three pieces
                parts = template.split(splitting_item)
                self.assertEqual(parts[0], prefix_base)
                self.assertEqual(parts[2], suffix_base)


                original_template_string = parts[1]
                logger.debug(f"Original template string: {original_template_string}")
                # Ensure there is at least one item in the base templates that matches the original, could be used multiple times
                base_template = [item for item in built_in.base_templates if item[0] == original_template_string]
                logger.debug(f'Matching base templates ({len(base_template)}): {base_template}')
                self.assertTrue(len(base_template) >= 1)

        logger.info("All templates accounted for")

        # Set all templates back to normal
        for built_in in built_in_log_file_types:
            built_in.templates = compile_templates(built_in.base_templates, search_string_criteria='copy')





