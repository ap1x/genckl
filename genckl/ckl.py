import os
import uuid
import zipfile
import csv
import subprocess
import shlex
import socket
from xml.etree import ElementTree
from xml.dom import minidom


class Ckl():
    '''Create a new Ckl object.'''

    def __init__(self):

        self.xccdfs = []
        self.asset = {'ROLE': 'None',
                      'ASSET_TYPE': 'Computing',
                      'HOST_NAME': '',
                      'HOST_IP': '',
                      'HOST_MAC': '',
                      'HOST_FQDN': '',
                      'TARGET_COMMENT': '',
                      'TECH_AREA': '',
                      'TARGET_KEY': '',
                      'WEB_OR_DATABASE': 'false',
                      'WEB_DB_SITE': '',
                      'WEB_DB_INSTANCE': ''}

    def write(self, filename):
        '''Write this Ckl to a file.'''

        # flatten the Ckl prior to writing
        self.flatten()

        # setup new ElementTree
        tree = ElementTree.ElementTree(ElementTree.Element('CHECKLIST'))
        asset_el = ElementTree.SubElement(tree.getroot(), 'ASSET')
        stigs_el = ElementTree.SubElement(tree.getroot(), 'STIGS')

        # add asset SubElements
        for name, value in self.asset.items():
            sub_el = ElementTree.SubElement(asset_el, name)
            sub_el.text = value

        # add each stig
        for xccdf in self.xccdfs:
            stigs_el.append(xccdf.toelement())

        # convert ElementTree to a DOM
        dom = minidom.parseString(ElementTree.tostring(
            tree.getroot(), encoding='unicode'))

        # make the DOM pretty
        dom = dom.toprettyxml()

        # convert the DOM back to an ElementTree
        tree = ElementTree.ElementTree(ElementTree.fromstring(dom))

        # convert the ElementTree to a list of lines
        lines = ElementTree.tostring(
            tree.getroot(), encoding='unicode', short_empty_elements=False).splitlines()

        # insert the XML declaration and stig viewer comment lines into the list
        # we have to do it this way because python's ElementTree lib doesn't
        # support comments before the first Element
        lines.insert(0, '<!--DISA STIG Viewer :: 2.11-->')
        lines.insert(0, '<?xml version="1.0" encoding="UTF-8"?>')

        # try to open, if TypeError assume already open
        try:
            output_file = open(filename, 'w', encoding='UTF-8')
        except TypeError:
            output_file = filename

        output_file.write('\n'.join(lines))
        output_file.close()

    def importxccdf(self, xccdf):
        '''
        Import an Xccdf into this Ckl.

        xccdf should be an Xccdf object (with or without results)

        Returns True if imported, False if already present
        '''

        # return False if we already have this xccdf
        for myxccdf in self.xccdfs:
            if myxccdf.getid() == xccdf.getid():
                return False

        # add the stig
        self.xccdfs.append(xccdf)

        # set target_key if it hasn't been set yet, this is not a bug. As
        # of STIG Viewer 2.11, it does no additional checks (like ensuring new
        # stigs have same key).
        if not self.asset['TARGET_KEY']:
            self.asset['TARGET_KEY'] = xccdf.getvulns()[0].getattrs()[
                'TargetKey']

        return True

    def flatten(self):
        '''
        Merges all result xccdfs with non-result xccdfs in this Ckl. Result 
        xccdfs that are completely merged are removed.
        '''

        # build 2 lists containing result and non-result xccdfs
        result_xccdfs = []
        for xccdf in self.xccdfs:
            if xccdf.hasresults:
                result_xccdfs.append(xccdf)

        plain_xccdfs = []
        for xccdf in self.xccdfs:
            if not xccdf.hasresults:
                plain_xccdfs.append(xccdf)

        for res_xccdf in result_xccdfs:

            # attempt to merge results with all non-result xccdfs, collect list
            # of successfully merged vulns
            merged_vulns = []
            for pl_xccdf in plain_xccdfs:
                merged_vulns = merged_vulns + pl_xccdf.mergexccdf(res_xccdf)

            # remove the merged vulns from the result xccdf
            for vuln in merged_vulns:
                if vuln in res_xccdf.vulns:
                    res_xccdf.vulns.remove(vuln)

            # if there are any vulns left in the result xccdf, append to plain list
            if res_xccdf.vulns:
                plain_xccdfs.append(res_xccdf)

        # set our xccdfs to the remaining ones in the plain list
        self.xccdfs = plain_xccdfs

    def addtemplate(self, filename, runcmds=False):
        '''
        Adds and applies a ckl template to this Ckl.

        filename should be csv filename 
        '''

        # flatten the Ckl prior to adding template
        self.flatten()

        # get list of all of our vulns
        vulns = []
        for xccdf in self.xccdfs:
            vulns.extend(xccdf.getvulns())

        # open file and read lines
        with open(filename) as f:
            csvlines = f.readlines()

        # clean first line as it's used for dictionary keys
        csvlines[0] = csvlines[0].replace(' ', '').lower()

        # parse and process each vuln template
        reader = csv.DictReader(csvlines)
        for vulntemp in reader:
            for vuln in vulns:
                if vulntemp['id'] == vuln.getid():

                    # set status
                    status = vulntemp['status'].replace(' ', '').lower()
                    if status == 'notreviewed':
                        vuln.status = Vuln.STATUS_NOT_REVIEWED
                    elif status == 'open':
                        vuln.status = Vuln.STATUS_OPEN
                    elif status == 'notafinding':
                        vuln.status = Vuln.STATUS_NOT_A_FINDING
                    elif status == 'notapplicable':
                        vuln.status = Vuln.STATUS_NOT_APPLICABLE

                    # set finding details and comments
                    if runcmds:
                        vuln.finding_details = runinlinecmds(
                            vulntemp['findingdetails'])
                        vuln.comments = runinlinecmds(vulntemp['comments'])
                    else:
                        vuln.finding_details = vulntemp['findingdetails']
                        vuln.comments = vulntemp['comments']

                    # set severity override
                    sevover = vulntemp['severityoverride'].replace(
                        ' ', '').lower()
                    if sevover == 'cati' or sevover == 'cat1':
                        vuln.severity_override = Vuln.SEVERITY_CAT_I
                    elif sevover == 'catii' or sevover == 'cat2':
                        vuln.severity_override = Vuln.SEVERITY_CAT_II
                    elif sevover == 'catiii' or sevover == 'cat3':
                        vuln.severity_override = Vuln.SEVERITY_CAT_III

                    # set severity override justification
                    vuln.severity_justification = vulntemp['severityoverridejustification']

    def sethostdata(self):
        '''Set this Ckl's host data from the local host.'''

        self.asset['HOST_NAME'] = socket.gethostname()
        self.asset['HOST_FQDN'] = socket.getfqdn()
        self.asset['HOST_IP'] = socket.gethostbyname(self.asset['HOST_NAME'])
        rawmac = str(hex(uuid.getnode()))[2:].upper()
        mac = ''
        for i in range(6):
            mac = mac + '-' + rawmac[i*2:(i*2)+2]
        self.asset['HOST_MAC'] = mac[1:]


