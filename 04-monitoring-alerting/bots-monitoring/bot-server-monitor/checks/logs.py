import os


def get_directory_size(path):
    total = 0

    if not os.path.exists(path):
        return 0

    for root, dirs, files in os.walk(
        path,
        topdown=True,
        followlinks=False,
    ):
        dirs[:] = [
            directory
            for directory in dirs
            if not os.path.islink(
                os.path.join(root, directory)
            )
        ]

        for filename in files:
            file_path = os.path.join(
                root,
                filename,
            )

            if os.path.islink(file_path):
                continue

            try:
                total += os.stat(
                    file_path,
                    follow_symlinks=False,
                ).st_size

            except (
                PermissionError,
                FileNotFoundError,
                OSError,
            ):
                continue

    return total


def get_logs():
    path = "/var/log"

    return {
        "path": path,
        "size": get_directory_size(path),
    }
