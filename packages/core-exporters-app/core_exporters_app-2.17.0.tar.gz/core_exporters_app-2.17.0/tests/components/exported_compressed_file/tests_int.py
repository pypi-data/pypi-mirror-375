"""Integration tests for exporter rest api
"""

from django.contrib.auth.models import AnonymousUser
from django.test import override_settings

from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.utils.integration_tests.integration_base_test_case import (
    IntegrationBaseTestCase,
)
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_exporters_app.components.exported_compressed_file import (
    api as exported_compressed_file_api,
)
from core_exporters_app.components.exported_compressed_file.models import (
    ExportedCompressedFile,
)
from tests.components.exported_compressed_file.fixtures.fixtures import (
    ExportedCompressedFileFixtures,
)

fixture_data = ExportedCompressedFileFixtures()


class TestGetByExportedCompressedFile(IntegrationBaseTestCase):
    """Test Get By Exported Compressed File"""

    fixture = fixture_data

    def setUp(self):
        """setUp"""

        super().setUp()

    def test_get_exported_compressed_file_raises_access_control_error_if_user_is_not_none(
        self,
    ):
        """test_get_exported_compressed_file_raises_access_control_error_if_user_is_not_none"""

        # Act # Assert
        with self.assertRaises(AccessControlError):
            exported_compressed_file_api.get_by_id(
                self.fixture.exported_compressed_file_1.id, None
            )

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_get_exported_compressed_file_returns_object_if_owner_is_none(
        self,
    ):
        """test_get_exported_compressed_file_returns_object_if_owner_is_none"""

        # Act
        result = exported_compressed_file_api.get_by_id(
            self.fixture.exported_compressed_file_3.id, None
        )
        # Assert
        self.assertEqual(result, self.fixture.exported_compressed_file_3)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_get_exported_compressed_file_if_owner_is_none_raises_access_control_error_with_setting_false(
        self,
    ):
        """test_get_exported_compressed_file_if_owner_is_none_raises_access_control_error_with_setting_false"""

        # Act # Assert
        with self.assertRaises(AccessControlError):
            exported_compressed_file_api.get_by_id(
                self.fixture.exported_compressed_file_3.id, None
            )

    def test_get_exported_compressed_file_as_anonymous_raises_access_control_error(
        self,
    ):
        """test_get_exported_compressed_file_as_anonymous_raises_access_control_error"""

        # Arrange
        user = create_mock_user(None, is_anonymous=True)

        # Act # Assert
        with self.assertRaises(AccessControlError):
            exported_compressed_file_api.get_by_id(
                self.fixture.exported_compressed_file_1.id, user
            )

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_get_exported_compressed_file_as_anonymous_returns_object_if_owner_is_none(
        self,
    ):
        """test_get_exported_compressed_file_as_anonymous_returns_object_if_owner_is_none"""

        # Act
        result = exported_compressed_file_api.get_by_id(
            self.fixture.exported_compressed_file_3.id, AnonymousUser()
        )

        # Assert
        self.assertEqual(result, self.fixture.exported_compressed_file_3)

    def test_get_exported_compressed_file_as_anonymous_raises_access_control_error_with_setting_false(
        self,
    ):
        """test_get_exported_compressed_file_as_anonymous_raises_access_control_error_with_setting_false"""

        # Arrange
        user = create_mock_user(None, is_anonymous=True)

        # Act # Assert
        with self.assertRaises(AccessControlError):
            exported_compressed_file_api.get_by_id(
                self.fixture.exported_compressed_file_3.id, user
            )

    def test_get_exported_compressed_file_not_owner_raises_access_control_error(
        self,
    ):
        """test_get_exported_compressed_file_not_owner_raises_access_control_error"""

        # Arrange
        user = create_mock_user("2")

        # Act # Assert
        with self.assertRaises(AccessControlError):
            exported_compressed_file_api.get_by_id(
                self.fixture.exported_compressed_file_1.id, user
            )

    def test_get_exported_compressed_file_as_owner_returns_object(self):
        """test_get_exported_compressed_file_as_owner_returns_object"""

        # Arrange
        user = create_mock_user("1")

        # Act
        result = exported_compressed_file_api.get_by_id(
            self.fixture.exported_compressed_file_1.id, user
        )

        # Assert
        self.assertEqual(result, self.fixture.exported_compressed_file_1)

    def test_get_exported_compressed_file_as_superuser_returns_object(self):
        """test_get_exported_compressed_file_as_superuser_returns_object"""

        # Arrange
        user = create_mock_user("1", is_superuser=True)

        # Act
        result = exported_compressed_file_api.get_by_id(
            self.fixture.exported_compressed_file_2.id, user
        )

        # Assert
        self.assertEqual(result, self.fixture.exported_compressed_file_2)


class TestUpsertExportedCompressedFile(IntegrationBaseTestCase):
    """Test Upsert Exported Compressed File"""

    fixture = fixture_data

    def setUp(self):
        """setUp"""

        super().setUp()

    def test_upsert_creates_exported_compressed_file(
        self,
    ):
        """test_upsert_creates_exported_compressed_file"""

        exported_compressed_file = ExportedCompressedFile(
            file_name="exported_compressed_file_1",
            mime_type="application/zip",
            is_ready=True,
            user_id="1",
        )
        # Act
        result = exported_compressed_file_api.upsert(exported_compressed_file)

        # Assert
        self.assertIsInstance(result, ExportedCompressedFile)

    def test_upsert_updates_exported_compressed_file(
        self,
    ):
        """test_upsert_updates_exported_compressed_file"""
        # Arrange
        self.fixture.exported_compressed_file_1.file_name = "new_file_name"
        # Act
        result = exported_compressed_file_api.upsert(
            self.fixture.exported_compressed_file_1
        )

        # Assert
        self.assertEqual(
            result.file_name, self.fixture.exported_compressed_file_1.file_name
        )
