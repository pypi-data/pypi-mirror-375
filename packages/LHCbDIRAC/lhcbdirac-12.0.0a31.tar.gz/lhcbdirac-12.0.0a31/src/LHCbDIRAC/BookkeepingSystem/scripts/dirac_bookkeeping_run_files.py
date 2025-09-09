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
"""Retrieve files for a given run."""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                f"  {Script.scriptName} [option|cfgfile] ... Run",
                "Arguments:",
                "  Run:      Run number (integer)",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    try:
        runID = int(args[0])
    except (ValueError, IndexError):
        Script.showHelp(exitCode=1)

    exitCode = 0

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    res = BookkeepingClient().getRunFiles(runID)
    if not res["OK"]:
        print(f"Failed to retrieve run files: {res['Message']}")
        exitCode = 2
    else:
        if not res["Value"]:
            print(f"No files found for run {runID}")
        else:
            print(f"{'FileName'.ljust(100)} {'Size'.ljust(10)} {'GUID'.ljust(40)} {'Replica'.ljust(8)}")
            for lfn in sorted(res["Value"]):
                size = res["Value"][lfn]["FileSize"]
                guid = res["Value"][lfn]["GUID"]
                hasReplica = res["Value"][lfn]["GotReplica"]
                print(f"{lfn.ljust(100)} {str(size).ljust(10)} {guid.ljust(40)} {str(hasReplica).ljust(8)}")

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
