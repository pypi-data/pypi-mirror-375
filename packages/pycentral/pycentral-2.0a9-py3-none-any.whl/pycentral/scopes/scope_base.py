# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_maps import ScopeMaps
from ..utils.scope_utils import (
    fetch_attribute,
)

scope_maps = ScopeMaps()


class ScopeBase:
    """
    Base class for all scope elements, such as Site, Site_Collection, and Device.
    Provides common functionality like:
      - Returning the object's ID or name.
      - Assigning and unassigning profiles.
    """

    def get_id(self):
        """
        Fetches the ID of the scope element.

        :return: ID of the scope element.
        :rtype: int
        """
        return fetch_attribute(self, "id")

    def get_name(self):
        """
        Fetches the name of the scope element.

        :return: Name of the scope element.
        :rtype: str
        """
        return fetch_attribute(self, "name")

    def get_type(self):
        """
        Fetches the ID of the scope element.

        :return: ID of the scope element.
        :rtype: int
        """
        return fetch_attribute(self, "type")

    def assign_profile(self, profile_name, profile_persona=None):
        """
        Assigns a profile (with the provided name and persona) to the scope.

        :param profile_name: Name of the profile to assign.
        :type profile_name: str
        :param profile_persona: Device Persona of the profile to assign. Optional if unassigning a profile from a device
        :type profile_persona: str

        :return: True if the profile assignment was successful, else False.
        :rtype: bool
        """
        profile_persona = self._resolve_profile_persona(profile_persona)
        if profile_persona is None:
            return False

        resp = scope_maps.associate_profile_to_scope(
            central_conn=self.central_conn,
            scope_id=self.get_id(),
            profile_name=profile_name,
            persona=profile_persona,
        )
        if resp["code"] == 200:
            self.add_profile(name=profile_name, persona=profile_persona)
            return True
        else:
            self.central_conn.logger.error(
                "Unable to assign profile "
                + profile_name
                + " to "
                + self.get_name()
            )
            return False

    def unassign_profile(self, profile_name, profile_persona=None):
        """
        Unassigns a profile (with the provided name and persona) from the scope.

        :param profile_name: Name of the profile to unassign.
        :type profile_name: str
        :param profile_persona: Persona of the profile to unassign. Optional if unassigning a profile from a device
        :type profile_persona: str

        :return: True if the profile unassignment was successful, else False.
        :rtype: bool
        """
        profile_persona = self._resolve_profile_persona(profile_persona)
        if profile_persona is None:
            return False

        resp = scope_maps.unassociate_profile_from_scope(
            central_conn=self.central_conn,
            scope_id=self.get_id(),
            profile_name=profile_name,
            persona=profile_persona,
        )
        if resp["code"] == 200:
            self.remove_profile(name=profile_name, persona=profile_persona)
            return True
        else:
            self.central_conn.logger.error(
                "Unable to unassign profile "
                + profile_name
                + " to "
                + self.get_name()
            )
            return False

    def _resolve_profile_persona(self, profile_persona):
        """
        Internal helper to validate and resolve the correct profile_persona for the scope.
        Returns the resolved persona or None if invalid.
        """
        if self.get_type() == "device":
            if not self.provisioned_status:
                self.central_conn.logger.error(
                    "Device is currently configured via Classic Central only. Please provision the device to new Central before assigning/unassigning profile to device."
                )
                return None
            if profile_persona is not None:
                if profile_persona != self.config_persona:
                    self.central_conn.logger.error(
                        f"Invalid profile persona(device function) '{profile_persona}' for device. Device's current persona is {self.persona} ({self.config_persona}). If you would like the profile to take the device's current persona, you can leave the profile_persona attribute empty."
                    )
                    return None
                return profile_persona
            else:
                return self.config_persona
        else:
            if profile_persona is None:
                self.central_conn.logger.error(
                    "Profile persona is required when assigning a profile to a scope other than device."
                )
                return None
            return profile_persona

    def add_profile(self, name, persona):
        """
        Helper function that adds a profile (with the provided name and persona) to the assigned profiles of the scope in the SDK.

        :param name: Name of the profile to add.
        :type name: str
        :param persona: Device Persona of the profile to add.
        :type persona: str
        """
        self.assigned_profiles.append({"persona": persona, "resource": name})

    def remove_profile(self, name, persona):
        """
        Helper function that removes a profile (with the provided name and persona) from the assigned profiles of the scope in the SDK.

        :param name: Name of the profile to remove.
        :type name: str
        :param persona: Device Persona of the profile to remove.
        :type persona: str

        :return: True if the profile was successfully removed, else False.
        :rtype: bool
        """
        remove_status = False
        index = None
        for id_element, element in enumerate(self.assigned_profiles):
            if element["persona"] == persona and element["resource"] == name:
                index = id_element
                break
        if index is not None:
            self.assigned_profiles.pop(index)
            remove_status = True
        return remove_status
