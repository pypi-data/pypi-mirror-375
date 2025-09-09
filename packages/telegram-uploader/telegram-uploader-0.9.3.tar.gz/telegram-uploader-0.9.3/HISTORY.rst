0.9.0 (2025-09-01)
------------------

* Add full documentation for all commands and options in docs/COMMANDS.md
* Add new options: --output-dir, --overwrite for download
* Add new commands: edit-message, upload-folder, get-message-info
* Improve forward-and-download and forward-messages commands
0.8.0 (2025-09-01)
------------------

* Feature: Add --json-output and --json-minimal options for clean JSON output after upload (no extra text).
* Fix: Suppress print_file_id and other messages when JSON output is enabled for better integration.
=======
History
=======

0.7.1 (2023-08-04)
------------------

* Issue #215: "TypeError: __init__() got an unexpected keyword argument 'reply_to_msg_id'" in command - "telegram-upload --directories "recursive" --album"

0.7.0 (2023-06-29)
------------------

* Issue #140: Speed up upload & download speed
* Issue #115: Add support for variables in the caption argument
* Issue #159: Telegram premium
* Issue #176: Bug uploading .flv files
* Issue #198: Improve README

0.6.1 (2023-06-17)
------------------

* Issue #197: if to.lstrip("-+").isdigit(): AttributeError: 'int' object has no attribute 'lstrip'

0.6.0 (2023-06-15)
------------------

* Issue #99: Combine split files when downloading
* Issue #118: Feature Request - Choose channel by ID
* Issue #113: Numbered files are uploaded in weird order
* Issue #111: telethon.errors.rpcerrorlist.FloodWaitError: A wait of 819 seconds is required (caused by CheckChatInviteRequest)
* Issue #108: RPCError 400: INPUT_GZIP_INVALID
* Issue #193: Remove Python 3.6 support
* Issue #194: Python 3.11 support.

0.5.1 (2022-05-18)
------------------

* Issue #154: Python classifiers for Python 3.1.0
* Issue #151: Error while uploading files
* Issue #121: Thumbnail gets auto deleted

0.5.0 (2022-02-27)
------------------

* Issue #34: Selective downloading option
* Issue #131: Selective uploading option
* Issue #61: Upload as album
* Issue #66: How to re-verify when I type in wrong app-id
* Issue #69: Create Dockerfile
* Issue #82: Error in files with corrupted or unsupported video mimetype
* Issue #83: Raise error when file is empty
* Issue #84: Catch ChatWriteForbiddenError
* Issue #94: Unclosed file ~/.config/telegram-upload.json wb
* Issue #110: Error uploading corrupt or unsupported video file
* Issue #129: Caption chars length
* Issue #149: Support Python 3.10


0.4.0 (2020-12-31)
------------------

* Issue #79: Python 3.9 support
* Issue #74: Help on dependency issues
* Issue #70: Document streamable file types
* Issue #68: Silence hachoir warnings ([warn] [/file[0]/uid] ...)
* Issue #65: Custom Thumbnail For the Files getting Uploaded
* Issue #43: Write tests
* Issue #40: Not using system HTTP Proxy
* Issue #38: Upload to Pypi using Github Actions
* Issue #36: Database is locked
* Issue #35: Document send files to a chat_id
* Issue #13: Change session directory enhancement
* Issue #11: Change session directory enhancement
* Issue #3: Split large files (> 2GB)


0.3.4 (2020-10-06)
------------------

* Issue #59: Stream upload videos

0.3.3 (2020-09-11)
------------------

* Pull request #54: Finalizing ProgressBar
* Pull request #55: Verifying document size returned by Telegram
* Pull request #56: Extra convenience options for no caption and no thumbnail

0.3.3 (2020-09-11)
------------------

* Pull request #54: Finalizing ProgressBar
* Pull request #55: Verifying document size returned by Telegram
* Pull request #56: Extra convenience options for no caption and no thumbnail


0.3.2 (2020-07-15)
------------------

* Issue #44: Caption problem

0.3.1 (2020-05-11)
------------------

* Issue #37: Directories recursive does not work


0.3.0 (2020-05-07)
------------------

* Issue #2: Upload directories
* Issue #30: Check available disk space in download file
* Issue #33: edit file name
* Issue #24: How to install and use in windows?
* Issue #29: Option to forward uploaded file enhancement
* Issue #20: Can't upload video as Document.
* Issue #12: Docs

0.2.1 (2019-07-30)
------------------

* Issue #26: Installation Error - hachoir3

0.2.0 (2019-00-00)
------------------

* Issue #10: Update docs and validation: mobile phone is required
* Issue #23: Create ~/.config directory if not exists
* Issue #15: Getting file_id of the uploaded file
* Issue #21: Windows support for videos
* Issue #22: Download files

0.1.10 (2019-03-22)
-------------------

* Issue #19: uploading video files with delay

0.1.9 (2019-03-15)
------------------

* Fixed setup: Included requirements.txt to MANIFEST.in.

0.1.8 (2019-03-08)
------------------

* Setup.py requirements only supports python3.

0.1.7 (2019-03-08)
------------------

* Support MKV videos

0.1.6 (2018-07-22)
------------------

* Update to Telethon 1.0

0.1.4 (2018-04-16)
------------------

* Pip 10.0 support

0.1.2 (2018-03-29)
------------------

* Best upload performance

0.1.0 (2018-03-26)
------------------

* First release on PyPI.
