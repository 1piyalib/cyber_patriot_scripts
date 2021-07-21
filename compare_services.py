#Run this in virtual machine
import subprocess
from subprocess import check_output
import argparse


def process_service_list(service_list):

    vm_services_list = []
    service_list.remove(service_list[0])
    service_list.remove(service_list[len(service_list)- 3]) #remove comments
    for service_item in service_list:
        if service_item == '' or "CCS Client" in service_item or "VMware" in service_item:
             continue
        else:
            vm_services_list.append(service_item.strip())
    return(vm_services_list)


def find_and_stop_services(windows_type = "win10" ):   #or winserver

    good_services_file = windows_type + "_good_services.txt"
    """
    Get current services running in vm using "net start" command
    """
    vm_services = check_output("net start", shell=True).decode()
    vm_services_list_temp = vm_services.split('\r\n')

    #clean up service list
    vm_services_list = process_service_list(vm_services_list_temp)

    """
    Get services list from good service file
    """

    file_good = open(good_services_file, 'r')
    Lines = file_good.readlines()
    good_list = []
    # Strips the newline character
    for line in Lines:
        #['Name', 'Description', 'Status', 'Startup', 'Type', 'Log', 'On', 'As']
        line_list = line.strip().split('\t')
        if "Running" in line_list[2] or "Started" in line_list[2]:
            good_list.append(line_list[0])  #dict of name and status
    file_good.close()

    """
    Find services that are running in vm that are not in good service list
    """
    bad_service_list = []
    for service in vm_services_list:
        if service not in good_list:
            bad_service_list.append(service)
    #print bad service list
    index = 1
    for sts in bad_service_list:
        print(str(index) + "." + sts)
        index = index + 1

    if(len(bad_service_list) > 6):
        print("Warning!! There are " , len(bad_service_list) , " bad services (too many). Please verify before stopping services")

    """
    Ask user which services they want to stop
    """
    services_to_stop_list = []
    prompt = "\r\nEnter files numbers you want to save (eg - 1,2,3 or none or all):"
    p_out = input(prompt)
    if ("none" in str(p_out).lower()):
        print("Stopped on user request")
    elif ("all" in str(p_out).lower()):
        services_to_stop_list = bad_service_list
    else:
        user_list = p_out.split(',')
        for service_num in user_list:
            if int(service_num)- 1 >= 0 and  int(service_num)- 1 < len(bad_service_list):
                services_to_stop_list.append(bad_service_list[int(service_num) - 1])

    """
    stop services. commands:
    # sc config "Name of Service" start= disabled
    # sc stop "Name of Service"
    """

    for service_to_stop in services_to_stop_list:
        print("stopping service: " + service_to_stop)
        try:
            service_name = ""
            outp = check_output("sc GetKeyName \"" + service_to_stop + "\"", shell=True).decode()
            if "SUCCESS" in outp and "Name" in outp:
                service_name = outp.split("=")[1].strip()
            if service_name != "":
                check_output("sc stop \"" + service_name + "\"", shell=True).decode()
                check_output("sc config \"" + service_name + "\" start= disabled", shell=True).decode()
            else:
                print("***********  error in stopping service ", service_to_stop, "*********************")
        except Exception as ex:
            print("***********  error in stopping service ", service_to_stop  , "*********************")
            #print("error: " , str(ex))



    """
    save services that were stopped in a file
    """
    with open(windows_type + "_stpped_services_log.txt", 'w') as f:
        for item in services_to_stop_list:
            f.write("%s\n" % item)




ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", type=str,
	default="winserver",
	help="win10 or winserver")
args = vars(ap.parse_args())

win_type = args["type"]
print(win_type)



find_and_stop_services(win_type)