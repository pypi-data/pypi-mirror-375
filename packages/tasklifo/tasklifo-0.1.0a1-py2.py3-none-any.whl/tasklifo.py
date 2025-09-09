# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the AGPL-3.0 License. See LICENSE file in the project root for full license information.
from __future__ import print_function
import argparse
import codecs
import datetime
import hashlib
import json
import os
import shutil
import sys

from io import DEFAULT_BUFFER_SIZE
from typing import Any, Dict, Iterable, Iterator, List, Optional, Text, Tuple, Type

from chat_completions_conversation import ChatCompletionsConversation
from get_multiline_input_with_editor import get_multiline_input_with_editor
from pytz import utc
from textcompat import utf_8_str_to_text, stdin_str_to_text, filesystem_str_to_text, DEFAULT_STDIN_ENCODING, \
    DEFAULT_STDOUT_ENCODING

DEFAULT_TASKLIFO_DIRECTORY = os.path.expanduser('~/.tasklifo')

if sys.version_info < (3,):
    def write_bytes_to_stdout(data):
        # type: (bytes) -> None
        sys.stdout.write(data)


    def write_bytes_to_stderr(data):
        # type: (bytes) -> None
        sys.stderr.write(data)


    def read_bytes_from_stdin():
        # type: () -> bytes
        return sys.stdin.read()
else:
    def write_bytes_to_stdout(data):
        # type: (bytes) -> None
        sys.stdout.buffer.write(data)


    def write_bytes_to_stderr(data):
        # type: (bytes) -> None
        sys.stderr.buffer.write(data)


    def read_bytes_from_stdin():
        # type: () -> bytes
        return sys.stdin.buffer.read()


def read_text_from_stdin():
    # type: () -> Text
    return read_bytes_from_stdin().decode(DEFAULT_STDIN_ENCODING, errors='replace')


def write_text_to_stdout(text):
    # type: (Text) -> None
    return write_bytes_to_stdout(text.encode(DEFAULT_STDOUT_ENCODING, errors='replace'))


def write_text_to_stderr(text):
    # type: (Text) -> None
    return write_bytes_to_stderr(text.encode(DEFAULT_STDOUT_ENCODING, errors='replace'))


def cat(file_path):
    # type: (str) -> Iterator[bytes]
    with open(file_path, 'rb') as fp:
        while True:
            chunk = fp.read(DEFAULT_BUFFER_SIZE)
            if not chunk:
                break
            yield chunk


def ensure_directory_exists(directory_path):
    # type: (str) -> None
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def generate_sha1(file_path):
    # type: (str) -> str
    hasher = hashlib.sha1()
    for chunk in cat(file_path):
        hasher.update(chunk)
    return hasher.hexdigest()


def get_utcnow():
    # type: () -> datetime.datetime
    return datetime.datetime.now(utc)


def get_reverse_sorted_task_json_paths(task_json_directory_paths):
    # type: (Iterable[str]) -> List[str]
    task_json_paths_to_filenames = {}  # type: Dict[str, str]
    for task_json_directory_path in task_json_directory_paths:
        for filename in os.listdir(task_json_directory_path):
            if filename.endswith('.json'):
                task_json_paths_to_filenames[os.path.join(task_json_directory_path, filename)] = filename

    return sorted(task_json_paths_to_filenames.keys(), key=task_json_paths_to_filenames.get, reverse=True)


