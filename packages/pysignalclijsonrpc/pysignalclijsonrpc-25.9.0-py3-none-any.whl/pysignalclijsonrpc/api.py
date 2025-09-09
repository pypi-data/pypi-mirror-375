"""
pysignalclijsonrpc.api
"""

from base64 import b64encode
from io import BytesIO
from os import remove as os_remove
from re import search as re_search
from re import sub as re_sub
from typing import Optional
from uuid import uuid4
from warnings import warn

from jmespath import search as j_search
from magic import from_buffer, from_file
from packaging.version import parse as version_parse
from requests import Session


def bytearray_to_rfc_2397_data_url(byte_array: bytearray):
    """
    Convert bytearray to RFC 2397 data url.

    Args:
        byte_array (bytearray)

    Returns:
        result (:obj:`str`): RFC 2397 data url
    """
    attachment_io_bytes = BytesIO()
    attachment_io_bytes.write(bytes(byte_array))
    mime = from_buffer(attachment_io_bytes.getvalue(), mime=True)
    return f"data:{mime};base64,{b64encode(bytes(byte_array)).decode()}"


def get_attachments(attachments_as_files, attachments_as_bytes):
    """
    Get attachments from either files and/or bytes.

    Args:
        attachments_as_files: (:obj:`list`, optional):
            List of `str` w/ files to send as attachment(s).
        attachments_as_bytes (:obj:`list`, optional):
            List of `bytearray` to send as attachment(s).

    Returns:
        attachments (:obj:`list`): List of attachments to send.
    """
    attachments = []
    if attachments_as_files is not None:
        for filename in attachments_as_files:
            mime = from_file(filename, mime=True)
            with open(filename, "rb") as f_h:
                base64 = b64encode(f_h.read()).decode()
            attachments.append(f"data:{mime};base64,{base64}")
    if attachments_as_bytes is not None:
        for attachment in attachments_as_bytes:
            attachments.append(bytearray_to_rfc_2397_data_url(attachment))
    return attachments


def get_recipients(client: object, recipients: list):
    """
    Get recipients. Could be either a valid recipient
    registered with the network or a group.

    Args:
        client (object): SignalCliJSONRPCApi
        recipients (:obj:`list`): List of recipients

    Returns:
        result (tuple): Tuple of `(unknown, contacts, groups)`
    """
    unknown = []
    contacts = []
    groups = []
    registered = []
    check_registered = []
    for recipient in recipients:
        if j_search(f"[?id==`{recipient}`]", client.list_groups()):  # pragma: no cover
            groups.append(recipient)
            continue
        if re_search("[a-zA-Z/=]", recipient):  # pragma: no cover
            unknown.append(recipient)
            continue
        check_registered.append(recipient)
    if check_registered:
        registered = client.get_user_status(recipients=check_registered)
    for recipient in check_registered:
        if j_search(f"[?number==`{recipient}`]", registered):
            contacts.append(recipient)
            continue
        unknown.append(recipient)  # pragma: no cover
    return (unknown, contacts, groups)


class SignalCliJSONRPCError(Exception):
    """
    SignalCliJSONRPCError
    """


