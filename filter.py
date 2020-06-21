from wordfilter import Wordfilter

# Filter class, which extends Wordfilter
class Filter(Wordfilter):
    # Gets the list of blacklisted words, excluding the words
    # built into the module
    def get_words(self):
        return self.blacklist[66:len(self.blacklist)]
