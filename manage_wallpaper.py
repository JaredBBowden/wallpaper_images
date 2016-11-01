import glob as glob
import shutil
import pandas as pd
from PIL import Image
from paths import paths


def main():

    # Read in the destination file path
    drive_files = glob.glob(paths["google_drive"] + "*")

    image_data = []
    good_images = []
    issue_files = []

    # Open files and check for issues
    for x in drive_files:

        try:
            image_data.append(Image.open(x).size)
            good_images.append(x)

        except:
            issue_files.append(x)

    print "\nThe following", len(issue_files), "source files contain issues:"
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

    # Identify images that are too small
    small_images = images[(images["X resolution"] < 1024) | \
                          (images["Y resolution"] < 768)]

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

        print "\nThe following", len(
            move_files), "images will be moved to local:"
        move_files["Filename"]

        print "\nMoving..."
        [shutil.move(x, paths["local"]) for x in move_files["Full path"]]

        print "Done"

    else:

        print "\nNo files to move. Done."


if __name__ == '__main__':
    main()
