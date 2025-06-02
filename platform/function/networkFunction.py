#! /usr/bin/env python

# Hugo Chargois - 17 jan. 2010 - v.0.1
# Parses the output of iwlist scan into a table

# You can add or change the functions to parse the properties
# of each AP (cell) below. They take one argument, the bunch of text
# describing one cell in iwlist scan and return a property of that cell.

import re
import subprocess
import os
import netifaces as ni
from netifaces import AF_INET

class networkFunction():
    def getSSID(interface):
        try:
            ssid = os.popen("iw dev " + interface + " link | grep SSID").read()
            ssid = ssid.replace('SSID:','')
            ssid = ssid.replace('\n','')
            ssid = ssid.replace('\t ','')
            if ssid == '':
                ssid = '-'
        except:
            ssid = 'N/A'
        return ssid

    def getInterface(interface):
        try:
            state = subprocess.check_output("cat /sys/class/net/"+interface+"/operstate", shell=True)
            state = state.decode("utf-8")
            state = state.replace("\n","")
            if "eth" in interface:
                tipe = 0
            else:
                tipe = 1
            iface = ni.ifaddresses(interface)
            mac = iface[17][0]['addr']
            if len(iface) == 3:
                ip = ni.ifaddresses(interface)[AF_INET][0]['addr']
            else:
                ip = '-'
        except:
            ip = 'N/A'
        return ip

def get_name(cell):
    """ Gets the name / essid of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The name / essid of the network.
    """

    return matching_line(cell, "ESSID:")[1:-1]

def get_quality(cell):
    """ Gets the quality of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The quality of the network.
    """

    quality = matching_line(cell, "Quality=").split()[0].split("/")
    return str(int(round(float(quality[0]) / float(quality[1]) * 100)))


def get_signal_level(cell):
    """ Gets the signal level of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The signal level of the network.
    """
    signal = matching_line(cell, "Signal level=").split("=")[1].split("/")
    return str(signal[0])

def get_channel(cell):
    """ Gets the channel of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The channel of the network.
    """


    channel = matching_line(cell, "Channel:")
    if channel:
        return channel
    frequency = matching_line(cell, "Frequency:")
    channel = re.sub(r".*\(Channel\s(\d{1,2})\).*", r"\1", frequency)
    return channel

def get_encryption(cell):
    """ Gets the encryption type of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The encryption type of the network.
    """

    enc = ""
    if matching_line(cell, "Encryption key:") == "off":
        enc = "Open"
    else:
        for line in cell:
            matching = match(line,"IE:")
            if matching != None:
                wpa = match(matching,"WPA Version ")
                if wpa != None:
                    enc = "WPA v." + wpa
        if enc == "":
            enc = "WEP"
    return enc

def get_address(cell):
    """ Gets the address of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The address of the network.
    """

    return matching_line(cell, "Address: ")

def get_bit_rates(cell):
    """ Gets the bit rate of a network / cell.
    @param string cell
        A network / cell from iwlist scan.
    @return string
        The bit rate of the network.
    """

    return matching_line(cell, "Bit Rates:")

# Here you can choose the way of sorting the table. sortby should be a key of
# the dictionary rules.

def sort_cells(cells):
    sortby = "Quality"
    reverse = True
    cells.sort(None, lambda el:el[sortby], reverse)


# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point

def matching_line(lines, keyword):
    """ Returns the first matching line in a list of lines.
    @see match()
    """
    for line in lines:
        matching = match(line,keyword)
        if matching != None:
            return matching
    return None

def match(line, keyword):
    """ If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise checks if keyword is
    anywhere in the line and returns that section, else returns None"""

    line = line.lstrip()
    length = len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        if keyword in line:
            return line[line.index(keyword):]
        else:
            return None

def parse_cell(cell, rules):
    """ Applies the rules to the bunch of text describing a cell.
    @param string cell
        A network / cell from iwlist scan.
    @param dictionary rules
        A dictionary of parse rules.
    @return dictionary
        parsed networks. """

    parsed_cell = {}
    for key in rules:
        rule = rules[key]
        parsed_cell.update({key: rule(cell)})
    return parsed_cell



def print_cells(cells, columns):
    table = [columns]
    for cell in cells:
        cell_properties = []
        for column in columns:
            if column == 'Quality':
                # make print nicer
                cell[column] = cell[column].rjust(3) + " %"
            cell_properties.append(cell[column])
        table.append(cell_properties)
    #print_table(table)

def get_parsed_cells(interface,rules=None):
    """ Parses iwlist output into a list of networks.
        @param list iw_data
            Output from iwlist scan.
            A list of strings.
        @return list
            properties: Name, Address, Quality, Channel, Encryption.
    """

    # Here's a dictionary of rules that will be applied to the description
    # of each cell. The key will be the name of the column in the table.
    # The value is a function defined above.
    proc = subprocess.Popen(["iwlist", interface, "scan"],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()
    iw_data = out.split("\n")
    rules = {
        "Name": get_name,
        "Quality": get_quality,
        "Channel": get_channel,
        "Encryption": get_encryption,
        "Address": get_address,
        "Signal Level": get_signal_level,
        "Bit Rates": get_bit_rates,
    }

    cells = [[]]
    parsed_cells = []

    for line in iw_data:
        cell_line = match(line, "Cell ")
        if cell_line != None:
            cells.append([])
            line = cell_line[-27:]
        cells[-1].append(line.rstrip())

    cells = cells[1:]

    for cell in cells:
        parsed_cells.append(parse_cell(cell, rules))

    #sort_cells(parsed_cells)
    return parsed_cells

