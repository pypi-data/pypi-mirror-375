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

"""Utilities for scripts dealing with transformations."""
from collections import defaultdict
import os
from datetime import datetime, timedelta, timezone
import random
import re
import subprocess
import time
import sys
import pickle
import numpy as np
from pathlib import Path

from collections import Counter
from threading import Lock

from cachetools import TTLCache, cached
from cachetools.keys import hashkey

from DIRAC import gConfig, gLogger, S_OK, S_ERROR
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise, convertToReturnValue


# from DIRAC.Core.Utilities.TimeUtilities import timeThis
from DIRAC.Core.Utilities.File import mkDir, convertSizeUnits
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers, resolveSEGroup
from DIRAC.Resources.Storage.StorageElement import StorageElement
from DIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient

from DIRAC.TransformationSystem.Client.Utilities import PluginUtilities as DIRACPluginUtilities
from DIRAC.TransformationSystem.Client.Utilities import isArchive, getActiveSEs

from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient, BKClientWithRetry
from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery, makeBKPath
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.DataManagementSystem.Client.DMScript import ProgressBar
from LHCbDIRAC.DataManagementSystem.Client.StorageUsageClient import StorageUsageClient
from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import getFileDescendents


def _stripNumDirectory(dirName):
    """Method to remove numeric directory form a directory path."""
    while True:
        subDir = os.path.basename(dirName)
        if subDir and not subDir.isdigit():
            return dirName
        dirName = os.path.dirname(dirName)


def _clearTaskLFNs(taskLfns):
    """Clear the input list of lists, keeping its reference."""
    nbLfns = 0
    for lfnList in taskLfns:
        nbLfns += len(lfnList)
        del lfnList[:]
    return nbLfns


