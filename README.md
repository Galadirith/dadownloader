# DeviantArt Downloader

A simple python program to help you download your favourite deviations from
[DeviantArt](http://www.deviantart.com).

## Installation

````bash
$ pip install https://github.com/Galadirith/dadownloader/archive/master.zip
````

### Requirements

- [Python 2.7.x](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/latest/installing.html)

## Usage

````bash
$ dadl [options] <username>

Arguments:
<username>  The username of the DeviantArt user whos favourites you want
            to download.

Options:
-a        Download the avatar of the creator of each deviations
-d        Download the description of each deviation
-f        Download the file (eg img file) associated with each deviation
-h --help Show dadl help menu (this screen)
````

Navigate to the folder where you would like to download the deviations and
execute `dadl`. It is suggested you only execute `dadl` in an empty folder or a
folder in which `dadl` was previously executed. If you want to download all of
the data for each deviation you can simply run the command:

````bash
$ dadl -adf <username>
````

### Login Details

````bash
$ dadl <username>
If you want to access restricted content please provide login detail.
Username: <your-username>
Password: <your-password>
````

`dadl` may prompt you for your log in details for DeviantArt. This is to access
any restricted deviations that may be in the favourites you wish to download. If
you would prefer not to log in to DeviantArt through `dadl` you can simply leave
the `Username` blank and `dadl` will download as much information as it can if
it encounters restricted deviations.

### File Descriptions

`dadl` will create a directory structure similar to the following:

````bash
./
├── cookies
├── credentials
├── <username>.json
└── <username>/
    ├── <collection-one-name>/
    │   ├── avatars/
    │   │   ├── <avatar-one-filename>
    │   │   ├── <avatar-two-filename>
    │   │
    │   ├── descriptions/
    │   │   ├── imgs/
    │   │   │   ├── <img-one-filename>
    │   │   │   ├── <img-two-filename>
    │   │   │
    │   │   ├── <description-one-name>.html
    │   │   ├── <description-one-name>.original
    │   │   ├── <description-two-name>.html
    │   │   ├── <description-two-name>.original
    │   │
    │   ├── <deviation-one-filename>
    │   ├── <deviation-two-filename>
    │
    ├── <collection-two-name>/
    │   ├── avatars/
    │   ├── descriptions/
````

- **cookies**  
  Stores cookies the last time `dadl` was used and successfully logged in to
  DeviantArt.
- **credentials**  
  Stores your username and password from the last time `dadl` was used and
  successfully logged in to DeviantArt. This means you don't have to re-enter
  your username and password every time authenticated cookies in `cookies`
  become
  invalid.
- **&lt;username&gt;.json**  
  Stores a json representation of &lt;username&gt;'s favourites.
- **&lt;username&gt;**  
  Folder in which all deviations, deviation descriptions and avatars are
  downloaded.
  - **&lt;collection-xxx-name&gt;**  
    Folder in which all deviations, deviation descriptions and avatars for this
    collection are downloaded. Note that the first collections name is always
    `Favourites`
    - **avatars**  
      Folder in which all avatars of the creators of the deviations in this
      collection are downloaded.
    - **descriptions**  
      Folder in which all descriptions of the deviations in this collection are
      downloaded. The original html is saved as a `.original` file along with a
      modified `.html` version that uses the `./img` sub-directory as its source
      for any images in the description.
    - **imgs**  
      Folder in which any images in the descriptions are downloaded.

## License

DeviantArt Downloader is released under the [MIT license](LICENSE.md).
