# pylint: disable=W0622
"""cubicweb-i18nfield application packaging information"""

modname = "i18nfield"
distname = "cubicweb-i18nfield"

numversion = (1, 0, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "Florent Cayré (Villejuif, FRANCE)"
author_email = "Florent Cayré <florent.cayre@gmail.com>"
description = "Provides a way to translate entity fields individually."
web = f"http://www.cubicweb.org/project/{distname}"

__depends__ = {
    "cubicweb": ">= 4.0.0, < 5.0.0",
    "cubicweb-web": ">= 1.4.0, < 2.0.0",
    "cubicweb-card": ">= 2.0.0, < 3.0.0",
}

__recommends__ = {}
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]
