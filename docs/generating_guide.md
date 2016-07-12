# Two options for builds of the static docs site:

1. Use the simple html reparse (reparse.py in the gitnet folder), which adds the image to all of the main module files and also creates the link back to the main page of gitnet. The only downside is that the html is limited to one line, and could be difficult for a site user to notice.
2. This one is more complicated, and involves using the edited mako files to autogenerate some of the added features that exist in the gitnet site.
  - Always leave an unedited copy of the mako theme files in the unedited directory. This ensures that if anything doesn't work, you can quickly patch the edited files.
  - You need to edit the build script to change which method is used. Instructions are simple and are contained in the script. It only involves on extra line of code.
  - For some reason, currently unknown, adding the top navigation bar to the html files (which is done by the current edited mako files), considerably slows down the load time.
    - Pinpointed the cause to the style files that are loaded by the gitnet website.
    - This problem may be simple to fix once they are both stored in the same place.

*For now, the best option is 1, as it solves the problem simply by linking back to the main gitnet site.*

# Further generation instructions:

1. The generated html files (along with their directory) need to be placed in the static folder of the HUGO build setup.
2. These files will remain untouched when the HUGO build is generated, and links are defined in the `config.toml` file.
  - The links must be directly to the static html files, ending in `.html`.
3. Images must also be included in the static folder.

- Although including the files at the time of generating the site is the best way, it is also possible to include the links to the static files, and then upload them to the correct spot in the hosted directory.
- This makes it possible to simply update and replace the documentation individually. It is likely still possible to do this after the first time generating, as long as all links and file names stay the same.
