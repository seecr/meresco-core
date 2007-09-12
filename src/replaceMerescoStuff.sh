#!/bin/bash
## begin license ##
#
#    Meresco Core is part of Meresco.
#    Copyright (C) 2007 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2007 Stichting Kennisnet Ict op school. 
#       http://www.kennisnetictopschool.nl
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
echo "core.index.xslice                         components.lucene.xslice
core.index.querywrapper                         components.lucene.querywrapper
core.index.hits                                 components.lucene.hits
core.drilldown.drilldown                        components.drilldown
queryserver.observers.oai.data                  components.http.oai.data
queryserver.observers.oai.oairecordverb         components.http.oai.oairecordverb
queryserver.observers.oai.oaivalidator          components.http.oai.oaivalidator
queryserver.observers.oai.oaitool               components.http.oai.oaitool
queryserver.observers.partscomponent            components.partscomponent
queryserver.observers.undertaker                components.undertaker
queryserver.observers.oaigetrecord              components.http.oai.oaigetrecord
queryserver.observers.oailist                   components.http.oai.oailist
queryserver.observers.oaisink                   components.http.oai.oaisink
queryserver.observers.oailistmetadataformats    components.http.oai.oailistmetadataformats
queryserver.observers.portal                    legacy.deathrow.portal
queryserver.observers.stampcomponent            components.stampcomponent
queryserver.observers.oaicomponent              components.http.oai.oaicomponent
queryserver.observers.setscomponent             components.setscomponent
queryserver.observers.oaiidentify               components.http.oai.oaiidentify
queryserver.observers.oailistsets               components.http.oai.oailistsets
queryserver.server                              legacy.deathrow.server
queryserver.pluginregistry                      legacy.pluginregistry
queryserver.plugins                             legacy.plugins
teddy.xmlpump                                   components.xmlpump
teddy.fields2xmlcomponent                       components.fields2xmlcomponent
teddy.printingserver                            legacy.deathrow.printingserver
teddy.indexcomponent                            components.lucene.indexcomponent
teddy.xml2document                              components.xml2document
teddy.configuration                             legacy.configuration
teddy.logcomponent                              components.logcomponent
teddy.teddyinterface                            legacy.teddyinterface
teddy.teddygrowlserver                          components.sshobservableserver
teddy.teddyinterfaceconstructor                 legacy.teddyinterfaceconstructor
teddy.lucenetools                               components.lucene.lucenetools
teddy.lucene                                    components.lucene.lucene
teddy.storagecomponent                          components.storagecomponent
teddy.pluginadapter                             legacy.pluginadapter
teddy.document                                  components.lucene.document
teddy.venturi                                   components.venturi
teddy.srurecordupdateplugin                     components.http.srurecordupdateplugin
httpserver.sru                                  components.http
cq2utils.observable                             meresco.framework.observable
cq2utils.filter                                 meresco.components.filter" | \
while read line
do
    set -- $line
    old=$1
    new=$2
    echo "$old --> $new"
    find -name '*.py' | grep -v '\.svn' | xargs sed "s,$old,$new," -i
done
