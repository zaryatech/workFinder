#!/usr/bin/env python
# -*- coding: utf-8 -*-



from tesserocr import PyTessBaseAPI

images = ['download.png']

with PyTessBaseAPI() as api:
    for img in images:
        api.SetVariable("tessedit_char_whitelist", "0123456789 -")
        api.SetImageFile(img)
        print api.GetUTF8Text()
        #print api.AllWordConfidences()



# download.png

