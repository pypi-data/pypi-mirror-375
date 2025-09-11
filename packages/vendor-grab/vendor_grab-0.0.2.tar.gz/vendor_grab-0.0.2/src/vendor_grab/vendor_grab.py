#!/usr/bin/env python

"""
Vendor Grab

vendor_grab path-to-config.toml

"""

import hashlib
import http.client
import logging
import os
import re
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

LOG_FORMAT = "%(levelname)s: %(name)s.%(module)s.%(funcName)s:\n  %(message)s"
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
logger = logging.getLogger("vendor_grab")
url_regex = re.compile(
    "^(?P<proto>https?)://(?P<host>[^:/]+):?(?P<port>[\d]*)(?P<route>.*)"
)
cache_dir_base = Path(
    os.getenv("XDG_CACHE_HOME", (os.path.join(os.getenv("HOME", ""), ".cache")))
)
cache_dir = cache_dir_base.joinpath("vendor-grab")
cache_dir.mkdir(parents=True, exist_ok=True)


class VendorGrabExit(Exception):
    "Base class for errors that require exiting."


class InvalidConfigError(VendorGrabExit):
    "Invalid config error"


class InvalidChecksum(VendorGrabExit):
    "Invalid Checksum"


class FailedDownload(VendorGrabExit):
    "Failed Download"


class MissingSrcFile(VendorGrabExit):
    "No src file in archive"


def process_vendors(vendors):
    """"""
    if not isinstance(vendors, list):
        raise InvalidConfigError("INVALID: The 'vendors' field should be a list.")

    valid_vendors = list(map(validate_vendor_obj, vendors))
    if not all(valid_vendors):
        raise InvalidConfigError("INVALID: Not all 'vendors' are valid.")

    for vendor_obj in vendors:
        files = vendor_obj["files"]
        dst_checksum = vendor_obj.get("dst_checksum", None)

        # Are the dst files there and match the dst_checksum?
        if dst_checksum is not None and check_dst_files(dst_checksum, files):
            continue
        elif not dst_checksum:
            logger.info(
                f"No dst_checksum set for archive {vendor_obj['archive']}. Grabbing from tar file now."
            )

        vendor_tar_file = get_vendor_tar_file(
            archive=vendor_obj["archive"], checksum=vendor_obj["checksum"]
        )

        strip_components = vendor_obj.get("strip_components", 1)
        src_tmp_dir = extract_files(
            vendor_tar_file,
            files,
            strip_components=strip_components,
        )
        for file_obj in files:
            src = file_obj["src"]
            dst = file_obj["dst"]
            src_path = Path(src_tmp_dir).joinpath(src)
            if not src_path.is_file():
                raise MissingSrcFile(
                    f"ERROR: The src file ({src}) was not found in {vendor_obj['archive']} archive.\n  Check files in tar file: {vendor_tar_file}\n  Note that the 'strip_components' was set to {strip_components}."
                )
            dst_path = Path(dst)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                src_path.replace(dst_path)
            except OSError:
                # Renaming a file across file systems may fail
                shutil.copy2(src_path, dst_path)
                os.unlink(src_path)


def check_dst_files(dst_checksum, files):
    dst_hash = hashlib.sha256()
    # Sort the dst files to ensure that the hash is the same regardless if the
    # order of the dst files change.
    dst_files = sorted(list(map(lambda x: x["dst"], files)))
    for dst in dst_files:
        dst_path = Path(dst)
        if not dst_path.is_file():
            logger.info(f"No {dst_path}.")
            break
        with open(dst_path, "rb") as f:
            while chunk := f.read(8192):
                dst_hash.update(chunk)
    else:
        dst_hash_digest = dst_hash.hexdigest()
        if dst_hash_digest == dst_checksum:
            return True
        else:
            dst_file_list = "\n  - ".join(list(map(lambda x: x["dst"], files)))
            logger.warning(
                f"The dst_checksum ({dst_checksum}) for files:\n  - {dst_file_list}\n  does not match computed dst files checksum ({dst_hash_digest}).\n  Replacing dst files now."
            )
    return False


