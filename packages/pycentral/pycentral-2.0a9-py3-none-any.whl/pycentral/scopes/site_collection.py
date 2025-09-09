# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils import NewCentralURLs
from ..utils.scope_utils import (
    set_attributes,
    get_scope_element,
)
from .scope_maps import ScopeMaps
from .site import Site
from ..exceptions import ParameterError
from .scope_base import ScopeBase

urls = NewCentralURLs()

OPTIONAL_ATTRIBUTES = {
    "id": None,
    "associated_sites": 0,
    "associated_devices": 0,
}

OBJECT_ATTRIBUTES = {"assigned_profiles": [], "sites": []}

API_ATTRIBUTE_MAPPING = {
    "id": "id",
    "scopeName": "name",
    "description": "description",
    "siteCount": "associated_sites",
    "deviceCount": "associated_devices",
}

REQUIRED_ATTRIBUTES = ["name", "description"]

scope_maps = ScopeMaps()


class Site_Collection(ScopeBase):
    """
    This class holds site collection and all of its attributes & related methods.
    """

    def __init__(
        self, collection_attributes, central_conn=None, from_api=False
    ):
        """
        Constructor for Site Collection object

        :param collection_attributes: Attributes of the site collection
        :type collection_attributes: dict
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param from_api: Boolean indicates if the collection_attributes is from the Central API response.
        :type from_api: bool, optional
        """
        if from_api:
            collection_attributes = self.__rename_keys(collection_attributes)
        else:
            valid_attributes = REQUIRED_ATTRIBUTES + ["sites"]
            for attribute in collection_attributes:
                if attribute not in valid_attributes:
                    raise ValueError(
                        f'Unexpected attribute: {attribute}. For collection_attributes(not via API) only the following attributes are supported - {", ".join(valid_attributes)}'
                    )
        self.materialized = from_api
        self.central_conn = central_conn
        self.type = "site_collection"
        self.id = None

        missing_required_attributes = [
            attr
            for attr in REQUIRED_ATTRIBUTES
            if attr not in collection_attributes
        ]
        if missing_required_attributes:
            raise ValueError(
                f'Missing required attributes: {", ".join(missing_required_attributes)}'
            )

        valid_attributes = (
            REQUIRED_ATTRIBUTES
            + list(OPTIONAL_ATTRIBUTES.keys())
            + list(OBJECT_ATTRIBUTES.keys())
        )
        unexpected_attributes = [
            attr
            for attr in collection_attributes
            if attr not in valid_attributes
        ]
        if unexpected_attributes:
            raise ValueError(
                f'Unexpected attributes: {", ".join(unexpected_attributes)}.\n If site_collections is being created based off api_response ensure that the from_api flag is set to True'
            )
        set_attributes(
            obj=self,
            attributes_dict=collection_attributes,
            required_attributes=REQUIRED_ATTRIBUTES,
            optional_attributes=OPTIONAL_ATTRIBUTES,
            object_attributes=OBJECT_ATTRIBUTES,
        )

    def create(self):
        """
        Perform a POST call to create a site collection on Central.

        :return: True if site collection was created, else False
        :rtype: bool
        """
        if self.materialized:
            raise Exception(
                "Unable to create a site collection that already exists"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_collection_creation_status = False
        api_method = "POST"
        api_path = urls.fetch_url("SCOPES", "SITE_COLLECTION")
        api_data = self.__generate_api_body()

        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200:
            try:
                site_collection_id = resp["msg"]["items"][0]
                self.id = int(site_collection_id)
                self.materialized = True
                site_collection_creation_status = True
                self.get()
                self.central_conn.logger.info(
                    f"Successfully created site collection {self.get_name()} in Central"
                )
            except KeyError:
                self.central_conn.logger.info(
                    f"Failed to set site collection id of site collection {self.get_name()}"
                )
                pass
        else:
            self.central_conn.logger.error(
                f'Failed to create site collection {self.get_name()} in Central.\nError message - {resp["msg"]}'
            )
        return site_collection_creation_status

    def get(self):
        """
        Performs a GET call to retrieve data of a site collection then sets attributes of self based on API response.

        :return: Returns JSON Data of GET call if success, else None
        :rtype: dict
        """
        if not self.materialized:
            raise Exception(
                "Unable to get a site collection that does not exist"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_collection_data = get_scope_element(
            obj=self, scope="site_collection", scope_id=self.get_id()
        )

        if not site_collection_data:
            self.materialized = False
            self.central_conn.logger.error(
                f"Unable to fetch site collection {self.get_name()} from Central"
            )
        else:
            collection_attributes = self.__rename_keys(site_collection_data)
            set_attributes(
                obj=self,
                attributes_dict=collection_attributes,
                required_attributes=REQUIRED_ATTRIBUTES,
                optional_attributes=OPTIONAL_ATTRIBUTES,
            )
            self.central_conn.logger.info(
                f"Successfully fetched site collection {self.get_name()} from Central."
            )
        return site_collection_data

    def update(self):
        """
        Performs a PUT call to update attributes of site collection on Central if any changes are detected. The source of truth is self

        :return: Returns JSON Data of GET call if success, else None
        :rtype: dict
        """
        if not self.materialized:
            raise Exception(
                "Unable to update a site collection that does not exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        modified = False
        site_collection_data = get_scope_element(
            obj=self, scope="site_collection", scope_id=self.get_id()
        )

        if not site_collection_data:
            self.materialized = False
            raise Exception(
                "Unable to upate site collection as it could not be found in Central."
            )

        collection_attributes = self.__rename_keys(site_collection_data)

        object_attributes = {
            key: getattr(self, key) for key in API_ATTRIBUTE_MAPPING.values()
        }

        if collection_attributes != object_attributes:
            api_method = "PUT"
            api_path = urls.fetch_url("SCOPES", "SITE_COLLECTION")
            api_data = self.__generate_api_body()

            resp = self.central_conn.command(
                api_method=api_method, api_path=api_path, api_data=api_data
            )
            if resp["code"] == 200:
                modified = True
                self.central_conn.logger.info(
                    f"Successfully updated site collection {self.get_name()} in Central"
                )
            else:
                self.central_conn.logger.info(
                    f"Failed to update site collection {self.get_name()} in Central.\n Error message - {resp['msg']}"
                )
        return modified

    def delete(self):
        """
        Performs DELETE call to delete Site Collection.

        :return: True if DELETE was successful, else returns False if DELETE was unsuccessful
        :rtype: bool
        """
        if not self.materialized:
            raise Exception(
                "Unable to delete a site collection that doesn't exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site collection without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_collection_deletion_status = False
        api_method = "DELETE"
        api_path = urls.fetch_url("SCOPES", "SITE_COLLECTION")
        api_params = {"scopeId": self.get_id()}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_params=api_params
        )
        if resp["code"] == 200:
            self.id = None
            self.materialized = False
            site_collection_deletion_status = True
            self.central_conn.logger.info(
                f"Successfully deleted site collection {self.get_name()}"
            )
        else:
            self.central_conn.logger.error(
                f"Failed to delete site collection {self.get_name()}.\n Error message - {resp['msg']}"
            )
        return site_collection_deletion_status

    def associate_site(self, sites):
        """
        Performs POST call to associate sites with a site collection.

        :param sites: List of sites that need to be associated with this site collection. Each element of this list is of type class:`Site` or list of site ids(integer type)
        :type sites: list

        :return: True if site association was successful, else returns False if site association failed.
        :rtype: bool
        """
        api_method = "POST"
        api_path = urls.fetch_url("SCOPES", "ADD_SITE_TO_COLLECTION")

        if all(isinstance(site, Site) for site in sites):
            site_ids = [str(site.get_id()) for site in sites]
        elif all(isinstance(site_id, int) for site_id in sites):
            site_ids = [str(site_id) for site_id in sites]
        else:
            raise ParameterError(
                "sites parameter should only be a list of type Site or int"
            )

        api_data = {
            "siteCollectionId": str(self.get_id()),
            "siteIds": site_ids,
        }
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200 and len(resp["msg"]["items"]) == len(site_ids):
            self.central_conn.logger.info(
                f'Successfully associated site(s) {", ".join([str(site.name) for site in sites])} to site collection {self.name}'
            )
            self.get()
            for site in sites:
                if isinstance(site, Site):
                    self.add_site(site_id=site.get_id())
                    site.add_site_collection(
                        site_collection_id=self.get_id(),
                        site_collection_name=self.get_name,
                    )
                elif isinstance(site, int):
                    self.add_site(site_id=site)
            return True
        else:
            self.central_conn.logger.error(
                f'Failed to associate site(s) {", ".join([str(site.name) for site in sites])} to site collection {self.name}.\n Error message - {resp["msg"]}'
            )
            return False

    def unassociate_site(self, sites):
        """
        Performs DELETE call to unassociate sites with a site collection.

        :param sites: List of sites that need to be unassociated with this site collection. Each element of this list is of type class:`Site` or list of site ids(integer type)
        :type sites: list

        :return: True if site unassociation was successful, else returns False if site unassociation failed.
        :rtype: bool
        """
        api_method = "DELETE"
        api_path = urls.fetch_url("SCOPES", "REMOVE_SITE_FROM_COLLECTION")
        if all(isinstance(site, Site) for site in sites):
            site_ids = [str(site.get_id()) for site in sites]
        elif all(isinstance(site_id, int) for site_id in sites):
            site_ids = [str(site_id) for site_id in sites]
        else:
            raise ParameterError(
                "sites parameter should only be a list of type Site or int"
            )
        api_params = {"siteIds": site_ids}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_params=api_params
        )
        if resp["code"] == 200 and len(resp["msg"]["items"]) == len(site_ids):
            self.central_conn.logger.info(
                f'Successfully unassociated site(s) {", ".join([str(site.name) for site in sites])} from site collection {self.name}'
            )
            self.get()
            for site in sites:
                if isinstance(site, Site):
                    site.remove_site_collection()
                    self.remove_site(site_id=site.get_id())
                elif isinstance(site, int):
                    self.remove_site(site_id=site)
            return True
        else:
            self.central_conn.logger.error(
                f'Failed to unassociate site(s) {", ".join([str(site.name) for site in sites])} to site collection {self.name}.\n Error message - {resp["msg"]}'
            )
            return False

    def add_site(self, site_id):
        """
        This function adds the site details(site ID) to the site collection attributes.

        :param site_id: Site ID of the site
        :type site_id: str

        :return: True if site details were successfully updated to site collection attributes, else returns False.
        :rtype: bool
        """
        if int(site_id):
            self.sites.append(int(site_id))
            return True
        return False

    def remove_site(self, site_id):
        """
        This function removes the site details(site ID) the site collection attributes.

        :param site_id: Site ID of the site
        :type site_id: str

        :return: True if site details were removed from site collection attributes, else returns False.
        :rtype: bool
        """
        if site_id in self.sites:
            self.sites.remove(site_id)
            return True
        return False

    def __str__(self):
        """
        This function returns the string containing the name and ID of the site collection.

        :return: String representation of this class
        :rtype: str
        """
        return f"Site Collection ID - {self.get_id()}, Site Collection Name - {self.get_name()}"

    def __rename_keys(self, api_attributes):
        """
        This function renames the keys of the site collection attributes from the API response

        :param api_attributes: Site collection attributes from Central API Response
        :type api_attributes: dict

        :return: Renamed dictionary of site collection attributes. The renamed keys maps to attributes that will be defined in the site collection object
        :rtype: dict
        """
        extra_keys = ["type", "scopeId"]
        for key in extra_keys:
            if key in extra_keys:
                del api_attributes[key]

        integer_attributes = ["id", "siteCount", "deviceCount"]
        renamed_dict = {}
        for key, value in api_attributes.items():
            new_key = API_ATTRIBUTE_MAPPING.get(key)
            if new_key:
                if key in integer_attributes:
                    value = int(value)
                renamed_dict[new_key] = value
            else:
                raise ValueError(
                    f"Unknown attribute {key} found in API response"
                )
        return renamed_dict

    def __generate_api_body(self):
        """
        This function returns the dictionary of site collection attributes are needed to making API calls

        :return: Dictionary of site collection attributes needed for making API calls to Central.
        :rtype: dict
        """
        api_body = {
            "scopeName": self.name,
            "description": self.description,
        }
        if self.materialized:
            api_body["scopeId"] = str(self.get_id())
        elif len(self.sites) > 0:
            api_body["siteIds"] = [str(site_id) for site_id in self.sites]

        return api_body
