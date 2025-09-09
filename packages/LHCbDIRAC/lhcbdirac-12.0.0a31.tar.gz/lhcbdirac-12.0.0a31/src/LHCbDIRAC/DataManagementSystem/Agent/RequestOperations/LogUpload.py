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
"""
:mod: LogUpload

.. module: LogUpload

:synopsis: logUpload operation handler

LogUpload operation handler
"""
# # imports
import os
from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Agent.RequestOperations.DMSRequestOperationsBase import DMSRequestOperationsBase


class LogUpload(DMSRequestOperationsBase):
    """.. class:: LogUpload.

    LogUpload operation handler
    """

    def __init__(self, operation=None, csPath=None):
        """c'tor.

        :param self: self reference
        :param Operation operation: Operation instance
        :param str csPath: CS path for this handler
        """
        # # base class ctor
        super().__init__(operation=operation, csPath=csPath)
        self.workDirectory = os.environ.get("LOGUPLOAD_CACHE", os.environ.get("AGENT_WORKDIRECTORY", "/tmp/LogUpload"))

    def __call__(self):
        """LogUpload operation processing."""
        # # list of targetSEs

        if len(self.operation.targetSEList) != 1:
            self.log.error(
                f"wrong value for TargetSE list = {self.operation.targetSEList}, should contain only one target!"
            )
            self.operation.Error = "Wrong parameters: TargetSE should contain only one targetSE"
            for opFile in self.operation:
                opFile.Status = "Failed"
                opFile.Error = "Wrong parameters: TargetSE should contain only one targetSE"

            return S_ERROR(f"TargetSE should contain only one target, got {self.operation.targetSEList}")

        targetSE = self.operation.targetSEList[0]

        # # check targetSEs for write
        bannedTargets = self.checkSEsRSS()
        if not bannedTargets["OK"]:
            return bannedTargets

        # # get waiting files
        waitingFiles = self.getWaitingFilesList()

        # # loop over files
        for opFile in waitingFiles:
            # # get LFN
            lfn = opFile.LFN
            self.log.info(f"processing file {lfn}")

            # compatibility with the old way of doing failover log with tar files.
            # Files were uploaded as
            # LFN: /lhcb/MC/Upgrade/LOG/00162343/0000/00162343_00007130.tar
            # destination: /lhcb/MC/Upgrade/LOG/00162343/0000/00007130/00162343_00007130.tar
            # (although being a zip file !)
            # Now we stick to zip file, and destination should be left empty
            if os.path.split(lfn) == ".tar":
                destination = "/".join(lfn.split("/")[0:-1]) + "/" + (os.path.basename(lfn)).split("_")[1].split(".")[0]
            else:
                destination = None

            # TPC does not work properly with LogSE-EOS, so use a substitue storage
            if targetSE == "LogSE-EOS" and not destination:
                targetSE = "LogSE-EOS-Write"
            logUpload = self.dm.replicate(lfn, targetSE, destPath=destination, localCache=self.workDirectory)
            if not logUpload["OK"]:
                #         self.dataLoggingClient().addFileRecord( lfn, "LogUploadFail", targetSE, "", "LogUpload" )
                self.log.error(f"completely failed to upload log file: {logUpload['Message']}")
                opFile.Error = str(logUpload["Message"])
                opFile.Attempt += 1
                self.operation.Error = opFile.Error
                if "No such file or directory" in opFile.Error:
                    opFile.Status = "Failed"
                continue

            if lfn in logUpload["Value"]:
                #         self.dataLoggingClient().addFileRecord( lfn, "LogUpload", targetSE, "", "LogUpload" )
                opFile.Status = "Done"
                self.log.info(f"Uploaded {lfn} to {targetSE}")

        return S_OK()
