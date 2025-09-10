import collections
import json
import os
import re
import shlex
import subprocess
import asyncio 

_VersionInfo = collections.namedtuple("WhatWebVersion", ['major', 'minor', 'micro'])
_whatweb_search_path = ('/usr/bin/whatweb', '/usr/local/bin/whatweb', '/opt/local/bin/whatweb')

regex_warning = re.compile('^Warning: .*', re.IGNORECASE)
regex_whatweb_banner = re.compile('WhatWeb version ([0-9]+)\.([0-9]+)(?:\.([0-9])+)[^ ]* \( https?://.* \)')

class WhatWeb(object):
    def __init__(self, exe_search_path = _whatweb_search_path):
        self._search_path = exe_search_path
        self._version_info = None
        self._whatweb_path = None
        
    def _ensure_path_and_version(self):
        if self._whatweb_path:
            return
        is_found = False
        
        for whatweb_path in self._search_path:
            proc = None
            try:
                command = whatweb_path + ' --version'
                shlexed = shlex.split(command)
                proc = subprocess.Popen(shlexed, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                
                while True:
                    line = proc.stdout.readline()
                    line = line.decode('utf8')
                    match_info = regex_whatweb_banner.match(line)
                    if match_info is None:
                        continue
                    is_found = True
                    self._whatweb_path = whatweb_path
                    
                    versions = match_info.groups()
                    if len(versions) == 2:
                        self._version_info = _VersionInfo(major = int(versions[0]), minor = int(versions[1]))
                    else:
                        self._version_info = _VersionInfo(major = int(versions[0]), minor = int(versions[1]), 
                                                          micro = int(versions[2]))
                    break
                    if proc.stdout.at_eof():
                        break
            except:
                pass
            else:
                if is_found:
                    break
            finally:
                if proc:
                    try:
                        proc.terminate()
                    except ProcessLookupError:
                        pass
                    proc.wait()
                    
        if not is_found:
            raise WhatWebError('whatweb was not found in path')

    def version(self):
        self._ensure_path_and_version()
        return self._version_info   

    def scan(self, targets, arguments = None):
        self._ensure_path_and_version()
        args = self._get_scan_args(targets, arguments)
        return (self._scan_proc(args))
        
    def _scan_proc(self, args):
        proc = None
        try:
            args.insert(0, self._whatweb_path)
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            whatweb_output, whatweb_err = process.communicate()
        except:
            raise
        finally:
            if proc:
                try:
                    proc.terminate()
                except ProcessLookupError:
                    pass
                proc.wait()
                
        if whatweb_output:
            try:
                whatweb_output = whatweb_output.decode('utf8')
                return json.loads(whatweb_output)
            except json.JSONDecodeError as e:
                print("JSON DECODE ERROR", e)
                return [{}]
            except Exception as e:
                return [{}]
       
    def _get_scan_args(self, targets, arguments):
        assert isinstance(targets, (str, list)), 'Wrong type for [hosts], should be a string or Iterable [was {0}]'.format(type(targets))
        
        if not isinstance(targets, str):
            targets = ' '.join(targets)
        if arguments:
            assert all(_ not in arguments for _ in ('--log-json',)), 'can set log option'
            scan_args = shlex.split(arguments)
        else:
            scan_args = []
        targets_args = shlex.split(targets)        
        return ['--log-json=-', '-q'] + targets_args + scan_args
    
class WhatWebError(Exception):
    """Exception error class for WhatWeb class"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return 'WhatWebError exception {0}'.format(self.value)
            
class WhatWebAsync(WhatWeb):
    def __init__(self):
        super(WhatWebAsync, self).__init__(_whatweb_search_path)
        
    async def scan(self, targets, arguments = None):
        args = self._get_scan_args(targets, arguments)
        return (await self._scan_proc(args))
    
    def _get_scan_args(self, targets, arguments):
        assert isinstance(targets, (str, list)), 'Wrong type for [hosts], should be a string or Iterable [was {0}]'.format(type(targets))
        
        if not isinstance(targets, str):
            targets = ' '.join(targets)
        if arguments:
            assert all(_ not in arguments for _ in ('--log-json',)), 'can set log option'
            scan_args = arguments
        else:
            scan_args = ''
        return '--log-json=- -q ' + targets + scan_args
        
    async def _scan_proc(self, args):
        proc = None
        try:
            if not self._whatweb_path:
                for path in _whatweb_search_path:
                    if os.path.isfile(path):
                        self._whatweb_path = path 
                        break 
            
            cmd = "{cmd} {args}".format(cmd=self._whatweb_path, args=args)
            process = await asyncio.create_subprocess_shell(cmd,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            whatweb_output, whatweb_err = await  process.communicate()
            
        except Exception as e:
            print("ERROR ", e)
            return [{}]
        else:
            if whatweb_output:
                try:
                    applications = whatweb_output.decode('utf8').replace("'", '"')
                    return json.loads(applications)
                except json.JSONDecodeError as e:
                    print("JSON DECODE ERROR", e)
                    return [{}]
                except Exception as e:
                    print("ERROR ", e)
                    return [{}]
