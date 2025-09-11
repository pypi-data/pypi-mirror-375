from typing import Union

from gbox_sdk.wrapper.box.linux import LinuxBoxOperator
from gbox_sdk.types.v1.boxes.dir import Dir
from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.types.v1.boxes.file import File
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.file_system import FileOperator, DirectoryOperator
from gbox_sdk.wrapper.box.android.android import AndroidBoxOperator


def is_android_box(box: Union[AndroidBox, LinuxBox]) -> bool:
    return getattr(box, "type", None) == "android"


def is_linux_box(box: Union[AndroidBox, LinuxBox]) -> bool:
    return getattr(box, "type", None) == "linux"


def is_android_operator(operator: Union[AndroidBoxOperator, LinuxBoxOperator]) -> bool:
    return operator.data.type == "android"


def is_linux_operator(operator: Union[AndroidBoxOperator, LinuxBoxOperator]) -> bool:
    return operator.data.type == "linux"


def is_file(item: Union[File, Dir]) -> bool:
    return item.type == "file"


def is_directory(item: Union[File, Dir]) -> bool:
    return item.type == "dir"


def is_file_operator(item: Union[FileOperator, DirectoryOperator]) -> bool:
    return item.data.type == "file"


def is_directory_operator(item: Union[FileOperator, DirectoryOperator]) -> bool:
    return item.data.type == "dir"
