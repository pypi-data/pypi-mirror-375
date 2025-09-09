from ..utils.url_utils import generate_url_with_params
import time
from ..exceptions import ParameterError
from ..utils.troubleshooting_utils import (
    SUPPORTED_DEVICE_TYPES,
    TROUBLESHOOTING_METHOD_DEVICE_MAPPING,
)


class Troubleshooting:
    @staticmethod
    def aaa_aps_test(
        central_conn,
        serial_number,
        radius_server_ip,
        username,
        password,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a AAA test on the specified device and polls for test result,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param radius_server_ip: RADIUS server IP address or hostname
        :param username: Username for authentication
        :param password: Password for authentication
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("aaa_test"),
        )

        try:
            response = Troubleshooting.initiate_aaa_aps_test(
                central_conn=central_conn,
                serial_number=serial_number,
                radius_server_ip=radius_server_ip,
                username=username,
                password=password,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_aaa_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating AAA test for {device_type} {serial_number} on {radius_server_ip}: {str(e)}"
            )
            raise

    @staticmethod
    def aaa_cx_test(
        central_conn,
        serial_number,
        radius_server_ip,
        username,
        password,
        auth_method_type,
        radius_server_port=None,
        vrf=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a AAA test on the specified device and polls for test result,
        supported device type includes CX.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param radius_server_ip: RADIUS server IP address or hostname
        :param username: Username for authentication
        :param password: Password for authentication
        :param auth_method_type: Authentication method type, chap or pap
        :param radius_server_port: RADIUS server port (optional)
        :param vrf: VRF (optional)
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("aaa_test"),
        )

        try:
            response = Troubleshooting.initiate_aaa_cx_test(
                central_conn=central_conn,
                serial_number=serial_number,
                auth_method_type=auth_method_type,
                radius_server_ip=radius_server_ip,
                username=username,
                password=password,
                radius_server_port=radius_server_port,
                vrf=vrf,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_aaa_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating AAA test for {device_type} {serial_number} on {radius_server_ip}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_aaa_aps_test(
        central_conn,
        serial_number,
        radius_server_ip,
        username,
        password,
    ):
        """
        Initiates a AAA test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param radius_server_ip: RADIUS server IP address or hostname
        :param username: Username for authentication
        :param password: Password for authentication
        :return: Response from the API containing task ID and other details
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if not radius_server_ip or not isinstance(radius_server_ip, str):
            raise ParameterError(
                "RADIUS server must be a valid string IP address or hostname."
            )
        elif radius_server_ip:
            api_data["serverName"] = radius_server_ip

        if not username or not isinstance(username, str):
            raise ParameterError("Username must be a valid string.")
        elif username:
            api_data["username"] = username

        if not password or not isinstance(password, str):
            raise ParameterError("Password must be a valid string.")
        elif password:
            api_data["password"] = password

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/aaa"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate AAA test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"AAA test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_aaa_cx_test(
        central_conn,
        serial_number,
        auth_method_type,
        radius_server_ip,
        username,
        password,
        radius_server_port=None,
        vrf=None,
    ):
        """
        Initiates a AAA test on the specified device,
        supported device type includes CX.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param radius_server_ip: RADIUS server IP address or hostname
        :param username: Username for authentication
        :param password: Password for authentication
        :param auth_method_type: Authentication method type, chap or pap
        :param radius_server_port: RADIUS server port (optional)
        :param vrf: VRF (optional)
        :return: Response from the API containing task ID and other details
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if (
            not auth_method_type
            or not isinstance(auth_method_type, str)
            or auth_method_type.lower() not in ["chap", "pap"]
        ):
            raise ParameterError(
                "Authentication method type must be 'chap' or 'pap'."
            )
        elif auth_method_type:
            api_data["authMethodType"] = auth_method_type

        if not radius_server_ip or not isinstance(radius_server_ip, str):
            raise ParameterError(
                "RADIUS server IP address must be a valid string."
            )
        elif radius_server_ip:
            api_data["radiusServerIp"] = radius_server_ip

        if not username or not isinstance(username, str):
            raise ParameterError("Username must be a valid string.")
        elif username:
            api_data["username"] = username

        if not password or not isinstance(password, str):
            raise ParameterError("Password must be a valid string.")
        elif password:
            api_data["password"] = password

        if (
            radius_server_port
            and not isinstance(radius_server_port, int)
            or (
                isinstance(radius_server_port, int)
                and not (1 <= radius_server_port <= 65535)
            )
        ):
            raise ParameterError(
                "Radius server port must be a valid integer between 1 to 65535."
            )
        elif radius_server_port:
            api_data["radiusServerPort"] = radius_server_port

        if vrf and not isinstance(vrf, str):
            raise ParameterError("VRF must be a valid string.")
        elif vrf:
            api_data["vrf"] = vrf

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/aaa"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate AAA test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"AAA test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_aaa_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """
        Retrieves the results of an AAA test on the specified device with the
        provided task ID, supported device type includes APs and CX.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/aaa/async-operations/{task_id}",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get AAA result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"AAA for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"AAA for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def cable_test(
        central_conn,
        device_type,
        serial_number,
        ports,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a cable test on the specified device and polls for test
        result, supported device types include cx and aos-s.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param ports: List of the ports to test
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
        )

        try:
            response = Troubleshooting.initiate_cable_test(
                central_conn=central_conn,
                ports=ports,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_cable_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating cable test for {device_type} {serial_number} on {ports}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_cable_test(
        central_conn,
        device_type,
        serial_number,
        ports,
    ):
        """
        Initiates a cable test on the specified device, supported device types
        include cx and aos-s.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param ports: List of the ports to test
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
        )

        if not ports or not isinstance(ports, list):
            raise ParameterError("Ports must be a non-empty list.")

        api_data = {"ports": ports}

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/cableTest"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate cable test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Cable test initiated successfully for {device_type}"
            f" {serial_number} on {ports}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_cable_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """
        Retrieves the results of a cable test on the specified device,
        supported device types include cx and aos-s.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("cable_test"),
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/cableTest/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get cable test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Cable test for {device_type} {serial_number} with task ID"
                f" {task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Cable test for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def disconnect_all_clients(central_conn, device_type, serial_number):
        """
        Disconnects all clients from the specified device, Gateways only.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the API
        """

        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_all_clients"
            ),
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/disconnectClientAll",
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                "Failed to initiate disconnect for all clients: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            "Disconnect all clients initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_all_users(central_conn, device_type, serial_number):
        """
        Disconnects all users from the specified device, APs only.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_all_users"
            ),
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/disconnectUserAll",
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                "Failed to initiate disconnect for all users: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            "Disconnect all users initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_all_users_ssid(
        central_conn, device_type, serial_number, network
    ):
        """
        Disconnects all users from the specified device on the specified
        network/SSID, APs only.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param network: SSID of the network to disconnect users from
        :return: Response from the API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_all_users_ssid"
            ),
        )

        api_data = dict()
        if not isinstance(network, str):
            raise ParameterError("SSID must be a valid string.")
        else:
            api_data["networkName"] = network

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/disconnectUserByNetwork",
            ),
            api_data=api_data,
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate disconnect for all users on SSID {network}: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Disconnect all users on SSID {network} initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_client_mac_addr(
        central_conn, device_type, serial_number, mac_address
    ):
        """
        Disconnects a client from the specified device by MAC address,
        Gateways only.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param mac_address: MAC address of the client to disconnect
        :return: Response from the API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_client_mac_addr"
            ),
        )

        api_data = dict()

        if not isinstance(mac_address, str):
            raise ParameterError("MAC address must be a valid string.")
        else:
            api_data["clientMacAddress"] = mac_address

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/disconnectClientByMacAddress",
            ),
            api_data=api_data,
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate disconnect for mac {mac_address}: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Disconnect client {mac_address} initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def disconnect_user_mac_addr(
        central_conn, device_type, serial_number, mac_address
    ):
        """
        Disconnects a user from the specified device by MAC address, APs only.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param mac_address: MAC address of the user to disconnect
        :return: Response from the API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "disconnect_user_mac_addr"
            ),
        )

        api_data = dict()

        if not isinstance(mac_address, str):
            raise ParameterError("MAC address must be a valid string.")
        else:
            api_data["userMacAddress"] = mac_address

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/disconnectUserByMacAddress",
            ),
            api_data=api_data,
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate disconnect for mac {mac_address}: "
                f"{resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Disconnect user {mac_address} initiated successfully for "
            f"{device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def http_test(
        central_conn,
        device_type,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a HTTP test on the specified device and polls for test result,
        supported device types include CX, APs, and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param vrf: CX device_type only, VRF to use, if None provided default VRF will be used
        :param source_interface: CX device_type only, Source interface for the test
        :param source_port: CX device_type only, Source port for the test
        :param name_server: CX device_type only, IPv4 address of the DNS server to use
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("http_test"),
        )

        try:
            response = Troubleshooting.initiate_http_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                destination=destination,
                vrf=vrf,
                source_interface=source_interface,
                source_port=source_port,
                name_server=name_server,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_http_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTP test for {device_type} {serial_number}"
                f" on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_http_test(
        central_conn,
        device_type,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
    ):
        """
        Initiates a HTTP test on the specified device,
        supported device types include CX, APs, and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param vrf: CX device_type only, VRF to use, if None provided default VRF will be used
        :param source_interface: CX device_type only, Source interface for the test
        :param source_port: CX device_type only, Source port for the test
        :param name_server: CX device_type only, IPv4 address of the DNS server to use
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("http_test"),
        )

        api_data = dict()

        if destination and isinstance(destination, str):
            # SWITCH require different key than ACCESS_POINT and GATEWAYS
            if device_type.lower() in ["aps", "gateways"]:
                api_data["url"] = destination
            else:
                api_data["destination"] = destination
                api_data["protocol"] = "HTTP"
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if vrf and not isinstance(vrf, str):
            raise ParameterError("VRF must be a valid string.")
        elif vrf:
            api_data["vrf"] = vrf

        if source_interface and not isinstance(source_interface, str):
            raise ParameterError("Source interface must be a valid string.")
        elif source_interface:
            api_data["source_interface"] = source_interface

        if (
            source_port
            and isinstance(source_port, int)
            and (0 <= source_port <= 65535)
        ):
            api_data["source_port"] = source_port
        elif source_port:
            raise ParameterError("Source port must be a valid integer 0-65535.")

        if name_server and not isinstance(name_server, str):
            raise ParameterError("Name server must be a valid string.")
        elif name_server:
            api_data["name_server"] = name_server

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/http"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTP test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTP test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_http_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """
        Retrieves the results of a HTTP test on the specified device,
        supported device types include CX, APs, and GATEWAYS.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("http_test"),
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/http/async-operations/{task_id}",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get HTTP test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"HTTP test for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"HTTP test for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def https_aps_test(
        central_conn,
        serial_number,
        destination,
        timeout=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a HTTPs test on the specified AP device and polls for test
        result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param timeout: Timeout for the test in seconds, APs only
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the API containing task ID and other details
        """
        device_type = "aps"
        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_https_aps_test(
                central_conn=central_conn,
                serial_number=serial_number,
                destination=destination,
                timeout=timeout,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_https_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTPS test for {device_type} {serial_number} on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def https_cx_test(
        central_conn,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a HTTPs test on the specified CX device and polls for test
        result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param vrf: VRF to use, if None provided default VRF will be used
        :param source_interface: Source interface for the test
        :param source_port: Source port for the test
        :param name_server: IPv4 address of the DNS server to use
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_https_cx_test(
                central_conn=central_conn,
                serial_number=serial_number,
                destination=destination,
                vrf=vrf,
                source_interface=source_interface,
                source_port=source_port,
                name_server=name_server,
            )
            task_id = Troubleshooting._get_task_id(response)
            # CX Uses HTTP GET using Protocol HTTPS
            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_http_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTPS test for {device_type} "
                f"{serial_number} on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def https_gateways_test(
        central_conn,
        serial_number,
        destination,
        count=None,
        interval=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a HTTPs test on the specified Gateway device and polls for
        test result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param count: Number of ping packets to send (1-10)
        :param interval: Time between ping packets in seconds (1-10)
        :param include_raw_output: Whether to include raw output in the response, true or false
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "gateways"
        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_https_gateways_test(
                central_conn=central_conn,
                serial_number=serial_number,
                destination=destination,
                count=count,
                interval=interval,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_https_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating HTTPS test for {device_type} {serial_number} on {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_https_aps_test(
        central_conn,
        serial_number,
        destination,
        timeout=None,
    ):
        """
        Initiates a HTTPs test on the specified AP device

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param timeout: Timeout for the test in seconds, APs only
        :return: Response from the API containing task ID and other details
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if timeout and not isinstance(timeout, int) and device_type != "aps":
            raise ParameterError(
                "Timeout must be a valid integer from 1-10 and is valid "
                "for device_type=APs only."
            )
        elif timeout:
            api_data["timeout"] = timeout

        if not destination or (
            destination and not isinstance(destination, str)
        ):
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )
        elif destination:
            api_data["url"] = destination

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/https"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTPS test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTPS test initiated successfully for {device_type} "
            f"{serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_https_cx_test(
        central_conn,
        serial_number,
        destination,
        vrf=None,
        source_interface=None,
        source_port=None,
        name_server=None,
    ):
        """
        Initiates a HTTPs test on the specified CX device

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param vrf: VRF to use, if None provided default VRF will be used
        :param source_interface: Source interface for the test
        :param source_port: Source port for the test
        :param name_server: IPv4 address of the DNS server to use
        :return: Response from the API containing task ID and other details
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if vrf and not isinstance(vrf, str):
            raise ParameterError("VRF must be a valid string.")
        elif vrf:
            api_data["vrf"] = vrf

        if source_interface and not isinstance(source_interface, str):
            raise ParameterError("Source interface must be a valid string.")
        elif source_interface:
            api_data["source_interface"] = source_interface

        if (
            source_port
            and isinstance(source_port, int)
            and (0 <= source_port <= 65535)
        ):
            api_data["source_port"] = source_port
        elif source_port:
            raise ParameterError("Source port must be a valid integer 0-65535.")

        if name_server and not isinstance(name_server, str):
            raise ParameterError("Name server must be a valid string.")
        elif name_server:
            api_data["name_server"] = name_server
        if destination and isinstance(destination, str):
            api_data["destination"] = destination
            api_data["protocol"] = "HTTPS"
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/http"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTPS test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTPS test initiated successfully for {device_type} "
            f"{serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_https_gateways_test(
        central_conn,
        serial_number,
        destination,
        count=None,
        interval=None,
        include_raw_output=None,
    ):
        """
        Initiates a HTTPs test on the specified Gateway device

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination hostname or IP address
        :param count: Number of ping packets to send (1-10)
        :param interval: Time between ping packets in seconds (1-10)
        :param include_raw_output: Whether to include raw output in the
        response, true or false
        :return: Response from the API containing task ID and other details
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        api_data = dict()

        if count and not isinstance(count, int):
            raise ParameterError(
                "Count must be a valid integer from 1-10 and is valid for"
                " device_type=gateways only."
            )
        elif count:
            api_data["count"] = count

        if interval and not isinstance(interval, int):
            raise ParameterError(
                "Interval must be a valid integer from 1-10 and is valid for"
                " device_type=gateways only."
            )
        elif interval:
            api_data["interval"] = interval

        if include_raw_output and not isinstance(include_raw_output, bool):
            raise ParameterError("Include raw output must be a boolean.")
        elif include_raw_output is not None:
            api_data["includeRawOutput"] = bool(include_raw_output)

        if destination and isinstance(destination, str):
            api_data["url"] = destination
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/https"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate HTTPS test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"HTTPS test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_https_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """
        Retrieves the results of a HTTPs test on the specified Gateway device

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/https/async-operations/{task_id}",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get HTTPS test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"HTTPS test for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"HTTPS test for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def iperf_test(
        central_conn,
        device_type,
        serial_number,
        server_address,
        port=None,
        duration=None,
        parallel=None,
        omit=None,
        include_reverse=None,
        vlan_interface=None,
        protocol=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates an iperf test on the specified device and polls for test
        result, supported device type includes Gateways.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param server_address: Server address for the iperf test
        :param port: TCP Port (1-65535) (optional)
        :param duration: Transmission time in seconds (10-120) (optional)
        :param parallel: Number of parallel streams, (1-128) (optional)
        :param omit: Omit the first n seconds of the test (optional)
        :param include_reverse: Include reverse test, true or false (optional)
        :param vlan_interface: VLAN interface for the test (optional)
        :param protocol: Protocol to use, tcp or udp (optional)
        :param include_raw_output: Include raw output in the response (optional)
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """

        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("iperf_test"),
        )

        try:
            response = Troubleshooting.initiate_iperf_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                server_address=server_address,
                port=port,
                duration=duration,
                parallel=parallel,
                omit=omit,
                include_reverse=include_reverse,
                vlan_interface=vlan_interface,
                protocol=protocol,
                include_raw_output=include_raw_output,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_iperf_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating iperf test for {device_type} "
                f"{serial_number} on {server_address}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_iperf_test(
        central_conn,
        device_type,
        serial_number,
        server_address,
        port=None,
        duration=None,
        parallel=None,
        omit=None,
        include_reverse=None,
        vlan_interface=None,
        protocol=None,
        include_raw_output=None,
    ):
        """
        Initiates an iperf test on the specified device,
        supported device type includes Gateways.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param server_address: Server address for the iperf test
        :param port: TCP Port (1-65535) (optional)
        :param duration: Transmission time in seconds (10-120) (optional)
        :param parallel: Number of parallel streams, (1-128) (optional)
        :param omit: Omit the first n seconds of the test (optional)
        :param include_reverse: Include reverse test, true or false (optional)
        :param vlan_interface: VLAN interface for the test (optional)
        :param protocol: Protocol to use, tcp or udp (optional)
        :param include_raw_output: Include raw output in the response (optional)
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("iperf_test"),
        )

        api_data = dict()

        if not server_address or not isinstance(server_address, str):
            raise ParameterError(
                "Server address must be a valid IP address string."
            )
        elif server_address:
            api_data["iperfServerAddress"] = server_address

        if port and (not isinstance(port, int) or not (1 <= port <= 65535)):
            raise ParameterError(
                "Port must be a valid integer between 1 and 65535."
            )
        elif port:
            api_data["port"] = port

        if duration and (
            not isinstance(duration, int) or not (10 <= duration <= 120)
        ):
            raise ParameterError(
                "Duration must be a valid integer between 10 and 120."
            )
        elif duration:
            api_data["duration"] = duration

        if parallel and (
            not isinstance(parallel, int) or not (1 <= parallel <= 128)
        ):
            raise ParameterError(
                "Parallel must be a valid integer between 1 and 128."
            )
        elif parallel:
            api_data["parallel"] = parallel

        if omit and (not isinstance(omit, int) or omit < 0):
            raise ParameterError(
                "Omit must be a valid integer greater than or equal to 0."
            )
        elif omit:
            api_data["omit"] = omit

        if include_reverse and not isinstance(include_reverse, bool):
            raise ParameterError("Include reverse must be a valid boolean.")
        elif include_reverse is not None:
            api_data["includeReverse"] = include_reverse

        if vlan_interface and not isinstance(vlan_interface, str):
            raise ParameterError("VLAN interface must be a valid string.")
        elif vlan_interface:
            api_data["vlanInterface"] = vlan_interface

        if protocol and protocol.lower() not in ["tcp", "udp"]:
            raise ParameterError("Protocol must be either 'tcp' or 'udp'.")
        elif protocol and protocol.lower() in ["tcp", "udp"]:
            api_data["protocol"] = protocol

        if include_raw_output and not isinstance(include_raw_output, bool):
            raise ParameterError("Include raw output must be a valid boolean.")
        elif include_raw_output is not None:
            api_data["includeRawOutput"] = include_raw_output

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/iperf"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate iPerf test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"iPerf test initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_iperf_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """
        Retrieves the results of an iperf test on the specified device,
        supported device type includes Gateways.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """

        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/iperf/async-operations/{task_id}",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get iPerf result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"iPerf for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"iPerf for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def locate_device(central_conn, device_type, serial_number):
        """
        Initiates a locate (e.g., blinking LED) operation on the specified
        device.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("locate_test"),
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting", f"{device_type}/{serial_number}/locate"
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate locate: {resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Locate initiated successfully for {device_type} {serial_number}. Please check the device for visual confirmation."
        )
        return resp

    @staticmethod
    def nslookup_test(
        central_conn,
        device_type,
        serial_number,
        host,
        dns_server=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates an nslookup test on the specified device and polls for test
        result, supported device type includes APs.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param host: Server address for the nslookup test
        :param dns_server: DNS server address (optional)
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("nslookup_test"),
        )

        try:
            response = Troubleshooting.initiate_nslookup_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                host=host,
                dns_server=dns_server,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_nslookup_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating nslookup test for {device_type} {serial_number} on {host}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_nslookup_test(
        central_conn,
        host,
        device_type,
        serial_number,
        dns_server=None,
    ):
        """
        Initiates an nslookup test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param host: Server address for the nslookup test
        :param dns_server: DNS server address (optional)
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("nslookup_test"),
        )

        api_data = {"host": host}

        if dns_server is not None:
            api_data["dnsServer"] = dns_server

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/nslookup"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate Nslookup test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Nslookup test initiated successfully for {device_type} {serial_number} to {host}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_nslookup_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """
        Retrieves the results of a nslookup test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/nslookup/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get nslookup test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Nslookup test for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Nslookup test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def ping_aoss_test(
        central_conn,
        serial_number,
        destination,
        use_ipv6=None,
        packet_size=None,
        count=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a ping test on the specified AOS-S device and polls for test
        result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param packet_size: Packet size in bytes (10-2000)
        :param count: Number of ping packets to send
        :param source_loopback_port: Port to use as source for ping
        :param source_vlan: VLAN ID to use as source for ping
        :param source_ip_address: Source IP address to use for ping
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_aoss_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                use_ipv6=use_ipv6,
                packet_size=packet_size,
                count=count,
                source_loopback_port=source_loopback_port,
                source_vlan=source_vlan,
                source_ip_address=source_ip_address,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def ping_aps_test(
        central_conn,
        serial_number,
        destination,
        packet_size=None,
        count=None,
        source_interface=None,
        source_vlan=None,
        source_role=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a ping test on the specified AP device and polls for test
        result

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param packet_size: Packet size in bytes (10-2000)
        :param count: Number of ping packets to send
        :param source_interface: Port to use as source for ping
        :param source_vlan: VLAN ID to use as source for ping
        :param source_role: Role to use for ping
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_aps_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                packet_size=packet_size,
                count=count,
                source_interface=source_interface,
                source_vlan=source_vlan,
                source_role=source_role,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def ping_cx_test(
        central_conn,
        serial_number,
        destination,
        use_ipv6=None,
        packet_size=None,
        count=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a ping test on the specified CX device and polls for test
        result

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param packet_size: Packet size in bytes (10-2000)
        :param count: Number of ping packets to send
        :param use_management_interface: Boolean indicating whether to use management interface
        :param vrf_name: Name of the VRF to use for the ping test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_cx_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                use_ipv6=use_ipv6,
                packet_size=packet_size,
                count=count,
                use_management_interface=use_management_interface,
                vrf_name=vrf_name,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def ping_gateways_test(
        central_conn,
        serial_number,
        destination,
        packet_size=None,
        count=None,
        use_ipv6=None,
        ttl=None,
        dscp=None,
        dont_fragment=None,
        source_interface=None,
        source_vlan=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a ping test on the specified Gateway device and polls for test
        result

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param packet_size: Packet size in bytes (10-2000)
        :param count: Number of ping packets to send
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param ttl: Time To Live for IP datagram (1-255)
        :param dscp: DSCP packet header value between 0 and 63(0-63)
        :param dont_fragment: Boolean indicating whether to fragment or not
        :param source_interface: Port to use as source for ping
        :param source_vlan: VLAN ID to use as source for ping
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_ping_gateways_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                packet_size=packet_size,
                count=count,
                use_ipv6=use_ipv6,
                ttl=ttl,
                dscp=dscp,
                dont_fragment=dont_fragment,
                source_interface=source_interface,
                source_vlan=source_vlan,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_ping_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ping test for {device_type} {serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_ping_aoss_test(
        central_conn,
        destination,
        serial_number,
        use_ipv6=None,
        packet_size=None,
        count=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
    ):
        """
        Initiates a ping test on the specified AOS-S device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param packet_size: Size of the ping packets
        :param count: Number of ping packets to send
        :param source_loopback_port: Port to use as source for ping
        :param source_vlan: VLAN ID to use as source for ping
        :param source_ip_address: Source IP address to use for ping
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if packet_size and isinstance(packet_size, int):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError("packet_size must be an integer value.")

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )

        if source_loopback_port and isinstance(source_loopback_port, int):
            api_data["loopbackPort"] = source_loopback_port
        elif source_loopback_port:
            raise ParameterError(
                "source_loopback_port must be an integer value."
            )
        if source_ip_address and isinstance(source_ip_address, str):
            api_data["ipAddress"] = source_ip_address
        elif source_ip_address:
            raise ParameterError("source_ip_address must be a string value.")

        if source_vlan and isinstance(source_vlan, int):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError("source_vlan must be an integer value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/ping"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_ping_aps_test(
        central_conn,
        destination,
        serial_number,
        packet_size=None,
        count=None,
        source_interface=None,
        source_vlan=None,
        source_role=None,
        include_raw_output=None,
    ):
        """
        Initiates a ping test on the specified AP device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param packet_size: Size of the ping packets
        :param count: Number of ping packets to send
        :param source_interface: Port to use as source for ping
        :param source_vlan: VLAN ID to use as source for ping
        :param source_role: Role to use for ping
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if (
            packet_size
            and isinstance(packet_size, int)
            and 10 <= packet_size <= 2000
        ):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError(
                "packet_size must be an integer value 10-2000."
            )

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )

        if source_interface and isinstance(source_interface, str):
            api_data["interfacePort"] = source_interface
        elif source_interface:
            raise ParameterError("source_interface must be a string value.")

        if (
            source_vlan
            and isinstance(source_vlan, int)
            and 1 <= source_vlan <= 4094
        ):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError("source_vlan must be an integer value 1-4094.")

        if source_role and isinstance(source_role, str):
            api_data["role"] = source_role
        elif source_role:
            raise ParameterError("source_role must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/ping"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_ping_cx_test(
        central_conn,
        destination,
        serial_number,
        use_ipv6=None,
        packet_size=None,
        count=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
    ):
        """
        Initiates a ping test on the specified CX device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param packet_size: Size of the ping packets
        :param count: Number of ping packets to send
        :param use_management_interface: Boolean indicating whether to use management interface
        :param vrf_name: Name of the VRF to use for the ping test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if packet_size and isinstance(packet_size, int):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError("packet_size must be an integer value.")

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )
        if use_management_interface is not None and isinstance(
            use_management_interface, bool
        ):
            api_data["useManagementInterface"] = use_management_interface
        elif use_management_interface is not None:
            raise ParameterError(
                "use_management_interface must be a boolean value."
            )

        if vrf_name and isinstance(vrf_name, str):
            api_data["vrfName"] = vrf_name
        elif vrf_name:
            raise ParameterError("vrf_name must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/ping"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_ping_gateways_test(
        central_conn,
        destination,
        serial_number,
        packet_size=None,
        count=None,
        use_ipv6=None,
        ttl=None,
        dscp=None,
        dont_fragment=None,
        source_interface=None,
        source_vlan=None,
        include_raw_output=None,
    ):
        """
        Initiates a ping test on the specified Gateway device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the ping test
        :param packet_size: Size of the ping packets
        :param count: Number of ping packets to send
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param ttl: Time To Live for IP datagram (1-255)
        :param dscp: DSCP packet header value between 0 and 63(0-63)
        :param dont_fragment: Boolean indicating whether to fragment or not
        :param source_interface: Port to use as source for ping
        :param source_vlan: VLAN ID to use as source for ping
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if (
            packet_size
            and isinstance(packet_size, int)
            and 10 <= packet_size <= 2000
        ):
            api_data["packetSize"] = packet_size
        elif packet_size:
            raise ParameterError(
                "packet_size must be an integer value 10-2000."
            )

        if count and isinstance(count, int) and 1 <= count <= 100:
            api_data["count"] = count
        elif count:
            raise ParameterError(
                "count must be an integer value between 1-100."
            )

        if ttl and isinstance(ttl, int) and 1 <= ttl <= 255:
            api_data["ttl"] = ttl
        elif ttl:
            raise ParameterError("ttl must be an integer value between 1-255.")

        if dscp and isinstance(dscp, int) and 0 <= dscp <= 63:
            api_data["dscp"] = dscp
        elif dscp:
            raise ParameterError("dscp must be an integer value between 0-63.")

        if source_interface and isinstance(source_interface, str):
            api_data["sourceInterface"] = source_interface
        elif source_interface:
            raise ParameterError("source_interface must be a string value.")

        if (
            source_vlan
            and isinstance(source_vlan, int)
            and 1 <= source_vlan <= 4094
        ):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError("source_vlan must be an integer value 1-4094.")

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if dont_fragment and isinstance(dont_fragment, bool):
            api_data["dontFragmentFlag"] = dont_fragment
        elif dont_fragment:
            raise ParameterError("dont_fragment must be a boolean value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/ping"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ping test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Ping test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_ping_test_result(central_conn, task_id, device_type, serial_number):
        """
        Retrieves the results of a ping test on the specified device.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/ping/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get ping test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Ping test for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Ping test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def poe_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a PoE test on the specified device and polls for test results,
        supported device types include CX, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param ports: List of the ports to test
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("poe_bounce_test"),
        )
        try:
            response = Troubleshooting.initiate_poe_bounce_test(
                central_conn=central_conn,
                ports=ports,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_poe_bounce_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating PoE bounce test for {device_type} {serial_number} on {ports}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_poe_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
    ):
        """
        Initiates a PoE test on the specified device,
        supported device types include CX, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param ports: List of the ports to test
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("poe_bounce_test"),
        )

        if not ports or not isinstance(ports, list):
            raise ParameterError("Ports must be a non-empty list.")

        api_data = {"ports": ports}

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/poeBounce"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate PoE test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"PoE bounce test initiated successfully for {device_type} {serial_number} on {ports}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_poe_bounce_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """
        Retrieves the results of a PoE test on the specified device,
        supported device types include CX, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("poe_bounce_test"),
        )

        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/poeBounce/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get PoE bounce test result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"PoE bounce test for {device_type} {serial_number} with task ID {task_id} is not yet completed. Current status: {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"PoE bounce test for {device_type} {serial_number} with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def port_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a port bounce test (disable/enable) on the specified device,
        supported device types include CX, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param ports: List of the ports to test
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "port_bounce_test"
            ),
        )

        try:
            response = Troubleshooting.initiate_port_bounce_test(
                central_conn=central_conn,
                ports=ports,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_port_bounce_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating port bounce test for {device_type} {serial_number} on {ports}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_port_bounce_test(
        central_conn,
        device_type,
        serial_number,
        ports,
    ):
        """
        Initiates a port bounce test (disable/enable) on the specified device,
        supported device types include CX, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param ports: List of the ports to test
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "port_bounce_test"
            ),
        )

        if not ports or not isinstance(ports, list):
            raise ParameterError("Ports must be a non-empty list.")

        api_data = {"ports": ports}

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/portBounce"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate port test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Port bounce test initiated successfully for {device_type} "
            f"{serial_number} on {ports}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_port_bounce_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """
        Retrieves the results of a port bounce test (disable/enable) on the
        specified device, supported device types include CX, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "port_bounce_test"
            ),
        )

        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/portBounce/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get port bounce test result: {resp['code']} -"
                f" {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Port bounce test for {device_type} {serial_number} with task"
                f" ID {task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Port bounce test for {device_type} {serial_number} with task"
                f" ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def reboot_device(central_conn, device_type, serial_number):
        """
        Reboots the specified device.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting", f"{device_type}/{serial_number}/reboot"
            ),
        )
        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate reboot: {resp['code']} - {resp['msg']}"
            )
        central_conn.logger.info(
            f"Reboot initiated successfully for {device_type} {serial_number}."
        )
        return resp

    @staticmethod
    def retrieve_arp_table_test(
        central_conn,
        device_type,
        serial_number,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a ARP table retrieval test on the specified device,
        supported device types include APs, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "retrieve_arp_table_test"
            ),
        )
        try:
            response = Troubleshooting.initiate_retrieve_arp_table_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_retrieve_arp_table_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating ARP table retrieval test for {device_type}"
                f" {serial_number}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_retrieve_arp_table_test(
        central_conn,
        device_type,
        serial_number,
    ):
        """
        Initiates a ARP table retrieval test on the specified device,
        supported device types include APs, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "retrieve_arp_table_test"
            ),
        )

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/getArpTable"
        )
        resp = central_conn.command(
            api_method="POST",
            api_path=api_path,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate ARP table retrieval test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"ARP table retrieval test initiated successfully for "
            f"{device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_retrieve_arp_table_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """
        Retrieves the results of an ARP table retrieval test on the specified
        device, supported device types include APs, AOS-S and GATEWAYS.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(
                "retrieve_arp_table_test"
            ),
        )

        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/getArpTable/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get ARP table retrieval test result: {resp['code']}"
                f" - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"ARP table retrieval test for {device_type} {serial_number} "
                f"with task ID {task_id} is not yet completed. Current status:"
                f" {resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"ARP table retrieval test for {device_type} {serial_number} "
                f"with task ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def speedtest_test(
        central_conn,
        device_type,
        serial_number,
        iperf_server_address,
        protocol=None,
        server_port=None,
        bandwidth=None,
        include_reverse=None,
        seconds_to_measure=None,
        parallel=None,
        omit=None,
        window_size=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a speed test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param iperf_server_address: Iperf server address
        :param protocol: Protocol to use (tcp/udp) (optional)
        :param server_port: Server port (0-65535) (optional)
        :param bandwidth: Bandwidth in kbps (optional)
        :param include_reverse: Include reverse test, true or false (optional)
        :param seconds_to_measure: Duration to measure speed in seconds (1-20) (optional)
        :param parallel: Number of parallel streams (1-30) (optional)
        :param omit: Omit the first n seconds of the test (1-5) (optional)
        :param window_size: TCP window size in KB (65-16384) (optional)
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("speedtest_test"),
        )

        try:
            response = Troubleshooting.initiate_speedtest_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                iperf_server_address=iperf_server_address,
                protocol=protocol,
                server_port=server_port,
                bandwidth=bandwidth,
                include_reverse=include_reverse,
                seconds_to_measure=seconds_to_measure,
                parallel=parallel,
                omit=omit,
                window_size=window_size,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_speedtest_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating speedtest test for {device_type} "
                f"{serial_number} on {iperf_server_address}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_speedtest_test(
        central_conn,
        device_type,
        serial_number,
        iperf_server_address,
        protocol=None,
        server_port=None,
        bandwidth=None,
        include_reverse=None,
        seconds_to_measure=None,
        parallel=None,
        omit=None,
        window_size=None,
    ):
        """
        Initiates a speed test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param iperf_server_address: Iperf server address
        :param protocol: Protocol to use (tcp/udp) (optional)
        :param server_port: Server port (0-65535) (optional)
        :param bandwidth: Bandwidth in kbps (optional)
        :param include_reverse: Include reverse test, true or false (optional)
        :param seconds_to_measure: Duration to measure speed in seconds (1-20) (optional)
        :param parallel: Number of parallel streams (1-30) (optional)
        :param omit: Omit the first n seconds of the test (1-5) (optional)
        :param window_size: TCP window size in KB (65-16384) (optional)
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("speedtest_test"),
        )

        api_data = dict()
        if not iperf_server_address or not isinstance(
            iperf_server_address, str
        ):
            raise ParameterError(
                "Iperf server address must be a valid IP address or hostname."
            )

        api_data["iperfServerAddress"] = iperf_server_address

        if protocol and protocol not in ["tcp", "udp"]:
            raise ParameterError("Protocol must be either tcp or udp.")
        elif protocol:
            api_data["protocol"] = protocol

        if (
            server_port
            and not isinstance(server_port, int)
            or (
                isinstance(server_port, int) and not (0 <= server_port <= 65535)
            )
        ):
            raise ParameterError(
                "Server port must be a valid integer between 0 to 65535."
            )
        elif server_port:
            api_data["serverPort"] = server_port

        if bandwidth and not isinstance(bandwidth, int):
            raise ParameterError("Bandwidth must be a valid integer.")
        elif bandwidth:
            api_data["bandwidth"] = bandwidth

        if include_reverse and not isinstance(include_reverse, bool):
            raise ParameterError("Include reverse must be a boolean.")
        elif include_reverse is not None:
            api_data["includeReverse"] = include_reverse

        if (
            seconds_to_measure
            and not isinstance(seconds_to_measure, int)
            or (
                isinstance(seconds_to_measure, int)
                and not 0 < seconds_to_measure <= 20
            )
        ):
            raise ParameterError(
                "Seconds to measure must be a valid integer between 0 to 20."
            )
        elif seconds_to_measure:
            api_data["secondsToMeasure"] = seconds_to_measure

        if (
            parallel
            and not isinstance(parallel, int)
            or (isinstance(parallel, int) and not 0 < parallel <= 30)
        ):
            raise ParameterError(
                "Parallel must be a valid integer between 0 to 30."
            )
        elif parallel:
            api_data["parallel"] = parallel

        if (
            omit
            and not isinstance(omit, int)
            or (isinstance(omit, int) and not 1 <= omit <= 5)
        ):
            raise ParameterError("Omit must be a valid integer between 1 to 5.")
        elif omit:
            api_data["omit"] = omit

        if (
            window_size
            and not isinstance(window_size, int)
            or (isinstance(window_size, int) and not (64 < window_size <= 1638))
        ):
            raise ParameterError(
                "Window size must be a valid integer between 64 to 1638."
            )
        elif window_size:
            api_data["windowSize"] = window_size

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/speedtest"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate speedtest: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Speedtest initiated successfully for {device_type} {serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_speedtest_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """
        Retrieves the results of a speed test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/speedtest/async-operations/{task_id}",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get speedtest result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Speedtest for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Speedtest for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def tcp_test(
        central_conn,
        device_type,
        serial_number,
        host,
        port,
        timeout=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a TCP test on the specified device and polls for test result,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param host: Hostname/IP Address
        :param port: TCP Port (1-65535)
        :param timeout: Timeout for the test in seconds (1-10) (optional)
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("tcp_test"),
        )

        try:
            response = Troubleshooting.initiate_tcp_test(
                central_conn=central_conn,
                device_type=device_type,
                serial_number=serial_number,
                host=host,
                port=port,
                timeout=timeout,
            )

            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_tcp_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating tcp test for {device_type} {serial_number}"
                f" on {host}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_tcp_test(
        central_conn,
        device_type,
        serial_number,
        host,
        port,
        timeout=None,
    ):
        """
        Initiates a TCP test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :param host: Hostname/IP Address
        :param port: TCP Port (1-65535)
        :param timeout: Timeout for the test in seconds (1-10) (optional)
        :return: Response from the API containing task ID and other details
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
            subset=TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get("tcp_test"),
        )

        api_data = dict()
        if not host or not isinstance(host, str):
            raise ParameterError("Host must be a valid IP address or hostname.")

        api_data["host"] = host

        if port and not isinstance(port, int):
            raise ParameterError("Port must be a valid integer.")
        elif port:
            api_data["port"] = port

        if timeout and not isinstance(timeout, int):
            raise ParameterError("Timeout must be a valid integer.")
        elif timeout:
            api_data["timeout"] = timeout

        api_path = generate_url_with_params(
            "troubleshooting", f"{device_type}/{serial_number}/tcp"
        )
        resp = central_conn.command(
            api_method="POST", api_path=api_path, api_data=api_data
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate tcp test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"TCP test initiated successfully for {device_type} "
            f"{serial_number}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_tcp_test_result(
        central_conn,
        task_id,
        device_type,
        serial_number,
    ):
        """
        Retrieves the results of a TCP test on the specified device,
        supported device type includes APs.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/tcp/async-operations/{task_id}",
            ),
        )

        if resp["code"] != 200:
            raise Exception(
                f"Failed to get TCP result: {resp['code']} - {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"TCP for {device_type} {serial_number} with task ID "
                f"{task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"TCP for {device_type} {serial_number} with task ID "
                f"{task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def traceroute_aoss_test(
        central_conn,
        serial_number,
        destination,
        source_interface=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a traceroute test on the specified AOS-S device and polls for test
        result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param source_interface: Source for traceroute test, options are loopback , vlan-interface , or ip-address
        :param source_loopback_port: Port to use as source for ping, source_interface must be set to loopback
        :param source_vlan: VLAN ID to use as source for ping, source_interface must be set to vlan-interface
        :param source_ip_address: Source IP address to use for ping, source_interface must be set to ip-address
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the API containing task ID and other details
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_aoss_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                source_interface=source_interface,
                source_loopback_port=source_loopback_port,
                source_vlan=source_vlan,
                source_ip_address=source_ip_address,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def traceroute_aps_test(
        central_conn,
        serial_number,
        destination,
        source_interface=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a traceroute test on the specified AP device and polls for test
        result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param source_interface: Port to use as source for traceroute test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the API containing task ID and other details
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_aps_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                source_interface=source_interface,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def traceroute_cx_test(
        central_conn,
        serial_number,
        destination,
        use_ipv6=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a traceroute test on the specified CX device and polls for
        test result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param use_management_interface: Boolean indicating whether to use management interface
        :param vrf_name: Name of the VRF to use for the traceroute test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the API containing task ID and other details
        """
        device_type = "cx"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_cx_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                use_ipv6=use_ipv6,
                use_management_interface=use_management_interface,
                vrf_name=vrf_name,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def traceroute_gateways_test(
        central_conn,
        serial_number,
        destination,
        source_vlan_ip=None,
        include_raw_output=None,
        max_attempts=5,
        poll_interval=5,
    ):
        """
        Initiates a traceroute test on the specified Gateway device and polls
        for test result.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param source_vlan_ip: VLAN IP address to use as source for traceroute test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :return: Response from the API containing task ID and other details
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        try:
            response = Troubleshooting.initiate_traceroute_gateways_test(
                central_conn=central_conn,
                destination=destination,
                serial_number=serial_number,
                source_vlan_ip=source_vlan_ip,
                include_raw_output=include_raw_output,
            )
            task_id = Troubleshooting._get_task_id(response)

            return Troubleshooting._poll_task_completion(
                Troubleshooting.get_traceroute_test_result,
                task_id,
                central_conn,
                max_attempts=max_attempts,
                poll_interval=poll_interval,
                device_type=device_type,
                serial_number=serial_number,
            )
        except Exception as e:
            central_conn.logger.error(
                f"Error initiating traceroute test for {device_type} "
                f"{serial_number} to {destination}: {str(e)}"
            )
            raise

    @staticmethod
    def initiate_traceroute_aoss_test(
        central_conn,
        destination,
        serial_number,
        source_interface=None,
        source_loopback_port=None,
        source_vlan=None,
        source_ip_address=None,
        include_raw_output=None,
    ):
        """
        Initiates a traceroute test on the specified AOS-S device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param source_interface: Source for traceroute test, options are loopback , vlan-interface , or ip-address
        :param source_loopback_port: Port to use as source for ping, source_interface must be set to loopback
        :param source_vlan: VLAN ID to use as source for ping, source_interface must be set to vlan-interface
        :param source_ip_address: Source IP address to use for ping, source_interface must be set to ip-address
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "aos-s"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if (
            source_interface
            and isinstance(source_interface, str)
            and source_interface in ["loopback", "vlan-interface", "ip-address"]
        ):
            api_data["sourceInterface"] = source_interface
        elif source_interface:
            raise ParameterError(
                "source_interface must be a string value of "
                "loopback, vlan-interface, or ip-address."
            )

        if source_loopback_port and isinstance(source_loopback_port, int):
            api_data["loopbackPort"] = source_loopback_port
        elif source_loopback_port:
            raise ParameterError(
                "source_loopback_port must be an integer value."
            )

        if source_vlan and isinstance(source_vlan, int):
            api_data["vlan"] = source_vlan
        elif source_vlan:
            raise ParameterError("source_vlan must be an integer value.")

        if source_ip_address and isinstance(source_ip_address, str):
            api_data["ipAddress"] = source_ip_address
        elif source_ip_address:
            raise ParameterError("source_ip_address must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting", f"{device_type}/{serial_number}/traceroute"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_traceroute_aps_test(
        central_conn,
        destination,
        serial_number,
        source_interface=None,
        include_raw_output=None,
    ):
        """
        Initiates a traceroute test on the specified AP device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param source_interface: Source interface to use for the traceroute test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "aps"

        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if source_interface and isinstance(source_interface, str):
            api_data["sourceInterface"] = source_interface
        elif source_interface:
            raise ParameterError("source_interface must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting", f"{device_type}/{serial_number}/traceroute"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} "
            f"{serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_traceroute_cx_test(
        central_conn,
        destination,
        serial_number,
        use_ipv6=None,
        use_management_interface=None,
        vrf_name=None,
        include_raw_output=None,
    ):
        """
        Initiates a traceroute test on the specified CX device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param use_ipv6: Boolean indicating whether to use IPv6
        :param use_management_interface: Boolean indicating whether to use management interface
        :param vrf_name: Name of the VRF to use for the traceroute test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "cx"
        Troubleshooting._validate_required_device_params(
            central_conn, device_type, serial_number
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if use_ipv6 is not None and isinstance(use_ipv6, bool):
            api_data["useIpv6"] = use_ipv6
        elif use_ipv6 is not None:
            raise ParameterError("use_ipv6 must be a boolean value.")

        if use_management_interface is not None and isinstance(
            use_management_interface, bool
        ):
            api_data["useManagementInterface"] = use_management_interface
        elif use_management_interface is not None:
            raise ParameterError(
                "use_management_interface must be a boolean value."
            )

        if vrf_name and isinstance(vrf_name, str):
            api_data["vrfName"] = vrf_name
        elif vrf_name:
            raise ParameterError("vrf_name must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting", f"{device_type}/{serial_number}/traceroute"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} "
            f"{serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def initiate_traceroute_gateways_test(
        central_conn,
        destination,
        serial_number,
        source_vlan_ip=None,
        include_raw_output=None,
    ):
        """
        Initiates a traceroute test on the specified Gateway device.

        :param central_conn: Central connection object
        :param serial_number: Serial number of the device
        :param destination: Destination IP or hostname for the traceroute test
        :param source_vlan_ip: VLAN IP address to use as source for traceroute test
        :param include_raw_output: Boolean indicating whether to include raw output in the response
        :return: Response from the API containing task ID and other details
        """
        device_type = "gateways"

        Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
        )

        if destination and isinstance(destination, str):
            api_data = {"destination": destination}
        else:
            raise ParameterError(
                "Destination must be a valid IP address or hostname."
            )

        if source_vlan_ip and isinstance(source_vlan_ip, str):
            api_data["vlanIp"] = source_vlan_ip
        elif source_vlan_ip:
            raise ParameterError("source_vlan_ip must be a string value.")

        if include_raw_output and isinstance(include_raw_output, bool):
            api_data["includeRawOutput"] = include_raw_output
        elif include_raw_output:
            raise ParameterError("include_raw_output must be a boolean value.")

        resp = central_conn.command(
            api_method="POST",
            api_path=generate_url_with_params(
                "troubleshooting", f"{device_type}/{serial_number}/traceroute"
            ),
            api_data=api_data,
        )

        if resp["code"] != 202:
            raise Exception(
                f"Failed to initiate traceroute test: {resp['code']} - {resp['msg']}"
            )

        response = resp["msg"]
        task_id = Troubleshooting._get_task_id(response)
        central_conn.logger.info(
            f"Traceroute test initiated successfully for {device_type} {serial_number} to {destination}. Task ID: {task_id}"
        )
        return response

    @staticmethod
    def get_traceroute_test_result(
        central_conn, task_id, device_type, serial_number
    ):
        """
        Retrieves the result of a traceroute test on the specified device.

        :param central_conn: Central connection object
        :param task_id: Task ID to poll for
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: Response from the test results API
        """
        device_type = Troubleshooting._validate_required_device_params(
            central_conn,
            device_type,
            serial_number,
        )
        resp = central_conn.command(
            api_method="GET",
            api_path=generate_url_with_params(
                "troubleshooting",
                f"{device_type}/{serial_number}/traceroute/async-operations/{task_id}",
            ),
        )
        if resp["code"] != 200:
            raise Exception(
                f"Failed to get traceroute test result: {resp['code']} -"
                f" {resp['msg']}"
            )

        if resp["msg"].get("status") in ["RUNNING", "INITIATED"]:
            central_conn.logger.info(
                f"Traceroute test for {device_type} {serial_number} with "
                f"task ID {task_id} is not yet completed. Current status: "
                f"{resp['msg'].get('status')}"
            )
        else:
            central_conn.logger.info(
                f"Traceroute test for {device_type} {serial_number} with task "
                f"ID {task_id} has successfully completed."
            )
        return resp["msg"]

    @staticmethod
    def _poll_task_completion(
        get_result_func,
        task_id,
        conn,
        max_attempts=5,
        poll_interval=5,
        *args,
        **kwargs,
    ):
        """
        Generic polling method for task completion with configurable timeout.

        :param get_result_func: Function to call for getting task result
        :param task_id: Task ID to poll for
        :param conn: Central connection object
        :param max_attempts: Maximum number of polling attempts
        :param poll_interval: Time to wait between polls in seconds
        :param args: Additional positional arguments for get_result_func
        :param kwargs: Additional keyword arguments for get_result_func
        :return: Final result from get_result_func
        """
        for attempt in range(max_attempts):
            result = get_result_func(conn, task_id, *args, **kwargs)
            if result["status"] in ["COMPLETED", "FAILED"]:
                return result
            time.sleep(poll_interval)

        conn.logger.warning(
            f"Task {task_id} did not complete after {max_attempts} attempts. "
            f"Current status: {result['status']}"
        )
        return result

    @staticmethod
    def _get_task_id(api_response):
        """
        Extracts the task ID from the API response.

        :param api_response: The API response containing the task information
        :return: The extracted task ID
        """
        return api_response.get("location", "").split("/")[-1]

    @staticmethod
    def _validate_required_device_params(
        central_conn, device_type, serial_number, subset=None
    ):
        """
        Validates required parameters are set
        :param central_conn: Central connection object
        :param device_type: Type of the device
        :param serial_number: Serial number of the device
        :return: verified device_type in lower case format
        :raises ParameterError: If any required parameter is missing
        """
        if not central_conn or not device_type or not serial_number:
            raise ParameterError(
                "central_conn(Central connection), device_type(aps, cx, aos-s,"
                " gateways) and serial_number are required"
            )
        if (subset and device_type.lower() not in subset) or (
            device_type.lower() not in SUPPORTED_DEVICE_TYPES
        ):
            supported_devices = ", ".join(
                subset if subset else SUPPORTED_DEVICE_TYPES
            )
            raise ParameterError(
                f"Unsupported device type: {device_type}, supported types are "
                f"{supported_devices}"
            )
        return device_type.lower()
