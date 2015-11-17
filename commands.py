
from ranger.api.commands import *
from ranger.config.commands import scout
from ranger.container.directory import accept_file
from fnmatch import fnmatch
import ranger


def dehumanize(size):
    """converts humanized size to bytes

    >>> dehumanize(20K)
    20480
    >>> dehumanize(2000)
    2000
    >>> dehumanize(2M)
    2097152
    >>> dehumanize(1G)
    1 * (1024 ** 3)
    """
    if size.isdigit(): return float(size)
    eq = {'K': 1024, 'M':1024 ** 2, 'G':1024 ** 3}
    value, unit = size[0:-1], size[-1].upper()
    if not value.isdigit: return 0
    return float(value) * eq[unit]

class filterby(Command):
    """:filterby condition1 condition2 ....

    Filters files in the current directory by size, name or user.
    Only works with files, directories are ignored.

    Available conditions:
    name:
        matches file name with a given pattern using Unix shell-style wildcards
        Ex: 
            name==*.py: filters any file which extension is py
            name!=*.py: filters any file which extension is not py
    size:
        matches file size with a given size
        Ex:
            size<10K
            size>10M
            size>1G
            size>=1024: filters any file which size is grather or equal than 1024 bytes
    user:
        matches file user with a given glob pattern using shell-style wildcards
        Ex: 
            user=='root': filters any file which user is root
            user!='ad*': filters any file which user starts with 'ad'

    Unix shell-style wildcards:
    Pattern     Meaning
    -------     -------
    *           matches everything
    ?           matches any single character
    [seq]       matches any character in seq
    [!seq]      matches any character not in seq

    """

    ARG_RE = {
        "size" : {'re': re.compile(r'^\s*size(<=|>=|!=|==|>|<)(.*?)\s*$'), 'apply_func':dehumanize},
        "name" : {'re': re.compile(r'^\s*name(==|!=)(.*?)\s*$')},
        "user" : {'re': re.compile(r'^\s*user(==|!=)(.*?)\s*$')}
    }

    COND_BUILDER = {
        "size" : "file.{attr}{operator}{value}",
        "name" : "{operator} fnmatch(file.{attr}, '{value}')",
        "user" : "{operator} fnmatch(file.{attr}, '{value}')"
    }

    CONVERT_OPERATOR = {
        "name" : {"!=":'not', "==":''},
        "user" : {"!=":'not', "==":''}
    }

    TRANSLATE_ATTR = {
        "name" : "relative_path"
    }

    def execute(self):
        self.cancel()
        parsed_args = self.parse_args(self.args)
        files = self.fm.thisdir.files

        filters = self.build_filters(parsed_args)

        self.fm.thisdir.files = [f for f in files if f.is_file and accept_file(f, filters)]
        
        if self.fm.thisdir.files:
            self.fm.thisdir.pointed_obj = self.fm.thisdir.files[0]
            self.fm.thisdir.move_to_obj(self.fm.thisdir.pointed_obj)

    def parse_args(self, arguments):
        """parses arguments

        >>> parse_args([])
        {}

        >>> parse_args(['size==1M'])
        {'size':{'operator': '==','value': 1024 ** 2 }}
        
        >>> parse_args(['name!=somename'])
        {'name':{'operator': '!=','value': 'somename'}}
        
        >>> parse_args(['size=9K'])
        {}
        """
        res_dict = {}
        for key, value in self.ARG_RE.iteritems():
            for arg in arguments:
                if arg.startswith(key):
                    match = value['re'].match(arg)
                    if match:
                        res_dict[key] = {
                            'operator': match.group(1),
                            'value': value.get('apply_func', str)(match.group(2))
                        }
        return res_dict

    def build_filters(self, parsed_args):
        """creates lambda functions for each argument
        """
        filters = []
        for attr, value in parsed_args.iteritems():
            operator = value['operator']

            fsobj_attr = self.TRANSLATE_ATTR.get(attr, attr)
            cond = self.COND_BUILDER[attr]
            if self.CONVERT_OPERATOR.get(attr, None):
                operator = self.CONVERT_OPERATOR[attr].get(operator, operator)

            cond = cond.format(attr=fsobj_attr,operator=operator,value=value['value'])
            filters.append(lambda file: eval(cond))
        return filters

    def cancel(self):
        self.fm.thisdir.temporary_filter = None
        self.fm.thisdir.refilter()

            
if __name__ == "__main__":
    import doctest
    doctest.testmod()