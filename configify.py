prog = "configify"
vrs = "1.0"; # First version

import argparse, os, fnmatch, datetime
from xml import etree as ET
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET

today = datetime.date.today()
now = datetime.datetime.now().isoformat()

def initArgs():
    parser = argparse.ArgumentParser(description='Produce a Config xml from a TDI/SDI project')
    parser.add_argument('-p', metavar='--project', help='path to the TDI/SDI Project folder in workspace', required=True)
    parser.add_argument('-v', action='version', version='%(prog)s %(vrs)s')
    parser.add_argument('-n', metavar='--name', help='solution name/id for the Config')
    parser.add_argument('-o', metavar='--overwrite', help='overwrite property files to encrypt protected properties',
                            choices=['true','false','True','False'])
    parser.add_argument('-c', metavar='--config', help='filepath of the output Config xml (default is Project name)')

    args = parser.parse_args().__dict__
    args['o'] = (str(args['o']).lower() == 'true')

    proj = args['p']
    if proj.endswith("/") or proj.endswith("\\"):
        proj = proj[:len(proj) - 1]
    proj = os.path.split(proj)[1]

    if args['n'] is None:
        args['n'] = proj
    if args['c'] is None:
        args['c'] = proj + ".xml"

    print "args: %s" % args

    return args

# Scan only these project folders
folders = ['AssemblyLines', 'Connectors', 'Functions', 'Parsers', 'Scripts', 'AttributeMaps', 'Schema',
            'Properties', 'Schedules', 'Sequences', 'References']
# Default Log & Settings content
defcfgxml = """<Folder name="Config">
        <LogConfig name="Logging"/>
        <InstanceProperties name="AutoStart">
            <AutoStart/>
        </InstanceProperties>
        <TombstonesConfig name="Tombstones">
            <ModTime>1522233253918</ModTime>
            <parameter name="AssemblyLines">false</parameter>
            <parameter name="Configuration">false</parameter>
        </TombstonesConfig>
        <SolutionInterface name="SolutionInterface">
            <ModTime>1510918977144</ModTime>
            <PollInterval>-1</PollInterval>
            <InstanceID>GTS_LoadUsers</InstanceID>
            <enabled>true</enabled>
        </SolutionInterface>
        <Container name="SystemStore">
            <ParameterList name="Default"/>
        </Container>
    </Folder>"""

def defaultConfig():
    cfg = Element("MetamergeConfig")
    fld = SubElement(cfg, "Folder")
    fld.attrib['name'] = "Config"
    #print ET.tostring(cfg)
    xml = ET.fromstring(defcfgxml)
    #print ET.tostring(xml)
    for child in xml.findall('./*'):
        #print "\n>> " + ET.tostring(child)
        fld.append(child)
        #print "\n-- " + ET.tostring(subel)
        #print ET.tostring(cfg)
    #print ET.tostring(cfg)
    return cfg


def initConfig():
    #config = Element("MetamergeConfig")
    logsNsettings = os.path.join(args['p'], "Log & Settings")
    #print "Log & Settings: %s" % logsNsettings
    try:
        baseCfg = ET.parse(logsNsettings)
        print "** found Log & Settings"
        cfg = Element("MetamergeConfig")
        for child in baseCfg.getroot():
            cfg.append(child)
    except Exception as ex:
        print "** Exception reading Log & Settings: %s" % str(ex)
        print "** creating default basic config **"
        cfg = defaultConfig()

    cfg.attrib['IDIversion'] = 'Compiled by ' + prog + " v" + vrs + " - " + today.__format__('%Y-%m-%d')
    cfg.attrib['created'] = now
    cfg.attrib['createdBy'] = prog + " v" + vrs
    cfg.attrib['version'] = "7.1.1"

    for folder in folders:
        #print "Looking for %s" % folder
        if folder == "Properties":
            fld = cfg.find(".//Properties[@name='%s']" % folder)
        elif folder == "References":
            fld = cfg.find(".//Folder[@name='Includes']")
        else:
            fld = cfg.find(".//Folder[@name='%s']" % folder)

        if fld is None:
            #print "Adding folder %s" % folder
            if folder == "Properties":
                fld = SubElement(cfg, "Properties")
                fld.attrib['name'] = folder
            elif folder == "References":
                fld = SubElement(cfg, "Folder")
                fld.attrib['name'] = "Includes"
            else:
                fld = SubElement(cfg, "Folder")
                fld.attrib['name'] = folder

    return cfg


