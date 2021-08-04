# -*- coding: utf-8 -*-
"Sasdi module to select ROIs from a video"

import cv2
import sasdi_functions as sf


def add_legend(extra_legend):
    " Add legend and infos to input image and return it"

    global DISPLAY_NAME, IMAGE, ORIGINAL_IMAGE, ROI_COORD
    display_name = DISPLAY_NAME
    image = IMAGE
    roi_coord = ROI_COORD
    font = cv2.FONT_HERSHEY_SIMPLEX
    mycolor = sf.color_generator(False)     # starts color generator
    # Draw ROIs
    for index, coord in enumerate(roi_coord):
        roi_color_rgb = next(mycolor)
        # Reverse RGB color to BGR for opencv
        roi_color = (roi_color_rgb[2], roi_color_rgb[1], roi_color_rgb[0], 0)
        cv2.rectangle(image,
                      coord[0],
                      coord[1],
                      color=roi_color,
                      thickness=2,
                      )
        cv2.putText(image,
                    str(index+1),
                    org=(coord[1][0] - 25, coord[1][1] - 25),
                    fontFace=font,
                    fontScale=0.8,
                    color=roi_color,
                    thickness=2,
                    )

    cv2.putText(image,
                f"ROI selection for {display_name}",
                org=(10, 30),
                fontFace=font,
                fontScale=0.8,
                color=(0, 255, 0),
                thickness=2
                )
    cv2.putText(image,
                "R = Record current ROI",
                org=(10, 60),
                fontFace=font,
                fontScale=0.6,
                color=(0, 255, 0),
                thickness=1
                )
    cv2.putText(image,
                "D = Discard last ROI",
                org=(10, 90),
                fontFace=font,
                fontScale=0.6,
                color=(0, 255, 00),
                thickness=1
                )
    cv2.putText(image,
                "S = Save all and quit ",
                org=(10, 120),
                fontFace=font,
                fontScale=0.6,
                color=(0, 255, 0),
                thickness=1
                )
    cv2.putText(image,
                f"{len(roi_coord)} selected roi(s)",
                org=(10, 150),
                fontFace=font,
                fontScale=0.6,
                color=(0, 255, 0),
                thickness=1
                )
    if extra_legend:
        cv2.putText(image,
                    extra_legend,
                    org=(10, 180),
                    fontFace=font,
                    fontScale=0.8,
                    color=(0, 255, 0),
                    thickness=2
                    )
    return image

