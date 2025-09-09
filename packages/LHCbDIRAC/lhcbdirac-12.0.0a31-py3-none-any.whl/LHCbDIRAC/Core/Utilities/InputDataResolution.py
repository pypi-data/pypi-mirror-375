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
"""The input data resolution module is a VO-specific plugin that allows to
define VO input data policy in a simple way using existing utilities in DIRAC
or extension code supplied by the VO.

The arguments dictionary from the Job Wrapper includes the file
catalogue result and in principle has all necessary information to
resolve input data for applications.
"""
from pathlib import Path

from DIRAC import S_OK
from DIRAC.WorkloadManagementSystem.Client.PoolXMLSlice import PoolXMLSlice
from DIRAC.WorkloadManagementSystem.Client.InputDataResolution import InputDataResolution as DIRACInputDataResolution

CREATE_CATALOG = False


class InputDataResolution(DIRACInputDataResolution):
    """Define the Input Data Policy."""

    def __init__(self, argumentsDict, bkkClient=None):
        """Standard constructor."""
        super().__init__(argumentsDict)

        if not bkkClient:
            from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

            self.bkkClient = BookkeepingClient()
        else:
            self.bkkClient = bkkClient

    #############################################################################

    def execute(self):
        """Given the arguments from the Job Wrapper, this function calls existing
        utilities in DIRAC to resolve input data according to LHCb VO policy."""
        result = super().execute()
        if not result["OK"] or not result["Value"].get("Successful", {}):
            return result
        resolvedData = result["Value"]["Successful"]

        resolvedData = self._addPfnType(resolvedData)
        if not resolvedData["OK"]:
            return resolvedData
        resolvedData = resolvedData["Value"]

        # TODO: Below is temporary behaviour to prepend mdf: to resolved TURL(s) for case when not a ROOT file
        # This instructs the Gaudi applications to use root to access different file types e.g. for MDF.
        # In the longer term this should be derived from file catalog metadata information.
        # 24/08/2010 - updated hack to use "mdf:" after udpates from Markus
        for lfn, mdataList in resolvedData.items():
            if not isinstance(mdataList, list):
                mdataList = [mdataList]
            for mdata in mdataList:
                if mdata["pfntype"] == "MDF":
                    mdata["turl"] = "mdf:" + mdata["turl"]
                    self.log.info(f"Prepending mdf: to TURL for {lfn}")

        catalogName = self.arguments["Configuration"].get("CatalogName", "pool_xml_catalog.xml")

        self.log.verbose(f"Catalog name will be: {catalogName}")
        appCatalog = PoolXMLSlice(catalogName, Path(self.arguments["Configuration"].get("JobIDPath", "")))
        check = appCatalog.execute(resolvedData)
        if not check["OK"]:
            return check
        return result

    #############################################################################

    def _addPfnType(self, resolvedData):
        """Add the pfn type to the lfn list in input."""

        typeVersions = self.bkkClient.getFileTypeVersion(list(resolvedData))
        if not typeVersions["OK"]:
            return typeVersions
        typeVersions = typeVersions["Value"]

        for lfn, mdataList in resolvedData.items():
            if not isinstance(mdataList, list):
                mdataList = [mdataList]
            if lfn not in typeVersions:
                self.log.warn(f"The file {lfn} do not exist in the BKK, assuming ROOT, unless it is a RAW (MDF)")
                if lfn.split(".")[-1].lower() == "raw":
                    lfnType = "MDF"
                else:
                    lfnType = "ROOT"
            else:
                self.log.verbose(f"Adding PFN file type {typeVersions[lfn]} for {lfn}")
                lfnType = typeVersions[lfn]

            for mdata in mdataList:
                mdata["pfntype"] = lfnType

        return S_OK(resolvedData)
