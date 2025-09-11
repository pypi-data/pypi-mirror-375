"""SharePoint class."""
from abc import ABC

import requests
from O365 import Account

from t_office_365.drive.drive import Drive, DriveSite
from t_office_365.utils import check_result


class SharepointSite(DriveSite, ABC):
    """Represents a SharePoint site in Microsoft Office 365.

    Provides access to SharePoint-specific services and Excel functionality.
    """

    def __init__(self, account: Account, site_name: str, drive_name: str = None) -> None:
        """Initializes instance of the SharepointService class.

        :param:
        - account (Account): The account object containing the authentication information.
        - site_name (str): The name of Microsoft Office site.
        - drive_name (str): Optional. The name of the desired Drive inside the site.
        """
        self.__site_name = site_name
        self.__drive_name = drive_name
        super().__init__(account)

    def _get_drive_id(self) -> str:
        """Get the Drive ID for SharePoint.

        :param:
        - site_name (str): The name of the site.

        :return:
        - str: The ID of the SharePoint Drive.
        """
        site_id = self.account.sharepoint().get_site("root", self.__site_name).object_id

        url = self.get_url(f"/sites/{site_id}/drives")
        result = requests.get(url, headers=self.headers())
        check_result(result, url)

        if not self.__drive_name:
            return result.json()["value"][0]["id"]
        return next((drive["id"] for drive in result.json()["value"] if drive["name"] == self.__drive_name), "")


class SharepointRootSite(DriveSite, ABC):
    """Represents a SharePoint root site in Microsoft Office 365.

    Provides access to SharePoint-specific services and Excel functionality.
    """

    def __init__(self, account: Account, drive_name: str) -> None:
        """Initializes instance of the SharepointRootSite class.

        :param:
        - account (Account): The account object containing the authentication information.
        - drive_name (str): Optional. The name of the desired Drive inside the root site.
        """
        self.__drive_name = drive_name
        super().__init__(account)

    def _get_drive_id(self) -> str:
        """Get the Drive ID for SharePoint.

        :return:
        - str: The ID of the SharePoint Drive.
        """
        site_id = self.account.sharepoint().get_root_site().object_id

        url = self.get_url(f"/sites/{site_id}/drives")
        result = requests.get(url, headers=self.headers())
        check_result(result, url)
        return next((drive["id"] for drive in result.json()["value"] if drive["name"] == self.__drive_name), "")


class Sharepoint(Drive):
    """SharePoint class is used for API calls to SharePoint."""

    def site(self, site_name: str, drive_name: str = None) -> SharepointSite:
        """Get a SharePoint site by its name.

        Used to access Sharepoints that have different sites configured, usually their URL will follow the pattern:
        - https://your_domain.sharepoint.com/sites/your_site/forms
        For the given example, 'sites/your_site' would be the site name.

        :param:
        - site_name (str): The name of the SharePoint site.
        - drive_name (str): Optional. The name of the desired Drive inside the site.

        :return:
        - A SharepointSite object representing the specified SharePoint site.
        """
        return SharepointSite(self.account, site_name, drive_name)

    def root_site(self, drive_name: str) -> SharepointRootSite:
        """Get a SharePoint site by its root site drive name.

        Some Sharepoints are not configured to use different sites.
        Instead, all drives are listed for the root site. Bellow is an example URL of how you can identify that:
        - https://your_domain.sharepoint.com/drive_name/forms

        :param:
        - drive_name (str): The name of the drive available for the root site.

        :return:
        - A SharepointRootSite object representing the specified SharePoint root site.
        """
        return SharepointRootSite(self.account, drive_name)