class PluginUtilities(DIRACPluginUtilities):
    """Utility class used by plugins."""

    def __init__(
        self,
        plugin="LHCbStandard",
        transClient=None,
        dataManager=None,
        fc=None,
        bkClient=None,
        rmClient=None,
        debug=False,
        transID=None,
    ):
        """c'tor."""
        # clients
        if transClient is None:
            self.transClient = TransformationClient()
        else:
            self.transClient = transClient
        if bkClient is None:
            bkClient = BookkeepingClient()
        self.bkClient = BKClientWithRetry(bkClient)
        if rmClient is None:
            self.rmClient = ResourceManagementClient()
        else:
            self.rmClient = rmClient

        self.suClient = StorageUsageClient()

        super().__init__(
            plugin=plugin, transClient=self.transClient, dataManager=dataManager, fc=fc, debug=debug, transID=transID
        )

        self.freeSpace = {}
        self.transFiles = []
        self.transReplicas = {}
        self.cachedLFNAncestors = {}
        self.cachedNbRAWFiles = {}
        self.usingRAWFiles = None
        self.cachedRunLfns = {}
        self.cachedProductions = {}
        self.cachedLastRun = 0
        self.cachedLFNProcessedPath = {}
        self.cacheFile = ""
        self.filesParam = {}
        self.transRunFiles = {}
        self.notProcessed = {}
        self.cacheHitFrequency = max(0.0, 1 - self.getPluginParam("RunCacheUpdateFrequency", 0.1))
        self.__runExpired = {}
        self.__recoType = ""
        self.dmsHelper = DMSHelpers()
        # < run_id: [dest, raw destination] >
        self.runDestinations = {}
        self.cachedDirMetadata = {}
        self.runsUsedForShares = set()
        self.shareMetrics = None
        self.lastCall = None
        self.excludedStatuses = self.getPluginParam("IgnoreStatusForFlush", ["Removed", "MissingInFC", "Problematic"])
        self.tsParams = ("FileSize", "FileType", "RunNumber")
        self.paramName = None
        self.onlineCondDB = None
        self.run3CondDB = None
        self.chunkForFileDescendants = None
        # Method aliases
        self.setCachedTimeExceeded = self.setCachedLastRun
        self.getCachedTimeExceeded = self.getCachedLastRun

        self.rnd_generator = np.random.default_rng()

    def setDebug(self, val):
        self.debug = val

    def updateSharesUsage(self, counters, se, count, runID):
        """Update the usage counters if share is by files, and the run duration
        otherwise."""
        inc = 0
        if self.shareMetrics == "Files":
            inc = count
        else:
            self.logVerbose(
                "Updating SE %s for run %d which is %salready used"
                % (se, runID, "not " if runID not in self.runsUsedForShares else "")
            )
            if runID not in self.runsUsedForShares:
                # Update with run duration
                res = self.__getRunDuration(runID)
                if not res["OK"]:
                    self.logError("Error getting run time", res["Message"])
                else:
                    inc = res["Value"]
                    self.runsUsedForShares.add(runID)
        if inc:
            counters[se] = counters.setdefault(se, 0) + inc
            self.logVerbose("New %s counter for %s: %d (+%d)" % (self.shareMetrics, se, counters[se], inc))
            self.printShares("New counters and used fraction (%)", counters, log=self.logVerbose)

    def printShares(self, title, shares, counters=None, log=None):
        """Print formatted shares and if provised counters.

        :param title: header of print out
        :type title: string
        :param shares: Shares per SE or site
        :type shares: dictionary
        :param counters: Current values per SE or site
        :type counters: dictionary
        :param log: (sub)Logger instance to be used
        :type log: logging method
        """
        if log is None:
            log = self.logInfo
        if counters is None:
            counters = shares
        normCounters = normaliseShares(counters) if counters else {}

        if self.shareMetrics:
            title += f" (metrics is {self.shareMetrics})"
        log(title)
        for se in sorted(shares):
            if isinstance(shares[se], int):
                infoStr = "%s: %d " % (se.rjust(15), shares[se])
            else:
                infoStr = f"{se.rjust(15)}: {shares[se]:4.1f} "
            if se in counters:
                infoStr += f"| {normCounters[se]:4.1f} %"
            log(infoStr)

    def getPluginShares(self, section=None, backupSE=None, log=None, counters=True):
        """Get shares from CS:

        * If backupSE is not present: just return the CS shares as they are
        * If backupSE is specified, the shares represent a percentage of the RAW
          at each site and the rest is for backupSE

        If the ShareMetrics is Files:
        * Use the number of files as metrics for SE usage
        Else:
        * Use the duration (in seconds) of runs as metrics for SE usage
        """
        if log is None:
            log = self.logInfo
        if section is None:
            # This is for reconstruction shares (CU)
            sharesSections = {"DataReconstruction": "CPUforRAW", "DataReprocessing": "CPUforReprocessing"}
            res = self.transClient.getTransformation(self.transID)
            if not res["OK"]:
                self.logError("Cannot get information on transformation")
                return res
            transType = res["Value"]["Type"]
            section = sharesSections.get(transType, "CPUforRAW")
        res = getShares(section)
        if not res["OK"]:
            self.logError(f"There is no CS section {section}", res["Message"])
            return res
        rawFraction = {}
        if backupSE:
            # Apply these processing fractions to the RAW distribution shares
            rawFraction = res["Value"]
            result = getShares("RAW", normalise=True)
            if result["OK"]:
                rawShares = result["Value"]
                shares = {se: rawShares[se] * rawFraction[se] for se in set(rawShares) & set(rawFraction)}
                shares[backupSE] = 100.0 - sum(shares.values())
            else:
                return res
            rawPercentage = {se: 100.0 * val for se, val in rawFraction.items()}  # can be an iterator
            self.printShares(
                f"Fraction of RAW ({section}) to be processed at each SE (%):", rawPercentage, counters=[], log=log
            )
        else:
            shares = normaliseShares(res["Value"])
            log("Obtained the following target distribution shares (%):")
            for se in sorted(shares):
                log(f"{se.ljust(15)}: {shares[se]:.1f}")

        # If counters are not requested, return only shares
        if not counters:
            return S_OK(({}, shares))

        if self.shareMetrics is None:
            self.shareMetrics = self.getPluginParam("ShareMetrics", "")
        # Get the existing destinations from the transformationDB, just for printing
        if self.shareMetrics == "Files":
            res = self.getExistingCounters(requestedSEs=sorted(shares))
        else:
            res = self.getSitesRunsDuration(requestedSEs=sorted(shares))
        if not res["OK"]:
            self.logError("Failed to get used share", res["Message"])
            return res
        existingCount = res["Value"]
        self.printShares("Target shares and usage for production (%):", shares, counters=existingCount, log=log)
        return S_OK((rawFraction if rawFraction else existingCount, shares))

    def __getRunDuration(self, runID):
        """Get the run duration."""
        # Get run metadata
        runMetadata = self.transClient.getRunsMetadata([runID]).get("Value", {})
        return S_OK(self.__extractRunDuration(runMetadata, runID))

    def __extractRunDuration(self, runMetadata, runID):
        """Obtain run duration from the TS run metadata table If not available, get
        it from BK."""
        duration = runMetadata.get(runID, {}).get("Duration")
        if duration is None:
            self.logVerbose("Run duration not found in TS for run %d, get it from BK" % runID)
            res = self.bkClient.getRunInformation({"RunNumber": [runID], "Fields": ["JobStart", "JobEnd"]})
            if not res["OK"]:
                self.logError("Error getting run start/end information", res["Message"])
                duration = 0
            if runID in res["Value"]:
                start = res["Value"][runID]["JobStart"]
                end = res["Value"][runID]["JobEnd"]
                duration = (end - start).seconds
            else:
                duration = 0
        return int(duration)

    def getSitesRunsDuration(self, transID=None, normalise=False, requestedSEs=None):
        """Get per site how much time of run was assigned."""
        res = self.getTransformationRuns(transID=transID)
        if not res["OK"]:
            return res
        runDictList = res["Value"]
        # Get run metadata
        runMetadata = self.transClient.getRunsMetadata([runDict["RunNumber"] for runDict in runDictList]).get(
            "Value", {}
        )

        seUsage = {}
        for runDict in runDictList:
            runID = runDict["RunNumber"]
            selectedSEs = runDict["SelectedSite"]
            selectedSEs = set(selectedSEs.split(",")) if selectedSEs is not None else set()
            if requestedSEs:
                selectedSEs &= set(requestedSEs)
                if not selectedSEs:
                    continue
            duration = self.__extractRunDuration(runMetadata, runID)
            self.runsUsedForShares.add(runID)
            for se in selectedSEs:
                seUsage[se] = seUsage.setdefault(se, 0) + duration

        if normalise:
            seUsage = normaliseShares(seUsage)
        return S_OK(seUsage)

    def getExistingCounters(self, transID=None, normalise=False, requestedSEs=None):
        """Used by RAWReplication and RAWProcessing plugins, gets what has been
        done up to now while distributing runs."""
        if transID is None:
            transID = self.transID
        res = self.transClient.getCounters("TransformationFiles", ["UsedSE"], {"TransformationID": transID})
        if not res["OK"]:
            return res
        usageDict = {}
        for usedDict, count in res["Value"]:
            usedSE = usedDict["UsedSE"]
            if usedSE != "Unknown":
                usageDict[usedSE] = count
        if requestedSEs:
            requestedSEs = set(requestedSEs)
            seDict = {}
            for se, count in usageDict.items():  # can be an iterator
                overlap = set(se.split(",")) & requestedSEs
                if overlap:
                    for ov in overlap:
                        seDict[ov] = seDict.setdefault(ov, 0) + count
                else:
                    self.logWarn(f"{se} is in counters but not in required list")
            usageDict = seDict
        if normalise:
            usageDict = normaliseShares(usageDict)
        return S_OK(usageDict)

    def getMetadataFromTSorBK(self, lfns, param):
        """Get BK parameters from BK unless they are already present in the TS."""
        if isinstance(lfns, str):
            lfns = [lfns]
        lfns = set(lfns)
        filesParam = {}
        # For parameters that are in the TS files DB, no need to go to BK
        if param in self.tsParams:
            par = param if param != "FileSize" else "Size"
            # We already have this information
            for fileDict in self.transFiles:
                lfn = fileDict["LFN"]
                if lfn in lfns:
                    value = fileDict.get(par)
                    if value:
                        filesParam[lfn] = value

            lfnsLeft = set(lfns) - set(filesParam)
            self.logVerbose(f"Found parameter {param} in transFiles for {len(filesParam)} files, {len(lfnsLeft)} left")
        else:
            lfnsLeft = lfns

        if lfnsLeft:
            for chunk in breakListIntoChunks(lfnsLeft, 1000):
                loggedError = False
                # Let's loop forever as this MUST succeed
                while True:
                    res = self.bkClient.getFileMetadata(chunk)
                    if res["OK"]:
                        success = res["Value"]["Successful"]
                        filesParam.update({lfn: success[lfn].get(param) for lfn in success})
                        break
                    if not loggedError:
                        self.logError("Error getting BK file metadata", res["Message"])
                        loggedError = True
                    time.sleep(1)
            # Check if all parameters are present in TS... If not, set them while we have them here
            lfnDict = {}
            for fileDict in self.transFiles:
                lfn = fileDict["LFN"]
                if lfn in success:
                    for param in self.tsParams:
                        par = param if param != "FileSize" else "Size"
                        if fileDict.get(par) is None:
                            lfnDict.setdefault(lfn, {}).update({par: success[lfn][param]})
            if lfnDict:
                res = self.transClient.setParameterToTransformationFiles(self.transID, lfnDict)
                self.logVerbose(
                    f"Updated files metadata in TS for {len(lfnDict)} files: {'OK' if res['OK'] else 'Failed'}"
                )

        return filesParam

    def getProductions(self, processingPasses, transStatus):
        """Get the list of productions matching a given list of processing
        passes.
        This is currently used only in _RemoveReplicasWhenProcessed, so very tailored
        """
        # Get information about the current transformation
        transQuery = self.getTransQuery(self.transReplicas)
        if transQuery is None:
            return S_ERROR("Could not get transformation BK query")
        transProcPass = transQuery["ProcessingPass"]
        eventType = transQuery["EventType"]
        if not transProcPass:
            self.logError("Unable to find processing pass for transformation")
            return S_ERROR("No processing pass found")

        # Build list of BK paths to look for
        fullBKPaths = [bkPath for bkPath in processingPasses if bkPath.startswith("/")]
        relBKPaths = [bkPath for bkPath in processingPasses if not bkPath.startswith("/")]
        bkPathList = {}
        if fullBKPaths:
            # We were given full BK paths, use them
            for bkPath in fullBKPaths:
                bkQuery = BKQuery(bkPath, visible="All")
                eventType = bkQuery.getEventTypeList()
                bkPathList.update(
                    {
                        bkPath.replace("RealData", "Real Data"): bkQuery.getQueryDict()["ProcessingPass"]
                        for bkPath in fullBKPaths
                    }
                )

        if relBKPaths:
            for procPass in relBKPaths:
                if not transProcPass.endswith(procPass):
                    newPass = os.path.join(transProcPass, procPass)
                else:
                    newPass = procPass
                transQuery.update({"ProcessingPass": newPass, "Visibility": "All"})
                transQuery.pop("FileType", None)
                bkPathList[makeBKPath(transQuery)] = newPass
        self.logVerbose(
            "List of BK paths:",
            "\n\t".join(
                [""]
                + [
                    "%s: %s"
                    % (bkPath.replace("Real Data", "RealData"), bkPathList[bkPath].replace("Real Data", "RealData"))
                    for bkPath in sorted(bkPathList)
                ]
            ),
        )

        now = datetime.utcnow()
        period = self.getPluginParam("Period", 6)
        cacheLifeTime = self.getPluginParam("CacheLifeTime", 24)
        productions = self.getCachedProductions()
        # Check if the cache lifetime expired
        if "CacheTime" in productions and (now - productions["CacheTime"]) < timedelta(hours=cacheLifeTime):
            # If we haven't found productions for one of the processing passes, retry
            cacheOK = len([bkPath for bkPath in bkPathList if bkPath not in productions.get("List", {})]) == 0
        else:
            cacheOK = False

        if cacheOK:
            # Check if it's worth processing (i.e. "period" hours have passed
            if (
                transStatus != "Flush"
                and not self.getCachedTimeExceeded()
                and (now - productions[f"LastCall_{self.transID}"]) < timedelta(hours=period)
            ):
                self.logInfo(f"Skip this loop (less than {period} hours since last call)")
                return S_OK()
        else:
            productions.setdefault("List", {})
            self.logVerbose("Cache is being refreshed (lifetime %d hours)" % cacheLifeTime)
            for bkPath in bkPathList:
                bkQuery = BKQuery(bkPath, visible="All")
                bkQuery.setOption("EventType", eventType)
                bkQuery.setOption("ReplicaFlag", "All")
                prods = bkQuery.getBKProductions()
                if not prods:
                    self.logVerbose(f"For bkPath {bkPath}, found no productions, wait next time")
                    return S_OK()
                productions["List"][bkPath] = []
                for prod in prods:
                    res = self.transClient.getTransformation(prod)
                    if not res["OK"]:
                        self.logError(f"Error getting transformation {prod}", res["Message"])
                    else:
                        if res["Value"]["Status"] != "Cleaned":
                            productions["List"][bkPath].append(int(prod))
                self.logInfo(
                    "For bkPath %s, selected productions: %s"
                    % (bkPath, ",".join("%s" % prod for prod in productions["List"][bkPath]))
                )
            productions["CacheTime"] = now

        # Record time of last call and update the cache
        productions[f"LastCall_{self.transID}"] = now
        self.setCachedProductions(productions)
        # Return the list of BK paths (with their processing passes),
        #   the list of productions and the depth of current processing pass
        return S_OK((bkPathList, productions))

    # @timeThis
    def getFilesParam(self, lfns, param):
        """Return for each LFN the value of a single parameter "param" that can be
        cached."""
        # Make sure we request the same parameter
        if self.paramName and self.paramName != param:
            self.logWarn(
                "Requested parameter %s not compatible with previously used parameter %s, \
get from BK"
                % (param, self.paramName)
            )
            return self.getMetadataFromTSorBK(lfns, param)

        self.paramName = param
        lfns = set(lfns)
        if not self.filesParam:
            nCached = 0
            for run in self.cachedRunLfns:
                for paramValue in self.cachedRunLfns[run]:
                    for lfn in self.cachedRunLfns[run][paramValue]:
                        self.filesParam[lfn] = paramValue
                        nCached += 1
            self.logVerbose("Obtained %s of %d files from disk cache" % (param, nCached))
        filesParam = {lfn: self.filesParam[lfn] for lfn in lfns & set(self.filesParam)}
        # Get parameter for LFNs not cached yet
        lfns = lfns - set(filesParam)
        if lfns:
            resDict = self.getMetadataFromTSorBK(list(lfns), param)
            filesParam.update(resDict)
            self.filesParam.update(resDict)
            self.logVerbose(f"Obtained {param} of {len(resDict)} files from TS or BK")
        return filesParam

    def getStorageFreeSpace(self, candSEs):
        """Get free space in a list of SEs from the RSS."""
        weight = {}
        for se in candSEs:
            weight[se] = self.getRMFreeSpace(se)
        self.logVerbose(f"Free space from RSS: {weight}")
        return weight

    def getRMFreeSpace(self, se):
        """Get free space in an SE from the RSS."""

        isTape = StorageElement(se).status()["TapeSE"]
        # For tape space token, the SRM information is useless, set it fixed
        if isTape:
            return 1000.0

        cacheLimit = datetime.utcnow() - timedelta(hours=12)

        if se not in self.freeSpace or self.freeSpace[se]["LastCheckTime"] < cacheLimit:
            res = self.rmClient.selectSpaceTokenOccupancyCache(token=se)
            if not res["OK"] or not res["Value"]:
                self.logError(f"Error when getting space for SE {se}", res.get("Message", ("empty return")))
                return 0

            self.freeSpace[se] = dict(zip(res["Columns"], res["Value"][0]))

        # Return free space in TB as RSS returns in MB
        free = self.freeSpace[se]["Free"] / 1000000.0
        self.logDebug("Free space for SE %s: %d" % (se, free))
        return free

    def rankSEs(self, candSEs):
        """Ranks the SEs according to their free space."""
        if len(candSEs) <= 1:
            return candSEs
        # Weights should be obtained from the RSS or CS
        weightForSEs = self.getStorageFreeSpace(candSEs)
        rankedSEs = []
        while weightForSEs:
            if len(weightForSEs) == 1:
                se = list(weightForSEs)[0]
            else:
                weights = weightForSEs.copy()
                total = 0.0
                orderedSEs = []
                for se, weight in weights.items():  # can be an iterator
                    # Minimum space 1 GB in case all are 0
                    total += max(weight, 0.001)
                    weights[se] = total
                    orderedSEs.append(se)
                rand = random.uniform(0.0, total)
                self.logVerbose(f"List of ordered SEs (random number is {rand:.1f} out of {total:.1f})")
                for se in orderedSEs:
                    self.logVerbose(f"{se}: {weights[se]:.1f}")
                for se in orderedSEs:
                    if rand <= weights[se]:
                        break
            self.logVerbose(f"Selected SE is {se}")
            rankedSEs.append(se)
            weightForSEs.pop(se)
        return rankedSEs

    def _get_percent_usable_space_key(self, se_name: str, pending_tasks_per_se: dict[str, int] | None = None):
        if pending_tasks_per_se:
            return hashkey(se_name, *sorted(pending_tasks_per_se))
        return hashkey(se_name)

    @cached(TTLCache(maxsize=100, ttl=600), key=_get_percent_usable_space_key)
    def getPercentUsableSpace(self, se_name: str, pending_tasks_per_se: dict[str, int] | None = None):
        """Get percentage of usable space in an SE. It is meant to work
        for ARCHIVE, DST and MC-DST storages
        The units here are a bit funky:

        * pledges are in TBytes (because there are no computer scientists in WLCG)
        * current_occupancy for tape are MB
        * getOccupancy is in TiB (or MiB)

        #
        It does not really matter in the end, as it is just used for comparing
        storage to one another


        """
        se = StorageElement(se_name)
        is_tape = se.status()["TapeSE"]
        # Estimated size of the transfers still pending to the SE/Site
        pending_tasks_size = 0

        # Archive are a bit special as we can't measure the actual free space
        # So look at their maximum allowed occupancy
        # as well as the current occupency measured by DIRAC
        if "ARCHIVE" in se_name:
            current_occupancy, last_update = returnValueOrRaise(self.suClient.getSEUsage(se_name))
            # This is in bytes, so convert to MB
            current_occupancy /= 1_000_000
            if (datetime.utcnow() - last_update).days >= 1:
                self.logWarn("SE Occupancy not updated for too long", f"{se_name=}, {last_update=}")

            max_archive_occupancy = returnValueOrRaise(getShares("MaxArchiveOccupancy"))
            # These are in TB
            # convert in MB
            total_space = max_archive_occupancy[se_name] * 1_000_000

            if pending_tasks_per_se:
                pending_tasks_size = pending_tasks_per_se.get(se_name, 0) * 10_000
        elif not is_tape:

            se_site = returnValueOrRaise(self.dmsHelper.getSitesForSE(se_name))[0]
            # These contains maximum occupancy in TB
            max_dst_occupancy = returnValueOrRaise(getShares("MaxDSTOccupancy"))

            rss_occupancy = self.rmClient.selectSpaceTokenOccupancyCache(token=se_name)
            returnValueOrRaise(rss_occupancy)
            occupancy_dict = dict(zip(rss_occupancy["Columns"], rss_occupancy["Value"][0]))

            # If we define a limit in the Share, use it
            if se_site in max_dst_occupancy:
                self.logVerbose("Found MaxDSTOccupancy defined")
                total_space = max_dst_occupancy[se_site] * 1_000_000
            else:
                # These are already in MB
                total_space = occupancy_dict["Total"]
            current_occupancy = occupancy_dict["Total"] - occupancy_dict["Free"]

            # We now need to check whether there is a BUFFER storage at the site,
            # in which case we keep some margin
            site_buffer = returnValueOrRaise(self.dmsHelper.getSEInGroupAtSite("Tier1-Buffer", se_site))
            if site_buffer:
                self.logVerbose("Found buffer at site, keep 1PB margin")
                current_occupancy += convertSizeUnits(1, "PB", "MB")

            if pending_tasks_per_se:

                site_counters = Counter()
                for se, pending_tasks in pending_tasks_per_se.items():
                    if "DST" in se:
                        site_counters[returnValueOrRaise(self.dmsHelper.getSitesForSE(se))[0]] += pending_tasks
                # Add 10GB per assigned files to the current_occupancy
                pending_tasks_size = site_counters.get(se_site, 0) * 10_000

        else:
            raise ValueError(f"{se_name} cannot be ranked")

        if pending_tasks_size:
            self.logVerbose(f"Pending files for {se_name}, keep {pending_tasks_size}MB aside")

        percent_free = 1 - (current_occupancy + pending_tasks_size) / total_space
        # Keep some margin
        percent_free -= 0.05
        self.logVerbose(f"Free space for SE {se_name}:  {percent_free:.2f}")

        return max(0, percent_free)

    def rankPercentageSEs(self, candSEs, pendingTasksPerSE=None):
        """Ranks the SEs according to their percentage of free space."""
        if len(candSEs) <= 1:
            return candSEs
        weightForSEs = {}
        for se in candSEs:
            se_weight = self.getPercentUsableSpace(se, pending_tasks_per_se=pendingTasksPerSE)
            if se_weight:
                weightForSEs[se] = se_weight
        total_weight = sum(weightForSEs.values())

        normalized_weight = [weight / total_weight for weight in weightForSEs.values()]

        ranked_ses = self.rnd_generator.choice(
            list(weightForSEs.keys()), size=len(weightForSEs), replace=False, p=normalized_weight
        ).tolist()

        return ranked_ses

    def setTargetSEs(
        self,
        numberOfCopies,
        archiveSEs,
        mandatorySEs,
        secondarySEs,
        existingSEs,
        exclusiveSEs=False,
        pendingTasksPerSE=None,
    ):
        """Decide on which SEs to target from lists and current status of
        replication Policy is max one archive1, one archive 2, all mandatory SEs
        and required number of copies elsewhere."""
        # Select active SEs

        nbArchive = min(1, len(archiveSEs))
        secondaryActiveSEs = getActiveSEs(secondarySEs)

        targetSEs = []
        self.logVerbose(
            "Selecting SEs from %s, %s, %s (%d copies) for files in %s"
            % (archiveSEs, mandatorySEs, secondarySEs, numberOfCopies, existingSEs)
        )
        # Select archive SEs if any requested
        if nbArchive:
            allArchiveSEs = resolveSEGroup("Tier1-Archive")
            archiveExisting = [se for se in allArchiveSEs if se in existingSEs]
            archiveActiveSEs = getActiveSEs(archiveSEs)
            # If none found active, use all
            if not archiveActiveSEs:
                archiveActiveSEs = archiveSEs
            archiveActiveSEs = [se for se in archiveActiveSEs if se not in archiveExisting]
            # Set existing archive SEs first, then other archives (check against all archives)
            candidateSEs = self.selectSEs(
                archiveExisting + self.rankPercentageSEs(archiveActiveSEs, pendingTasksPerSE=pendingTasksPerSE),
                nbArchive,
                existingSEs,
            )
            self.logVerbose(f"Selected ArchiveSEs: {candidateSEs}")
            if len(candidateSEs) < nbArchive:
                self.logError("Cannot select enough archive SEs")
                return None
            targetSEs += candidateSEs

        # Now select the disk replicas
        # 1. add mandatory SEs
        candidateSEs = [se for se in mandatorySEs if not self.isSameSEInList(se, existingSEs)]
        # 2. add existing disk SEs that are either mandatory or secondary
        candidateSEs += [
            se
            for se in existingSEs
            if se in (mandatorySEs + secondarySEs)
            and not self.isSameSEInList(se, targetSEs + candidateSEs)
            and not isArchive(se)
        ]
        # 3. add ranked list of secondary SEs
        candidateSEs += [
            se
            for se in self.rankPercentageSEs(secondaryActiveSEs, pendingTasksPerSE=pendingTasksPerSE)
            if not self.isSameSEInList(se, targetSEs + candidateSEs + existingSEs)
        ]
        # 4. Select the proper number of SEs in the candidate ordered list
        candidateSEs = self.selectSEs(candidateSEs, numberOfCopies, existingSEs)
        self.logVerbose(f"Selected SecondarySEs: {candidateSEs}")
        if len(candidateSEs) < numberOfCopies:
            self.logError("Can not select enough Active SEs as SecondarySE")
            return None
        targetSEs += candidateSEs

        # Remove existing SEs if requested
        if exclusiveSEs:
            targetSEs = [se for se in targetSEs if se not in existingSEs]
        self.logVerbose(f"Selected target SEs: {targetSEs}")
        return ",".join(sorted(targetSEs))

    def selectSEs(self, candSEs, needToCopy, existingSEs):
        """Select SEs from a list, preferably from existing SEs in order to obtain
        the required number of replicas."""
        targetSEs = []
        # Put existing SEs first
        for se in [se for se in candSEs if se in existingSEs]:
            if needToCopy <= 0:
                break
            targetSEs.append(se)
            needToCopy -= 1
        # If more are needed, add them
        if needToCopy > 0:
            for se in [s for s in candSEs if s not in existingSEs]:
                if needToCopy <= 0:
                    break
                if not self.isSameSEInList(se, existingSEs):
                    targetSEs.append(se)
                    needToCopy -= 1
        return targetSEs

    def assignTargetToLfns(self, lfns, replicas, stringTargetSEs):
        """Assign target SEs for each LFN, excluding the existing ones Returns a
        dictionary for files to be transferred and a list of files already in
        place."""
        # Suppress duplicate SEs from list
        targetSEs = self.uniqueSEs([se for se in stringTargetSEs.split(",") if se])
        alreadyCompleted = []
        fileTargetSEs = {}
        for lfn in lfns:
            # At this stage, protection against Failover has been done
            existingSEs = replicas.get(lfn, [])
            if not existingSEs:
                self.logWarn("File found without replicas", lfn)
                continue
            # Discard existing SEs or SEs with similar description
            neededSEs = [se for se in targetSEs if not self.isSameSEInList(se, existingSEs)]
            if not neededSEs:
                alreadyCompleted.append(lfn)
            else:
                fileTargetSEs[lfn] = ",".join(sorted(neededSEs))
        return (fileTargetSEs, alreadyCompleted)

    # @timeThis
    def getProcessedFiles(self, lfns):
        """Check which files have been processed by a given production, i.e. have a
        meaningful descendant."""

        return getFileDescendents(self.transID, lfns, transClient=self.transClient, dm=self.dm, bkClient=self.bkClient)

    # @timeThis
    def getRAWAncestorsForRun(self, runID, param=None, paramValue=None, getFiles=False):
        """Determine from BK how many ancestors files from a given run we have.

        This is used for deciding when to flush a run (when all RAW files
        have been processed)
        """
        ancestorFiles = set()
        # The transformation files cannot be cached globally as they evolve at each cycle
        lfns = self.transRunFiles.get(runID, [])
        if not lfns:
            res = self.getTransformationFiles(runID=runID)
            if not res["OK"]:
                self.logError(f"Cannot get transformation files for run {str(runID)}: {res['Message']}")
                return 0
            lfns = [fileDict["LFN"] for fileDict in res["Value"] if fileDict["Status"] not in self.excludedStatuses]
            self.transRunFiles[runID] = lfns
            self.logVerbose("Obtained %d input files for run %d" % (len(lfns), runID))

        if not lfns:
            return 0

        # Restrict to files with the required parameter
        if param:
            paramValues = self.getFilesParam(lfns, param)
            lfns = [f for f, v in paramValues.items() if v == paramValue]  # can be an iterator

        if lfns:
            lfnToCheck = lfns[0]
        else:
            return 0
        #
        # If files are RAW files, no need to get the number of ancestors!
        #
        if self.usingRAWFiles is None:
            self.usingRAWFiles = self.getMetadataFromTSorBK(lfnToCheck, "FileType")[lfnToCheck] == "RAW"
        if self.usingRAWFiles:
            return len(lfns) if not getFiles else lfns
        #
        # Get number of ancestors for known files
        cachedLfns = self.cachedLFNAncestors.get(runID, {})
        # If we cached a number, clean the cache
        if cachedLfns and True in {isinstance(val, int) for val in cachedLfns.values()}:  # can be an iterator
            cachedLfns = {}
        setLfns = set(lfns)
        hitLfns = setLfns & set(cachedLfns)
        if hitLfns and not getFiles:
            self.logVerbose("Ancestors cache hit for run %d: %d files cached" % (runID, len(hitLfns)))
            for lfn in hitLfns:
                ancestorFiles.update(cachedLfns[lfn])
            lfns = setLfns - hitLfns

        # If some files are unknown, get the ancestors from BK
        if lfns:
            res = self.getFileAncestors(list(lfns))
            if res["OK"]:
                ancestorDict = res["Value"]["Successful"]
            else:
                self.logError(f"Error getting ancestors: {res['Message']}")
                ancestorDict = {}
            for lfn in ancestorDict:
                ancFiles = {os.path.basename(f["FileName"]) for f in ancestorDict[lfn] if f["FileType"] == "RAW"}
                ancestorFiles.update(ancFiles)
                self.cachedLFNAncestors.setdefault(runID, {})[lfn] = ancFiles

        if getFiles:
            return ancestorFiles
        notProcessed = self.__getNotProcessedAncestors(runID, lfnToCheck)
        ancestors = len(ancestorFiles)
        if notProcessed:
            self.logVerbose("Found %d files not processed for run %d" % (notProcessed, runID))
            ancestors += notProcessed
        self.logVerbose("found %d for run %d" % (ancestors, runID))
        return ancestors

    def __getNotProcessedAncestors(self, runID, lfnToCheck):
        """returns the number of RAW ancestor files that were not processed by the
        reconstruction production This is necessary only if that produciton is not
        processing all files, but in the doubt we check it."""
        if runID in self.notProcessed or not lfnToCheck:
            return self.notProcessed.get(runID, 0)
        ancestorFullDST = None
        recoProduction = None
        notProcessed = 0
        if not self.__recoType:
            self.__recoType = self.getPluginParam("RecoFileType", ["FULL.DST"])
        # Check if the file itself is a FULL.DST
        res = self.bkClient.getFileMetadata(lfnToCheck)
        if res["OK"]:
            if res["Value"]["Successful"].get(lfnToCheck, {}).get("FileType") in self.__recoType:
                ancestorFullDST = lfnToCheck
            else:
                # If not, get its ancestors
                res = self.getFileAncestors(lfnToCheck, replica=False)
                if res["OK"]:
                    fullDst = [
                        f["FileName"]
                        for f in res["Value"]["Successful"].get(lfnToCheck, [{}])
                        if f.get("FileType") in self.__recoType
                    ]
                    if fullDst:
                        ancestorFullDST = fullDst[0]
                else:
                    self.logError(f"Error getting ancestors of {lfnToCheck}", res["Message"])
        if ancestorFullDST:
            self.logDebug(f"Ancestor {self.__recoType} found: {ancestorFullDST}")
            res = self.bkClient.getJobInfo(ancestorFullDST)
            if res["OK"]:
                try:
                    recoProduction = res["Value"][0][18]
                    self.logVerbose("Reconstruction production is %d" % recoProduction)
                except IndexError as e:
                    self.logException(f"Exception extracting reco production from {str(res['Value'])}", lException=e)
                    recoProduction = None
            else:
                self.logError("Error getting job information", res["Message"])
        else:
            self.logVerbose(f"No ancestor {self.__recoType} file found")
        if recoProduction:
            res = self.transClient.getTransformationFiles({"TransformationID": recoProduction, "RunNumber": runID})
            if res["OK"]:
                notProcessed = len([fileDict for fileDict in res["Value"] if fileDict["Status"] == "NotProcessed"])
        self.notProcessed[runID] = notProcessed
        return notProcessed

    # @timeThis
    def getTransformationFiles(self, runID):
        return self.transClient.getTransformationFiles({"TransformationID": self.transID, "RunNumber": runID})

    # @timeThis
    def getFileAncestors(self, lfns, depth=10, replica=True):
        return self.bkClient.getFileAncestors(lfns, depth=depth, replica=replica)

    def checkAncestorsAtSE(self, taskLfns, seList):
        """Check if ancestors of a list of files are present at a set of SEs.

        :param list taskLfns: list of lfn lists for all tasks
        :param list seList: list of SEs to consider

        :return int missingAtSEs: number of files that are not at the specified SEs
        """
        # We request also that ancestors are at the fromSEs
        lfns = [lfn for lfnList in taskLfns for lfn in lfnList]
        nbLfns = len(lfns)
        ancestors = self.getFileAncestors(lfns, depth=1, replica=True)
        if not ancestors["OK"]:
            self.logError("Error getting ancestors", ancestors["Message"])
            return _clearTaskLFNs(taskLfns)
        ancestors = ancestors["Value"]["Successful"]
        ancLfns = [anc["FileName"] for ancList in ancestors.values() for anc in ancList]  # can be an iterator
        self.logVerbose(f"Checking ancestors presence at {','.join(sorted(seList))} for {len(ancLfns)} files")
        res = self.dm.getReplicasForJobs(ancLfns, getUrl=False)
        if not res["OK"]:
            self.logError("Error getting replicas of ancestors", res["Message"])
            # Fake no replicas for all files
            return _clearTaskLFNs(taskLfns)
        success = res["Value"]["Successful"]
        for lfn, ancList in ancestors.items():  # can be an iterator
            for anc in ancList:
                # Note: it may happen that an ancestor has no active replica
                if not seList & set(success.get(anc["FileName"], set())):
                    # Remove the LFN from the list of lists
                    for lfnList in taskLfns:
                        if lfn in lfnList:
                            lfnList.remove(lfn)
        missingAtSEs = nbLfns - len([lfn for lfnList in taskLfns for lfn in lfnList])
        if missingAtSEs:
            self.logVerbose("%d ancestor files found not to be at %s" % (missingAtSEs, ",".join(sorted(seList))))
        return missingAtSEs

    # @timeThis
    def getTransformationRuns(self, runs=None, transID=None, insertMissingRuns: bool = True):
        """get the run table for a list of runs, if missing, add them.

        :param (list,tuple,dict,set,int,long): iterable with run numbers or single run number
        :param int transID: transformation ID. If not speficied, use the current ID
        :param insertMissingRuns: if True and some runs aren't in the table, insert them

        :return S_OK / S_ERROR: value is the list of run dictionaries
        """
        if transID is None:
            transID = self.transID
        condDict = {"TransformationID": transID}
        if isinstance(runs, (dict, list, tuple, set)):
            condDict["RunNumber"] = list(runs)
        elif isinstance(runs, int):
            runs = [runs]
            condDict["RunNumber"] = runs
        result = self.transClient.getTransformationRuns(condDict)
        if not result["OK"]:
            return result
        # Check that all runs are there, if not add them
        runsFound = {run["RunNumber"] for run in result["Value"]}
        if runs:
            missingRuns = set(runs) - runsFound
            if missingRuns and insertMissingRuns:
                self.logInfo(
                    "Add missing runs in transformation runs table: %s"
                    % ",".join(str(run) for run in sorted(missingRuns))
                )
                for runID in missingRuns:
                    res = self.transClient.insertTransformationRun(transID, runID, "")
                    if not res["OK"]:
                        return res
                result = self.transClient.getTransformationRuns(condDict)
        return result

    def getFilesGroupedByParam(self, param, lfns=None):
        """Group LFNs by a parameter e.g. FileType."""
        fileTypeDict = defaultdict(list)
        # no need to query the BK as we have the answer from files
        if lfns is None:
            lfns = [f["LFN"] for f in self.transFiles]
        self.logVerbose(
            "Starting getFilesGroupedByParam for %d files, %s" % (len(lfns), "by %s" % param if param else "no param")
        )

        resDict = self.getFilesParam(lfns, param)
        for lfn, paramValue in resDict.items():  # can be an iterator
            fileTypeDict[paramValue].append(lfn)
        return dict(fileTypeDict)

    # @timeThis
    def getFilesGroupedByRunAndParam(self, lfns=None, param=""):
        """Group files by run and another BK parameter (e.g. file type or event
        type)"""
        runDict = {}
        # no need to query the BK as we have the answer from files
        if lfns is None:
            files = self.transFiles
        else:
            files = [fileDict for fileDict in self.transFiles if fileDict["LFN"] in lfns]
        self.logVerbose(
            "Starting getFilesGroupedByRunAndParam for %d files, %s"
            % (len(files), "by %s" % param if param else "no param")
        )
        runGroups = groupByRun(files)
        for runNumber, runLFNs in runGroups.items():  # can be an iterator
            if not param:
                runDict[runNumber] = {None: runLFNs}
            else:
                runDict[runNumber] = self.getFilesGroupedByParam(param=param, lfns=runLFNs)

        # If necessary fix files with run number 0
        zeroRunDict = runDict.pop(0, None)
        if zeroRunDict:
            nZero = 0
            for paramValue, zeroRun in zeroRunDict.items():  # can be an iterator
                newRuns = self.setRunForFiles(zeroRun)
                for newRun, runLFNs in newRuns.items():  # can be an iterator
                    runDict.setdefault(newRun, {}).setdefault(paramValue, []).extend(runLFNs)
                    nZero += len(runLFNs)
            self.logInfo("Set run number for %d files with run #0, which means it was not set yet" % nZero)

        if param:
            self.logVerbose(f"Grouped {len(files)} files by run and {param}")
        return runDict

    def getFilesGroupedByRun(self, lfns=None):
        """Get files per run in a dictionary and set the run number if not done."""
        # Split the files in run groups
        if lfns is None:
            files = self.transFiles
        else:
            files = [fileDict for fileDict in self.transFiles if fileDict["LFN"] in lfns]
        runGroups = groupByRun(files)
        if not runGroups:
            # No files, no tasks!
            self.logVerbose("No runs found!")
            return []

        # If some files don't have a run number, get it and set it
        zeroRun = runGroups.pop(0, None)
        if zeroRun:
            nZero = 0
            newRuns = self.setRunForFiles(zeroRun)
            for newRun, runLFNs in newRuns.items():  # can be an iterator
                runGroups.setdefault(newRun, []).extend(runLFNs)
                nZero += len(runLFNs)
            self.logInfo("Set run number for %d files with run #0, which means it was not set yet" % nZero)
        self.logVerbose(f"Obtained {len(runGroups)} runs")
        return runGroups

    def createTasks(self, storageElementGroups, chunkSize=None):
        """Create reasonable size tasks."""
        tasks = []
        if not chunkSize:
            chunkSize = self.getPluginParam("MaxFilesPerTask", 100)
        for stringTargetSEs in sorted(storageElementGroups):
            stringTargetLFNs = storageElementGroups[stringTargetSEs]
            for lfnGroup in breakListIntoChunks(sorted(stringTargetLFNs), chunkSize):
                tasks.append((stringTargetSEs, lfnGroup))
        self.logVerbose(f"{len(tasks)} tasks created")
        return tasks

    def readCacheFile(self, workDirectory):
        """Utility function."""

        # Now try and get the cached information
        tmpDir = os.environ.get("TMPDIR", "/tmp")
        cacheFiles = (
            (workDirectory, ("TransPluginCache",)),
            (
                tmpDir,
                (
                    "dirac",
                    "TransPluginCache",
                ),
            ),
        )
        for cacheFile, prefixes in cacheFiles:
            if not cacheFile:
                continue
            for node in prefixes:
                cacheFile = os.path.join(cacheFile, node)
                mkDir(cacheFile)
            cacheFile = os.path.join(cacheFile, f"Transformation_{str(self.transID)}.pkl")
            if not self.cacheFile:
                self.cacheFile = cacheFile
            try:
                with open(cacheFile, "rb") as cacheFile_o:
                    self.cachedLFNAncestors = pickle.load(cacheFile_o)
                    # Do not cache between cycles, only cache temporarily,
                    #  but keep same structure in file, i.e. fake load
                    _cachedNbRAWFiles = pickle.load(cacheFile_o)
                    _cachedLFNSize = pickle.load(cacheFile_o)
                    self.cachedRunLfns = pickle.load(cacheFile_o)
                    self.cachedProductions = pickle.load(cacheFile_o)
                    self.cachedLastRun = pickle.load(cacheFile_o)
                    self.cachedLFNProcessedPath = pickle.load(cacheFile_o)
                    self.lastCall = pickle.load(cacheFile_o)
                self.logVerbose(f"Cache file {cacheFile} successfully loaded")
                # print '*****'
                # print '\n'.join( ['%s %s' % ( key, val ) for key, val in self.cachedLFNProcessedPath.items()] )
                break
            except (OSError, LookupError, pickle.UnpicklingError, EOFError) as e:
                self.logException("Cache file could not be loaded", cacheFile, lException=e)

    def getCachedRunLFNs(self, runID, paramValue):
        """Keep track of all files for a given parameter value."""
        return set(self.cachedRunLfns.get(runID, {}).get(paramValue, []))

    def setCachedRunLfns(self, runID, paramValue, lfnList):
        """Cache the list of LFNs for a given parameter value."""
        self.cachedRunLfns.setdefault(runID, {})[paramValue] = lfnList

    def getCachedProductions(self):
        return self.cachedProductions

    def setCachedProductions(self, productions):
        self.cachedProductions = productions

    def getCachedLastRun(self):
        return self.cachedLastRun

    def setCachedLastRun(self, lastRun):
        self.cachedLastRun = lastRun

    def cacheExpired(self, runID):
        if runID not in self.__runExpired:
            self.__runExpired[runID] = random.uniform(0.0, 1.0) > self.cacheHitFrequency
        return self.__runExpired[runID]

    # @timeThis
    def getNbRAWInRun(self, runID, evtType):
        """Get the number of RAW files in a run."""
        # Every now and then refresh the cache
        rawFiles = self.cachedNbRAWFiles.get(runID, {}).get(evtType)
        if not rawFiles:
            res = self.bkClient.getNbOfRawFiles({"RunNumber": runID, "EventTypeId": evtType, "Finished": "Y"})
            if not res["OK"]:
                self.logError("Cannot get number of RAW files for run %d, evttype %d" % (runID, evtType))
                return 0
            rawFiles = res["Value"]
            self.cachedNbRAWFiles.setdefault(runID, {})[evtType] = rawFiles
            if rawFiles:
                self.logVerbose("Run %d has %d RAW files" % (runID, rawFiles))
            else:
                self.logVerbose("Run %d is not finished yet" % runID)
        return rawFiles

    def writeCacheFile(self):
        """Utility function."""

        if self.cacheFile:
            try:
                with open(self.cacheFile, "wb") as cacheFile_o:
                    pickle.dump(self.cachedLFNAncestors, cacheFile_o)
                    pickle.dump(self.cachedNbRAWFiles, cacheFile_o)
                    pickle.dump(self.cachedLFNSize, cacheFile_o)
                    pickle.dump(self.cachedRunLfns, cacheFile_o)
                    pickle.dump(self.cachedProductions, cacheFile_o)
                    pickle.dump(self.cachedLastRun, cacheFile_o)
                    pickle.dump(self.cachedLFNProcessedPath, cacheFile_o)
                    pickle.dump(self.lastCall, cacheFile_o)
                self.logVerbose(f"Cache file {self.cacheFile} successfully written")
            except Exception as e:
                self.logException("Could not write cache file", self.cacheFile, lException=e)

    def setRunForFiles(self, lfns):
        """For files that are missing the run number, set it from BK."""
        res = self.bkClient.getFileMetadata(lfns)
        runFiles = {}
        if res["OK"]:
            for lfn, metadata in res["Value"]["Successful"].items():  # can be an iterator
                runFiles.setdefault(metadata["RunNumber"], []).append(lfn)
            for run in sorted(runFiles):
                if not run:
                    self.logInfo(
                        "%d files found with void run '%s': \n%s"
                        % (len(runFiles[run]), str(run), "\n".join(runFiles[run]))
                    )
                    runFiles.pop(run)
                    continue
                res = self.transClient.addTransformationRunFiles(self.transID, run, runFiles[run])
                # print run, runFiles[run], res
                if not res["OK"]:
                    self.logError(
                        "Error setting files to run",
                        " - %d files to run %d: %s" % (len(runFiles[run]), run, res["Message"]),
                    )
                    runFiles.pop(run)
        else:
            self.logError(f"Error getting metadata for {len(lfns)} files", res["Message"])
        return runFiles

    def getTransQuery(self, transReplicas):
        """Get BK query for the current transformation."""
        res = self.transClient.getBookkeepingQuery(self.transID)
        if not res["OK"]:
            self.logError("Failed to get BK query for transformation", res["Message"])
            transQuery = {}
        else:
            transQuery = res["Value"]
        if "ProcessingPass" not in transQuery:
            # Get processing pass of the first file... This assumes all have the same...
            lfn = list(transReplicas)[0]
            res = self.bkClient.getDirectoryMetadata(lfn)
            if not res["OK"]:
                self.logError("Error getting directory metadata", res["Message"])
                return None
            transQuery = res["Value"]["Successful"].get(lfn, [{}])[0]
            # Strip off most of it
            for key in ("FileType", "Production"):
                transQuery.pop(key, None)
        return transQuery

    def cleanFiles(self, transFiles, transReplicas, status=None):
        """Remove from transFiles all files without a replica and set their
        status."""
        noReplicaFiles = []
        for fileDict in list(transFiles):
            if fileDict["LFN"] not in transReplicas:
                noReplicaFiles.append(fileDict["LFN"])
                transFiles.remove(fileDict)
        if noReplicaFiles:
            if status is None:
                status = "Problematic" if self.plugin not in getRemovalPlugins() else "Processed"
            info = "without replicas" if status == "Problematic" else "already processed"
            res = self.transClient.setFileStatusForTransformation(self.transID, status, noReplicaFiles)
            if not res["OK"]:
                self.logError(f"Error setting file status for {len(noReplicaFiles)} files", res["Message"])
            else:
                self.logInfo(f"Found {len(noReplicaFiles)} files {info}, status set to {status}")

    def __getRunDestinations(self, runIDList):
        """Get the site destination for a set of runs and cache this information in
        memory."""

        runSet = set(runIDList) - set(self.runDestinations)
        if runSet:
            # Try and get a run destination from TS
            res = self.transClient.getAllDestinationForRuns(list(runSet))

            if res["OK"]:
                dest = res["Value"]
                if dest:
                    if isinstance(dest, list):
                        dest = dict(dest)
                    # run_destinations is [destination,RAWDestination]
                    for runID, run_destinations in dest.items():

                        self.runDestinations[runID] = run_destinations

    def getSEForDestination(self, runID, targets, rawDestination=False):
        """for a given run, get the information on destination SE from within a
        list of SEs.
        If RAW is True, lookup the RAW destination instead of the processing destination"""
        self.__getRunDestinations([runID])
        destSite, rawSite = self.runDestinations.get(runID, [None, None])
        site = rawSite if rawDestination else destSite
        if site:
            self.logVerbose("Destination found for run %d: %s" % (runID, site))
            # Avoid spurious warning if no match found
            savedLevel = gLogger.getLevel()
            gLogger.setLevel("ERROR")
            res = self.dmsHelper.getSEInGroupAtSite(targets, site)
            gLogger.setLevel(savedLevel)
            return res.get("Value")
        return None

    def _selectProcessedFiles(self, lfns, prodList):
        """
        Select only the files that are not in a status other than Processed in a list of productions
        Beware: this is not the same as Processed files as some files may not be in any production
                because they are intermediate files
        """
        startTime = time.time()
        res = self.transClient.getTransformationFiles({"LFN": list(lfns), "TransformationID": prodList})
        if not res["OK"]:
            self.logError("Error getting transformation files", res["Message"])
            return {}
        fDictList = res["Value"]
        unProcessedLfns = {fDict["LFN"] for fDict in fDictList if fDict["Status"] != "Processed"}
        procLfns = lfns - unProcessedLfns
        prodLfns = {}
        processedLfns = set()
        for fDict in fDictList:
            lfn = fDict["LFN"]
            if lfn in procLfns:
                processedLfns.add(lfn)
                prodLfns.setdefault(fDict["TransformationID"], []).append(lfn)
        # This is for files that are not in any production, accept them by default
        notInProdLfns = procLfns - processedLfns
        if notInProdLfns:
            processedLfns = procLfns
            for prod in prodList:
                prodLfns.setdefault(prod, []).extend(list(notInProdLfns))

        if len(processedLfns) != len(lfns):
            self.logVerbose(
                "Reduce files from %d to %d "
                "(removing non-processed files) in %.1f s" % (len(lfns), len(processedLfns), time.time() - startTime)
            )
        return prodLfns

    def __getChunkSize(self):
        """Cache the chunk size."""
        if self.chunkForFileDescendants is None:
            self.chunkForFileDescendants = self.getPluginParam("MaxFilesToGetDescendants", 100)
        return self.chunkForFileDescendants

    def checkForDescendants(self, lfnSet, prodList, depth=0):
        """check if the files have an existing descendant in the list of
        productions."""
        finalResult = set()
        if not lfnSet or not prodList:
            return S_OK(finalResult)
        self.logVerbose(
            "Checking descendants for %d files in productions %s, depth %d"
            % (len(lfnSet), ",".join(str(prod) for prod in prodList), depth)
        )
        excludeTypes = ("LOG", "BRUNELHIST", "DAVINCIHIST", "GAUSSHIST", "HIST", "INDEX.ROOT")
        if isinstance(lfnSet, str):
            lfnSet = {lfnSet}
        elif isinstance(lfnSet, list):
            lfnSet = set(lfnSet)
        # Select files that have been processed in one of the productions,
        #   and return the list of these prods
        prodLfns = self._selectProcessedFiles(lfnSet, prodList)
        if not prodLfns:
            return S_OK(finalResult)
        # Get daughters of processed files in each production
        success = {}
        descProd = {}
        chunkSize = self.__getChunkSize()
        for prod, lfns in prodLfns.items():  # can be an iterator
            progressBar = ProgressBar(
                len(lfns),
                title="Getting descendants for %d files in production %d" % (len(lfns), prod),
                chunk=chunkSize,
                interactive=sys.stdout.isatty(),
                log=self.logVerbose,
            )
            for lfnChunk in breakListIntoChunks(lfns, chunkSize):
                progressBar.loop()
                # prod is a long and server expects an int!
                res = self.bkClient.getFileDescendents(lfnChunk, depth=1, production=int(prod), checkreplica=False)
                if not res["OK"]:
                    return res
                for lfn, descDict in res["Value"]["WithMetadata"].items():  # can be an iterator
                    # Only keep the file type as metadata in teh dict
                    success.setdefault(lfn, {}).update(
                        {
                            desc: {"FileType": metadata["FileType"], "GotReplica": metadata["GotReplica"]}
                            for desc, metadata in descDict.items()  # can be an iterator
                            if metadata["FileType"] not in excludeTypes
                        }
                    )
                    # Record information about which production created each descendant
                    for desc in descDict:
                        descProd[desc] = prod
            progressBar.endLoop()

        # Get set of file types
        fileTypes = sorted(
            {metadata["FileType"] for descendants in success.values() for metadata in descendants.values()}
        )  # can be an iterator
        self.logVerbose(f"Will check file type{'s' if len(fileTypes) > 1 else ''} {','.join(fileTypes)}")

        # Try and find descendants for each file type in turn as this is sufficient
        for fileType in fileTypes:
            # Invert list of descendants: descToCheck has descendant as key and list of parents
            descToCheck = {}
            descMetadata = {}
            for lfn, descendants in success.items():  # can be an iterator
                if lfn not in finalResult:
                    descMetadata.update(descendants)
                    for desc, metadata in descendants.items():  # can be an iterator
                        if metadata["FileType"] == fileType:
                            descToCheck.setdefault(desc, set()).add(lfn)
            if not descToCheck:
                break

            prodDesc = {}
            # Check if we found a descendant in the requested productions
            foundProds = {}
            for desc in list(descToCheck):  # pylint: disable=consider-iterating-dictionary
                prod = descProd[desc]
                # If we found an existing descendant in the list of productions, all OK
                if descMetadata[desc]["GotReplica"] == "Yes" and prod in prodList:
                    foundProds.setdefault(prod, set()).update(descToCheck[desc])
                    finalResult.update(descToCheck[desc])
                    del descToCheck[desc]
                else:
                    # Sort remaining descendants in productions
                    prodDesc.setdefault(prod, set()).add(desc)
            for prod, found in foundProds.items():
                self.logVerbose(
                    "Found %s descendants with replicas for %d files (out of %d) in production %d at depth %d"
                    % (fileType, len(found), len(lfnSet), prod, depth + 1)
                )

            # Check descendants without replicas in reverse order of productions
            for prod in sorted(prodDesc, reverse=True):
                # Check descendants whose parent was not yet found processed
                toCheckInProd = {desc for desc in prodDesc[prod] if not descToCheck[desc] & finalResult}
                if toCheckInProd:
                    self.logVerbose(
                        "Found %d %s descendants without replicas in production %d at depth %d,"
                        " check them for descendants" % (len(toCheckInProd), fileType, prod, depth + 1)
                    )
                    res = self.checkForDescendants(toCheckInProd, prodList, depth=depth + 1)
                    if not res["OK"]:
                        return res
                    foundInProd = set()
                    for desc in res["Value"]:
                        foundInProd.update(descToCheck[desc])
                    if foundInProd:
                        self.logVerbose(
                            "Found %s descendants of %d files at depth %d" % (fileType, len(foundInProd), depth + 2)
                        )
                        finalResult.update(foundInProd)

        return S_OK(finalResult)

    def __getStorageUsage(self, dirList, seList):
        """Get from StorageUsage the actual number of files for a list of
        directories at a list of SEs."""
        suClient = StorageUsageClient()
        result = {}
        if isinstance(seList, (dict, set, tuple)):
            seList = list(seList)
        self.logVerbose("Get storage usage for directories", ",".join(dirList))
        for dirName in dirList:
            res = suClient.getStorageSummary(dirName, None, None, seList)
            if not res["OK"]:
                return res
            for se, stat in res["Value"].items():  # can be an iterator
                result[se] = result.setdefault(se, 0) + stat["Files"]
        return S_OK(result)

    def _countRecentFiles(self, recentFiles, status, destSEs, dirList, delay):
        """Get files in a given status, and count how many are targeted for SEs in
        a list with a lastUpdate more recent than 'delay' hours."""
        self.logDebug(
            "Getting %s files in dir %s at %s in last %d hours" % (status, ",".join(dirList), ",".join(destSEs), delay)
        )
        condDict = {"TransformationID": self.transID, "Status": status}
        res = self.transClient.getTransformationFiles(condDict)
        if not res["OK"]:
            return res
        limitTime = datetime.now() - timedelta(hours=delay)
        for fileDict in res["Value"]:
            dirName = stripDirectory(fileDict["LFN"])
            usedSE = fileDict["UsedSE"]
            if dirName in dirList and usedSE in destSEs and (not delay or fileDict["LastUpdate"] > limitTime):
                recentFiles[usedSE] += 1
        self.printShares(
            "Number of files %s in transformation %s (%d hours):" % (status, condDict["TransformationID"], delay),
            recentFiles,
            counters=[],
            log=self.logDebug,
        )
        return S_OK()

    def __getMaxFilesAtSE(self, targetFilesAtDestination, directories, destSEs):
        """Get the number of files already present at SEs for a list of LFN
        directories Using the processing and RAW distribution shares, split the
        maximum number of files to be staged on these SEs and return the number of
        files that can possibly be added."""
        # We strip off the directory to a default depth of 4 as we ignore the production
        dirList = stripDirectory(directories)
        # Add possibility to throttle the frequency of the plugin, but not clear if this is useful
        period = self.getPluginParam("Period", 0)
        now = datetime.utcnow()
        if self.lastCall and (now - self.lastCall) < timedelta(hours=period):
            self.logInfo(f"Skip this loop (less than {period} hours since last call)")
            return S_OK(None)
        self.lastCall = now
        self.writeCacheFile()
        self.logVerbose(
            f"Checking how many files can be sent to {','.join(destSEs)}\n\t for directories {','.join(dirList)}"
        )

        # Get current storage usage per SE
        storageUsage = self.__getStorageUsage(dirList, destSEs)
        if not storageUsage["OK"]:
            return storageUsage
        storageUsage = storageUsage["Value"]
        self.printShares("Current storage usage per SE:", storageUsage, counters=[], log=self.logVerbose)

        # Get the shares (including processing fraction) at each site (from RAW SEs)
        rawShares = self.getPluginShares(section="CPUforRAW", backupSE="CERN-RAW", log=self.logDebug, counters=False)
        if not rawShares["OK"]:
            return rawShares
        # Turn a RAW share into a share on selected SEs
        shares = {}
        for rawSE, share in rawShares["Value"][1].items():  # can be an iterator
            selectedSEs = self.closerSEs([rawSE], destSEs, local=True)
            if selectedSEs:
                share *= targetFilesAtDestination / 100.0
                shares[selectedSEs[0]] = share

        self.printShares(
            "Shares per SE for %d files:" % targetFilesAtDestination, shares, counters=[], log=self.logVerbose
        )

        recentFiles = dict.fromkeys(destSEs, 0)
        # Get the number of files already assigned for each SE, as it should be substracted from possible number
        res = self._countRecentFiles(recentFiles, "Assigned", destSEs, dirList, 0)
        if not res["OK"]:
            return res

        # Get the number of files Processed in the last 12 hours
        delay = 12
        res = self._countRecentFiles(recentFiles, "Processed", destSEs, dirList, delay)
        if not res["OK"]:
            return res
        self.printShares(
            "Number of files Assigned or recently Processed (%d hours):" % delay,
            recentFiles,
            counters=[],
            log=self.logVerbose,
        )

        # Share targetFilesAtDestination on the SEs taking into account current usage
        maxFilesAtSE = {}
        for se, share in shares.items():  # can be an iterator
            maxFilesAtSE[se] = max(0, int(share - storageUsage.get(se, 0) - recentFiles.get(se, 0)))
        self.printShares("Maximum number of files per SE:", maxFilesAtSE, counters=[], log=self.logInfo)
        return S_OK(maxFilesAtSE)

    def getMaxFilesToReplicate(self, workDirectory):
        """Get the watermark and max files per SE if defined The keys of
        maxFilesAtSE are the destination SEs If plugin should just return, set
        watermark to None."""
        destSEs = set(resolveSEGroup(self.getPluginParam("DestinationSEs", [])))
        maxFilesAtSE = dict.fromkeys(destSEs, sys.maxsize)
        if not destSEs:
            self.logWarn("No destination SE given")
            return S_OK((None, maxFilesAtSE))
        # Check if destination is tape; no throttling is required
        allTapeSEs = all(StorageElement(se).status()["TapeSE"] for se in destSEs)
        if allTapeSEs:
            self.logVerbose("All SEs are on tape: no throttling")
            return S_OK((0, maxFilesAtSE))
        watermark = self.getPluginParam("MinFreeSpace", 30)
        targetFilesAtDestination = self.getPluginParam("TargetFilesAtDestination", 0)

        # if there is a maximum number of files to get at destination, get the current usage
        if targetFilesAtDestination:
            self.readCacheFile(workDirectory)
            # Directories limited to the top 4 directories
            directories = stripDirectory(self.transReplicas)
            # Get the maximum number of files that are allowed to be copied at this round (for prestaging mainly)
            result = self.__getMaxFilesAtSE(targetFilesAtDestination, directories, destSEs)
            if not result["OK"]:
                return result
            # This happens when the cycle is to be skipped, then return None
            if not result["Value"]:
                watermark = None
            # Update dictionary
            maxFilesAtSE.update(result["Value"])
        return S_OK((watermark, maxFilesAtSE))

    def _getFileSize(self, lfns):
        """Overwrite the DIRAC method and get the file size from the TS tables."""
        return S_OK(self.getMetadataFromTSorBK(lfns, "FileSize"))

    def checkCondDBRunTick(self, runID):
        """Check for the presence of the run tick in the ConDB."""
        if not self.onlineCondDB:
            self.onlineCondDB = self.getPluginParam(
                "OnlineCondDB", "/cvmfs/lhcb.cern.ch/lib/lhcb/git-conddb/ONLINE.git"
            )

        if not os.path.exists(self.onlineCondDB):
            self.logWarn("OnlineCondDB not found", self.onlineCondDB)
            return None
        cmd = "git --git-dir %s  grep -q '^%d$' HEAD -- Conditions/Online/valid_runs.txt" % (
            self.onlineCondDB,
            int(runID),
        )
        retCode = os.system(cmd)
        return not bool(retCode)

    def checkRun3CondDB(self, runID: int) -> bool:
        """Check for the presence of the run in the Run3 CondDB"""
        if not self.run3CondDB:
            self.run3CondDB = Path(
                self.getPluginParam("Run3CondDB", "/cvmfs/lhcb-condb.cern.ch/git-conddb/lhcb-conditions-database.git/")
            )

        if not self.run3CondDB.exists():
            self.logWarn("Run3CondDB not found", self.run3CondDB)
            return None

        # We are sure this file to always exist for each run because it
        # contains the readout configuration
        cmd = [
            "git",
            "--git-dir",
            self.run3CondDB,
            "ls-tree",
            "--name-only",
            "master",
        ]

        # The runs are batched in groups of 1000
        filename = f"Conditions/LHCb/Online/Tell40Links.yml/{runID // 1000}000/{runID}"
        ret = subprocess.run(cmd + [filename], capture_output=True, text=True)
        if str(runID) in ret.stdout:
            return True

        # Before lhcb-conditions-database!51 the runs weren't partitioned
        filename = f"Conditions/LHCb/Online/Tell40Links.yml/{runID}"
        ret = subprocess.run(cmd + [filename], capture_output=True, text=True)
        return str(runID) in ret.stdout

    def getPendingTasks(self, transType):
        """Get the number of tasks/files not yet running for each TargetSE as a dictionary"""

        # First check the cycling period
        now = datetime.utcnow()
        period = self.getPluginParam("Period", 6)
        if self.lastCall and (now - self.lastCall) < timedelta(hours=period):
            self.logInfo(f"Skip this loop (less than {period} hours since last call)")
            return S_OK(None)
        self.lastCall = now
        self.writeCacheFile()

        res = self.transClient.getTransformations({"Type": transType, "Status": "Active"})
        if not res["OK"]:
            return res
        transList = [td["TransformationID"] for td in res["Value"]]
        cond = {"TransformationID": transList}
        if transType in ("Replication", "Removal"):
            # For DMS transformations, count number of Assigned files
            transTable = "Files"
            cond["Status"] = "Assigned"
            item = "UsedSE"
        else:
            # For WMS productions, count the number of tasks not yet Running
            transTable = "Tasks"
            cond["ExternalStatus"] = ["Waiting", "Received", "Checking", "Created", "Staging", "Submitted"]
            item = "TargetSE"
        self.logVerbose(f"Get number of {transTable} by {item}", f"for {transType} transformations {str(transList)}")
        res = self.transClient.getCounters(f"Transformation{transTable}", [item], cond)
        if not res["OK"]:
            return res
        # Count number of pending tasks as TargetSE can be multiple
        pendingTasksPerSE = defaultdict(int)
        for dd, count in res["Value"]:
            for se in dd[item].split(","):
                pendingTasksPerSE[se] += count
        self.logVerbose("Pending tasks at TargetSEs", str(dict(pendingTasksPerSE)))
        return S_OK(pendingTasksPerSE)

    def throttleFiles(self, candidateSEs, pendingTasksPerSE, throttleLimit):
        """
        Remove all files in excess to throttleLimit at SEs

        I have tested this new throttling feature extensively with a set of real files and the dirac-test-plugin script.

        It will be useful in the following circumstances:

        Staging: one can put a large run range and let the system create requests by batches of e.g. 5000 files per SE
        Stripping: similarly one can launch productions with a whole range and set the throttling limit to 5000
        Large removals from disk: in order to not overload the RMS, one can create removals by few 1000's per SE
        """
        removedFiles = defaultdict(int)
        self.logVerbose("Throttle files", "to %d per SE for SEs %s" % (throttleLimit, sorted(candidateSEs)))
        acceptedRuns = set()
        suppressedRuns = set()
        # Loop on files, sorted by run number
        for fileDict in sorted(self.transFiles, key=lambda x: x["RunNumber"]):
            lfn = fileDict["LFN"]
            run = fileDict["RunNumber"]
            # If no replica, forget (should not happen)
            if lfn not in self.transReplicas:
                self.transFiles.remove(fileDict)
                continue
            setSEs = set(self.transReplicas[lfn]) & candidateSEs if candidateSEs else set(self.transReplicas[lfn])
            # If run is already suppressed, or no replica left, suppress it all
            if run in suppressedRuns or not setSEs:
                self.transReplicas.pop(lfn)
                self.transFiles.remove(fileDict)
                for se in setSEs:
                    removedFiles[se] += 1
                continue

            # We accept whole runs, even if SE already "full"
            if run not in acceptedRuns:
                # Remove files that are at an SE already busy over threshold
                for se in setSEs & set(pendingTasksPerSE):
                    if pendingTasksPerSE[se] >= throttleLimit:
                        self.transReplicas.pop(lfn)
                        self.transFiles.remove(fileDict)
                        suppressedRuns.add(run)
                        removedFiles[se] += 1
                        break
            # If the file is still there, count it as Pending
            if lfn in self.transReplicas:
                acceptedRuns.add(run)
                for se in setSEs:
                    pendingTasksPerSE[se] += 1
        self.logVerbose("Throttled files per TargetSE", str(dict(removedFiles)))
        if acceptedRuns or suppressedRuns:
            self.logVerbose(f"Throttled {len(suppressedRuns)} runs", f", accepted {len(acceptedRuns)} runs")

    def checkRunForFlush(self, runID, runStatus, forceFlush, param, paramValue, paramStr, evtType):
        """
        Check if a run has to be flushed (if not already)
        """
        # If all files in that run have been processed and received, flush
        # Get the number of RAW files in that run
        if not forceFlush:
            retried = False
            ancestorRawFiles = self.getRAWAncestorsForRun(runID, param, paramValue)
            self.logVerbose("Obtained %d ancestor RAW files" % ancestorRawFiles)
            while True:
                rawFiles = self.getNbRAWInRun(runID, evtType)
                if not retried and rawFiles and ancestorRawFiles > rawFiles:
                    # In case there are more ancestors than RAW files
                    # we may have to refresh the number of RAW files: try once
                    self.cachedNbRAWFiles[runID][evtType] = 0
                    retried = True
                else:
                    runProcessed = ancestorRawFiles == rawFiles
                    break
        else:
            runProcessed = False
        if forceFlush or runProcessed:
            if runProcessed:
                # The whole run was processed by the parent production and we received all files
                self.logInfo("All RAW files (%d) ready for run %d%s- Flushing run" % (rawFiles, runID, paramStr))
            runStatus = "Flush"
            self.transClient.setTransformationRunStatus(self.transID, runID, "Flush")
        elif rawFiles:
            self.logVerbose(
                "Only %d ancestor RAW files (of %d) available for run %d" % (ancestorRawFiles, rawFiles, runID)
            )
        return runStatus

    def getRunList(self, transRuns, runFileDict):
        # Restart where we finished last time and wrap to beginning
        lastRun = self.getCachedLastRun()
        runNumbers = sorted(run["RunNumber"] for run in transRuns if run["RunNumber"] > lastRun) + sorted(
            run["RunNumber"] for run in transRuns if run["RunNumber"] <= lastRun
        )
        # Find out how many files we have currently Unused per run
        res = self.transClient.getTransformationFilesCount(
            self.transID, "RunNumber", {"Status": "Unused", "RunNumber": runNumbers}
        )
        if not res["OK"]:
            self.logError("Error getting file counts per run", res["Message"])
            return res
        unusedFilesPerRun = res["Value"]
        # Check that the total number of files we got for that run is equal to the number of Unused files
        nRunsLeft = len(runNumbers)
        for runID in list(runNumbers):
            runFiles = sum(len(lfns) for lfns in runFileDict[runID].values())  # can be an iterator
            if runFiles != unusedFilesPerRun.get(runID, 0):
                runNumbers.remove(runID)
        if nRunsLeft != len(runNumbers):
            self.logWarn("Removed %d runs with less files than Unused" % (nRunsLeft - len(runNumbers)))
            nRunsLeft = len(runNumbers)
        # Get the list of runs in the same order as runNumbers
        runList = sorted(
            (run for run in transRuns if run["RunNumber"] in runNumbers),
            key=lambda x: runNumbers.index(x["RunNumber"]),
        )
        if nRunsLeft:
            self.logInfo(
                "Processing %d runs between runs %d and %d, starting at run %d"
                % (nRunsLeft, min(runNumbers), max(runNumbers), runNumbers[0])
            )
        else:
            self.logInfo("No runs to process, exit")
            return S_OK([])
        return S_OK(runList)

    def selectTasksFromSEs(self, runID, tasks, addAncestors, fromSEs):
        """
        Check that files (and ancestors) in tasks are at required SEs
        Update tasks list accordingly, and return it as well as a flag indicating if some were removed
        """
        missingAtSEs = False
        if fromSEs:
            # The files and if needed its ancestors have to be in a set of SEs
            # This is used to force processing from disk replicas
            missingAncestors = 0
            okDict = {}
            # Group the LFNs by (set of) SEs in order to speed up the check for ancestors
            nbTasks = len(tasks)
            for task in tasks:
                # Restrict target SEs to those in fromSEs
                okSEs = fromSEs.intersection(task[0].split(","))
                if okSEs:
                    okDict.setdefault(tuple(okSEs), []).append(task[1])
            # Create the real tasks now
            tasks = []
            for okSEs, taskLfns in okDict.items():  # can be an iterator
                if addAncestors:
                    # taskLfns is modified by this method: lfns are eventually removed
                    missing = self.checkAncestorsAtSE(taskLfns, fromSEs)
                    if missing:
                        missingAncestors += missing
                # Now create the list of tasks
                tasks += [(",".join(sorted(okSEs)), lfnList) for lfnList in taskLfns if lfnList]
            # Log if files are not at the required SEs
            if missingAncestors:
                missingAtSEs = True
                self.logInfo(
                    "%d files have been removed from tasks as ancestors were not present at required SEs"
                    % missingAncestors
                )
            if nbTasks != len(tasks):
                missingAtSEs = True
                self.logInfo(
                    "%d tasks could not be created for run %d as files are not at required SEs"
                    % (nbTasks - len(tasks), runID)
                )
        return tasks, missingAtSEs

    def getEventType(self, lfn, runEvtType, paramValue):
        """Get and cache event type for a file"""
        # Determine which event type is used, in order to get the corresponding number of RAW files
        if not runEvtType.get(paramValue):
            runEvtType[paramValue] = self.getMetadataFromTSorBK(lfn, "EventType")[lfn]
        return runEvtType[paramValue]


