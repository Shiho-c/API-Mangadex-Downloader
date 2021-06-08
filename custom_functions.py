from PIL import Image

from fpdf import FPDF
import glob
import os
import requests
def convert_to_pdf(directory, current_chapter):
    pdf = FPDF()
    w,h = 0,0
    files = glob.glob(directory + "/**/*.png", recursive=True)
    files += glob.glob(directory + "/**/*.jpg", recursive=True)
    files.sort(key=os.path.getmtime)
    counter = 0
    for fname in files:
        if counter == 0:
            cover = Image.open(fname)
            w,h = cover.size
            pdf = FPDF(unit = "pt", format = [w,h])
        
        pdf.add_page()
        pdf.image(fname,0,0,w,h)
        os.remove(fname) 
        counter+=1
    pdf.output(directory + "/" + current_chapter + ".pdf", "F")


def download_image(base_url, images, chapter_directory, current_chapter):
    for x in range(len(images)):
        image = images[x]
        with open('{}/{}.{}'.format(chapter_directory, x, image[-3:]), 'wb+') as handle:
                download_url = base_url + image
                response = requests.get(download_url, stream=True)


                if not response.ok:
                    pass

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

    #convert_to_pdf(chapter_directory, current_chapter)