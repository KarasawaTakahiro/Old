import pickle

dire=r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\nicoDL_dev\nicoDL\data\library_ALL.ndl"
file = open(dire)
lib = pickle.load(file)
file.close()

edlist=[]
f = open(r"C:\Documents and Settings\TOSHIBA\My Documents\My Documents\Takahiro\log.txt", "w")
for item in lib:
    if item["format"] == "MOVIE":
        #print item
        if item["state"] == "True":
            continue
        for key in item.iterkeys():
            f.write(str(key))
            f.write(" : ")
            f.write(str(item[key]))
            f.write("\n")
        #raw_input()
        f.write("\n")
    else:
        pass
f.close()

