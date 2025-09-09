# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_base import ScopeBase
from ..utils.scope_utils import (
    fetch_attribute,
    get_scope_elements,
    get_all_scope_elements,
    DEFAULT_LIMIT,
    validate_find_scope_elements,
    lookup_in_map,
)
from .device import Device
from .site import Site
from .site_collection import Site_Collection
from .scope_maps import ScopeMaps
from .device_group import Device_Group
from ..utils import NewCentralURLs
from ..exceptions import ParameterError
from concurrent.futures import ThreadPoolExecutor, as_completed

SUPPORTED_SCOPES = ["site", "site_collection", "device", "device_group"]

urls = NewCentralURLs()

scope_maps = ScopeMaps()


class Scopes(ScopeBase):
    """
    This class holds the Scopes(Global heirarchy) class & methods that can be used to manage sites & site collections within the Global Heirarchy
    """

    def __init__(self, central_conn):
        """
        Constructor for Scopes object. This represents

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        """
        if central_conn is None:
            raise ParameterError(
                "Central connection is required to create Scopes object."
            )
        self.central_conn = central_conn
        self.id = None
        self.name = "Global"
        self.type = "global"
        self.materialized = True
        self.assigned_profiles = []
        self._lookup_maps = {"id": {}, "serial": {}, "name": {}}

        self.site_collections = []
        self.sites = []
        self.devices = []
        self.device_groups = []

        self.get()

    def get(self):
        """
        Performs GET calls to Central to retrieve latest data of all scope elements(Global, Site Collections, Sites, Devices, & Device Groups).

        :return: Returns True if all scope elements are successfully fetched, else False
        :rtype: bool
        """
        try:
            self.central_conn.logger.info(
                "Fetching all scopes (Global, Site Collection, Site, Device, Device Groups)..."
            )
            self.get_all_sites()
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        self.get_all_site_collections
                    ): "site_collections",
                    executor.submit(self.get_all_devices): "devices",
                    executor.submit(
                        self.get_all_device_groups
                    ): "device_groups",
                }

            for future in as_completed(futures):
                try:
                    future.result()  # Ensure exceptions are raised if any
                except Exception as e:
                    self.central_conn.logger.error(
                        f"Error fetching {futures[future]}: {e}"
                    )

            self._correlate_scopes()
            self.get_id()
            self.central_conn.logger.info(
               "Mapping configuration profiles to scopes..."
            )
            self.get_scope_profiles()

            self.central_conn.logger.info(
               "Successfully fetched configuration hierarchy details from Central"
            )
            self.materialized = True
            return True

        except Exception as e:
            self.central_conn.logger.error(f"Error in scope get method: {e}")
            return False

    def get_all_sites(self):
        """
        Performs GET calls to retrieve all the sites from Central.

        :return: Returns list of sites. Each element of this list is of type class:`Site`
        :rtype: list
        """
        sites_response = get_all_scope_elements(obj=self, scope="site")
        if not sites_response:
            raise Exception(
                "Failed to fetch sites from Central. Sites are a required construct of new Central. Please check your Central account & ensure that you have at least one site created."
            )
        self.sites = [
            Site(
                central_conn=self.central_conn,
                site_attributes=site,
                from_api=True,
            )
            for site in sites_response
        ]
        return self.sites

    def get_all_site_collections(self):
        """
        Performs GET calls to retrieve all the site collections from Central.

        :return: Returns list of site collections. Each element of this list is of type class:`Site_Collection`
        :rtype: list
        """
        site_collections_response = get_all_scope_elements(
            obj=self, scope="site_collection"
        )

        self.site_collections = [
            Site_Collection(
                central_conn=self.central_conn,
                collection_attributes=collection,
                from_api=True,
            )
            for collection in site_collections_response
        ]
        return self.site_collections

    def get_all_devices(self):
        """
        Performs GET calls to retrieve all the devices from Central.

        :return: Returns list of devices. Each element of this list is a dictionary with device details.
        :rtype: list
        """

        device_list = Device.get_all_devices(
            central_conn=self.central_conn,
        )
        self.devices = [
            Device(
                central_conn=self.central_conn,
                device_attributes=device,
                from_api=True,
            )
            for device in device_list
        ]
        return self.devices

    def get_all_device_groups(self):
        """
        Performs GET calls to retrieve all the device groups from Central.

        :return: Returns list of device groups. Each element of this list is a dictionary with device group details.
        :rtype: list
        """
        device_groups_list = get_all_scope_elements(
            obj=self, scope="device_group"
        )
        self.device_groups = [
            Device_Group(
                central_conn=self.central_conn,
                device_group_attributes=device_group,
                from_api=True,
            )
            for device_group in device_groups_list
        ]
        return device_groups_list

    def get_id(self):
        """
        Returns the ID of the Global scope. If the ID hasn't been set, the function will fetch the ID.

        :return: ID of global scope
        :rtype: int
        """
        global_scope_id = None
        if self.id is not None:
            global_scope_id = fetch_attribute(self, "id")
        elif len(self.sites) > 0:
            sample_site = self.sites[0]
            heirarchy = None
            heirarchy = self.get_hierarchy(
                scope="site", id=sample_site.get_id()
            )
            if heirarchy is not None:
                org_data = None
                heirarchy_data = heirarchy[0]["hierarchy"]
                for scope in heirarchy_data:
                    if scope["scopeType"] == "org":
                        org_data = scope
                        break
                if org_data is not None:
                    global_scope_id = int(org_data["scopeId"])
                    self.id = global_scope_id
                    self._lookup_maps["id"].update({global_scope_id: self})
                    self.central_conn.logger.info(
                        "Global scope ID set successfully."
                    )
                else:
                    self.central_conn.logger.error(
                        "Unable to get global scope ID"
                    )
        else:
            self.central_conn.logger.error(
                "Unable to get global scope ID without having 1 site in the central account."
            )
        return global_scope_id

    def get_sites(
        self, limit=DEFAULT_LIMIT, offset=0, filter_field="", sort=""
    ):
        """
        Fetches the list of sites from Central based on the provided attributes.

        :param limit: Number of sites to be fetched, defaults to 100
        :type limit: int
        :param offset: Pagination start index, defaults to 1
        :type offset: int
        :param filter_field: Field that needs to be used for sorting the list of sites. Accepted values for this argument is scope-name, address, state, country, city, device-count, collection-name, zipcode, timezone
        :type filter_field: str, optional
        :param sort: Direction of sorting for the field. ASC or DESC are accepted values for this argument
        :type sort: str, optional

        :return: List of sites based on the provided arguments. If there are errors it will return None.
        :rtype: list
        """
        return get_scope_elements(
            obj=self,
            scope="site",
            limit=limit,
            offset=offset,
            filter_field=filter_field,
            sort=sort,
        )

    def get_site_collections(
        self,
        limit=DEFAULT_LIMIT,
        offset=0,
        filter_field="",
        sort="",
    ):
        """
        Fetches the list of site collections from Central based on the provided attributes.

        :param limit: Number of site collections to be fetched, defaults to 100
        :type limit: int
        :param offset: Pagination start index, defaults to 1
        :type offset: int
        :param filter_field: Field that needs to be used for sorting the list of sites. Accepted values for this argument is site-count, device-count, scope-name
        :type filter_field: str, optional
        :param sort: Direction of sorting for the field. ASC or DESC are accepted values for this argument
        :type sort: str, optional

        :return: List of site collections based on the provided arguments. If there are errors it will return None.
        :rtype: list
        """
        return get_scope_elements(
            obj=self,
            scope="site_collection",
            limit=limit,
            offset=offset,
            filter_field=filter_field,
            sort=sort,
        )

    def _correlate_scopes(self):
        """
        Correlates sites with site collections and devices with sites using internal maps.
        """
        self._update_lookup_map()

        for site in self.sites:
            collection_id = fetch_attribute(site, "site_collection_id")
            if collection_id and int(collection_id) in self._lookup_maps["id"]:
                self._lookup_maps["id"][int(collection_id)].add_site(
                    site.get_id()
                )

        for device in self.devices:
            site_id = fetch_attribute(device, "site_id")
            if site_id and int(site_id) in self._lookup_maps["id"]:
                self._lookup_maps["id"][int(site_id)].devices.append(
                    device.get_id()
                )
            group_id = fetch_attribute(device, "group_id")
            if group_id and int(group_id) in self._lookup_maps["id"]:
                self._lookup_maps["id"][int(group_id)].devices.append(
                    device.get_id()
                )

    def find_site_collection(
        self, site_collection_ids=None, site_collection_names=None
    ):
        """
        This function returns the site collection(of type class:`Site_Collection`) based on the provided parameters. Only one of collection_name or collection_id is required to find the site collection(s).

        :param site_collection_ids: ID(s) of site collections to find, optional
        :type site_collection_ids: int or list
        :param site_collection_names: Name(s) of site collections to find, optional
        :type site_collection_names: str or list

        :return: Found site collection(s) or None if not found.
        :rtype: list or None
        """
        site_collections = self._find_scope_element(
            ids=site_collection_ids,
            names=site_collection_names,
            scope="site_collection",
        )
        if not site_collections:
            self.get_all_sites()
            site_collections = self._find_scope_element(
                ids=site_collection_ids,
                names=site_collection_names,
                scope="site_collection",
            )
        return site_collections

    def find_site(self, site_ids=None, site_names=None):
        """
        This function returns the site(of type class:`Site`) based on the provided parameters. Only one of site_ids or site_names is required to find the site(s).

        :param site_ids: ID of site or list of site IDs
        :type site_ids: str or list
        :param site_names: Name of site or list of site names
        :type site_names: str or list

        :return: If the site(s) are found, the site(s) are returned, else None is returned.
        :rtype: dict
        """
        sites = self._find_scope_element(
            ids=site_ids, names=site_names, scope="site"
        )
        if not sites:
            self.get_all_sites()
            sites = self._find_scope_element(
                ids=site_ids, names=site_names, scope="site"
            )
        return sites

    def find_device(
        self, device_ids=None, device_names=None, device_serials=None
    ):
        """
        This function returns the device(of type class:`Device`) based on the
            provided parameters. Only one of device_ids or device_names or
            device_serials is required to find the device(s).

        :param device_ids: ID(s) of devices to find, optional
        :type device_ids: int or list
        :param device_names: Name(s) of devices to find, optional
        :type device_names: str or list
        :param device_serials: Serial number(s) of devices to find, optional
        :type device_serials: str or list

        :return: Found device(s) or None if not found.
        :rtype: list or None
        """
        devices = self._find_scope_element(
            ids=device_ids,
            names=device_names,
            serials=device_serials,
            scope="device",
        )
        if not devices:
            self.get_all_devices()
            devices = self._find_scope_element(
                ids=device_ids,
                names=device_names,
                serials=device_serials,
                scope="device",
            )
        return devices

    def find_device_group(
        self,
        device_group_ids=None,
        device_group_names=None,
    ):
        """
        This function returns the device group(of type class:`DeviceGroup`) based on the
            provided parameters. Only one of device_group_ids or device_group_names is required to find the device group(s).

        :param device_group_ids: ID(s) of device groups to find, optional
        :type device_group_ids: int or list
        :param device_group_names: Name(s) of device groups to find, optional
        :type device_group_names: str or list

        :return: Found device group(s) or None if not found.
        :rtype: list or None
        """
        device_groups = self._find_scope_element(
            ids=device_group_ids,
            names=device_group_names,
            scope="device_group",
        )
        if not device_groups:
            self.get_all_device_groups()
            device_groups = self._find_scope_element(
                ids=device_group_ids,
                names=device_group_names,
                scope="device_group",
            )
        return device_groups

    def _find_scope_element(
        self, ids=None, names=None, serials=None, scope=""
    ):
        """
        Helper function to find scope elements based on provided parameters.

        :param ids: ID(s) of the element(s), optional
        :type ids: str or list
        :param names: Name(s) of the element(s), optional
        :type names: str or list
        :param serials: Serial number(s) of the element(s) (only for devices), optional
        :type serials: str or list
        :param scope: Specific scope to search in (e.g., "site", "device"), optional
        :type scope: str, optional

        :return: Found element(s) or None if not found
        :rtype: list, or None
        """
        # Validate input parameters
        validate_find_scope_elements(
            ids=ids, names=names, serials=serials, scope=scope
        )
        self._update_lookup_map()
        result = self._search_scope_elements(ids, names, serials, scope)

        if not result:
            params = [("ids", ids), ("names", names), ("serials", serials)]
            param_type, param_value = next(
                ((k, v) for k, v in params if v), ("unknown", None)
            )

            self.central_conn.logger.error(
                f"Unable to find scope element for scope '{scope}'. Parameter: {param_type}={param_value}. Please check the provided parameter(s)."
            )
            result = None

        return result

    def _search_scope_elements(
        self, ids=None, names=None, serials=None, scope=""
    ):
        """
        Searches for scope elements using the lookup maps.

        :param ids: ID(s) of the element(s), optional
        :type ids: str or list
        :param names: Name(s) of the element(s), optional
        :type names: str or list
        :param serials: Serial number(s) of the element(s) (only for devices)
        :type serials: str or list
        :param scope: Specific scope to search in (e.g., "site", "device"), optional
        :type scope: str, optional

        :return: Found element(s) or None if not found.
        :rtype: list or None
        """
        found_elements = None
        if ids:
            found_elements = lookup_in_map(ids, self._lookup_maps["id"])
        elif serials:
            found_elements = lookup_in_map(
                serials, self._lookup_maps["serial"]
            )
        elif names:
            self._update_name_lookup_map()
            if scope:
                scope = scope.lower()
                found_elements = lookup_in_map(
                    names, self._lookup_maps["name"][scope + "s"]
                )
            else:
                # If no scope is provided, check all scopes
                for scope in SUPPORTED_SCOPES:
                    found_elements = lookup_in_map(
                        names, self._lookup_maps["name"][scope + "s"]
                    )
                    if found_elements:
                        break
        return found_elements

    def _update_name_lookup_map(self):
        """
        Updates the name lookup map for all supported scopes.
        """
        for scope in SUPPORTED_SCOPES:
            self._lookup_maps["name"][scope + "s"] = {
                element.get_name(): element
                for element in getattr(self, scope + "s", [])
            }

    def _update_lookup_map(self):
        """
        Updates the lookup maps for IDs and serials.
        """
        # if key is None:
        for element_list in [
            self.sites,
            self.site_collections,
            self.devices,
            self.device_groups,
        ]:
            self._lookup_maps["id"].update(
                {element.get_id(): element for element in element_list}
            )
        self._lookup_maps["serial"].update(
            {device.get_serial(): device for device in self.devices}
        )

    def add_sites_to_site_collection(
        self,
        site_collection_id=None,
        site_collection_name=None,
        site_ids=None,
        site_names=None,
    ):
        """
        Adds site(s) to a site collection.

        :param site_collection_id: ID of the site collection. Either site_collection_name or site_collection_id is required.
        :type site_collection_id: int, optional
        :param site_collection_name: Name of the site collection. Either site_collection_name or site_collection_id is required.
        :type site_collection_name: str, optional
        :param site_ids: ID of the site that needs to be associated with the site collection. If multiple sites need to be associated, a list of site IDs can be provided. Either site_ids or site_names is required.
        :type site_ids: int or list, optional
        :param site_names: Name of the site that needs to be associated with the site collection. If multiple sites need to be associated, a list of site names can be provided. Either site_ids or site_names is required.
        :type site_names: str or list, optional

        :return: True if successful, else False.
        :rtype: bool
        """
        site_collection = self.find_site_collection(
            site_collection_ids=site_collection_id,
            site_collection_names=site_collection_name,
        )
        if site_collection:
            sites = self.find_site(site_ids=site_ids, site_names=site_names)
            if isinstance(sites, Site):
                sites = [sites]
            if all(sites):
                site_association = site_collection.associate_site(sites=sites)
                if site_association:
                    return True
                else:
                    self.central_conn.logger.error(
                        "Unable to complete site association with site collection."
                    )
                    return False

            else:
                self.central_conn.logger.error(
                    "Unable to associate invalid site(s) with site collection. Please provide valid site id(s) or name(s)."
                )
                return False
        elif site_collection is None:
            self.central_conn.logger.error(
                "Unable to associate site(s) with invalid site collection. Please provide a valid site collection id or name."
            )
            return False

    def remove_sites_from_site_collection(
        self, site_ids=None, site_names=None
    ):
        """
        Removes site(s) from a site collection.

        :param site_ids: ID of the site that needs to be unassociated from site collection. If multiple sites need to be unassociated, a list of site IDs can be provided. Either site_ids or site_names is required.
        :type site_ids: int or list, optional
        :param site_names: Name of the site that needs to be unassociated from site collection. If multiple sites need to be unassociated, a list of site names can be provided. Either site_ids or site_names is required.
        :type site_names: str or list, optional

        :return: True if successful, else False.
        :rtype: bool
        """
        sites = self.find_site(site_ids=site_ids, site_names=site_names)
        if not isinstance(sites, list):
            sites = [sites]
        if all(sites):
            api_method = "DELETE"
            api_path = urls.fetch_url("SCOPES", "REMOVE_SITE_FROM_COLLECTION")
            api_params = {
                "siteIds": ",".join([str(site.get_id()) for site in sites])
            }
            resp = self.central_conn.command(
                api_method=api_method, api_path=api_path, api_params=api_params
            )
            if resp["code"] == 200:
                site_name_str = ", ".join(
                    [str(site.get_name()) for site in sites]
                )
                self.central_conn.logger.info(
                    "Successfully removed sites "
                    + site_name_str
                    + " from site collection."
                )
                self._update_site_collection_attributes(sites=sites)
                return True
            else:
                self.central_conn.logger.error(resp["msg"])
                return False
        else:
            self.central_conn.logger.error(
                "Unable to remove invalid site(s) from site collection. Please provide valid site id(s) or name(s)."
            )
        return False

    def _update_site_collection_attributes(self, sites):
        """
        Helper function to update site collection attributes after removing sites.

        :param sites: List of sites to update.
        :type sites: list
        """
        for site in sites:
            old_collection_attributes = site.get_site_collection_attributes()
            if old_collection_attributes is not None:
                old_collection = self.find_site_collection(
                    site_collection_ids=old_collection_attributes["id"]
                )
                if old_collection:
                    old_collection.remove_site(site_id=site.get_id())
                site.remove_site_collection()

    def create_site(
        self,
        site_attributes,
        site_collection_id=None,
        site_collection_name=None,
    ):
        """
        Creates a new site in Central and optionally associates it with a site collection.

        :param site_attributes: Attributes of the site to create.
        :type site_attributes: dict
        :param site_collection_id: ID of the site collection. Either site_collection_name or site_collection_id is required if the site has to be associated to a site collection.
        :type site_collection_id: int, optional
        :param site_collection_name: Name of the site collection. Either site_collection_name or site_collection_id is required if the site has to be associated to a site collection.
        :type site_collection_name: str, optional

        :return: True if successful, else False.
        :rtype: bool
        """
        site_obj = Site(
            site_attributes=site_attributes, central_conn=self.central_conn
        )
        site_creation_status = site_obj.create()

        if site_creation_status:
            self.sites.append(site_obj)
            if site_collection_id or site_collection_name:
                self.add_sites_to_site_collection(
                    site_collection_id=site_collection_id,
                    site_collection_name=site_collection_name,
                    site_ids=[site_obj.get_id()],
                )

        else:
            self.central_conn.logger.error(
                f"Unable to create site {site_obj.get_name()}"
            )
        return site_creation_status

    def delete_site(self, site_id=None, site_name=None):
        """
        Deletes a site in Central.

        :param site_id: ID of the site that needs to be deleted. Either site_id or site_name is required.
        :type site_id: int, optional
        :param site_name: Name of the site that needs to be deleted. Either site_id or site_name is required.
        :type site_name: str, optional

        :return: True if successful, else False.
        :rtype: bool
        """
        site_deletion_status = False
        site = self.find_site(site_ids=site_id, site_names=site_name)
        if site:
            site_id = site.get_id()
            site_deletion_status = site.delete()
            if site_deletion_status:
                self._remove_scope_element(
                    scope="site", element_id=site.get_id()
                )
                if site.site_collection_id:
                    site_collection = self.find_site_collection(
                        site_collection_ids=site.site_collection_id
                    )
                    site_collection.remove_site(site_id)

            else:
                error_resp = site_deletion_status
                self.central_conn.logger.error(
                    "Unable to delete site. "
                    + "Error-message -> "
                    + error_resp["msg"]["message-code"][0]["code"]
                )
        else:
            self.central_conn.logger.error(
                "Please provide a valid site id or name to be deleted."
            )
        return site_deletion_status

    def _remove_scope_element(self, scope, element_id):
        """
        Removes a scope element from the internal list.

        :param scope: Type of the element (e.g., site, site_collection).
        :type scope: str
        :param element_id: ID of the element to remove.
        :type element_id: int

        :return: True if successful, else False.
        :rtype: bool
        """
        if scope not in SUPPORTED_SCOPES:
            self.central_conn.logger.error(
                "Unknown scope provided. Please provide one of the supported scopes - "
                ", ".join(SUPPORTED_SCOPES)
            )
            return False
        if scope == "site":
            element_list = self.sites
        elif scope == "site_collection":
            element_list = self.site_collections

        index = None
        for id_element, element in enumerate(element_list):
            if element.get_id() == element_id:
                index = id_element
                break
        if index is not None:
            element_list.pop(index)
            return True
        return False

    def create_site_collection(
        self, collection_attributes, site_ids=None, site_names=None
    ):
        """
        Creates a new site collection in Central and optionally associates sites with it.

        :param collection_attributes: Attributes of the site collection to create.
        :type collection_attributes: dict
        :param site_ids: ID of the site(s). If multiple sites need to be associated with the site collection, a list of site ids can be provided. Either site_ids or site_names is required if the site collection has to be associated with site(s)
        :type site_ids: int or list, optional
        :param site_names: Name of the site(s). If multiple sites need to be associated with the site collection, a list of site names can be provided. Either site_ids or site_names is required if the site collection has to be associated with site(s)
        :type site_names: str or list, optional

        :return: True if successful, else False.
        :rtype: bool
        """
        site_collection_obj = Site_Collection(
            collection_attributes=collection_attributes,
            central_conn=self.central_conn,
        )
        site_collection_creation_status = site_collection_obj.create()
        if site_collection_creation_status:
            self.site_collections.append(site_collection_obj)
            if site_ids or site_names:
                site_addition_status = self.add_sites_to_site_collection(
                    site_collection_id=site_collection_obj.get_id(),
                    site_ids=site_ids,
                    site_names=site_names,
                )
                if site_addition_status:
                    self.central_conn.logger.info(
                        f"Successfully associated sites with site collection {site_collection_obj.get_name()}"
                    )
                else:
                    self.central_conn.logger.error(
                        f"Failed to associate sites with site collection {site_collection_obj.get_name()}"
                    )
        else:
            self.central_conn.logger.error(
                f"Unable to create site collection {site_collection_obj.get_name()}"
            )
        return site_collection_creation_status

    def delete_site_collection(
        self,
        site_collection_id=None,
        site_collection_name=None,
        remove_sites=False,
    ):
        """
        Deletes a site collection in Central. Optionally removes associated sites first.

        :param site_collection_id: ID of the site collection that needs to be deleted. Either site_collection_id or site_collection_name is required.
        :type site_collection_id: int, optional
        :param site_collection_name: Name of the site that needs to be deleted. Either site_collection_id or site_collection_name is required.
        :type site_collection_name: str, optional
        :param remove_sites: Boolean indicates if the method should remove sites associated with the site collection before deleting it. If set to true, it will first delete site(s) associated with the site collection & then delete it. If set to False & the site collection has site(s) associated with it, the method will not allow you to delete the site collection.
        :type remove_sites: bool, optional

        :return: True if successful, else False.
        :rtype: bool
        """
        site_collection_deletion_status = False
        site_collection = self.find_site_collection(
            site_collection_ids=site_collection_id,
            site_collection_names=site_collection_name,
        )
        if site_collection:
            num_associated_sites = len(site_collection.sites)
            if remove_sites is False and num_associated_sites > 0:
                self.central_conn.logger.error(
                    "Unable to delete site collection with "
                    f"{num_associated_sites} sites associated with it. "
                    "Set remove_sites argument to True to remove sites associated with site collection before deleting it."
                )
                return site_collection_deletion_status
            elif remove_sites and num_associated_sites > 0:
                self.central_conn.logger.info(
                    f"Attempting to remove {num_associated_sites} associated sites before deleting site collection "
                    + site_collection.get_name()
                )
                site_unassociated_status = (
                    self.remove_sites_from_site_collection(
                        site_ids=site_collection.sites
                    )
                )
                if site_unassociated_status is not True:
                    self.central_conn.logger.info(
                        f"Unable to remove {num_associated_sites} associated sites from site collection "
                        + f"{site_collection.get_name()}."
                    )
                    return site_unassociated_status
            site_collection_deletion_status = site_collection.delete()
            if site_collection_deletion_status:
                self._remove_scope_element(
                    scope="site_collection",
                    element_id=site_collection.get_id(),
                )
            else:
                error_resp = site_collection_deletion_status
                self.central_conn.logger.error(
                    "Unable to delete site collection. "
                    + "Error-message -> "
                    + error_resp["msg"]["message-code"][0]["code"]
                )
        else:
            self.central_conn.logger.error(
                "Please provide a valid site collection id or name to be deleted."
            )
        return site_collection_deletion_status

    def get_hierarchy(self, scope, id=None, name=None):
        """
        Fetches the hierarchy of the specified scope element in the global hierarchy.

        :param scope: Type of the element (e.g., site, site_collection).
        :type scope: str
        :param id: ID of the element, optional
        :type id: int
        :param name: Name of the element, optional
        :type name: str

        :return: Hierarchy of the specified element.
        :rtype: dict
        """
        if scope not in SUPPORTED_SCOPES:
            self.central_conn.logger.error(
                "Unknown scope provided. Please provide one of the supported scopes - "
                ", ".join(SUPPORTED_SCOPES)
            )
            return None

        scope_id = None
        if id:
            scope_id = id
        else:
            if scope == "site":
                site = self.find_site(site_names=name)
                if site is not None:
                    scope_id = site.get_id()
            elif scope == "site_collection":
                site_collection = self.find_site_collection(
                    site_collection_names=name
                )
                if site_collection is not None:
                    scope_id = site.get_id()
            if not scope_id:
                self.central_conn.logger.error(
                    f"Unable to find id of specified scope element with name of {name}"
                )
                return None

        api_method = "GET"
        api_path = urls.fetch_url("SCOPES", "HIERARCHY")
        api_params = {"scopeId": scope_id, "scopeType": scope.lower()}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_params=api_params
        )
        if resp["code"] == 200:
            self.central_conn.logger.info(
                f"Successfully fetched scope heirarchy of "
                f"{scope} with id {id}"
            )
            return resp["msg"]["items"]
        else:
            self.central_conn.logger.error(
                f"Unable to fetch scope heirarchy of {scope} with id {id}"
            )
            return None

    def __str__(self):
        """
        Returns a string representation of the Global scope.

        :return: String representation of the Global scope.
        :rtype: str
        """
        return f"Global ID - {self.id}"

    def get_scope_profiles(self):
        """
        Fetches all configuration profiles associated with different scope elements.
        """
        scope_map_list = scope_maps.get(central_conn=self.central_conn)
        self.central_conn.logger.info(
            f"Total scope mappings fetched from account: {len(scope_map_list)}"
        )
        unknown_scopes = []
        for mapping in scope_map_list:
            scope_id = mapping.pop("scope-name")
            if scope_id in unknown_scopes:
                continue
            required_scope_element = self._find_scope_element(ids=scope_id)
            if required_scope_element:
                required_scope_element.add_profile(
                    name=mapping["resource"],
                    persona=mapping["persona"],
                )
            else:
                unknown_scopes.append(scope_id)

    def assign_profile_to_scope(
        self,
        profile_name,
        profile_persona=None,
        scope=None,
        scope_name=None,
        scope_id=None,
    ):
        """
        Assigns a configuration profile to the specified scope.

        :param profile_name: Name of the configuration profile.
        :type profile_name: str
        :param profile_persona: Device Persona of the profile to assign. Optional if assigning a profile to a device
        :type profile_persona: str
        :param scope: Type of the scope (e.g., global, site, site_collection, device), optional
        :type scope: str
        :param scope_name: Name of the scope element. Either scope_name or scope_id is required
        :type scope_name: str
        :param scope_id: ID of the scope element. Either scope_name or scope_id is required
        :type scope_id: int

        :return: True if successful, else False.
        :rtype: bool
        """
        return self._profile_to_scope_helper(
            "assign",
            profile_name,
            profile_persona,
            scope,
            scope_name,
            scope_id,
        )

    def unassign_profile_to_scope(
        self,
        profile_name,
        profile_persona=None,
        scope=None,
        scope_name=None,
        scope_id=None,
    ):
        """
        Unassigns a configuration profile from the specified scope.

        :param profile_name: Name of the configuration profile.
        :type profile_name: str
        :param profile_persona: Device Persona of the profile to unassign. Optional if unassigning a profile from a device
        :type profile_persona: str
        :param scope: Type of the scope (e.g., global, site, site_collection, device), optional
        :type scope: str
        :param scope_name: Name of the scope element. Either scope_name or scope_id is required
        :type scope_name: str
        :param scope_id: ID of the scope element. Either scope_name or scope_id is required
        :type scope_id: int

        :return: True if successful, else False.
        :rtype: bool
        """
        return self._profile_to_scope_helper(
            "unassign",
            profile_name,
            profile_persona,
            scope,
            scope_name,
            scope_id,
        )

    def _profile_to_scope_helper(
        self,
        operation,
        profile_name,
        profile_persona=None,
        scope=None,
        scope_name=None,
        scope_id=None,
    ):
        """
        Helper method for assigning or unassigning profiles to/from scopes.

        :param operation: Operation type (assign or unassign).
        :type operation: str
        :param profile_name: Name of the configuration profile.
        :type profile_name: str
        :param profile_persona: Persona of the profile.
        :type profile_persona: str
        :param scope: Type of the scope (e.g., global, site, site_collection), optional
        :type scope: str
        :param scope_name: Name of the scope element. Either scope_name or scope_id is required
        :type scope_name: str
        :param scope_id: ID of the scope element. Either scope_name or scope_id is required
        :type scope_id: int

        :return: True if successful, else False.
        :rtype: bool
        """
        required_scope_element = None
        if scope == "global":
            required_scope_element = self
        else:
            required_scope_element = self._find_scope_element(
                names=scope_name, ids=scope_id, scope=scope
            )
        if required_scope_element:
            if (
                required_scope_element.get_type() != "device"
                and profile_persona is None
            ):
                self.central_conn.logger.error(
                    "Profile persona is required for assigning or unassigning profiles to/from scopes other than devices."
                )
                return False
            if operation == "assign":
                return required_scope_element.assign_profile(
                    profile_name=profile_name,
                    profile_persona=profile_persona,
                )
            elif operation == "unassign":
                return required_scope_element.unassign_profile(
                    profile_name=profile_name,
                    profile_persona=profile_persona,
                )

    def move_devices_between_sites(
        self,
        current_site,
        new_site,
        device_serial,
        device_type=None,
        device_identifier=None,
        deployment_mode=None,
    ):
        """
        This is a method that is used to move devices between sites.

        :param current_site: ID or name or Site instance of the the current site of the device
        :type current_site: int or str or class:`Site`
        :param new_site: ID or name or Site instance of the the site to which the device has to be moved
        :type new_site: int or str class:`Site`
        :param device_serial: Serial number of device that has to be moved
        :type device_serial: str
        :param device_type: Type of device that will be moved. For eg. AP, SWITCH, GATEWAY
        :type device_type: str, optional
        :param device_identifier: Name of the scope element. Either scope_name or scope_id is required
        :type device_identifier: str, optional
        :param deployment_mode: Deployment type of device. For eg. Standalone, Virtual Controller
        :type deployment_mode: str, optional

        :return: True if the device was successfully moved to the new site
        :rtype: bool
        """
        print(
            "Moving devices between sites via NBAPI is not currently supported"
        )
        return False