class Xccdf():
    '''
    This class represents a set of xccdf data.

    source is a filename or file object containing XML data in xccdf format
    '''

    def __init__(self, source):

        # try to open, assume already open if wrong type
        try:
            xml = open(source)
        except TypeError:
            xml = source

        # setup instance vars
        self.attrs = {}
        self.vulns = []
        self.uuid = str(uuid.uuid4())
        self.hasresults = False
        self.results_tool = ''
        self.results_time = ''

        # parse the xml data, close the xml
        tree = ElementTree.parse(xml)
        xml.close()

        # setup xml namespace with default tag d, this is ugly, needfix
        self.ns = None
        if tree.getroot().tag[0] == '{':
            self.ns = {'d': tree.getroot().tag.split('}')[0][1:]}
            for e in tree.iter():
                if e.tag[-6:] == 'source':
                    self.ns['dc'] = e.tag.split('}')[0][1:]
                    break

        # build attrs dictionary
        self.attrs['version'] = tree.find('d:version', self.ns).text
        # NEEDFIX dont know where this value is coming from see ckl file
        self.attrs['classification'] = ''
        self.attrs['customname'] = ''
        self.attrs['stigid'] = tree.getroot().get('id')
        self.attrs['description'] = tree.find('d:description', self.ns).text
        self.attrs['filename'] = os.path.basename(xml.name)
        self.attrs['releaseinfo'] = tree.find('d:plain-text', self.ns).text
        self.attrs['title'] = tree.find('d:title', self.ns).text

        # this is not a bug, within ckl all vulns have same uuid (the xccdf uuid),
        # but "STIG_INFO" uuid differs, open a ckl as text and see for yourself...
        self.attrs['uuid'] = str(uuid.uuid4())

        self.attrs['notice'] = tree.find('d:notice', self.ns).get('id')
        self.attrs['source'] = tree.find(
            'd:reference', self.ns).find('dc:source', self.ns).text

        # get result info (if any), set that we have results
        if tree.find('d:TestResult', self.ns):
            testresult_el = tree.find('d:TestResult', self.ns)
            self.results_tool = testresult_el.get('test-system')
            self.results_time = testresult_el.get('start-time')
            self.hasresults = True

        # add the vulns
        for vuln_el in tree.findall('d:Group', self.ns):

            # check if any result elements apply to this vuln
            result = None
            if self.hasresults:
                for result_el in tree.find('d:TestResult', self.ns).findall('d:rule-result', self.ns):
                    if vuln_el.find('d:Rule', self.ns).get('id') == result_el.get('idref'):
                        result = result_el

            self.vulns.append(Vuln(vuln_el, self, result, self.ns))

    def getattrs(self):
        '''
        Return a dictionary with this Xccdf's attributes.

        Dictionary will have the following keys, with values that describe
        the Xccdf (some values may be empty strings):
         - version
         - classification
         - customname
         - stigid
         - description
         - filename
         - releaseinfo
         - title
         - uuid
         - notice
         - source
        '''

        return self.attrs

    def getref(self):
        '''
        Return the Reference string for this Xccdf.

        The Reference string is constructed from the title, version, and 
        release info strings.
        '''

        ref = self.attrs['title'] + ' :: Version ' + \
            self.attrs['version'] + ', ' + self.attrs['releaseinfo']
        return ref

    def getid(self):
        '''Return the ID of this Xccdf.'''
        return self.attrs['stigid']

    def getvulns(self):
        '''Return a list of Vuln() objects in this Xccdf.'''

        return self.vulns

    def getuuid(self):
        '''Return the uuid for this Xccdf as a string.'''

        return self.uuid

    def toelement(self):
        '''
        Return an Element object representing this Xccdf.

        Returns Element object (tag: iSTIG)
        '''

        # create iSTIG Element, this is the root element for this stig
        istig_el = ElementTree.Element('iSTIG')

        # add STIG_INFO Element, and subelements
        stig_info_el = ElementTree.SubElement(istig_el, 'STIG_INFO')
        for name, value in self.attrs.items():
            si_data_el = ElementTree.SubElement(stig_info_el, 'SI_DATA')
            sid_name_el = ElementTree.SubElement(si_data_el, 'SID_NAME')
            sid_name_el.text = name
            if value:
                sid_data_el = ElementTree.SubElement(si_data_el, 'SID_DATA')
                sid_data_el.text = value

        # add each vuln
        for vuln in self.vulns:
            istig_el.append(vuln.toelement())

        # return the root xml Element
        return istig_el

    def mergexccdf(self, xccdf):
        '''
        Merge xccdf results from another Xccdf object.

        Returns list of Vuln objects that were imported, or an empty list.
        '''

        imports = []

        for vuln in xccdf.getvulns():
            imported = False
            chkstr = vuln.attrs.get('Group_Title') + vuln.attrs.get('Rule_Ver')

            # attempt to match and import
            for myvuln in self.vulns:
                mychkstr = myvuln.attrs.get(
                    'Group_Title') + myvuln.attrs.get('Rule_Ver')

                # if matches, import results, set imported
                if chkstr == mychkstr:
                    myvuln.importresult(vuln)
                    imported = True

            if imported:
                imports.append(vuln)

        return imports