def get_vendor_tar_file(archive, checksum):
    archive_hash_tar_file = cache_dir.joinpath(checksum + ".tar.gz")

    if not archive_hash_tar_file.exists():
        tmp_tar_file = download_vendor_tar_file(archive, checksum)
        shutil.move(tmp_tar_file, archive_hash_tar_file)

    return archive_hash_tar_file


def download_vendor_tar_file(archive, checksum):
    def get_file_at_location(location):
        m = re.match(url_regex, location)
        url = m.groupdict()
        logger.debug(url)

        if url["proto"] == "http":
            conn_class = http.client.HTTPConnection
        else:
            conn_class = http.client.HTTPSConnection

        port = url["port"] if url["port"] else None

        conn = conn_class(url["host"], port=port)
        try:
            conn.request("GET", url["route"], headers={})
        except (ConnectionError, OSError) as err:
            logger.error(err)
            sys.exit(1)

        response = conn.getresponse()

        response_headers = response.getheaders()
        logger.debug(f"{response_headers=}")
        logger.debug(f"{response.status=}")
        logger.debug(f"{response.reason=}")

        if response.status == 200:
            tf = tempfile.NamedTemporaryFile(delete=False)
            tf.write(response.read())
            tf.close()
            conn.close()

            return tf.name

        elif response.status in (302, 307, 301, 308):
            header_location = list(
                filter(lambda x: x[0].lower() == "Location".lower(), response_headers)
            )
            if not header_location:
                raise Exception("ERROR: no Location to follow")

            if response.status in (301, 308):
                logger.warning(
                    f"Moved permanently {location} -> {header_location[0][1]}"
                )

            conn.close()
            return get_file_at_location(header_location[0][1])

        else:
            raise FailedDownload(
                f"ERROR: Failed to get tar file at {location}. Status code is {response.status}."
            )

    tmp_tar_file = get_file_at_location(archive)

    with open(tmp_tar_file, "rb") as tf:
        tar_file_hash = hashlib.sha256()
        while chunk := tf.read(8192):
            tar_file_hash.update(chunk)
    tar_file_hash_digest = tar_file_hash.hexdigest()
    if tar_file_hash_digest != checksum:
        raise InvalidChecksum(
            f"ERROR: The archive {archive} does not match checksum. Update the checksum to: {tar_file_hash_digest} after reviewing contents in temporary file: {tmp_tar_file}"
        )

    return tmp_tar_file


def extract_files(archive_file, files, strip_components):
    src_file_to_dst_mapping = dict(list(map(lambda x: [x["src"], x["dst"]], files)))

    def filter_members(tarfile):
        def only_src_files(tarinfo_obj):
            if not tarinfo_obj.isfile():
                return False
            file_name = "/".join(tarinfo_obj.name.split("/")[strip_components:])
            if file_name in src_file_to_dst_mapping.keys():
                return True
            return False
        return filter(only_src_files, tarfile.getmembers())

    with tarfile.open(archive_file, mode="r:gz") as af:
        logger.debug(af.getnames())
        src_tmp_dir = tempfile.mkdtemp()

        # The extracted members must be within the defined src directory; the
        # filter_members ensures this. Ignoring bandit LOW severity (nosec).
        if hasattr(tarfile, "data_filter"):
            af.extractall(path=src_tmp_dir, members=filter_members(af), filter=tarfile.data_filter) # nosec
        else:
            logger.warning("Extracting may be unsafe; consider updating Python")
            af.extractall(path=src_tmp_dir, members=filter_members(af)) #nosec

    src_tmp_dir_path = Path(src_tmp_dir)
    for src in src_tmp_dir_path.glob("**/*"):
        if not src.is_file():
            continue
        logger.debug(f"{src=}")
        file_name = "/".join(
            src.parts[len(src_tmp_dir_path.parts) + strip_components :]
        )
        logger.debug(f"{file_name=}")
        file_name_path = src_tmp_dir_path.joinpath(file_name)
        file_name_path.parent.mkdir(parents=True, exist_ok=True)
        src.rename(file_name_path)

    return src_tmp_dir


