import os
import tempfile

from PIL import Image

from . import mxfile


def transponse(img_dir: str, terget_dir: str = "Converted") -> None:
    """
    Mirror Images
    :param img_dir: path to images dir
    :param terget_dir: dirname for stored the images are saved.
    :return: None
    """
    img_list = mxfile.imgs(img_dir, ["jpg", "JPG", "PNG", "png"])
    if img_list:
        target_dir = os.path.join(img_dir, terget_dir)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        for img_name in img_list:
            target_image = Image.open(os.path.join(img_dir, img_name))
            target_path = os.path.join(target_dir, img_name)
            target_image.transpose(Image.FLIP_LEFT_RIGHT).save(target_path)


def mirror(img_path: str) -> Image.Image:
    """
    Mirror the Image
    :param img_path: path to input image file
    :return: PIL.Image obj
    """
    img = Image.open(img_path)

    return img.transpose(Image.FLIP_LEFT_RIGHT)


def comp(
    img_path: str, target_size: int = 1000, step: int = 1, quality: int = 100
) -> Image.Image:
    """
    Compress the image filezie to the target filesize without changing the image size
    :param img_path: the path of image file
    :param target_size: the filesize of output image with KB
    :param step: offset of quality for calculating
    :param quality: base quality for calculating
    :return PIL.Image obj
    """
    img_quality = quality
    filesize = os.path.getsize(img_path) // 1024
    img = Image.open(img_path)
    img_filename = os.path.split(img_path)[-1]
    img_temp_path = os.path.join(tempfile.gettempdir(), img_filename)

    if filesize >= 2500:
        tmp_img = Image.new("RGB", img.size)
        tmp_img.paste(img)
        # tmp_img = tmp_img.rotate(90)
        tmp_img.save(img_temp_path, quality=80)
        # filesize = os.path.getsize(img_temp_path)//1024

        return Image.open(img_temp_path)

    if filesize <= target_size:
        return img

    while filesize > target_size and quality > 0:
        img_quality = img_quality - step
        img.save(img_temp_path, quality=img_quality)
        filesize = os.path.getsize(img_temp_path) // 1024
        print(f"\t图片质量:{img_quality} %\t\t文件大小:{filesize} KB")

        img = Image.open(img_temp_path)

    return img


def watermask(img_path: str, mark_path: str) -> Image.Image:
    """
    Add Watermark into Image
    :param img_path: path of image file
    :param mark_path: path of the mark file
    :return PIL.Image obj
    """
    img = Image.open(img_path)
    mark = Image.open(mark_path)
    mark = mark.resize((mark.size[0] // 2, mark.size[1] // 2))
    new_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    new_img.paste(mark, (15, 15))
    # new_img.paste(mask, (200, 200))

    return Image.composite(new_img, img, new_img)