class Vuln():
    '''
    This class represents a single vulnerability.

    element should be the xml Element object to parse
    xccdf should be the parent Xccdf object
    result_element should be the result Element object for this Vuln
    namespace should be an xml namespace dict
    '''

    # Constants
    STATUS_NOT_REVIEWED = 'Not_Reviewed'
    STATUS_OPEN = 'Open'
    STATUS_NOT_A_FINDING = 'NotAFinding'
    STATUS_NOT_APPLICABLE = 'Not_Applicable'
    SEVERITY_CAT_I = 'high'
    SEVERITY_CAT_II = 'medium'
    SEVERITY_CAT_III = 'low'

    def __init__(self, element, xccdf, result_element=None, namespace=None):

        # setup instance vars
        self.parent = xccdf
        self.ns = namespace
        self.attrs = {}
        self.legacy_ids = []
        self.cci_refs = []

        self.status = Vuln.STATUS_NOT_REVIEWED
        self.finding_details = ''
        self.comments = ''
        self.severity_override = ''
        self.severity_justification = ''

        # build attrs dictionary
        rule = element.find('d:Rule', self.ns)
        self.attrs['Vuln_Num'] = element.attrib.get('id')
        self.attrs['Severity'] = rule.get('severity')
        self.attrs['Group_Title'] = element.find('d:title', self.ns).text
        self.attrs['Rule_ID'] = rule.get('id')
        self.attrs['Rule_Ver'] = rule.find('d:version', self.ns).text
        self.attrs['Rule_Title'] = rule.find('d:title', self.ns).text

        # parse the xml inside the rule description text
        desc_el = ElementTree.fromstring(
            '<desc>'+rule.find('d:description', self.ns).text+'</desc>')
        self.attrs['Vuln_Discuss'] = desc_el.find('VulnDiscussion').text
        self.attrs['IA_Controls'] = desc_el.find('IAControls').text

        # result xccdfs usually don't have this field, need to be careful
        self.attrs['Check_Content'] = None
        check_con_el = rule.find('d:check', self.ns).find(
            'd:check-content', self.ns)
        if ElementTree.iselement(check_con_el):
            self.attrs['Check_Content'] = check_con_el.text

        self.attrs['Fix_Text'] = rule.find('d:fixtext', self.ns).text
        self.attrs['False_Positives'] = desc_el.find('FalsePositives').text
        self.attrs['False_Negatives'] = desc_el.find('FalseNegatives').text
        self.attrs['Documentable'] = desc_el.find('Documentable').text
        self.attrs['Mitigations'] = desc_el.find('Mitigations').text
        self.attrs['Potential_Impact'] = desc_el.find('PotentialImpacts').text
        self.attrs['Third_Party_Tools'] = desc_el.find('ThirdPartyTools').text
        self.attrs['Mitigation_Control'] = desc_el.find(
            'MitigationControl').text
        self.attrs['Responsibility'] = desc_el.find('Responsibility').text
        self.attrs['Security_Override_Guidance'] = desc_el.find(
            'SeverityOverrideGuidance').text
        self.attrs['Check_Content_Ref'] = rule.find('d:check', self.ns).find(
            'd:check-content-ref', self.ns).get('name')
        self.attrs['Weight'] = rule.get('weight')
        # NEEDFIX dont know where this is coming from
        # (could be from filename starts with "U_" means unclass? "U_RHEL_7_STIG_V3R1_Manual-xccdf.xml")
        # (could be from "<?xml-stylesheet type='text/xsl' href='STIG_unclass.xsl'?>" in stig?)
        self.attrs['Class'] = ''
        self.attrs['STIGRef'] = self.getparent().getref()
        self.attrs['TargetKey'] = rule.find(
            'd:reference', self.ns).find('dc:identifier', self.ns).text
        self.attrs['STIG_UUID'] = self.getparent().getuuid()

        # setup list for legacy ID's, CCI References
        for ident in rule.findall('d:ident', self.ns):
            # account for both "SV-86483" and "V-71859"
            if ident.text[0:2] == 'V-' or ident.text[1:3] == 'V-':
                self.legacy_ids.append(ident.text)
            if ident.text[0:3] == 'CCI':
                self.cci_refs.append(ident.text)

        # update result vars if we got result
        if result_element:
            result = result_element.find('d:result', self.ns).text
            if result == 'pass':
                self.status = Vuln.STATUS_NOT_A_FINDING
            if result == 'fail':
                self.status = Vuln.STATUS_OPEN
            self.finding_details = 'Tool: ' + self.getparent().results_tool + '\nTime: ' + \
                self.getparent().results_time + '\nResult: ' + result

    def getparent(self):
        '''Return the parent Xccdf object for this Vuln.'''
        return self.parent

    def toelement(self):
        '''
        Return an Element object representing this Vuln.

        Returns Element object (tag: VULN)
        '''

        # add VULN Element, this is the root element for this Vuln
        vuln_el = ElementTree.Element('VULN')

        # define inner function to get xml Element from attribute
        def getattrxml(name, value):
            stig_data_el = ElementTree.Element('STIG_DATA')
            vuln_attribute_el = ElementTree.SubElement(
                stig_data_el, 'VULN_ATTRIBUTE')
            vuln_attribute_el.text = name
            attribute_data_el = ElementTree.SubElement(
                stig_data_el, 'ATTRIBUTE_DATA')
            attribute_data_el.text = value
            return stig_data_el

        # add each vuln attribute
        for name, value in self.attrs.items():
            vuln_el.append(getattrxml(name, value))

        # add each vuln legacy id attribute
        for legacy_id in self.legacy_ids:
            vuln_el.append(getattrxml('LEGACY_ID', legacy_id))

        # add each vuln cci ref attribute
        for cci_ref in self.cci_refs:
            vuln_el.append(getattrxml('CCI_REF', cci_ref))

        # add status, finding_details, etc. elements
        status_el = ElementTree.SubElement(vuln_el, 'STATUS')
        status_el.text = self.status
        finding_details_el = ElementTree.SubElement(vuln_el, 'FINDING_DETAILS')
        finding_details_el.text = self.finding_details
        comments_el = ElementTree.SubElement(vuln_el, 'COMMENTS')
        comments_el.text = self.comments
        sev_override_el = ElementTree.SubElement(vuln_el, 'SEVERITY_OVERRIDE')
        sev_override_el.text = self.severity_override
        sev_just_el = ElementTree.SubElement(vuln_el, 'SEVERITY_JUSTIFICATION')
        sev_just_el.text = self.severity_justification

        # return the root xml Element
        return vuln_el

    def getattrs(self):
        '''Return a dictionary containing this Vuln's attributes.'''
        return self.attrs

    def getid(self):
        '''Return the ID of this Vuln.'''
        return self.attrs.get('Vuln_Num')

    def importresult(self, vuln):
        '''
        Import result from another Vuln.

        vuln should be a Vuln object
        '''

        self.status = vuln.status
        self.finding_details = vuln.finding_details


