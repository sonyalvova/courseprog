#coding: utf-8
import codecs, re, operator, string, subprocess, os, json

class Database:
    def __init__(self):
        self.dbText = u""
        self.entries = []
        self.attributes = []
        self.mystemArray = []

        self.path_cwd = os.getcwd()

        self.mystemLimit = 20 #50000


    def load(self):
        print "self.load_database_text()"
        self.load_database_text()
        print "self.load_table_structure()"
        self.load_table_structure()
        print "self.load_entries()"
        self.load_entries()
        print "self.refine_entries()"
        self.refine_entries()
        print "self.mystem_entries()"
        self.mystem_entries()

        self.print_entries()


    def load_database_text(self, filename="poetry_database.sql"):
        dbFile = codecs.open(filename, "r", "utf-8")
        self.dbText = dbFile.read()
        dbFile.close()

    def load_table_structure(self):
        structRE = re.findall(u"CREATE TABLE .*? \\((.*)\\) ENGINE=myisam", self.dbText[:2000].replace("\r\n", " "), re.MULTILINE)
        if len(structRE) != 0:
            attributes = re.findall(u"`(.+?)`", structRE[0])
            for i in attributes: self.attributes.append(i)
        else: print "Structure load error"

    def load_entries(self):
        entriesRE = re.findall(u"VALUES ?\\((.*?)\\);\r", self.dbText)
        for entry in entriesRE:
            entryRE = re.findall(u"(NULL|\'.*?\')", entry) # то что нужно
            if len(entryRE) != 33:
                entry = re.sub(u"'(, |$)", u"\"\\1", entry)
                entry = re.sub(u"(, |^)'", u"\\1\"", entry)
                entryRE = re.findall(u"(NULL|\".*?\",|^\".*?\"|\".*?\"$)", entry)
                if len(entryRE) != 33:
                    continue
            self.add_entry(entryRE)

    def add_entry(self, entryRe):
        entryClass = Entry()
        for i in range(33):
            entryClass.attrib[self.attributes[i]] = entryRe[i]
        self.entries.append(entryClass)

    def refine_entries(self):
        for entry in self.entries:
            entry.attrib[u"название"] = entry.attrib[u"название"].strip(string.punctuation)

    def make_bat(self):
        f = codecs.open("run_mystem.bat", "w", "utf-8")
        #f.write(u"cd /d D:\Documents\opinion\ & mystem -dig --eng-gr --format json < input.txt > mystem.json")
        f.write(u"cd /%s %s\ & mystem -dig --eng-gr --format json < input.txt > mystem.json" % (self.path_cwd[0], self.path_cwd))
        f.close()

    def initiate_mystem(self):
        self.make_bat()
        if os.path.isfile("input.txt"): return
        f = codecs.open("input.txt", "w", "utf-8")
        f.write(self.attrib_text())
        p = subprocess.Popen("run_mystem.bat", shell=True, stdout = subprocess.PIPE)
        f.close()
        stdout, stderr = p.communicate()

    def print_entries(self):
        for entry in self.entries[:self.mystemLimit]:
            print entry.attrib[u"название"]
            for word in entry.mystem:
                print word["lex"], word["gr"]
            print "-----"

    def attrib_text(self, atr=u"название"):
        text = u""
        for entry in self.entries:
            text += entry.attrib[atr] + u"\r\n"
        return text[:-2]

    def load_mystem_array(self):
        f = codecs.open("mystem.json", "r", "utf-8")
        c = 0
        for line in f:
            a = json.loads(line.strip())
            mystemArray = []
            for key in a:
                ans = key["analysis"][0]
                mystemArray.append(ans)
                #print self.entries[c].attrib[u"название"], "|" , ans["lex"], ans
            self.entries[c].mystem = mystemArray #запись mystem разбора в db entry
            c += 1
            if c > self.mystemLimit: break
        f.close()

    def mystem_entries(self):
        print "MyStem is working..."
        self.initiate_mystem()
        self.load_mystem_array()


class Entry:
    def __init__(self):
        self.attrib = {}
        self.mystem = []


class Research:
    def __init__(self):
        pass



if __name__ == "__main__":
    db = Database()
    db.load()


# for i in db.entries:
    # print i.attrib[u"название"]
    # for at in i.attrib:
    #     print at, i.attrib[at]
    # print "-------------------------"
    # print