def validate_vendor_obj(vendor_obj):
    if not isinstance(vendor_obj, dict):
        raise InvalidConfigError("INVALID: The items in 'vendors' must be objects.")
    required_fields = {"archive", "checksum", "files"}
    if not required_fields.issubset(set(vendor_obj.keys())):
        raise InvalidConfigError(
            f"INVALID: Each vendor object must have fields: {required_fields}"
        )

    if not isinstance(vendor_obj["archive"], str):
        raise InvalidConfigError(
            "INVALID: The 'archive' field should be a string value."
        )
    if not re.match(url_regex, vendor_obj["archive"]):
        logger.info(
            f"The 'archive' value ({vendor_obj['archive']}) did not match regex: {url_regex.pattern}"
        )
        raise InvalidConfigError(
            f"INVALID: The 'archive' field value ({vendor_obj['archive']}) needs to be a URL."
        )

    if not isinstance(vendor_obj["checksum"], str):
        raise InvalidConfigError(
            "INVALID: The 'checksum' field should be a string value."
        )
    if not vendor_obj["checksum"]:
        raise InvalidConfigError("INVALID: The 'checksum' field is empty.")
    if not isinstance(vendor_obj["files"], list):
        raise InvalidConfigError("INVALID: The 'files' field should be a list.")

    if vendor_obj.get("dst_checksum", None) is not None:
        if not isinstance(vendor_obj["dst_checksum"], str):
            raise InvalidConfigError(
                "INVALID: The optional 'dst_checksum' field should be a string value."
            )

    valid_files = list(map(validate_file_obj, vendor_obj["files"]))

    return all(valid_files)


def validate_file_obj(file_obj):
    if not isinstance(file_obj, dict):
        raise InvalidConfigError("INVALID: The items in 'files' must be objects.")
    required_fields = {"src", "dst"}
    if not required_fields.issubset(set(file_obj.keys())):
        raise InvalidConfigError(
            f"INVALID: Each file object must have fields: {required_fields}"
        )

    # Paths need to be within working directory (no ../../ or absolute paths).
    working_directory = Path(".").resolve()
    for key in ["src", "dst"]:
        if file_obj[key][:1] == "/":
            raise InvalidConfigError(
                f"INVALID: The '{key}' value can't start with '/'."
            )
        try:
            Path(file_obj[key]).resolve().relative_to(working_directory)
        except ValueError as err:
            raise InvalidConfigError(
                f"INVALID: The '{key}' value '{file_obj[key]}' is not within the working directory {working_directory} . \n {err}"
            )

    return True


def main(config_file):
    """"""
    with open(config_file, "rb") as f:
        try:
            data = tomllib.load(f)
        except tomllib.TOMLDecodeError as err:
            raise InvalidConfigError(
                f"INVALID: Failed to parse the {f.name} file.\n  {err}"
            )

        vendors = data.get("vendors", None)
        if vendors is None:
            raise InvalidConfigError(
                f"INVALID: No 'vendors' field in the {f.name} file."
            )

    process_vendors(vendors)


def script():
    def usage(err=None):
        print(__doc__)
        sys.exit(err)

    if len(sys.argv) != 2:
        usage("No arg passed")
    arg1 = sys.argv[1]

    if arg1 in ("-h", "--help"):
        usage()

    if arg1 in ("-v", "--version"):
        from vendor_grab import _version

        print(_version.__version__)
        sys.exit()

    config_file = Path(arg1).resolve()

    if not config_file.exists() or not config_file.is_file():
        usage(f"No config file at {config_file}")

    try:
        main(config_file)
    except VendorGrabExit as err:
        sys.exit(str(err))


if __name__ == "__main__":
    script()