def openstigzip(filename):
    '''
    Return STIG xml data from a STIG zip file.

    filename should be a path to a zip 

    Returns an open file object containing the STIG xml data
    '''

    stigzip = zipfile.ZipFile(filename)
    for innername in stigzip.namelist():
        if innername[-9:] == 'xccdf.xml':
            innerfile = stigzip.open(innername)
            break
    stigzip.close()
    return innerfile


def runinlinecmds(string, cmdtag='<cmd>'):
    '''
    Returns string with command output in place of tagged commands.

    string should be a string
    cmdtag should be start/end tag to identify commands

    string is split at every tag, every other substring is assumed to be a 
    command and is executed. The output of each command replaces the tagged 
    command in the string. Commands are run directly (not in a shell), both
    stdout and stderr output captured.
    '''

    # setup return var
    returnstring = ''

    # split string at cmdtag into string list
    strings = string.split(cmdtag)

    # start count at 0, assume every other string in list is a command since we
    # split at the tags
    count = 0
    for s in strings:
        count = count + 1

        # run command and append output
        if count % 2 == 0:
            compproc = subprocess.run(shlex.split(
                s), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            returnstring = returnstring + \
                str(compproc.stdout, encoding='utf-8')

        # append normal text
        else:
            returnstring = returnstring + s

    return returnstring
