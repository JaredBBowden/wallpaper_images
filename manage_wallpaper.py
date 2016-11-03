import glob as glob
import shutil

import pandas as pd
from PIL import Image

from paths import paths


def read_file_paths(in_path):
    """
    Return a list of files located within the source path, removing
    the 'discard' directory.
    """
    # Read in ALL files within the path
    drive_files = glob.glob(in_path + "*")

    # Remove the 'discard directory'
    for x in drive_files:

        if x.find("discard") > 0:

            drive_files.remove(x)

    return drive_files


def clean_image_attibutes(to_clean):
    """
    Identify files that do not load as images and shift them to the
    'discard' directory.

    Return a data frame containing paths, image titles, and image
    resolutions.
    """

    image_data = []
    good_images = []
    issue_files = []

    # Open files and check for issues
    for x in to_clean:

        try:
            image_data.append(Image.open(x).size)
            good_images.append(x)

        except:
            issue_files.append(x)

    if len(issue_files) > 0:

        print "\nThe following", len(
            issue_files), "source files contain issues:"
        print pd.DataFrame(
            data={"Filename": [x.split("/")[-1] for x in issue_files]})

        # Move files with issues to the discard directory
        [shutil.move(x, paths["discard"]) for x in issue_files]

    # Make a data frame from the remaining images
    images = pd.DataFrame(
        data={"Full path": good_images,
              "Filename": [x.split("/")[-1] for x in good_images],
              "X resolution": [x[0] for x in image_data],
              "Y resolution": [x[1] for x in image_data]})

    return images


def main():

    # Read in image file paths
    drive_files = read_file_paths(paths["google_drive"])

    # Remove non-images, and return a data frame with image attributes
    images = clean_image_attibutes(drive_files)

    # Identify images that are too small
    # TODO add an option to move images to a 'review' directory
    small_images = images[(images["X resolution"] < 1024) | (images[
        "Y resolution"] < 768)]

    print "\nThe following", len(small_images), "source images are too small:"
    print small_images.drop("Full path", axis=1)

    # Make a data frame with full size images
    large_images = images.drop(small_images.index)

    # Find images that don't already exist in the destination
    local_files = [x.split("/")[-1] for x in glob.glob(paths["local"] + "*")]

    # Take the inverse
    diff = large_images["Filename"].isin(local_files)
    diff = ~diff

    if sum(diff) > 0:

        move_files = large_images[diff]

        print "\nFound", len(move_files), "new image(s) that meet criteria:"
        print move_files["Filename"]

        answer = raw_input("\nMove images to local? [y/n]: ")

        if answer == "y":

            print "\nMoving new images to local..."
            [shutil.copy(x, paths["local"]) for x in move_files["Full path"]]

            print "\nDone"

        else:
            print "Image move aborted"

    else:

        print "\nNo files to move. Done."


if __name__ == '__main__':
    main()
