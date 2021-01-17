""" Work in progress """

from xml.parsers.expat import ExpatError
from xml.dom.minidom import parseString, Document
import re

__all__ = ["AliasCommands", "load", "loads"]


class AliasCommands:
    """ Stores/manipulates alias commands """

    def __init__(self):
        self.aliases = {}

    def __repr__(self):
        return repr(self.aliases)

    def __setitem__(self, name, value):
        # Checks here...
        pass
        self.aliases[name] = str(value)

    def __getitem__(self, name):
        try:
            return self.aliases[name]
        except KeyError:
            raise KeyError(repr(name) + " is not an existing alias command")

    def __delitem__(self, name):
        try:
            del self.aliases[command]
        except KeyError:
            raise KeyError(repr(command) + " is not an existing alias command")

    def items(self):
        return self.aliases.items()

    def keys(self):
        return self.aliases.keys()

    def values(self):
        return self.aliases.values()

    def dump(self, file_obj, client):
        file_obj.write(self.dumps(client))

    def dumps(self, client):
        if client.lower() == "vrc":
            # Write to '.txt' format (VRC)
            output = ""
            for cmd, act in self.aliases.items():
                output += f"{cmd} {act}\n"
            return output
        elif client.lower() in ("vstars", "veram"):
            # Write to '.xml' format (vSTARS & vERAM)
            root = self.dumpxml()
            
            return root.toprettyxml(indent="  ")
        else:
            raise ValueError("unknown client " + repr(client))

    def dumpxml(self):
        doc = Document()
        root = doc.createElement("CommandAliases")
        for cmd, act in self.aliases.items():
            a = doc.createElement("CommandAlias")
            a.setAttribute("Command", cmd)
            a.setAttribute("ReplaceWith", act)
            root.appendChild(a)


def load(file_obj):
    return AliasCommands.loads(file_obj.read())

def loads(text):
    if text.strip().startswith("<"):
        # (xml)
        # Check if it's invalid xml
        try:
            doc = parseString(text)
        except ExpatError as e:
            raise ValueError(f"invalid xml at line {e.lineno} col {e.offset}")
        # Check if it doesn't have a <CommandAliases> tag
        try:
            root = doc.getElementsByTagName("CommandAliases")[0]
        except IndexError:
            raise KeyError("no <CommandAliases> tag found")
        # Begin loading
        ac = AliasCommands()  # Create AliasCommands
        for tag in root.getElementsByTagName("CommandAlias"):
            # Check if 'Command' exists
            if "Command" not in tag.attributes.keys():
                raise KeyError("'Command' attribute not found in " +
                    tag.toxml())
            # Check if 'ReplaceWith' exists
            if "ReplaceWith" not in tag.attributes.keys():
                raise KeyError("'ReplaceWith' not attribute found in " +
                    tag.toxml())
            ac[tag.getAttribute("Command")] = tag.getAttribute("ReplaceWith")
        return ac
    else:
        # (txt)
        # Split each line
        lines = text.strip().split("\n")
        # Being loading
        ac = AliasCommands()  # Create AliasCommands
        for line in lines:
            stripped_line = line.strip()
            # Skip lines that are comments
            if stripped_line.strip().startswith(";"):
                continue
            # Get the non-comment part of the line
            pattern = r"(\.\w+) ([^;]+)"
            match = re.match(pattern, stripped_line.strip())
            # Raise error if NO part of the line is valid
            if not match:
                raise ValueError("invalid line: " + repr(stripped_line))
            ac[match.group(1)] = match.group(2)
        return ac