# copyright 2011 Florent Cayré (Villejuif, FRANCE), all rights reserved.
# contact http://www.cubicweb.org/project/cubicweb-i18nfield
# mailto:Florent Cayré <florent.cayre@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-i18nfield automatic tests"""

import unittest
from cubicweb_web.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):
    """provides `to_test_etypes` and/or `list_startup_views` implementation
    to limit test scope
    """

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity("I18nLang", code="en", name="English")
            cnx.commit()

    def test_ten_each_config(self):
        # Would need more config
        pass

    def test_one_each_config(self):
        # This cause the creation of invalid I18nLang
        pass


if __name__ == "__main__":
    unittest.main()
