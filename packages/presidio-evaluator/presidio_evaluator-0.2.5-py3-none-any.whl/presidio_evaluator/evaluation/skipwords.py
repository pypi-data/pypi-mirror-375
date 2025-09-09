from typing import List
import string

from spacy.lang.en.stop_words import STOP_WORDS


def get_skip_words() -> List[str]:
    """Return a list of tokens to ignore during evaluation."""
    skip_words = [x for x in string.punctuation]
    skip_words += [x for x in string.whitespace]
    skip_words.extend(
        [
            " ",
            "",
            "\n",
            "\n\n",
            "\n\n\n",
            "\n\n\n\n",
            "\t",
            "\t\t",
            "\t\t\t",
            "\t\t\t\t",
            ">>",
            ">>>",
            ">>>>",
            ">>>>>",
            ">>>>>>",
            "'s",
            "street",
            "st.",
            "st",
            "de",
            "rue",
            "via",
            "and",
            "a",
            "the",
            "or",
            "do",
            "as",
            "of",
            "day",
            "address",
            "country",
            "state",
            "city",
            "zip",
            "po",
            "apt",
            "unit",
            "corner",
            "p.o.",
            "box",
            "suite",
            "mr.",
            "mrs.",
            "miss",
            "year",
            "years",
            "y/o",
            "month",
            "months",
            "old",
            "morning",
            "noon",
            "afternoon",
            "night",
            "evening",
            "this",
            "first",
            "last",
            "week",
            "weeks",
            "weekend",
            "day",
            "days",
            "age",
            "ago",
            "inc",
            "inc.",
            "ltd",
        ]
    )

    skip_words.extend(STOP_WORDS)

    return list(set(skip_words))
