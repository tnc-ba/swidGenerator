# -*- coding: utf-8 -*-

from xml.etree import cElementTree as ET
from xml.dom import minidom
import subprocess
import platform


class PackageInfo(object):
    package = ''
    version = ''


class DpkgEnvironment(object):
    command_args = ["dpkg-query", "-W", "-f=${Package}\\t${Version}\\n"]

    @staticmethod
    def get_list(data):
        line_list = data.split('\n')

        result = []

        for line in line_list:
            split_line = line.split('\t')
            if len(split_line) == 2:
                info = PackageInfo()
                info.package = split_line[0]
                info.version = split_line[1]

                result.append(info)

        return result

    @staticmethod
    def get_os_string():
        dist = platform.dist()
        return dist[0] + '_' + dist[1]


class OutputGenerator(object):
    regid = "regid.2004-03.org.strongswan"
    role = "tagcreator"
    version_scheme = "alphanumeric"
    xmlns = "http://standards.iso.org/iso/19770/-2/2014/schema.xsd"

    def __init__(self, environment):
        self.environment = environment

    def _call_package_manager(self):
        self.raw_output = subprocess.check_output(self.environment.command_args)

    def _get_list(self):
        self._call_package_manager()
        return self.environment.get_list(self.raw_output)

    def _get_os_string(self):
        return self.environment.get_os_string()

    def create_swid_tags(self):
        pkg_info = self._get_list()
        os_info = self._get_os_string()

        swidtags = []

        for pi in pkg_info:
            software_identity = ET.Element("SoftwareIdentity")
            software_identity.set('xmlns', self.xmlns)
            software_identity.set('name', pi.package)
            software_identity.set('uniqueId', '{os_info}-{pi.package}-{pi.version}'.format(os_info=os_info, pi=pi))
            software_identity.set('version', pi.version)
            software_identity.set('versionScheme', self.version_scheme)

            entity = ET.SubElement(software_identity, "Entity")
            entity.set('name', pi.package)
            entity.set('regid', self.regid)
            entity.set('role', self.role)

            swidtag_flat = ET.tostring(software_identity, 'UTF-8')
            swidtag_reparsed = minidom.parseString(swidtag_flat)

            swidtags.append(swidtag_reparsed.toprettyxml(indent="\t", encoding='UTF-8'))

        return '\n'.join(swidtags)


def main():
    dpkg_env = DpkgEnvironment()
    gen = OutputGenerator(dpkg_env)
    print gen.create_swid_tags()


if __name__ == '__main__':
    main()