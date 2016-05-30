#!/usr/bin/env python
#===============================================================================
# Copyright (C) 2014-2015 Anton Vorobyov
#
# This file is part of Phobos.
#
# Phobos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Phobos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Phobos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


import sys
import os.path

from flow import FlowManager
from miner import *
from translator import Translator
from writer import *

def run(rvr, path_json):
    pickle_miner = ResourcePickleMiner(rvr)
    trans = Translator(pickle_miner)
    bulkdata_miner = BulkdataMiner(rvr, trans)
    staticcache_miner = ResourceStaticCacheMiner(rvr, trans)
    miners = (
        MetadataMiner(path_eve),
        bulkdata_miner,
        staticcache_miner,
        TraitMiner(staticcache_miner, bulkdata_miner, trans),
        SqliteMiner(rvr.paths.root, trans),
        CachedCallsMiner(rvr, trans),
        pickle_miner
    )

    writers = (
        JsonWriter(path_json, indent=2),
    )

    FlowManager(miners, writers).run(args.list, args.translate)

if __name__ == '__main__':

    try:
        major = sys.version_info.major
        minor = sys.version_info.minor
    except AttributeError:
        major = sys.version_info[0]
        minor = sys.version_info[1]
    if major != 2 or minor < 7:
        sys.stderr.write('This application requires Python 2.7 to run, but {0}.{1} was used\n'.format(major, minor))
        sys.exit()


    import argparse
    import os.path

    import reverence

    parser = argparse.ArgumentParser(description='This script pulls data out of EVE client and writes it in JSON format')
    parser.add_argument('-r', '--res', help='Path to EVE SharedCache folder', required=True)
    parser.add_argument('-j', '--json', help='Output folder for the JSON files', required=True)
    servers = {'tranquility': 'tq', 'singularity': 'sisi', 'duality': 'duality', 'serenity': 'serenity'}
    parser.add_argument('-s', '--server', default='tranquility', choices=servers.keys(), help='Server to pull data from. Defaults to tranquility')
    parser.add_argument('-e', '--eve', help='Path to EVE folder. Defaults to standard directory location under SharedCache')
    parser.add_argument('-c', '--cache', help='Path to EVE cache folder. Reverence will attempt to find cache by default if none is provided')
    languages = ('de', 'en-us', 'es', 'fr', 'it', 'ja', 'ru', 'zh', 'multi')
    parser.add_argument('-t', '--translate', default='multi', choices=languages, help='Attempt to translate strings into specified language. Defaults to multi')
    parser.add_argument('-l', '--list', default='', help='Comma-separated list of container names to dump')
    args = parser.parse_args()

    # Expand home directory
    path_res = os.path.expanduser(args.res)
    path_json = os.path.expanduser(args.json)
    path_eve = os.path.expanduser(args.eve) if args.eve else None
    path_cache = os.path.expanduser(args.cache) if args.cache else None

    if path_eve is None:
        path_eve = os.path.join(path_res, servers[args.server])

    rvr_language = args.translate if args.translate != 'multi' else 'en-us'
    rvr = reverence.blue.EVE(path_eve, cachepath=path_cache, sharedcachepath=path_res, server=args.server, languageID=rvr_language)

    run(rvr, path_json)
