import unittest
from io import StringIO, BytesIO

from template_log_parser.pre_df_functions import (
    tag_and_or_combine_lines,
    link_log_file_lines,
)

from test.resources import kodi_unlinked_lines
from template_log_parser.templates.kodi_templates import kodi_line_linking_arguments

from test.resources import logger

class TestPreDFFunctions(unittest.TestCase):
    """Defines a class to test functions that run before the df stage"""

    def test_tag_and_or_combine_lines(self):
        """Test function to assert that tag_and_or_combine_lines returns the correct list"""
        ex_list = [
            "Null",
            "(info): Hello there",
            "(info): Good morning",
            "(info): Goodbye",
            "Nothing",
            "  This. ",
            "  Is.   ",
            " The. ",
            "Start.",
            "of.",
            "Something.",
            "Wonderful",
        ]

        tag = "Friend"

        tag_only = tag_and_or_combine_lines(
            ex_list.copy(),
            start_text="Hello",
            end_text="Goodbye",
            tag="(info) " + tag,
            tag_replace_text="(info)",
        )
        expected_tagged_lines = tag_only[1:4]
        for line in expected_tagged_lines:
            self.assertTrue(tag in line)
            self.assertEqual(
                [
                    "(info) Friend: Hello there",
                    "(info) Friend: Good morning",
                    "(info) Friend: Goodbye",
                ],
                expected_tagged_lines,
            )

        combine_only = tag_and_or_combine_lines(
            ex_list.copy(), start_text="This", end_text="Wonderful", combine=True
        )
        expected_combined_line = combine_only[-1]
        self.assertEqual(
            "This.Is.The.Start.of.Something.Wonderful", expected_combined_line
        )

        both = tag_and_or_combine_lines(
            ex_list.copy(),
            start_text="This",
            end_text="Wonderful",
            combine=True,
            tag=tag + ": This",
            tag_replace_text="This",
        )
        expected_combined_tagged_line = both[-1]
        self.assertEqual(
            "Friend: This.Is.The.Start.of.Something.Wonderful",
            expected_combined_tagged_line,
        )

    def test_link_log_file_lines(self):
        """Test function to assert link_log_file_lines returns a StringIO object with correctly modified lines"""
        types_to_test = [
            kodi_unlinked_lines,  # Path
        ]

        with open(kodi_unlinked_lines, "r", encoding="utf-8") as f:
            lines = f.read()
            string_io_kodi_unlinked_lines = StringIO(lines)
            types_to_test.append(string_io_kodi_unlinked_lines)

        with open(kodi_unlinked_lines, "rb") as f:
            bytes_io_kodi_unlinked = BytesIO(f.read())
            types_to_test.append(bytes_io_kodi_unlinked)

        for item in types_to_test:
            output = link_log_file_lines(item, kodi_line_linking_arguments)
            self.assertIsInstance(output, StringIO)
            logger.info("Correct Type")

            actual_output = output.read().splitlines()
            expected_output = [
                "xml advancedsettings <advancedsettings><videodatabase><type>mysql</type><host>1.1.1.1</host><port>3307</port><user>kodi</user><pass>*****</pass></videodatabase><musicdatabase><type>mysql</type><host>1.1.1.1</host><port>3307</port><user>kodi</user><pass>*****</pass></musicdatabase><videolibrary><importwatchedstate>true</importwatchedstate><importresumepoint>true</importresumepoint></videolibrary></advancedsettings>",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7     Device 7",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_deviceName      : hdmi:CARD=HDMI,DEV=1",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_displayName     : HDA Intel",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_displayNameExtra: HDMI #1",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_deviceType      : AE_DEVTYPE_HDMI",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_channels        : FL, FR",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_sampleRates     : 32000,44100,48000,88200,96000,176400,192000",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_dataFormats     : AE_FMT_S32NE,AE_FMT_S16NE,AE_FMT_S16LE,AE_FMT_RAW",
                "2025-04-12 06:27:11.088 T:17       info <general>: Device7         m_streamTypes     : STREAM_TYPE_AC3,STREAM_TYPE_DTSHD,STREAM_TYPE_DTSHD_MA,STREAM_TYPE_DTSHD_CORE,STREAM_TYPE_DTS_1024,STREAM_TYPE_DTS_2048,STREAM_TYPE_DTS_512,STREAM_TYPE_EAC3,STREAM_TYPE_TRUEHD",
                "2025-04-12 06:30:56.902 T:270     debug <general>: [metadata.tvshows.themoviedb.org.python (1.7.3)]: returning ratings of{'tmdb': {'rating': 8.0, 'votes': 2}}",
                "2025-05-17 06:14:15.348 T:98448   error <general>: SMBFile->Open: Unable to open file : 'smb://1.1.1.1/Movies/some_movie.mkv'unix_err:'2' error : 'No such file or directory'",
                "2025-05-17 06:14:35.535 T:98465   error <general>: SMBDirectory->GetDirectory: Unable to open directory : 'smb://1.1.1.1/Movies/some_folder'unix_err:'d' error : 'Permission denied'",
                "Line that does not require linking",
                "2025-04-12 06:27:11.088 T:17       info <general>:     Device 7 This line meets start text criteria, but end line criteria does not exist and will exceed the limit of ten lines",
                "2025-04-12 06:27:11.088 T:17       info <general>:         m_channels        : FL, FR",
                "line three",
                "line four",
                "line five",
                "line six",
                "line seven",
                "line eight",
                "line nine",
                "line ten",
                "line eleven",
                "2025-04-12 06:27:11.088 T:17       info <general>:     Device 7 This line meets start text criteria but file ends before end text criteria is found",
            ]

            logger.debug(f"Expected Output ({len(expected_output)}): {expected_output}")
            logger.debug(f"Actual Output ({len(actual_output)}): {actual_output}")

            self.assertEqual(expected_output, actual_output)

        improper_file_type = []
        self.assertRaises(
            ValueError,
            link_log_file_lines,
            improper_file_type,
            kodi_line_linking_arguments,
        )
