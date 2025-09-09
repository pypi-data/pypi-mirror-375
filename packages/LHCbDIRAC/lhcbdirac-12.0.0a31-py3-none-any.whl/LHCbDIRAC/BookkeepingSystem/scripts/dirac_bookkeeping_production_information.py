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
"""Retrieve information from the Bookkeeping for a given production."""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                f"  {Script.scriptName} [option|cfgfile] ... ProdID",
                "Arguments:",
                "  ProdID:   Production ID (mandatory)",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    if len(args) < 1:
        Script.showHelp(exitCode=1)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()
    prod = int(args[0])

    res = bk.getProductionInformation(prod)
    if not res["OK"]:
        print(f"ERROR {prod}: {res['Message']}")
        DIRAC.exit(2)

    val = res["Value"]
    print("Production Info: ")

    infs = val["Production information"]
    if infs is not None:
        for inf in infs:
            if inf[2] is not None:
                print("    Configuration Name:", inf[0])
                print("    Configuration Version:", inf[1])
                print("    Event type:", inf[2])

    steps = val["Steps"]

    for step in steps:
        print("-----------------------")
        print(f" StepName: {step[0]} ")
        print(f"    StepId             : {step[7]}")
        print(f"    ApplicationName    : {step[1]}")
        print(f"    ApplicationVersion : {step[2]}")
        print(f"    OptionFiles        : {step[3]}")
        print(f"    DDB                : {step[4]}")
        print(f"    CONDDB             : {step[5]}")
        print(f"    ExtraPackages      : {step[6]}")
        print(f"    Visible            : {step[8]}")
        print("-----------------------")
    print("Number of Steps  ", val["Number of jobs"][0][0])
    files = val["Number of files"]
    if files:
        print("Total number of files:", files[0][2])
    else:
        print("Total number of files: 0")
    for file in files:
        print("         " + str(file[1]) + ":" + str(file[0]))
    nbevent = val["Number of events"]
    if nbevent:
        print("Number of events")
        print("File Type".ljust(20) + "Number of events".ljust(20) + "Event Type".ljust(20) + "EventInputStat")
        for i in nbevent:
            print(str(i[0]).ljust(20) + str(i[1]).ljust(20) + str(i[2]).ljust(20) + str(i[3]))
    else:
        print("Number of events", 0)
    print("Path: ", val["Path"])


if __name__ == "__main__":
    main()
