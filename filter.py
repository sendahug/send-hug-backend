# MIT License
#
# Copyright (c) 2020 Send A Hug
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

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
        remove_index = int(index) + 65
        return self.blacklist.pop(remove_index)

    # Check if there's a blacklisted word in the text
    def blacklisted(self, string):
        test_string = string.lower()
        badword_indexes = []
        is_blacklisted = False;

        # Check each word
        for badword in self.blacklist:
            if(badword in test_string):
                is_blacklisted = True;
                badword_indexes.append({
                    'badword': badword,
                    'index': test_string.index(badword)
                })

        # return
        return {
            'blacklisted': is_blacklisted,
            'indexes': badword_indexes
        }
