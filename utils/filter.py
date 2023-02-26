# MIT License
#
# Copyright (c) 2020-2023 Send A Hug
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
#
# The provided Software is separate from the idea behind its website. The Send A Hug
# website and its underlying design and ideas are owned by Send A Hug group and
# may not be sold, sub-licensed or distributed in any way. The Software itself may
# be adapted for any purpose and used freely under the given conditions.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import dataclass


@dataclass(init=True)
class BadWordData:
    badword: str
    index: int


@dataclass(init=True)
class Blacklisted:
    is_blacklisted: bool
    badword_indexes: list[BadWordData]
    forbidden_words: str


# Filter class
# inspired by Wordfilter: https://pypi.org/project/wordfilter/
class WordFilter:
    def blacklisted(self, string: str, filtered_words: list[str]) -> Blacklisted:
        """
        Check if there's a blacklisted word in the text

        param string: The string to check for blacklisted words
        """
        test_string = string.lower()
        badword_indexes: list[BadWordData] = []
        is_blacklisted = False

        # Check each word
        for filter in filtered_words:
            if filter in test_string:
                is_blacklisted = True
                badword_indexes.append(
                    BadWordData(badword=filter, index=test_string.index(filter))
                )

        # return
        return Blacklisted(
            is_blacklisted=is_blacklisted,
            badword_indexes=badword_indexes,
            forbidden_words=",".join([word.badword for word in badword_indexes]),
        )
