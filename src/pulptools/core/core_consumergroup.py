#!/usr/bin/python
#
# Pulp Repo management module
#
# Copyright (c) 2010 Red Hat, Inc.
#
# Authors: Sayli Karmarkar <skarmark@redhat.com>

# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

import os
import sys
import time
import base64

import pulptools.utils as utils
import pulptools.constants as constants
from pulptools.core.basecore import BaseCore, systemExit
from pulptools.connection import ConsumerGroupConnection, RestlibException
from pulptools.logutil import getLogger

import gettext
_ = gettext.gettext
log = getLogger(__name__)

class consumergroup(BaseCore):
    def __init__(self):
        usage = "usage: %prog consumergroup [OPTIONS]"
        shortdesc = "consumer group specific actions to pulp server."
        desc = ""

        BaseCore.__init__(self, "consumergroup", usage, shortdesc, desc)
        self.actions = {"create" : "Create a consumer group",
                        "update" : "Update a consumer group",
                        "list"   : "List available consumer groups",
                        "delete" : "Delete a consumer group",}

        self.username = None
        self.password = None
        self.name = "consumergroup"
        self.cgconn = ConsumerGroupConnection(host="localhost", port=8811)
        self.generate_options()

    def generate_options(self):

        possiblecmd = []

        for arg in sys.argv[1:]:
            if not arg.startswith("-"):
                possiblecmd.append(arg)
        self.action = None
        if len(possiblecmd) > 1:
            self.action = possiblecmd[1]
        elif len(possiblecmd) == 1 and possiblecmd[0] == self.name:
            self._usage()
            sys.exit(0)
        else:
            return
        if self.action not in self.actions.keys():
            self._usage()
            sys.exit(0)
        if self.action == "create":
            usage = "usage: %prog consumergroup create [OPTIONS]"
            BaseCore.__init__(self, "consumergroup create", usage, "", "")
            self.parser.add_option("--id", dest="id",
                           help="consumer group id"),
            self.parser.add_option("--name", dest="name",
                           help="consumer group name"),
            self.parser.add_option("--description", dest="description",
                           help="description of consumer group")
            self.parser.add_option("--consumerids", dest="consumerids",
                           help="consumer id list to be included in this group")
        if self.action == "delete":
            usage = "usage: %prog consumergroup delete [OPTIONS]"
            BaseCore.__init__(self, "consumergroup delete", usage, "", "")
            self.parser.add_option("--name", dest="name",
                           help="Consumer group name")
        if self.action == "list":
            usage = "usage: %prog consumergroup list [OPTIONS]"
            BaseCore.__init__(self, "consumergroup list", usage, "", "")

    def _validate_options(self):
        pass

    def _usage(self):
        print "\nUsage: %s MODULENAME ACTION [options] --help\n" % os.path.basename(sys.argv[0])
        print "Supported Actions:\n"
        items = self.actions.items()
        items.sort()
        for (name, cmd) in items:
            print("\t%-14s %-25s" % (name, cmd))
        print("")

    def _do_core(self):
        self._validate_options()
        if self.action == "create":
            self._create()
        if self.action == "list":
            self._list()
        if self.action == "delete":
            self._delete()

    def _create(self):
        (self.options, self.args) = self.parser.parse_args()
        if not self.options.id:
            print("consumer group id required. Try --help")
            sys.exit(0)
        if not self.options.name:
            print("consumer group name required. Try --help")
            sys.exit(0)
        if not self.options.description:
            self.options.description = ""
        if not self.options.consumerids:
            print("Creating empty consumer group")
            self.options.consumerids = []
        try:
            consumergroup = self.cgconn.create(self.options.id, self.options.name, self.options.description,
                                    self.options.consumerids)
            print _(" Successfully created Consumer group [ %s ] with description [ %s ]" % \
                                     (consumergroup['name'], consumergroup["description"]))
        except RestlibException, re:
            log.error("Error: %s" % re)
            systemExit(re.code, re.msg)
        except Exception, e:
            log.error("Error: %s" % e)
            raise

    def _list(self):
        print "In list function"
        (self.options, self.args) = self.parser.parse_args()
        print self.options, self.args
        try:
            groups = self.cgconn.consumergroups()
            print(groups)
            columns = ["id", "name", "description", "consumerids"]
            data = [ _sub_dict(group, columns) for group in groups]
            if not len(data):
                print _("No consumer groups available to list")
                sys.exit(0)
            print """+-------------------------------------------+\n    List of Available Consumer Groups \n+-------------------------------------------+"""
            for group in data:
                    print constants.AVAILABLE_CONSUMER_GROUP_INFO % (group["id"], group["name"], group["description"], group["consumerids"] )
        except RestlibException, re:
            log.error("Error: %s" % re)
            systemExit(re.code, re.msg)
        except Exception, e:
            log.error("Error: %s" % e)
            raise


    def _delete(self):
        (self.options, self.args) = self.parser.parse_args()
        if not self.options.id:
            print("Group id required. Try --help")
            sys.exit(0)
        try:
            self.cgconn.delete(id=self.options.id)
            print _(" Successful deleted Consumer Group [ %s ] " % self.options.id)
        except RestlibException, re:
            print _(" Deleted operation failed Consumer Group [ %s ] " % \
                  self.options.label)
            log.error("Error: %s" % re)
            sys.exit(-1)
        except Exception, e:
            print _(" Deleted operation failed on Consumer Group [ %s ]. " % \
                  self.options.label)
            log.error("Error: %s" % e)
            sys.exit(-1)


def _sub_dict(datadict, subkeys, default=None) :
    return dict([ (k, datadict.get(k, default) ) for k in subkeys ] )
