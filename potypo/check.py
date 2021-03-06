import os

import polib
from enchant import DictWithPWL, Dict, errors, Broker
from enchant.checker import SpellChecker

class Check:
    """
    A Check represents a po-file and a corresponding spellchecker for the
    po-files language. It also handles the output-file and some metadata.

    :param popath: The path to the po-file
    :type popath: path
    :param po: The po-file itself
    :type po: pofile
    :param checker: The spellchecker corresponding to the po-file's language
    :type checker: SpellChecker
    """
    def __init__(self, path, wl_dir, chunkers, filters):
        self.popath = path
        self.po = polib.pofile(path)
        self.lang = self.po.metadata["Language"]

        available_lang = Broker().list_languages()
        if self.lang not in available_lang:
            baselang = self.lang.split("_")[0]
            if baselang in available_lang:
                self.lang = baselang
            else:
                print("Dictionary for language '%s' could not be found." % self.lang)
                raise(errors.DictNotFoundError)

        wordlist = Check.get_wordlist(self.lang, wl_dir, path)
        try:
            check_dict = DictWithPWL(self.lang, pwl=wordlist)
        except errors.Error as e:
            check_dict = Dict(self.lang)
            print(e)
        self.checker = SpellChecker(check_dict, chunkers=chunkers, filters=filters)

    @staticmethod
    def get_wordlist(lang, wl_dir, po_path):
        #print("Looking for Wordlist in:\nlang {}\nwl_dir {}\npo_path {}".format(lang, wl_dir, po_path))
        po_path = os.path.abspath(po_path)

        """
        If wl_dir is given, there may be a file called "<lang>.txt". If this is
        the case, this should be the wordlist we are looking for.
        """
        if wl_dir is not None:
            wl_path = os.path.join(wl_dir, lang + '.txt')
            if os.path.isfile(wl_path):
                return wl_path

        """
        If wl_dir is not given, the wordlist should live in a file named
        "wordlist.txt" either in the locales_dir for the default language or in
        the same directory as the .po-files
        """
        if po_path.endswith("po"):
            # translated language
            po_dir = os.path.dirname(po_path)
            for f in os.scandir(po_dir):
                if f.name == "wordlist.txt":
                    #print("found wordlist in", f.path)
                    return f.path
            #print("Checked po-dir, None Found")

            """
            If no file was found so far, the po-files seem to lie in
            <lang>/LC_MESSAGES, and the wordlist should be in the directory
            above.
            """
            if os.path.basename(po_dir) == "LC_MESSAGES":
                for f in os.scandir(os.path.join(po_dir, "..")):
                    if f.name == "wordlist.txt":
                        #print("found wordlist in", f.path)
                        return f.path
            #print("Checked LC_MESSAGES-dir. none found")
        #print("Checked lang-specific files")

        if os.path.isdir(po_path):
            # default language
            for f in os.scandir(po_path):
                if f.name == "wordlist.txt":
                    #print("found wordlist in", f.path)
                    return f.path
        #print("If this shows up, no wordlist was found")
        return None
