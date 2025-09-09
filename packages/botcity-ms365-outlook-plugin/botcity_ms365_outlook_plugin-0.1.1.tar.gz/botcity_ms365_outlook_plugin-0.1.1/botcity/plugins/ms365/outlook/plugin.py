import time
from typing import List, Union

from O365.mailbox import Folder, MailBox, Message

try:
    from O365.utils import Query
except ImportError:
    from O365.utils import QueryBuilder as Query

from botcity.plugins.ms365.credentials import MS365CredentialsPlugin


class MS365OutlookPlugin:
    def __init__(self, service_account: MS365CredentialsPlugin) -> None:
        """
        MS365OutlookPlugin.

        Args:
            service_account (MS365CredentialsPlugin): The authenticated Microsoft365 account.
                The authentication process must be done through the credentials plugin.
        """
        self._mailbox = service_account.ms365_account.mailbox()
        self.mail_folder = self._mailbox.inbox_folder()

    @property
    def outlook_service(self) -> MailBox:
        """
        The Office365/Microsoft365 account service.

        You can use this property to access Outlook functionality.
        """
        return self._mailbox

    @property
    def mail_folder(self) -> Folder:
        """
        The email folder that will be used as a reference in operations.

        By default, the 'inbox' folder will be used.
        """
        return self._mail_folder

    @mail_folder.setter
    def mail_folder(self, folder: Folder):
        """
        Set the email folder that will be used as a reference in operations.

        By default, the 'inbox' folder will be used.
        """
        self._mail_folder = folder

    def new_query_filter(self) -> Query:
        """
        Return a Query object that can be used to create a search filter.

        Returns:
            Query: The Query object to build the query filter.
        """
        new_query = self.outlook_service.new_query()
        return new_query

    def get_folder(self, folder_name: str, parent_folder: Folder = None) -> Folder:
        """
        Get email folder by name.

        Args:
            folder_name (str): The name of the folder to be searched.
            parent_folder (Folder, optional): Get a child folder from this parent folder.

        Returns:
            Folder: The folder object.
        """
        parent_folder = parent_folder or self.outlook_service
        folder = parent_folder.get_folder(folder_name=folder_name)
        if not folder:
            raise ValueError(f"No folder found using this folder name: {folder_name}")
        return folder

    def get_folders(self, parent_folder: Folder = None) -> List[Folder]:
        """
        Get a list of available email folders.

        Args:
            parent_folder (Folder, optional): Get child folders from this parent folder.

        Returns:
            List[Folder]: The list containing the object of each found folder.
        """
        parent_folder = parent_folder or self.outlook_service
        mail_folders = parent_folder.get_folders()
        return mail_folders

    def create_folder(self, folder_name: str, parent_folder: Folder = None) -> Folder:
        """
        Create a new email folder.

        Args:
            folder_name (str): The name of the folder to be created.
            parent_folder (Folder, optional): Create a child folder under this parent folder.

        Returns:
            Folder: The reference of the new folder that was created.
        """
        parent_folder = parent_folder or self.outlook_service
        return parent_folder.create_child_folder(folder_name=folder_name)

    def delete_folder(self, folder_name: str, parent_folder: Folder = None) -> None:
        """
        Delete a email folder.

        Args:
            folder_name (str): The name of the folder to be deleted.
            parent_folder (Folder, optional): Delete a child folder from this parent folder.
        """
        parent_folder = parent_folder or self.outlook_service
        folder = self.get_folder(folder_name, parent_folder)
        folder.delete()

    def set_default_folder(self, folder: Union[Folder, str]) -> None:
        """
        Set a specific folder as the default folder.

        Args:
            folder (Folder | str): The name or Folder object of the folder that will be used in operations.
        """
        if isinstance(folder, Folder):
            self.mail_folder = folder
        else:
            self.mail_folder = self.get_folder(folder)

    def search_messages(self, criteria: Union[Query, str] = None, include_attachments=False,
                        mark_read=False, limit=25, timeout=0) -> List[Message]:
        """
        Search for all emails messages based on criteria.

        Args:
            criteria (Query | str, optional): The criteria that will be used as a message filter.
            include_attachments (bool, optional): Whether or not to include the attachments in the message object.
            mark_read (bool, optional): Whether the email should be marked as read. Defaults to False.
            limit (int, optional): Limits the result set.
            timeout (int, optional): Wait for a new message until this timeout.
                Defaults to 0 seconds (don't wait for new messages).

        Returns:
            List[Message]: The list of emails found.
        """
        start_time = time.time()
        while True:
            messages = list(self.mail_folder.get_messages(
                limit=limit,
                query=criteria,
                download_attachments=include_attachments
            ))
            if messages:
                break
            elapsed_time = (time.time() - start_time)
            if elapsed_time > timeout:
                return []
            time.sleep(1)

        if mark_read:
            for msg in messages:
                msg.mark_as_read()
        return messages

    def send_message(self, subject: str, text_content: str, to_addrs: List[str], cc_addrs: List[str] = [],
                     bcc_addrs: List[str] = [], attachments: List[str] = []) -> None:
        """
        Send a new email message.

        Args:
            subject (str): The subject of the email.
            text_content (str): The content of the email body.
            to_addrs (List[str]): The list of email addresses that will receive the message.
            cc_addrs (List[str], optional): The list of email addresses that will receive the message as CC.
            bcc_addrs (List[str], optional): The list of email addresses that will receive the message as BCC.
            attachments (List[str], optional): The list with the paths of the files that will be sent as attachments.
        """
        new_message = self.outlook_service.new_message()
        new_message.subject = subject
        new_message = self._build_message(new_message, text_content, to_addrs, cc_addrs, bcc_addrs, attachments)
        new_message.send()

    def reply(self, msg: Message, text_content: str, attachments: List[str] = [],
              to_addrs: List[str] = [], cc_addrs: List[str] = [], bcc_addrs: List[str] = []) -> None:
        """
        Reply a received email message.

        Args:
            msg (Message): The message to reply.
            text_content (str): The content of the email body.
            attachments (List[str], optional): The list with the paths of the files that will be sent as attachments.
            to_addrs (List[str], optional): The list of email addresses that will receive the message.
            cc_addrs (List[str], optional): The list of email addresses that will receive the message as CC.
            bcc_addrs (List[str], optional): The list of email addresses that will receive the message as BCC.
        """
        reply_message = msg.reply(to_all=False)
        reply_message = self._build_message(reply_message, text_content, to_addrs, cc_addrs, bcc_addrs, attachments)
        reply_message.send()

    def reply_to_all(self, msg: Message, text_content: str, attachments: List[str] = []) -> None:
        """
        Reply to all email addresses included in the original message.

        Args:
            msg (Message): The message to reply.
            text_content (str): The content of the email body.
            attachments (List[str], optional): The list with the paths of the files that will be sent as attachments.
        """
        reply_message = msg.reply(to_all=True)
        reply_message = self._build_message(msg=reply_message, text_content=text_content, attachments=attachments)
        reply_message.send()

    def forward(self, msg: Message, to_addrs: List[str], cc_addrs: List[str] = [],
                bcc_addrs: List[str] = [], text_content: str = "") -> None:
        """
        Forward a received email message.

        Args:
            msg (Message): The message to forward.
            to_addrs (List[str]): The list of email addresses that will receive the message.
            cc_addrs (List[str], optional): The list of email addresses that will receive the message as CC.
            bcc_addrs (List[str], optional): The list of email addresses that will receive the message as BCC.
            text_content (str, optional): The additional content of the email body.
        """
        fwd_message = msg.forward()
        fwd_message = self._build_message(fwd_message, text_content, to_addrs, cc_addrs, bcc_addrs)
        fwd_message.send()

    def download_attachments(self, msg: Message, download_folder_path: str = "") -> None:
        """
        Download attachments from a given email message.

        Args:
            msg (Message): The message that contains the attachments.
            download_folder_path (str, optional): The path of the folder where the files will be saved.
        """
        for file in msg.attachments:
            file.save(download_folder_path)

    def mark_as_read(self, msg: Message) -> None:
        """
        Mark a received email message as read.

        Args:
            msg (Message): The message to be marked.
        """
        msg.mark_as_read()

    def mark_as_unread(self, msg: Message) -> None:
        """
        Mark a received email message as unread.

        Args:
            msg (Message): The message to be marked.
        """
        msg.mark_as_unread()

    def delete(self, msg: Message) -> None:
        """
        Delete a email message.

        Args:
            msg (Message): The message to be deleted.
        """
        msg.delete()

    def move(self, msg: Message, folder_name: str) -> None:
        """
        Move a email message to a destination folder.

        Args:
            msg (Message): The message to be moved.
            folder_name (str): The name of the destination folder.
        """
        folder = self.get_folder(folder_name)
        msg.move(folder)

    def copy(self, msg: Message, folder_name: str) -> None:
        """
        Copy a email message to a destination folder.

        Args:
            msg (Message): The message to be copied.
            folder_name (str): The name of the destination folder.
        """
        folder = self.get_folder(folder_name)
        msg.copy(folder)

    def _build_message(
            self,
            msg: Message,
            text_content: str = "",
            to_addrs: List[str] = [],
            cc_addrs: List[str] = [],
            bcc_addrs: List[str] = [],
            attachments: List[str] = []) -> Message:

        if text_content:
            msg.body = text_content

        for addrs in to_addrs:
            msg.to.add(addrs)
        for addrs in cc_addrs:
            msg.cc.add(addrs)
        for addrs in bcc_addrs:
            msg.bcc.add(addrs)
        for attachment in attachments:
            msg.attachments.add(attachment)

        if not msg.to and not msg.cc and not msg.bcc:
            msg.to.add(msg.sender)

        return msg