class TaskLIFO(object):
    """Last-in-first-out task manager with Git-like storage.

    This class provides a stack-like task management system where tasks are stored
    as JSON files and attachments are content-addressed using SHA-1 hashes.

    Attributes:
        tasklifo_directory (str): Root directory of the tasklifo
        objects_directory (str): Directory for content-addressed attachments
        active_tasks_directory (str): Directory for active task JSON files
        completed_tasks_directory (str): Directory for completed task JSON files
    """
    __slots__ = (
        'tasklifo_directory',
        'objects_directory',
        'active_tasks_directory',
        'completed_tasks_directory'
    )

    # Main Operations
    @classmethod
    def init(cls, tasklifo_directory):
        # type: (Type[TaskLIFO], str) -> TaskLIFO
        """Initialize a new tasklifo in a directory.

        Args:
            tasklifo_directory: Directory to initialize the tasklifo

        Returns:
            TaskLIFO: Initialized TaskLIFO instance

        Raises:
            ValueError: If directory is already a tasklifo directory
        """
        objects_directory = os.path.join(tasklifo_directory, 'objects')
        active_tasks_directory = os.path.join(tasklifo_directory, 'tasks', 'active')
        completed_tasks_directory = os.path.join(tasklifo_directory, 'tasks', 'completed')

        if (
                os.path.isdir(tasklifo_directory)
                and os.path.isdir(objects_directory)
                and os.path.isdir(active_tasks_directory)
                and os.path.isdir(completed_tasks_directory)
        ):
            raise ValueError('Already a tasklifo directory: `%s`' % tasklifo_directory)

        ensure_directory_exists(tasklifo_directory)
        ensure_directory_exists(objects_directory)
        ensure_directory_exists(active_tasks_directory)
        ensure_directory_exists(completed_tasks_directory)

        self = super(TaskLIFO, cls).__new__(cls)
        self.tasklifo_directory = tasklifo_directory
        self.objects_directory = objects_directory
        self.active_tasks_directory = active_tasks_directory
        self.completed_tasks_directory = completed_tasks_directory
        return self

    @classmethod
    def load(cls, tasklifo_directory):
        # type: (Type[TaskLIFO], str) -> TaskLIFO
        """Load an existing tasklifo directory.

        Args:
            tasklifo_directory: Path to existing tasklifo directory

        Returns:
            TaskLIFO: Loaded TaskLIFO instance

        Raises:
            ValueError: If directory is not a valid tasklifo directory
        """
        objects_directory = os.path.join(tasklifo_directory, 'objects')
        active_tasks_directory = os.path.join(tasklifo_directory, 'tasks', 'active')
        completed_tasks_directory = os.path.join(tasklifo_directory, 'tasks', 'completed')

        if not (
                os.path.isdir(tasklifo_directory)
                and os.path.isdir(objects_directory)
                and os.path.isdir(active_tasks_directory)
                and os.path.isdir(completed_tasks_directory)
        ):
            raise ValueError('Not a tasklifo directory: `%s`' % tasklifo_directory)

        self = super(TaskLIFO, cls).__new__(cls)
        self.tasklifo_directory = tasklifo_directory
        self.objects_directory = objects_directory
        self.active_tasks_directory = active_tasks_directory
        self.completed_tasks_directory = completed_tasks_directory
        return self

    def store_attachment(self, attachment_path):
        # type: (str) -> Tuple[Text, str]
        """Store an attachment file in the content-addressed object store.

        Args:
            attachment_path: Path to the attachment file

        Returns:
            Tuple[Text, str]: SHA-1 hash of the file and path where it was stored

        Raises:
            IOError: If the file cannot be read or copied
        """
        sha1 = generate_sha1(attachment_path)

        blob_directory = os.path.join(self.objects_directory, sha1[:2])
        ensure_directory_exists(blob_directory)

        blob_path = os.path.join(blob_directory, sha1[2:])

        shutil.copy(attachment_path, blob_path)

        return sha1, blob_path

    def push(self, title, description, attachment_paths):
        # type: (Text, Text, Iterable[str]) ->  Dict[Text, Any]
        """Push a new task onto the stack.

        Args:
            title: Task title
            description: Task description
            attachment_paths: Iterable of paths to attachment files

        Returns:
            Dict[Text, Any]: The created task JSON

        Raises:
            IOError: If any file operation fails
        """
        utcnow = get_utcnow()
        timestamp = utcnow.strftime('%Y%m%dT%H%M%SZ')
        unicode_timestamp = utf_8_str_to_text(timestamp)

        attachments = []  # type: List[Dict[Text, Text]]
        for attachment_path in attachment_paths:
            filename = os.path.basename(attachment_path)
            unicode_filename = filesystem_str_to_text(filename)

            sha1, blob_path = self.store_attachment(attachment_path)
            unicode_sha1 = utf_8_str_to_text(sha1)

            attachments.append({u'sha1': unicode_sha1, u'filename': unicode_filename})

        task_json = {
            u'timestamp': unicode_timestamp,
            u'title': title,
            u'description': description,
            u'attachments': attachments
        }

        with codecs.open(
                os.path.join(self.active_tasks_directory, timestamp + '.json'),
                'w',
                encoding='utf-8'
        ) as fp:
            json.dump(task_json, fp)

        return task_json

    def top(self):
        # type: () -> Dict[Text, Any]
        """Get the top (most recent) active task.

        Returns:
            Dict[Text, Any]: The top task JSON

        Raises:
            ValueError: If there are no active tasks
        """
        reverse_sorted_task_json_paths = get_reverse_sorted_task_json_paths([self.active_tasks_directory])

        if not reverse_sorted_task_json_paths:
            raise ValueError('No active tasks')

        with codecs.open(reverse_sorted_task_json_paths[0], 'r', 'utf-8') as fp:
            return json.load(fp)

    def log(self, all_tasks=False):
        # type: (bool) -> Iterator[Dict[Text, Any]]
        """Get tasks in reverse chronological order.

        Args:
            all_tasks: If True, include completed tasks

        Yields:
            Dict[Text, Any]: Task JSONs for each task
        """
        task_json_directory_paths = [self.active_tasks_directory]
        if all_tasks:
            task_json_directory_paths.append(self.completed_tasks_directory)

        reverse_sorted_task_json_paths = get_reverse_sorted_task_json_paths(task_json_directory_paths)

        for task_json_path in reverse_sorted_task_json_paths:
            with codecs.open(task_json_path, 'r', encoding='utf-8') as fp:
                yield json.load(fp)

    def checkout(self, sha1):
        # type: (str) -> Iterator[bytes]
        """Checkout an attachment by its SHA-1.

        Args:
            sha1: Attachment SHA-1

        Yields:
            bytes: Chunks of the attachment file content

        Raises:
            ValueError: If the attachment SHA-1 is invalid
        """
        blob_path = os.path.join(self.objects_directory, sha1[:2], sha1[2:])
        if not os.path.isfile(blob_path):
            raise ValueError('Invalid attachment SHA-1: %s' % sha1)

        return cat(blob_path)

    def pop(self, timestamp=None):
        # type: (Optional[str]) -> Dict[Text, Any]
        """Pop (complete) an active task.

        Args:
            timestamp: Optional ISO timestamp of specific task to pop

        Returns:
            Dict[Text, Any]: The popped task JSON

        Raises:
            ValueError: If no active tasks exist or timestamp is invalid
        """
        if timestamp is not None:
            task_json_path = os.path.join(self.active_tasks_directory, timestamp + '.json')
            if not os.path.isfile(task_json_path):
                raise ValueError('Invalid timestamp: %s' % timestamp)
        else:
            reverse_sorted_task_json_paths = get_reverse_sorted_task_json_paths([self.active_tasks_directory])

            if not reverse_sorted_task_json_paths:
                raise ValueError('No active tasks')

            task_json_path = reverse_sorted_task_json_paths[0]

        with codecs.open(task_json_path, 'r', encoding='utf-8') as fp:
            task_json = json.load(fp)

        task_json_basename = os.path.basename(task_json_path)
        destination_path = os.path.join(self.completed_tasks_directory, task_json_basename)
        shutil.move(task_json_path, destination_path)

        return task_json