def files(path):
    parts = os.path.split(path[:len(path) - 1])
    type = parts[len(parts)-1]
    utype = type.lower()
    utype = type[:len(utype)-1]
    mask = "*." + utype
    #print "Using mask %s" % mask
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            #if fnmatch.filter(file, type):
                yield file

def dirs(path):
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            yield file

def scan(path):
    for dir in dirs(path):
        if dir == "Resources":
            scan(os.path.join(path, dir))
        elif dir in folders:
            print "checking %s" % dir

            if dir == "Properties":
                folder = config.find(".//Properties[@name='%s']" % dir)
            elif dir == "References":
                folder = config.find(".//Folder[@name='Includes']")
            else:
                folder = config.find(".//Folder[@name='%s']" % dir)

            if folder is None:
                raise Exception("Missing <Folder> with name = %s" % dir)

            if dir == "Properties":
                elemName = "PropertyStore"
            elif dir == "References":
                elemName = "Include"
            elif dir == "Schedules":
                elemName = "Scheduler"
            else:
                elemName = dir[:len(dir) - 1]

            #print "**** Looking for %s in %s" % (elemName, path + "/" + dir)
            for file in files(path + "/" + dir):
                #subfolder = SubElement(folder, type)
                #name = os.path.splitext(file)[0]
                #subfolder.attrib['name'] = name
                if file.find('Java-Properties') >= 0:
                    continue

                filepath = os.path.join(os.path.join(path,dir), file)
                xml = ET.parse(filepath)

                #print "Parsed file %s" % filepath
                if dir == "Properties":
                    parent = xml.findall(".//PropertyStore")
                    useFolder = folder.find("./Stores")
                    if useFolder is None:
                        useFolder = ET.SubElement(folder, "Stores")
                    folder = useFolder
                    #print "Folder set to %s" % ET.tostring(folder)
                elif dir == "References":
                    parent = xml.findall(".//Include")
                else:
                    parent = xml.getroot()

                for child in parent:
                    #print "Checking %s == %s" % (child.tag, elemName)
                    if child.tag == elemName:
                        try:
                            childName = file
                            p = childName.rfind(".")
                            if p > 0:
                                childName = childName[:p]
                                #print "--> reduced childName to %s from %s" % (childName, file)
                            #childName = child.attrib['name']
                            if childName.startswith("."):
                                childName = childName[1:]
                            if childName.endswith(".script"):
                                childName = childName[:len(childName) - 7]
                            if childName.endswith(".assemblyline"):
                                childName = childName[:len(childName) - 13]
                            child.attrib['name'] = childName
                            print " ..adding %s" % child.attrib['name']
                            folder.append(child)
                        except Exception as ex:
                            print "!! Skipping due to %s - %s" % (ex, child)
                            i = 42 # Skip those tag without the 'name' attribute

                #print '    <%s name="%s" />' % (type, name)
                i = 42 # do nothing


def saveConfig(config, path):
    print "saving %s" % path
    file = open(path, "w")
    #file.write(prettify(config))
    file.write(ET.tostring(config))
    file.close

def applyArgs():
    # Set the Solution Instance name
    config.find(".//SolutionInterface/InstanceID").text = args['n']

    # Now set auto-rewrite for all properties
    if args['o']:
        overwrite = 'true'
    else:
        overwrite = 'false'
    props = config.findall(".//PropertyStore")
    for prop in props:
        print "setting auto-rewrite to %s for %s Property Store" % (overwrite, prop.attrib['name'])
        rawctr = prop.find("./RawConnector")
        param = rawctr.find("./parameter[@name='autorewrite']")
        if param is None:
            param = Element("parameter");
            param.attrib['name'] = "autorewrite"
            rawctr.append(param)
            #print "Param: %s" % ET.tostring(param)
            #print "RawCTR: %s" % ET.tostring(rawctr)
            #print "New prop: %s" % ET.tostring(prop)
        param.text = overwrite

print "%s - Compiling config" % (prog + " v" + vrs)

args = initArgs()
config = initConfig()

# Compile Config
scan(args['p']);

# Adjust Config according to arguments
applyArgs()

#print ET.tostring(config)
saveConfig(config, args['c'])