class SignalCliJSONRPCApi:
    """
    SignalCliJSONRPCApi
    """

    def __init__(
        self,
        endpoint: str,
        account: Optional[str] = "",
        auth: Optional[tuple] = (),
        verify_ssl: Optional[bool] = True,
    ) -> None:
        """
        SignalCliJSONRPCApi

        Args:
            endpoint (:obj:`str`): signal-cli JSON-RPC endpoint.
            account (:obj:`str`, optional): signal-cli account to use.
            auth (:obj:`tuple`, optional): basic authentication credentials
                (e.g. `("user", "pass")`)
            verify_ssl (:obj:`bool`, optional): SSL verfification for https endpoints.
                Defaults to True.
        """
        self._session = Session()
        self._endpoint = endpoint
        self._account = account
        self._auth = auth
        self._verify_ssl = verify_ssl

    def _jsonrpc(self, method: str, params: object = None, **kwargs) -> dict:
        """
        Args:
            method (:obj:`str`): JSON-RPC method. Equals signal-cli command.
            params (:obj:`dict`): Method parameters.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            result (:obj:`dict`): The JSON-RPC result.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        request_id = kwargs.get("request_id") or str(uuid4())
        if not params:
            params = {}
        if self._account:
            params.update({"account": self._account})
        data = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        try:
            res = self._session.post(
                url=f"{self._endpoint}",
                json=data,
                auth=self._auth,
                verify=self._verify_ssl,
            )
            res.raise_for_status()
            ret = res.json()
            if ret.get("id") == request_id:
                if ret.get("error"):
                    error = ret.get("error").get("message")
                    raise SignalCliJSONRPCError(error)
            return ret.get("result")
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    @property
    def version(self) -> str:
        """
        Fetch version.

        Returns:
            version (:obj:`str`): Version of signal-cli

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        return self._jsonrpc(method="version").get("version")

    def send_message(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        recipients: list,
        message: str = "",
        mention: str = "",
        attachments_as_files: list = None,
        attachments_as_bytes: list = None,
        cleanup_attachments: bool = False,
        **kwargs,
    ) -> None:
        """
        Send message.

        Args:
            recipients (:obj:`list`):
                List of recipients.
            message (:obj:`str`, optional):
                Message to be sent.
            mention (:obj:`str`, optional):
                Mention string (`start:end:recipientNumber`).
            attachments_as_files: (:obj:`list`, optional):
                List of `str` w/ files to send as attachment(s).
            attachments_as_bytes (:obj:`list`, optional):
                List of `bytearray` to send as attachment(s).
            cleanup_attachments (:obj:`bool`, optional):
                Wether to remove files in `attachments_as_files`
                after message(s) has been sent. Defaults to False.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Returns:
            result (:obj:`dict`): Dictionary of timestamps and related recipients.
                Example: `{'timestamps': {timestamp: {'recipients': ['...']}}}`

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        response_method_mapping = {
            "recipient": "recipientAddress.number",
        }
        timestamps = {}
        unknown = []  # pylint: disable=unused-variable
        contacts = []
        groups = []
        attachments = []
        try:
            attachments = get_attachments(
                attachments_as_files,
                attachments_as_bytes,
            )
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"Error while parsing attachments: {error}"
            ) from err
        try:
            unknown, contacts, groups = get_recipients(self, recipients)
        except Exception as err:  # pylint: disable=broad-except  # pragma: no cover
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(f"Error preparing recipients: {error}") from err

        try:
            if not message and not attachments:
                raise SignalCliJSONRPCError("Message or attachment is required")
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"Error validating message content: {error}"
            ) from err

        try:
            params = {
                "account": self._account,
                "message": message,
                "attachment": attachments,
            }
            if mention:  # pragma: no cover
                # covered in tests/test_quit_group.py
                params.update({"mention": mention})
            for key, value in {"recipient": contacts, "groupId": groups}.items():
                if value:
                    t_params = params.copy()
                    t_params.update({key: value})
                    t_res = self._jsonrpc(
                        method="send",
                        params=t_params,
                        **kwargs,
                    )
                    t_timestamp = t_res.get("timestamp")
                    if t_timestamp:
                        search_for = f"[*].{response_method_mapping.get(key, key)}"
                        timestamps.update(
                            {
                                t_timestamp: {
                                    "recipients": list(
                                        set(
                                            j_search(
                                                search_for,
                                                t_res.get("results"),
                                            )
                                        )
                                    )
                                }
                            }
                        )
            return {"timestamps": timestamps}
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err
        finally:
            if cleanup_attachments:
                for filename in attachments_as_files:
                    os_remove(filename)

    def update_group(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        name: str,
        members: list,
        add_member_permissions: str = "only-admins",
        edit_group_permissions: str = "only-admins",
        group_link: str = "disabled",
        admins: list = None,
        description: str = "",
        message_expiration_timer: int = 0,
        avatar_as_bytes: bytearray = bytearray(),
        **kwargs,
    ) -> str:
        """
        Update (create) a group.

        Args:
            name (:obj:`str`): Group name.
            members (:obj:`list`): Group members. List of strings.
            add_member_permissions (:obj:`str`, optional): Group permissions for adding members.
                `every-member` or `only-admins` (default).
            edit_group_permissions (:obj:`str`, optional):
                Group permissions for editing settings/details.
                `every-member` or `only-admins` (default).
            group_link (GroupLinkChoices, optional): Group Link settings.
                One of `disabled` (default), `enabled` or `enabled-with-approval`.
            admins (:obj:`list`, optional): List of additional group admins.
            description (:obj:`str`, optional): Group description.
            message_expiration_timer (int, optional): Message expiration timer in seconds.
                Defaults to 0 (disabled).
            avatar_as_bytes (bytearray, optional): `bytearray` containing image to set as avatar.
                Supported since signal-cli 0.11.6.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Returns:
            group_id (:obj:`str`): The group id.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {
                "name": name,
                "member": members,
                "setPermissionAddMember": add_member_permissions,
                "setPermissionEditDetails": edit_group_permissions,
                "link": group_link,
                "admin": admins,
                "description": description,
                "expiration": message_expiration_timer,
            }
            if avatar_as_bytes:  # pragma: no cover
                if version_parse(self.version) < version_parse("0.11.6"):
                    warn("'avatar_as_bytes' not supported (>= 0.11.6), skipping.")
                else:
                    params.update(
                        {"avatarFile": bytearray_to_rfc_2397_data_url(avatar_as_bytes)}
                    )
            ret = self._jsonrpc(method="updateGroup", params=params, **kwargs)
            return ret.get("groupId")
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def quit_group(
        self,
        groupid: str,
        delete: bool = False,
        **kwargs,
    ) -> dict:
        """
        Quit (leave) group.

        Args:
            groupid (:obj:`str`): Group id to quit (leave).
            delete (:obj:`bool`, optional): Also delete group.
                Defaults to `False`.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Returns:
            result (:obj:`dict`)

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {
                "groupId": groupid,
                "delete": delete,
            }
            return self._jsonrpc(method="quitGroup", params=params, **kwargs)
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def list_groups(
        self,
        **kwargs,
    ) -> list:
        """
         List groups.

        Args:
             **kwargs: Arbitrary keyword arguments passed to
                 :meth:`._jsonrpc`.

         Returns:
             result (:obj:`list`)

         Raises:
             :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            res = self._jsonrpc(
                method="listGroups",
                **kwargs,
            )
            return res or []
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def get_group(self, groupid: str) -> dict:
        """
        Get group details.

        Args:
            groupid (:obj:`str`): Group id to fetch information for.

        Returns:
            result (:obj:`dict`)

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            groups = self.list_groups()
            return j_search(f"[?id==`{groupid}`]", groups) or [{}]
        except Exception as err:  # pylint: disable=broad-except  # pragma: no cover
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def join_group(
        self,
        uri: str,
        **kwargs,
    ):
        """
        Join group.

        Args:
            uri (:obj:`str`): Group invite link like https://signal.group/#...
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {
                "uri": uri,
            }
            return self._jsonrpc(method="joinGroup", params=params, **kwargs)
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def update_profile(
        self,
        given_name: str = "",
        family_name: str = "",
        about: str = "",
        avatar_as_bytes: bytearray = bytearray(),
        **kwargs,
    ) -> bool:
        """
        Update profile.

        Args:
            given_name (:obj:`str`, optional): Given name.
            family_name (:obj:`str`, optional): Family name.
            about (:obj:`str`, optional): About information.
            avatar_as_bytes (bytearray, optional): `bytearray` containing image to set as avatar.
                Supported since signal-cli 0.11.6.

        Returns:
            result (:obj:`bool`): True for success.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {}
            if given_name:
                params.update({"givenName": family_name})
            if family_name:
                params.update({"familyName": family_name})
            if about:
                params.update({"about": about})
            if avatar_as_bytes:  # pragma: no cover
                if version_parse(self.version) < version_parse("0.11.6"):
                    warn("'avatar_as_bytes' not supported (>= 0.11.6), skipping.")
                else:
                    params.update(
                        {"avatar": bytearray_to_rfc_2397_data_url(avatar_as_bytes)}
                    )
            if params:
                self._jsonrpc(method="updateProfile", params=params, **kwargs)
            return True
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def send_reaction(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        recipient: str,
        emoji: str,
        target_author: str,
        target_timestamp: int,
        remove: bool = False,
        groupid: str = "",
        **kwargs,
    ) -> int:
        """
        Send reaction.

        Args:
            recipient (:obj:`str`): Specify the recipients' phone number.
            emoji (:obj:`str`): Specify the emoji, should be a single unicode grapheme cluster.
            target_author (:obj:`str`):
                Specify the number of the author of the message to which to react.
            target_timestamp (int): Specify the timestamp of the message to which to react.
            remove (:obj:`bool`, optional): Remove an existing reaction.
                Defaults to `False`.
            groupid (:obj:`str`, optional): Specify the recipient group ID.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Returns:
            timestamp (int): Timestamp of reaction.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {
                "emoji": emoji,
                "remove": remove,
                "targetAuthor": target_author,
                "targetTimestamp": target_timestamp,
                "recipient": recipient,
            }
            if groupid:  # pragma: no cover
                params.update({"groupId": groupid})
            ret = self._jsonrpc(method="sendReaction", params=params, **kwargs)
            return ret.get("timestamp")
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def get_user_status(self, recipients: list, **kwargs) -> dict:
        """
        Get user network status (is registered?).

        Args:
            recipients (:obj:`list`): List of `str` where each item is a phone number.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Returns:
            result (:obj:`dict`): The network result.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            recipients[:] = [re_sub("^([1-9])[0-9]+$", r"+\1", s) for s in recipients]
            return self._jsonrpc(
                method="getUserStatus",
                params={
                    "recipient": recipients,
                },
                **kwargs,
            )
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def register(self, captcha: str = "", voice: bool = False, **kwargs) -> dict:
        """
        Register account.

        Args:
            captcha (:obj:`str`, optional): The captcha token, required if registration
                failed with a captcha required error.
            voice (:obj:`bool`): The verification should be done over voice, not SMS.
                Defaults to `False`.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`._jsonrpc`.

        Returns:
            result (:obj:`dict`): The network result. `{}` if successful.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {}
            if captcha:  # pragma: no cover
                params.update({"captcha": captcha})
            if voice:  # pragma: no cover
                params.update({"voice": voice})
            return self._jsonrpc(method="register", params=params, **kwargs)
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err

    def verify(self, verification_code: str, pin: str = "", **kwargs) -> dict:
        """
        Verify pending account registration.

        Args:
            verification_code (:obj:`str`):
                The verification code you received via sms or voice call.
            pin (:obj:`str`, optional): The registration lock PIN, that was set by the user.
            **kwargs: Arbitrary keyword arguments passed to
                :meth:`pysignalclijsonrpc.SignalCliJSONRPCApi._jsonrpc`.

        Returns:
            result (:obj:`dict`): The network result. `{}` if successful.

        Raises:
            :exc:`pysignalclijsonrpc.api.SignalCliJSONRPCError`
        """
        try:
            params = {
                "verificationCode": verification_code,
            }
            if pin:  # pragma: no cover
                params.update({"pin": pin})
            return self._jsonrpc(method="verify", params=params, **kwargs)
        except Exception as err:  # pylint: disable=broad-except
            error = getattr(err, "message", repr(err))
            raise SignalCliJSONRPCError(
                f"signal-cli JSON RPC request failed: {error}"
            ) from err
