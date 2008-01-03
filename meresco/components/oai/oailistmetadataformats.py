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

from meresco.components.oai.oaiverb import OaiVerb
from meresco.framework.observable import Observable

class OaiListMetadataFormats(OaiVerb, Observable):
    """4.4 ListMetadataFormats
Summary and Usage Notes

This verb is used to retrieve the metadata formats available from a repository. An optional argument restricts the request to the formats available for a specific item.
Arguments

    * identifier an optional argument that specifies the unique identifier of the item for which available metadata formats are being requested. If this argument is omitted, then the response includes all metadata formats supported by this repository. Note that the fact that a metadata format is supported by a repository does not mean that it can be disseminated from all items in the repository.

Error and Exception Conditions

    * badArgument - The request includes illegal arguments or is missing required arguments.
    * idDoesNotExist - The value of the identifier argument is unknown or illegal in this repository.
    * noMetadataFormats - There are no metadata formats available for the specified item.
    """

    def __init__(self):
        OaiVerb.__init__(self, ['ListMetadataFormats'], {'identifier': 'optional'})
        Observable.__init__(self)

    def listMetadataFormats(self, aWebRequest):
        self.startProcessing(aWebRequest)

    def preProcess(self, webRequest):
        metadataFormats = self.any.getAllPrefixes()
        if self._identifier:
            if not self.any.isAvailable(self._identifier):
                return self.writeError(webRequest, 'idDoesNotExist')
            prefixes = self.any.getParts(self._identifier)
            metadataFormats = [(prefix, xsd, ns) for prefix, xsd, ns in metadataFormats if prefix in prefixes]
        self.displayedMetadataFormats = metadataFormats

    def process(self, webRequest):
        for metadataPrefix, schema, metadataNamespace in self.displayedMetadataFormats:
            webRequest.write("""<metadataFormat>
                <metadataPrefix>%s</metadataPrefix>
                <schema>%s</schema>
                <metadataNamespace>%s</metadataNamespace>
            </metadataFormat>""" % (metadataPrefix, schema, metadataNamespace))