##################################################################
# Set of utility functions used by LHCbDirac transformation system
##################################################################


def getRemovalPlugins():
    """Returns list of removal plugins."""
    return (
        "DestroyDataset",
        "DestroyDatasetWhenProcessed",
        "RemoveDatasetFromDisk",
        "RemoveReplicasKeepDestination",
        "ReduceReplicasKeepDestination",
        "RemoveReplicas",
        "RemoveReplicasWhenProcessed",
        "RemoveReplicasWithAncestors",
        "ReduceReplicas",
    )


def getReplicationPlugins():
    """Returns list of replication plugins."""
    return (
        "LHCbDSTBroadcast",
        "TurboDSTBroadcast",
        "LHCbMCDSTBroadcastRandom",
        "LHCbWGBroadcastRandom",
        "ArchiveDataset",
        "ReplicateDataset",
        "RAWReplication",
        "ReplicateToRunDestination",
        "FakeReplication",
        "ReplicateToLocalSE",
        "ReplicateWithAncestors",
        "Healing",
        "DataChallengeReplication",
    )


def getShares(sType, normalise=False):
    """Get the shares from the Operations section of the CS If not found, look in
    the Resources section."""
    optionPath = f"Shares/{sType}"
    res = Operations().getOptionsDict(optionPath)
    if not res["OK"]:
        res = gConfig.getOptionsDict(os.path.join("/Resources", optionPath))
    if not res["OK"]:
        return res
    if not res["Value"]:
        return S_ERROR(f"/Resources/{optionPath} option contains no shares")
    shares = res["Value"]
    for site, value in shares.items():  # can be an iterator
        shares[site] = float(value)
    if normalise:
        shares = normaliseShares(shares)
    if not shares:
        return S_ERROR("No non-zero shares defined")
    return S_OK(shares)


