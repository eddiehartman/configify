# configify

Perl script to 'compile' an SDI/TDI workspace project folder into the monolithic Config xml used by the Server

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Downloading / installing

Open a terminal window and enter the following command:

```
git clone https://github.com/eddiehartman/configify.git
```

### Usage

./cgf

configify v1.0 - Compiling config
usage: configify.py [-h] -p --project [-v] [-n --name] [-o --overwrite]
                    [-c --config]
configify.py: error: argument -p is required

### Help

./csf -help

Produce a Config xml from a TDI/SDI project

optional arguments:
  -h, --help      show this help message and exit
  -p --project    path to the TDI/SDI Project folder in workspace
  -v              show program's version number and exit
  -n --name       solution name/id for the Config
  -o --overwrite  overwrite property files to encrypt protected properties
  -c --config     filepath of the output Config xml (default is Project name)

### Prequisites

Check to see if python is available:

```
python --version
```

If not then install it

```
sudo apt-get python3.6
```

You need python installed.

### Examples

```
# Compile GTS_LoadUsers from RTC and write to SolDir folder for zipping
./cfg -p GTS_LoadUsers -overwrite -c $TDI_SOLDIR/GTS_LoadUsers.xml
```

A## Built With

python is fun!

## Authors

* **Eddie Hartman** - *It lives!* - [configify](https://github.com/eddiehartman/configify.git)
