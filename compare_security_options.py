#Run this in virtual machine
import subprocess
from subprocess import check_output
import argparse
import os

def find_changed_security_options(windows_type = "win10" ):   #or winserver

    good_security_file = "good_security_options.txt"  #windows_type
    vm_security_file = "vm_security.txt"

    """
    Ask to save file
    """
    while True:
        working_dir = os.path.dirname(os.path.realpath(__file__))
        print("In local Security Policy window, right click local policy → Security Options and select Export List")
        print("Please save the file as " + vm_security_file + " in the directory " + working_dir)
        prompt = "press any key to continue.."
        p_out = input(prompt)
        if os.path.exists(working_dir + "\\" + vm_security_file):
            break
        else:
            print("can not find the saved file")
    """
    Get security list from good service file
    """

    file_good = open(good_security_file, 'r')
    Lines = file_good.readlines()
    good_dict = {}
    # Strips the newline character
    for line in Lines:
        line_list = line.strip().split('\t')
        if len(line_list) >= 2:
            if "Enabled" in line_list[1] or "Disabled" in line_list[1]:
                good_dict[line_list[0].strip()] = line_list[1].strip()  #dict of name and status
            if "15 minutes" in line_list[1] or "Require 128-bit encryption" in line_list[1] or "Deny All Accounts  User must enter a password each time they use a key" in line_list[1]:
                good_dict[line_list[0].strip()] = line_list[1].strip()

    file_good.close()

    """
    Find security that are running in vm 
    """
    file_vm = open(vm_security_file, 'r')
    Lines = file_vm.readlines()
    vm_dict = {}
    # Strips the newline character
    for line in Lines:
        # ['Name', 'Description', 'Status', 'Startup', 'Type', 'Log', 'On', 'As']
        line_list = line.strip().split('\t')
        if len(line_list) >= 2:
            try:
                vm_dict[line_list[0].strip()] = line_list[1]  # dict of name and status
            except:
                continue

    file_vm.close()


    bad_option_list = []
    for item in good_dict.keys():
        if item in good_dict.keys() and item in vm_dict.keys():
            if good_dict[item] != vm_dict[item]:
                bad_option_list.append(item + " --> " + good_dict[item])

    #print bad service list
    index = 1
    for sts in bad_option_list:
        print(sts)
        index = index + 1

    if(len(bad_option_list) > 6):
        print("Warning!! There are " , len(bad_option_list) , " bad security (too many). Please verify before stopping security")

    print("Please change above settings in local policy → Security Options (manually)")
    """
    save security that were bad
    """
    if len(bad_option_list) > 0:
        with open(windows_type + "bad_security_log.txt", 'w') as f:
            for item in bad_option_list:
                f.write("%s\n" % item)


ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", type=str,
	default="winserver",
	help="win10 or winserver")
args = vars(ap.parse_args())

win_type = args["type"]
print(win_type)
find_changed_security_options(win_type)