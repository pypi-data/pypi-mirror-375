# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



if __name__ == '__main__':


    import re

    from pybear.feature_extraction.text._TextJustifier._transform._transform import \
        _transform


    text = [
        "Jojo was a man who thought he was a loner",
        "But he knew it couldn't last",
        "Jojo left his home in Tucson, Arizona",
        "For some California grass",
        "Get back, get back",
        "Get back to where you once belonged",
        "Get back, get back",
        "Get back to where you once belonged",
        "Get back Jojo",
        "Go home",
        "Get back, get back",
        "Back to where you once belonged",
        "Get back, get back",
        "Back to where you once belonged, yeah",
        "Oh, get back, Jo",
        "Sweet Loretta Martin thought she was a woman",
        "But she was another man",
        "All the girls around her say she's got it coming",
        "But she gets it while she can",
        "Oh, get back, get back",
        "Get back to where you once belonged",
        "Get back, get back",
        "Get back to where you once belonged",
        "Get back Loretta, woo, woo",
        "Go home",
        "Oh, get back, yeah, get back",
        "Get back to where you once belonged",
        "Yeah, get back, get back",
        "Get back to where you once belonged",
        "Ooh",
        "Ooh, ooh",
        "Get back, Loretta",
        "Your mommy's waitin' for you",
        "Wearin' her high-heel shoes",
        "And a low-neck sweater",
        "Get back home, Loretta",
        "Get back, get back",
        "Get back to where you once belonged",
        "Oh, get back, get back",
        "Get back, oh yeah"
    ]


    n_chars = 40

    out = _transform(
        text,
        _n_chars=n_chars,
        _sep=(re.compile(' '), ),
        _line_break=None,
        _backfill_sep=' '
    )

    print(f"=" * (n_chars-1) + "|")
    [print(_) for _ in out]