def normaliseShares(shares):
    """Normalise to 1 the sum of shares.

    :param shares: shares per SE or site
    :type shares: dict
    """
    total = 0.0
    normShares = shares.copy()
    for site in shares:
        total += float(shares[site])
    if not total:
        return shares
    for site in shares:
        normShares[site] = 100.0 * (float(shares[site]) / total)
    return normShares


# @timeThis


def groupByRun(files):
    """Groups files by run files is a list of dictionaries containing the run
    number."""
    runDict = {}
    for fileDict in files:
        runID = fileDict.get("RunNumber")
        lfn = fileDict["LFN"]
        if lfn:
            runDict.setdefault(runID if runID else 0, []).append(lfn)
    return runDict


def addFilesToTransformation(transID, lfns, addRunInfo=True, resetPresentFiles=False):
    """Add files to a transformation, including the run number if required As
    this is also used by the add-files script, we also add run metadata to the TS
    is not present."""
    transClient = TransformationClient()
    bk = BookkeepingClient()
    gLogger.info(f"Adding {len(lfns)} files to transformation {transID}")
    res = transClient.getTransformation(transID)
    if not res["OK"]:
        return res
    transPlugin = res["Value"]["Plugin"]
    pluginsWithRunInfo = Operations().getValue("TransformationPlugins/PluginsWithRunInfo", [])
    addRunInfo = addRunInfo and transPlugin in pluginsWithRunInfo
    addedLfns = {}
    presentLfns = set()
    failedLfns = {}
    for lfnChunk in breakListIntoChunks(lfns, 1000):
        runDict = {}
        if addRunInfo:
            res = bk.getFileMetadata(lfnChunk)
            if res["OK"]:
                resMeta = res["Value"]["Successful"]
                for lfn, metadata in resMeta.items():  # can be an iterator
                    runID = metadata.get("RunNumber")
                    if runID:
                        runDict.setdefault(int(runID), set()).add(lfn)
            else:
                failedLfns.update(dict.fromkeys(lfnChunk, res["Message"]))
                continue
        errorLogged = False
        retries = 10
        while retries:
            res = transClient.addFilesToTransformation(transID, lfnChunk)
            if not res["OK"]:
                if not errorLogged:
                    errorLogged = True
                    gLogger.error(f"Error adding {len(lfnChunk)} files to transformation, retry...", res["Message"])
                time.sleep(1)
                retries -= 1
            else:
                break
        if not retries:
            failedLfns.update(dict.fromkeys(lfnChunk, res["Message"]))
            continue
        added = {lfn for (lfn, status) in res["Value"]["Successful"].items() if status == "Added"}  # can be an iterator
        present = {
            lfn for (lfn, status) in res["Value"]["Successful"].items() if status == "Present"
        }  # can be an iterator
        addedLfns.update(dict.fromkeys(added, "Added"))
        presentLfns.update(present)
        if addRunInfo:
            gLogger.info(f"Add information for {len(runDict)} runs to transformation {transID}")
            for runID, runLfns in runDict.items():  # can be an iterator
                runLfns &= added
                if runLfns:
                    res = transClient.addTransformationRunFiles(transID, runID, list(runLfns))
                    if not res["OK"]:
                        gLogger.error(
                            "Error adding files to run",
                            f"for {len(runLfns)} files to run {runID}: {res['Message']}",
                        )
            # Add run metadata if not present in TS
            res = transClient.getRunsMetadata(list(runDict))
            if res["OK"]:
                missingRuns = []
                for runID, meta in res["Value"].items():  # can be an iterator
                    if "TCK" not in meta or "CondDb" not in meta or "DDDB" not in meta:
                        missingRuns.append(runID)
            else:
                missingRuns = list(runDict)
            if missingRuns:
                res = bk.getRunInformation({"RunNumber": missingRuns, "Fields": ["TCK", "CondDb", "DDDB"]})
                if not res["OK"]:
                    gLogger.error("Error getting run information", res["Message"])
                else:
                    for runID, meta in res["Value"].items():  # can be an iterator
                        res = transClient.addRunsMetadata(runID, meta)
                        if not res["OK"]:
                            gLogger.error("Error setting run metadata in TS", res["Message"])

    gLogger.verbose(f"{len(addedLfns)} files successfully added to transformation")
    resetLfns = 0
    if resetPresentFiles and presentLfns:
        for lfnChunk in breakListIntoChunks(presentLfns, 1000):
            res = transClient.setFileStatusForTransformation(transID, "Unused", lfnChunk, force=True)
            if not res["OK"]:
                gLogger.error("Error resetting files Unused", f"for {len(lfnChunk)} files: {res['Message']}")
                failedLfns.update(dict.fromkeys(lfnChunk, res["Message"]))
            else:
                resetLfns += len(lfnChunk)
                addedLfns.update(dict.fromkeys(lfnChunk, "Reset"))
        gLogger.verbose("Successfully reset %d files Unused in transformation %s" % (resetLfns, transID))
    return S_OK({"Successful": addedLfns, "Failed": failedLfns})


def stripDirectory(files, depth=None):
    """Return set of directories for a list of LFNs, and directory for a single LFN."""
    if depth is None:
        depth = 4
    if isinstance(files, str):
        return os.path.sep + os.path.join(*files.split(os.path.sep)[: depth + 1])
    return {os.path.sep + os.path.join(*lfn.split(os.path.sep)[: depth + 1]) for lfn in files}
