progress_info = {
    'messages': [],
    'complete': False
}


def reset_info_object():
    progress_info['messages'] = []
    progress_info['complete'] = False


def get_image(get_jpg_clicks, elements):
    if elements and len(elements):
        # File type to output of 'svg, 'png', 'jpg', or 'jpg'
        ftype = 'jpg'

        # 'store': Stores the image data in 'imageData' !only jpg/png are supported
        # 'download'`: Downloads the image as a file with all data handling
        # 'both'`: Stores image data and downloads image as file.
        action = 'store'

        if get_jpg_clicks and int(get_jpg_clicks) > 0:
            action = "download"

        return {
                   'type': ftype,
                   'action': action,
               }, False

    return {}, True


def add_progress_message(message, is_last_message=False):
    global progress_info
    progress_info['messages'].append(message)

    if is_last_message:
        progress_info['complete'] = True  # if it's the last message