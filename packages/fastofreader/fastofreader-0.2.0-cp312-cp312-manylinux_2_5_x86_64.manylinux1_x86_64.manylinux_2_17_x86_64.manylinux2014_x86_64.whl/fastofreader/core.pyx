# distutils: language = c
# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
from libc.stdint cimport int64_t
from cpython.bytes cimport PyBytes_AS_STRING, PyBytes_GET_SIZE
from libc.stdlib cimport strtod

cdef inline bint _is_digit(unsigned char b) nogil:
    return b >= 48 and b <= 57      # '0'..'9'

cdef inline bint _is_sep(unsigned char b) nogil:
    # separators between numbers inside (...) — spaces, comma, semicolon, tabs, newlines
    return b in (32, 9, 10, 13, 44, 59)    # ' ', '\t', '\n', '\r', ',', ';'

cdef list _parse_groups_from_bytes(bytes data):
    """
    Parse all (...) groups from raw bytes and return List[List[int]].

    Grammar (simplified):
      groups := { '(' numbers? ')' }*
      numbers := number (sep number)*
      number  := [sign] digits
      sign    := '+' | '-'
      sep     := comma/semicolon/whitespace
    """
    cdef:
        const unsigned char* buf = <const unsigned char*> PyBytes_AS_STRING(data)
        Py_ssize_t n = PyBytes_GET_SIZE(data)
        Py_ssize_t i = 0

        bint in_paren = False
        bint have_num = False
        int sign = 1
        int64_t val = 0

        list result = []
        list group = None

        unsigned char b

    while 1:
        b = buf[i]
        i += 1
        if b == ord('('):
            break
        

    while i < n:
        b = buf[i]

        if not in_paren:
            if b == ord('('):
                in_paren = True
                group = []
                have_num = False
                sign = 1
                val = 0
            # else: ignore everything outside parentheses
            i += 1
            continue

        # We are inside (...)
        if b == ord(')'):
            # flush last number if any
            if have_num:
                group.append(sign * val)
                have_num = False
                sign = 1
                val = 0
            # close group
            result.append(group)
            group = None
            in_paren = False
            i += 1
            continue

        # handle separators between numbers
        if _is_sep(b):
            if have_num:
                group.append(sign * val)
                have_num = False
                sign = 1
                val = 0
            i += 1
            continue

        # handle optional sign only if a number is not in progress
        if (b == ord('+') or b == ord('-')) and not have_num:
            sign = -1 if b == ord('-') else 1
            i += 1
            # next character should be digit; if not, we will ignore later
            continue

        # digits
        if _is_digit(b):
            have_num = True
            val = val * 10 + (b - 48)
            i += 1
            continue

        # Any other character inside (...) that is not digit/sep/sign/')'
        # acts like a separator boundary: flush if we were parsing a number.
        if have_num:
            group.append(sign * val)
            have_num = False
            sign = 1
            val = 0

        i += 1  # skip unknown char

    # If file ends while inside a '(' ... unmatched — ignore trailing partial group
    return result


def read_faces(path: str):
    """
    Read a file and return all integer lists found inside parentheses.

    Returns
    -------
    list[list[int]]
        One inner list per '(...)' group. Numbers may be separated by commas and/or whitespace.
    """
    with open(path, "rb") as f:
        data = f.read()
    return _parse_groups_from_bytes(data)


def read_faces_from_text(text: str):
    """Read groups from an in-memory string (text variant of read_faces)."""
    cdef bytes data = text.encode("utf-8", "ignore")
    return _parse_groups_from_bytes(data)

# Backwards compatibility
def read_int_groups_from_text(text: str):  # deprecated
    return read_faces_from_text(text)


# -------------------------------------------------------------
# Points parser (triplets of floats inside parentheses)
# Expected format: count, then '(', then multiple lines like '(x y z)', then ')'
# We accept any triplet ( ... ) anywhere in file and collect them.

def read_points(path: str):
    """Read triplets of floats from a points file.

    Returns list of [x, y, z].
    """
    with open(path, "rb") as f:
        data = f.read()
    return _parse_points_from_bytes(data)

def read_points_from_text(text: str):
    cdef bytes data = text.encode("utf-8", "ignore")
    return _parse_points_from_bytes(data)

cdef list _parse_points_from_bytes(bytes data):
    cdef:
        const char* buf = <const char*> PyBytes_AS_STRING(data)
        Py_ssize_t n = PyBytes_GET_SIZE(data)
        Py_ssize_t i = 0
        list result = []
        char c
        char* start
        char* endptr
        double v
        int k
        list point

    while i < n:
        if buf[i] == '(':
            j = i + 1
            # Skip whitespace
            while j < n and buf[j] in (32,9,10,13):
                j += 1
            # If next char is another '(' and looks like a point start after that, treat first as wrapper
            if j < n and buf[j] == '(':
                k = j + 1
                while k < n and buf[k] in (32,9,10,13):
                    k += 1
                if k < n and ((48 <= buf[k] <= 57) or buf[k] in (43,45,46)):
                    i = j  # shift to inner '('
                    continue
            # Try parse 1st float
            start = <char*> (buf + j)
            v1 = strtod(start, &endptr)
            if endptr == start:
                i += 1
                continue  # not a number after '('
            j = <Py_ssize_t>(endptr - buf)
            while j < n and buf[j] in (32,9,10,13):
                j += 1
            # 2nd float
            start = <char*> (buf + j)
            v2 = strtod(start, &endptr)
            if endptr == start:
                i += 1
                continue
            j = <Py_ssize_t>(endptr - buf)
            while j < n and buf[j] in (32,9,10,13):
                j += 1
            # 3rd float
            start = <char*> (buf + j)
            v3 = strtod(start, &endptr)
            if endptr == start:
                i += 1
                continue
            j = <Py_ssize_t>(endptr - buf)
            while j < n and buf[j] in (32,9,10,13):
                j += 1
            if j < n and buf[j] == ')':
                result.append([v1, v2, v3])
                i = j + 1
                continue
        i += 1
    return result


## Removed sum_of_squares and NumPy dependency per user request.
