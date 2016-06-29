## Two options for builds of the static docs site:

1. Use the simple html reparse, which adds the image to all of the main module files and also creates the link back to the main page of gitnet.
2. This one is much more complicated, and involves using the edited mako files to autogenerate some of the added features that exist in the gitnet site.
  - Always leave an unedited copy of the mako theme files in the unedited directory.
  - You need to edit the build script to change which method is used. Instructions are simple and are contained in the script.
  - For some reason, currently unknown, adding the top navigation bar to the html files (which is done by the current edited mako files), considerably slows down the load time.
    - Pinpointed the cause to the style files that are loaded by the gitnet website.

## For now, the best option is 1, as it solves the problem by linking back to the main gitnet site.
## Still, we may need to edit the theme files for other reasons.