# STARTING FUNCTION
def click(video_pathname, screen_width, screen_height, old_coord, name):
    """ INPUT video pathname to be used, screen width and height in pixels (int), and subserie directory name (or "")
        RETURN selected roi coordinates and message if error
    """
    global DIM_IMAGE, REF_POINT, REF_ENDPOINT, CROPPING, DISPLAY_NAME, IMAGE, ORIGINAL_IMAGE, ROI_COORD

    # SUBFUNCTION FOR CALLBACK (flags and params are unused)
    def click_and_crop(event, x_ref, y_ref, flags, params):

        global DIM_IMAGE, REF_POINT, REF_ENDPOINT, CROPPING, DISPLAY_NAME, IMAGE, ORIGINAL_IMAGE, ROI_COORD
        # If left mouse button starts recording of coordinates as shown by (x_ref, y_ref)
        if event == cv2.EVENT_LBUTTONDOWN:
            REF_POINT = [(x_ref, y_ref)]
            CROPPING = True
        # Check if left button is released
        elif event == cv2.EVENT_LBUTTONUP:              # Save (x_ref, y_ref) and indicates that selection is over
            # check coordinates of second ROI angle are within image dimensions
            if x_ref > DIM_IMAGE[0] - 1:
                x_ref = DIM_IMAGE[0] - 1
            if y_ref > DIM_IMAGE[1] - 1:
                y_ref = DIM_IMAGE[1] - 1
            if x_ref < 0:
                x_ref = 0
            if y_ref < 0:
                y_ref = 0
            REF_POINT.append((x_ref, y_ref))
            cv2.rectangle(IMAGE, REF_POINT[0], REF_POINT[1], color=(0, 255, 0), thickness=1)# Draw a green rectangle with thickness of 1 px
            # Add legend and infos to image
            IMAGE = add_legend("")
            CROPPING = False

        elif event == cv2.EVENT_MOUSEMOVE and CROPPING:
            REF_ENDPOINT = [(x_ref, y_ref)]

    # STARTING MAIN FUNCTION CLICK

    DISPLAY_NAME = name
    success = False
    # Create image from first valid frame of video, start SelectROI
    count = 0
    while not success and count < 1000:
        try:
            # read first frame
            vidcap = cv2.VideoCapture(video_pathname)
            success, IMAGE = vidcap.read()
        except cv2.error as cv2_error:   #Exclude empty video or with read error
            vidcap.release()
            success = False
            print(f"Error reading {video_pathname} : {cv2_error}")
        else:       # video is correctly read
            vidcap.release()
            # success = cv2.imwrite(path_image, image)
        count += 1
    if not success:
        return None, "No valid frame found"



    # Initialise variables
    REF_POINT = []                         # REF_POINT list of 2 coordinates tuple [(x_ref1, y_ref1),(x_ref2, y_ref2)]
    REF_ENDPOINT = []
    CROPPING = False                       # boolean indicates if croping is ON or OFF

    # Get height and width of image (pixels)
    image_height = IMAGE.shape[0]
    image_width = IMAGE.shape[1]
    # Check that image is smaller than screen or set a ratio to be around 70% of screen size
    ratio_width = 1
    ratio_height = 1
    if image_width > screen_width * 0.8:
        ratio_width = round(screen_width/(image_width * 1.3), 1)
    if image_height > screen_height * 0.8:
        ratio_height = round(screen_height/(image_height * 1.3), 1)
    # Keep the smallest ratio for BOTH DIMENSIONS
    ratio_image = min(ratio_width, ratio_height)
    # Set ratioed dimension tuple (width, height)
    DIM_IMAGE = (int(ratio_image * image_width), int(ratio_image * image_height))
    IMAGE = cv2.resize(IMAGE, DIM_IMAGE, interpolation=cv2.INTER_AREA)

    # Apply the image ratio to saved coordinates
    # list of 2 pairs of coordinates [ [ [[x_ref1, y_ref1], [x_ref2, y_ref2]] ] ]
    ROI_COORD = []
    for coord in old_coord[0]:
        ROI_COORD.append([(int(coord[0][0] * ratio_image),
                           int(coord[0][1] * ratio_image)
                          ),
                          (int(coord[1][0] * ratio_image),
                           int(coord[1][1] * ratio_image)
                          )
                         ]
                        )

    # Get a copy of redimensioned image (to refresh display)
    ORIGINAL_IMAGE = IMAGE.copy()
    # Add legend and infos to image
    IMAGE = add_legend("")
    # Configure callback function of mouse
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
    key = cv2.waitKey(1) & 0xFF

    while (key != ord("s") and key != ord("S")):                    # Continue to loop until 's' is used
        cv2.imshow('image', IMAGE)                              # Display image and wait for keyboard
        if CROPPING and REF_ENDPOINT:
            IMAGE = ORIGINAL_IMAGE.copy()
            x_endref = REF_POINT[0]
            y_endref = REF_ENDPOINT[0]
            cv2.rectangle(IMAGE, x_endref, y_endref, (0, 0, 255), 1)    # Draw a blue rectangle with thickness of 1 px
            # Add legend and infos to image
            IMAGE = add_legend("")
            cv2.imshow('image', IMAGE)

        key = cv2.waitKey(1) & 0xFF
        if (key == ord("r") or key == ord("R")):                  # If key 'r' save coordinates
            if len(ROI_COORD) == 8:
                IMAGE = add_legend("Maximum 8 ROIs are possible")
            elif len(REF_POINT) == 2:                     # save coordinates if they exist
                # reverts REF_POINT coordinates [(x_ref1, y_ref1),(x_ref2, y_ref2)] that are not from top-left to bottom-right
                x_ref1 = REF_POINT[0][0]
                y_ref1 = REF_POINT[0][1]
                x_ref2 = REF_POINT[1][0]
                y_ref2 = REF_POINT[1][1]
                if  x_ref1 > x_ref2:
                    x_ref1, x_ref2 = x_ref2, x_ref1   # swap values
                if  y_ref1 > y_ref2:
                    y_ref1, y_ref2 = y_ref2, y_ref1   # swap values
                # Convert coordinates with ratios
                # x_ref1, y_ref1, x_ref2, y_ref2 = int(x_ref1/ratio_image), int(y_ref1/ratio_image), int(x_ref2/ratio_image), int(y_ref2/ratio_image)
                ROI_COORD.append([(x_ref1, y_ref1), (x_ref2, y_ref2)])
                # Add legend and infos to image
                IMAGE = ORIGINAL_IMAGE.copy()
                IMAGE = add_legend("")

        # If key 'd' delete last ROI and reinitialise zone
        elif (key == ord("d") or key == ord("D")):
            if ROI_COORD:
                ROI_COORD = ROI_COORD[:-1]
                IMAGE = ORIGINAL_IMAGE.copy()
                # Add legend and infos to image
                IMAGE = add_legend(f"ROI {len(ROI_COORD) + 1} deleted")


    # End of selection 'q' was pressed
    # del ROI_COORD[:]
    cv2.destroyAllWindows()
    if ROI_COORD:
        # Apply the image ratio to return correct coordinates
        # list of 2 tuples of coordinates [[(x_ref1, y_ref1), (x_ref2, y_ref2)]]
        original_coord = []
        for coord in ROI_COORD:
            original_coord.append([(int(coord[0][0] / ratio_image),
                                    int(coord[0][1] / ratio_image)
                                   ),
                                   (int(coord[1][0] / ratio_image),
                                    int(coord[1][1] / ratio_image)
                                   )
                                  ]
                                 )
        return original_coord, ""
    else:
        return None, "No ROI selected"
