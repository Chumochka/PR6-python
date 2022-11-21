import subprocess
import base64
import os

with open("./test/test.txt", "+rb") as file:
    b64=base64.b64encode(file.read())
if not os.path.exists("./test/text"):
    os.makedirs("./test/text")
with open("./test/text/text2.txt","wb") as output_file:
    output_file.write(base64.b64decode(b64))
