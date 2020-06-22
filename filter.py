from wordfilter import Wordfilter

# Filter class, which extends Wordfilter
class Filter(Wordfilter):
    # Gets the list of blacklisted words, excluding the words
    # built into the module
    def get_words(self):
        return self.blacklist[66:len(self.blacklist)]

    # Gets the full list of blacklisted words
    # Only to be used by the backend!
    def get_full_list(self):
        return self.blacklist

    # Remove a word from the list
    def remove_word(self, index):
        remove_index = int(index) + 66
        return self.blacklist.pop(remove_index)
