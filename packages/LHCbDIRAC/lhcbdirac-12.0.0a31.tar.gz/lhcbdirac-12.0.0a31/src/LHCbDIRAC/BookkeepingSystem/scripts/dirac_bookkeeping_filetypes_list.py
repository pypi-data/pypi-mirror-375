#!/usr/bin/env python
###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""List file types from the Bookkeeping."""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", f"  {Script.scriptName} [option|cfgfile]"]))
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    res = BookkeepingClient().getAvailableFileTypes()

    if res["OK"]:
        dbresult = res["Value"]
        print("Filetypes:")
        for record in dbresult["Records"]:
            print(str(record[0]).ljust(30) + str(record[1]))

    DIRAC.exit()


if __name__ == "__main__":
    main()
