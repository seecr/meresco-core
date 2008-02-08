## begin license ##
#
#    Meresco Core is an open-source library containing components to build
#    searchengines, repositories and archives.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#
#    This file is part of Meresco Core.
#
#    Meresco Core is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Core; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.framework.observable import Observable
from meresco.components.oai.oairecordverb import OaiRecordVerb

class OaiGetRecord(OaiRecordVerb, Observable):
    """4.1 GetRecord
Summary and Usage Notes

This verb is used to retrieve an individual metadata record from a repository. Required arguments specify the identifier of the item from which the record is requested and the format of the metadata that should be included in the record. Depending on the level at which a repository tracks deletions, a header with a "deleted" value for the status attribute may be returned, in case the metadata format specified by the metadataPrefix is no longer available from the repository or from the specified item.

Arguments

    * identifier a required argument that specifies the unique identifier of the item in the repository from which the record must be disseminated.
    * metadataPrefix a required argument that specifies the metadataPrefix of the format that should be included in the metadata part of the returned record . A record should only be returned if the format specified by the metadataPrefix can be disseminated from the item identified by the value of the identifier argument. The metadata formats supported by a repository and for a particular record can be retrieved using the ListMetadataFormats request.

Error and Exception Conditions

    * badArgument - The request includes illegal arguments or is missing required arguments.
    * cannotDisseminateFormat - The value of the metadataPrefix argument is not supported by the item identified by the value of the identifier argument.
    * idDoesNotExist - The value of the identifier argument is unknown or illegal in this repository.
"""
    def __init__(self):
        OaiRecordVerb.__init__(self, ['GetRecord'], {
            'identifier': 'required',
            'metadataPrefix': 'required'})
        Observable.__init__(self)

    def getRecord(self, webRequest):
        self.startProcessing(webRequest)

    def preProcess(self, webRequest):
        if not self._metadataPrefix in [prefix for prefix, na, na in self.any.getAllPrefixes()]:
            return self.writeError(webRequest, 'cannotDisseminateFormat')

        hasId, hasPartName = self.any.isAvailable(self._identifier, self._metadataPrefix)

        if not hasId:
            return self.writeError(webRequest, 'idDoesNotExist')

        if not hasPartName:
            return self.writeError(webRequest, 'cannotDisseminateFormat')

    def process(self, webRequest):
        self.writeRecord(webRequest, self._identifier)

