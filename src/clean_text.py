import codecs

with codecs.open("list.txt", "rb", "unicode_escape") as my_input:
    contents = my_input.read()
# type(contents) = unicode

with codecs.open("utf8-out.txt", "wb", "utf8") as my_output:
    my_output.write(contents)
