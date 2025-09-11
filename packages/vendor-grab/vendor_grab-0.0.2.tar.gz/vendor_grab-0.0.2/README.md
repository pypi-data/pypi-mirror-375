# Vendor Grab

Download gzipped tar files from URLs and extract only selected files to
destination paths in current working directory.

Configuration file is in TOML format. Takes a list of vendors that can have
multiple files.

```toml
[[vendors]]
archive = "https://github.com/csstools/normalize.css/archive/refs/tags/12.0.0.tar.gz"

# Verify the downloaded tar file with this sha256 hash hexdigest.
checksum = "0820f46861766b7aef99ffd1601e61279d399700e1683e7863f9400af068e3ed"

# The dst_checksum is optional. Delete it to always replace dst files from the downloaded tar file.
#dst_checksum = ""

# The strip_components will default to 1. It is the same as --strip-components flag in tar command.
#strip_components = 1

[[vendors.files]]
# The source (src) of the file in the tar (with the first component stripped off
# since it is usually a directory with the version.
src = "normalize.css"
# The destination (dst) is where it extracts the file to.
dst = "vendor/normalize.css/normalize.css"

# It is common to grab any license files and include them along with source
# files.
[[vendors.files]]
src = "LICENSE.md"
dst = "vendor/normalize.css/LICENSE.md"
```

The created dst files can be committed to source control (git, fossil, etc.) and
if the dst_checksum fields are set; it won't needlessly fetch the tar file each
time. This also prevents the vendor dst files from being modified without also
updating the dst_checksum value.

## Install

```sh
pip install vendor_grab
```

## Usage

Create a configuration file in TOML format that has 'vendors' list. See example
above or the [example-vendors.toml](./example-vendors.toml) file in this
project.

Pass the configuration file as the only arg:
```sh
vendor_grab example-vendors.toml
```

View the downloaded files in the 'vendors' directory (if using the
example-vendors.toml configuration file).


## Why?

_*The Simplest Thing That Could Possibly Work.*_

Why use a tool like `npm` to download some CSS files? That was the main reason
I created this script. I did not need all the capability (and potential security
holes) that the `npm` tool provided. I simply wanted to automate getting some
vendor files into my git repository and keep them up to date.

Initially this script started off as a 
[messy shell script](https://github.com/jkenlooper/cookiecutters/blob/1730ae32c526008973300dcd3321a7d35533fc7e/client-side-public/%7B%7Bcookiecutter.project_slug%7D%7D/Dockerfile#L44)
that used `jq`, `wget`, `md5sum` commands. It also used JSON for the
configuration, which isn't great for adding inline comments. It was rewritten in
Python to be more compatible and easier to follow.

---

## Contributing

Please contact [Jake Hickenlooper](mailto:jake@massive.xyz) or 
[create a ticket](https://todo.sr.ht/~jkenlooper/vendor-grab).

Instructions for preparing a patch are available at
[git-send-email.io](https://git-send-email.io/).

Any submitted changes to this project require the commits to be signed off with
the [git command option
'--signoff'](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---signoff).
This ensures that the committer has the rights to submit the changes under the
project's license and agrees to the [Developer Certificate of
Origin](https://developercertificate.org).

## Maintenance

Where possible, an upkeep comment has been added to various parts of the source
code. These are known areas that will require updates over time to reduce
software rot. The upkeep comment follows this pattern to make it easier for
commands like grep to find these comments.

Example UPKEEP comment has at least a 'due:' or 'label:' or 'interval:' value
surrounded by double quotes (").
````
Example-> # UPKEEP due: "2022-12-14" label: "an example upkeep label" interval: "+4 months"
````
