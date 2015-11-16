import ranger.api
from time import strftime, localtime
from ranger.core.linemode import LinemodeBase
from ranger.ext.human_readable import human_readable

@ranger.api.register_linemode
class FileAttrLinemode(LinemodeBase):
    name = "fileattr"
    timeformat = '%Y-%m-%d %H:%M'

    def filetitle(self, file, metadata):
        return file.relative_path

    def infostring(self, file, metadata):
        ctime=strftime(self.timeformat, localtime(file.stat.st_ctime))
        size = human_readable(file.size, separator='')
        return "%s %s %s %s %s" % (file.get_permission_string(),
                file.user, file.group, size, ctime)