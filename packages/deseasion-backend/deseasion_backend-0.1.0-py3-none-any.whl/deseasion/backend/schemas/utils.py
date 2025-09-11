import re

from marshmallow import ValidationError


def validate_name(name):
    """Validate a name against the python2 identifiers and keywords

    View https://docs.python.org/2/reference/lexical_analysis.html#identifiers

    Raises:
        ValidationError if the name is not valid
    """
    # python2 identifier definition, without allowing '_' as the first
    # character
    pattern = re.compile("[a-zA-Z][0-9a-zA-Z_]*")
    # python2 keywords and 'True', 'False' and 'None'
    reserved = [
        "and",
        "del",
        "from",
        "not",
        "while",
        "as",
        "elif",
        "global",
        "or",
        "with",
        "assert",
        "else",
        "if",
        "pass",
        "yield",
        "break",
        "except",
        "import",
        "print",
        "class",
        "exec",
        "in",
        "raise",
        "continue",
        "finally",
        "is",
        "return",
        "def",
        "for",
        "lambda",
        "try",
        "True",
        "False",
        "None",
    ]
    if name in reserved:
        raise ValidationError('"{}" is a reserved python name'.format(name))
    elif pattern.fullmatch(name) is None:
        raise ValidationError('"{}" is not a valid name'.format(name))
