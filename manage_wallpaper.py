import glob as glob
import shutil
import pandas as pd
from PIL import Image
from paths import paths


def read_file_paths(in_path):
    """
    Return a list of files located within the source path, removing
    the 'review' directory.

    in_path: Path to the source directory containing images
    """
    # Read in ALL files within the path
    drive_files = glob.glob(in_path + "*")

    # Remove the 'discard directory'
    for x in drive_files:

        if x.find("review") > 0:

            drive_files.remove(x)

    return drive_files


def clean_image_attributes(to_clean):
    """
    Identify files that do not load as images and shift them to the
    'review/non_image' directory.

    Return a data frame containing paths, image titles, and image
    resolutions.

    to_clean: list of images
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

        # Print out files that are not reading as images
        print "\nThe following", len(
            issue_files), "source files contain issues:"
        print pd.DataFrame(
            data={"Filename": [x.split("/")[-1] for x in issue_files]})

        # Move files with issues to the discard directory
        [shutil.move(x, paths["remote_non_image"]) for x in issue_files]

    # Make a data frame from the remaining images
    images = pd.DataFrame(
        data={"Full path": good_images,
              "Filename": [x.split("/")[-1] for x in good_images],
              "X resolution": [x[0] for x in image_data],
              "Y resolution": [x[1] for x in image_data]})

    return images


def remove_small_images(input_frame, x_limit, y_limit):
    """
    Return a frame containing images that are equal to or larger than the
    specified resolution values

    input_frame:
    x_limit:
    y_limit:

    """
    # TODO add an option to move images to a 'review' directory

    # Identify images that are too small
    small_images = input_frame[(input_frame["X resolution"] <= x_limit) | (input_frame[
        "Y resolution"] <= y_limit)]

    print "\nThe following", len(small_images), "source images are too small:"
    print small_images.drop("Full path", axis=1)

    # Make a data frame with full size images
    large_images = input_frame.drop(small_images.index)

    return large_images


def main():

    # Read in image file paths
    drive_files = read_file_paths(paths["remote"])

    # Remove non-images, and return a data frame with image attributes
    images = clean_image_attributes(drive_files)

    # Remove images that are smaller than specified values
    large_images = remove_small_images(images, 1024, 768)

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
