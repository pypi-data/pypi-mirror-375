import os
import pytest

import conftest
from botcity.plugins.ms365.outlook import MS365OutlookPlugin


def test_send_message(bot: MS365OutlookPlugin, tmp_file: str, subject: str):
    to = [os.getenv("MS365_OUTLOOK_EMAIL")]
    cc = [os.getenv("MS365_OUTLOOK_EMAIL")]
    subject_1 = f"[1]-{subject}"
    subject_2 = f"[2]-{subject}"
    body = "Hello! This is a test message!"
    files = [tmp_file]
    bot.send_message(subject_1, body, to, cc, attachments=files)
    bot.send_message(subject_2, body, to, cc, attachments=files)


@pytest.mark.depends(name="test_send_message")
def test_search_message(bot: MS365OutlookPlugin, subject: str):
    query_filter1 = bot.new_query_filter().equals("subject", f"{subject}-1")
    query_filter2 = bot.new_query_filter().equals("subject", f"[1]-{subject}")

    messages = bot.search_messages(criteria=query_filter1)
    assert len(messages) == 0

    messages = bot.search_messages(criteria=query_filter2, timeout=10)
    assert len(messages) == 1


@pytest.mark.depends(name="test_search_message")
def test_reply(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().equals("subject", f"[1]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1)
    bot.reply(msg=messages[0], text_content="OK!", to_addrs=[os.getenv("MS365_OUTLOOK_EMAIL")])

    query_filter = bot.new_query_filter().equals("subject", f"RE: [1]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1, timeout=10)
    assert messages[0].subject == f"RE: [1]-{subject}"


@pytest.mark.depends(name="test_reply")
def test_reply_to_all(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().equals("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1)
    bot.reply_to_all(msg=messages[0], text_content="OK to all!")

    query_filter = bot.new_query_filter().equals("subject", f"RE: [2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1, timeout=10)
    assert messages[0].subject == f"RE: [2]-{subject}"


@pytest.mark.depends(name="test_reply_to_all")
def test_forward(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().equals("subject", f"[1]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1)
    bot.forward(msg=messages[0], to_addrs=[os.getenv("MS365_OUTLOOK_EMAIL")])

    query_filter = bot.new_query_filter().equals("subject", f"FW: [1]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1, timeout=10)
    assert messages[0].subject == f"FW: [1]-{subject}"


@pytest.mark.depends(name="test_forward")
def test_delete(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().contains("subject", f"[1]-{subject}")
    messages = bot.search_messages(criteria=query_filter)
    for message in messages:
        bot.delete(message)
    messages = bot.search_messages(criteria=query_filter)
    assert len(messages) == 0


def test_download_attachment(bot: MS365OutlookPlugin, subject: str, tmp_folder: str, tmp_file: str):
    os.remove(tmp_file)
    query_filter = bot.new_query_filter().equals("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, include_attachments=True, limit=1)
    bot.download_attachments(msg=messages[0], download_folder_path=tmp_folder)
    assert os.path.exists(path=f"{tmp_folder}/{messages[0].attachments[0].name}")


def test_mark_as_read(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().equals("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1)
    bot.mark_as_read(msg=messages[0])
    assert messages[0].is_read


@pytest.mark.depends(name="test_mark_as_read")
def test_mark_as_unread(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().equals("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1)
    bot.mark_as_unread(msg=messages[0])
    assert not messages[0].is_read


def test_create_new_folder(bot: MS365OutlookPlugin):
    bot.create_folder(conftest.EMAIL_FOLDER)
    folder = bot.get_folder(folder_name=conftest.EMAIL_FOLDER)
    assert folder.name == conftest.EMAIL_FOLDER


@pytest.mark.depends(name="test_create_new_folder")
def test_get_mail_folders(bot: MS365OutlookPlugin):
    folders = bot.get_folders()
    assert isinstance(folders, list)
    created_folder = bot.get_folder(folder_name=conftest.EMAIL_FOLDER)
    assert created_folder in folders


def test_move_to_folder(bot: MS365OutlookPlugin, subject: str):
    query_filter = bot.new_query_filter().contains("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter)
    for message in messages:
        bot.move(message, conftest.EMAIL_FOLDER)

    bot.set_default_folder(conftest.EMAIL_FOLDER)
    query_filter = bot.new_query_filter().equals("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, limit=1)
    assert len(messages) == 1


@pytest.mark.depends(name="test_move_to_folder")
def test_copy_to_folder(bot: MS365OutlookPlugin, subject: str):
    bot.set_default_folder(conftest.EMAIL_FOLDER)
    folder_2 = bot.create_folder(folder_name=f"[2]-{conftest.EMAIL_FOLDER}")

    query_filter = bot.new_query_filter().contains("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter)
    for message in messages:
        bot.copy(message, folder_name=f"[2]-{conftest.EMAIL_FOLDER}")

    bot.set_default_folder(folder_2)
    query_filter = bot.new_query_filter().equals("subject", f"[2]-{subject}")
    messages = bot.search_messages(criteria=query_filter, mark_read=True, limit=1)
    assert len(messages) == 1


@pytest.mark.depends(name="test_copy_to_folder")
def test_delete_folder(bot: MS365OutlookPlugin):
    folder_1 = conftest.EMAIL_FOLDER
    folder_2 = f"[2]-{conftest.EMAIL_FOLDER}"
    bot.delete_folder(folder_name=folder_1)
    bot.delete_folder(folder_name=folder_2)

    folders = [folder.name for folder in bot.get_folders()]
    assert folder_1 not in folders
    assert folder_2 not in folders