def get_model_response_and_write_to_stderr(conversation, prompt):
    # type: (ChatCompletionsConversation, Text) -> Text
    write_text_to_stderr(u'"""')

    # Attempt to stream the response
    try:
        chunks = []
        for chunk in conversation.send_and_stream_response(prompt):
            write_text_to_stderr(chunk)
            chunks.append(chunk)
        response = u''.join(chunks)
    # Could not stream the response? Assume Streaming API not supported.
    except:
        response = conversation.send_and_receive_response(prompt)
        write_text_to_stderr(response)

    write_text_to_stderr(u'"""\n')

    return response


def correct_model_response_and_write_to_stderr(conversation, model_response, what):
    # type: (ChatCompletionsConversation, Text, Text) -> Text
    write_text_to_stderr(u'"""')

    corrected_model_response = get_multiline_input_with_editor(
        unicode_initial_input=model_response,
        unicode_prompt_at_bottom=u'# Correct model-generated %s above.\n# Lines starting with # will be ignored.' % what
    )
    conversation.correct_last_response(corrected_model_response)

    write_text_to_stderr(corrected_model_response)
    write_text_to_stderr(u'"""\n')

    return corrected_model_response


def print_json(json_object):
    write_text_to_stdout(json.dumps(json_object, indent=2, sort_keys=True))
    write_text_to_stdout(u'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', default=DEFAULT_TASKLIFO_DIRECTORY, required=False, help='Task LIFO directory')
    subparsers = parser.add_subparsers(dest='command')

    # init
    init_parser = subparsers.add_parser('init')

    # push
    push_parser = subparsers.add_parser('push')
    push_parser.add_argument('--title', default='', required=False, help='Task title')
    push_parser.add_argument('--description', default='', required=False, help='Task description')
    push_parser.add_argument('attachments', nargs='*', metavar='attachment', help='Attachment files')

    # llmpush
    llmpush_parser = subparsers.add_parser('llmpush')
    llmpush_parser.add_argument('--api-key', required=True, help='LLM API key')
    llmpush_parser.add_argument('--base-url', required=True, help='LLM base URL')
    llmpush_parser.add_argument('--model', required=True, help='LLM model name')
    llmpush_parser.add_argument('--message', action='append', help='Message(s) for LLM prompt')
    llmpush_parser.add_argument('attachments', nargs='*', metavar='attachment', help='Attachment files')

    # top
    top_parser = subparsers.add_parser('top')

    # log
    log_parser = subparsers.add_parser('log')
    log_parser.add_argument('--all', action='count', help='Show completed tasks too')

    # checkout
    checkout_parser = subparsers.add_parser('checkout')
    checkout_parser.add_argument('sha1', help='Attachment SHA-1')

    # pop
    pop_parser = subparsers.add_parser('pop')
    pop_parser.add_argument('timestamp', nargs='?', help='Pop task with specific ISO timestamp')

    args = parser.parse_args()

    command = args.command
    if command == 'init':
        TaskLIFO.init(args.directory)
        print("Initialized tasklifo in '%s'" % args.directory)
    elif command == 'push':
        tasklifo = TaskLIFO.load(args.directory)

        task_json = tasklifo.push(
            stdin_str_to_text(args.title),
            stdin_str_to_text(args.description),
            args.attachments
        )

        print_json(task_json)
    elif command == 'llmpush':
        tasklifo = TaskLIFO.load(args.directory)

        conversation = ChatCompletionsConversation(
            stdin_str_to_text(args.api_key),
            stdin_str_to_text(args.base_url),
            stdin_str_to_text(args.model),
        )

        if args.message is None:
            unicode_message = get_multiline_input_with_editor(
                unicode_prompt_at_bottom=u'# Enter a message to send to the LLM above.\n# Lines starting with # will be ignored.'
            )
            conversation.append_user_message(unicode_message)
        else:
            for message in args.message:
                conversation.append_user_message(stdin_str_to_text(message))

        write_text_to_stderr(u'\nModel-generated task title: ')
        model_generated_task_title = get_model_response_and_write_to_stderr(conversation, u'Generate a task title:')
        write_text_to_stderr(u'\nUser-corrected task title: ')
        user_corrected_task_title = correct_model_response_and_write_to_stderr(conversation, model_generated_task_title,
                                                                               u'TASK TITLE')

        write_text_to_stderr(u'\nModel-generated task description: ')
        model_generated_task_description = get_model_response_and_write_to_stderr(conversation,
                                                                                  u'Generate a task description:')
        write_text_to_stderr(u'\nUser-corrected task description: ')
        user_corrected_task_description = correct_model_response_and_write_to_stderr(conversation,
                                                                                     model_generated_task_description,
                                                                                     u'TASK DESCRIPTION')

        task_json = tasklifo.push(
            user_corrected_task_title,
            user_corrected_task_description,
            args.attachments
        )

        print_json(task_json)
    elif command == 'top':
        tasklifo = TaskLIFO.load(args.directory)
        task_json = tasklifo.top()
        print_json(task_json)
    elif command == 'log':
        tasklifo = TaskLIFO.load(args.directory)
        for task_json in tasklifo.log(args.all):
            print_json(task_json)
    elif command == 'checkout':
        tasklifo = TaskLIFO.load(args.directory)
        for chunk in tasklifo.checkout(args.sha1):
            write_bytes_to_stdout(chunk)
    elif command == 'pop':
        tasklifo = TaskLIFO.load(args.directory)
        task_json = tasklifo.pop(args.timestamp)
        print_json(task_json)
    else:
        parser.error('Invalid command %s' % (command,))


if __name__ == '__main__':
    main()
