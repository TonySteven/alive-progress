import math
from functools import wraps
from itertools import chain, repeat

from ..utils.cells import combine_cells, fix_cells, mark_graphemes, split_graphemes


def spinner_player(spinner):
    """Create an infinite generator that plays all cycles of a spinner indefinitely."""

    def inner_play():
        while True:
            yield from spinner()  # instantiates a new cycle in each iteration.

    return inner_play()  # returns an already initiated generator.


def bordered(borders, default):
    """Decorator to include controllable borders in the outputs of a function."""

    def wrapper(fn):
        @wraps(fn)
        def inner_bordered(*args, **kwargs):
            content, right = fn(*args, **kwargs)
            return combine_cells(left_border, content, right or right_border)

        return inner_bordered

    left_border, right_border = extract_fill_graphemes(borders, default)
    return wrapper


def extract_fill_graphemes(text, default):
    """Extract the exact same number of graphemes as default, filling missing ones."""
    text, default = (tuple(split_graphemes(c or '') for c in p) for p in (text or default, default))
    return (mark_graphemes(t or d) for t, d in zip(chain(text, repeat('')), default))


def static_sliding_window(sep, gap, contents, length, right, initial):
    """Implement a sliding window over some content interspersed with a separator.
    It is very efficient, storing data in only one string.

    Note that the implementation is "static" in the sense that the content is pre-
    calculated and maintained static, but actually when the window slides both the
    separator and content seem to be moved."""

    def sliding_window():
        pos = initial
        while True:
            if pos < 0:
                pos += original
            elif pos >= original:
                pos -= original
            yield content[pos:pos + length]
            pos += step

    adjusted_sep = fix_cells((sep * math.ceil(gap / len(sep)))[:gap]) if gap else ''
    content = tuple(chain.from_iterable(chain.from_iterable(zip(repeat(adjusted_sep), contents))))
    original, step = len(content), -1 if right else 1
    assert length <= original, 'window slides inside content, length must be <= len(content)'
    content += content[:length]
    return sliding_window()


def overlay_sliding_window(background, gap, contents, length, step, initial):
    """Implement a sliding window over some content on top of a background.
    It uses internally a static sliding window, but dynamically swaps the separator
    characters for the background ones, thus making it appear immobile, with the
    contents sliding over it."""

    def overlay_window():
        for cells in window:  # pragma: no cover
            yield tuple(b if c == '\0' else c for c, b in zip(cells, background))

    background = (background * math.ceil(length / len(background)))[:length]
    window = static_sliding_window('\0', gap, contents, length, step, initial)
    return overlay_window()


def combinations(nums):
    """Calculate the number of total combinations a few spinners should have together,
    can be used for example with cycles or with frames played at the same time."""

    def lcm(a, b):
        """Calculate the lowest common multiple of two numbers."""
        return a * b // math.gcd(a, b)

    return reduce(lcm, nums)


def split_options(options, expects_tuple=False):
    """Split options that apply to dual elements, either duplicating or splitting."""
    if not expects_tuple:
        return options if isinstance(options, tuple) else (options, options)

    if not isinstance(options, tuple):
        return (options,), (options,)
    if any(isinstance(elem, tuple) for elem in options):
        return tuple(elem if isinstance(elem, tuple) else (elem,) for elem in options)
    return options, options
