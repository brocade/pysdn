

from pybvc.common.utils import load_dict_from_file

from pybvc.applications.overlay_manager.overlay_mgr import Ovrly_mgr



def read_in_ovrly_cfg():

    f = "ovrly_mgr_cfg.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit()

    try:
        ctrlIpAddr = d['ctrlIpAddr']
        ctrlPortNum = d['ctrlPortNum']
        ctrlUname = d['ctrlUname']
        ctrlPswd = d['ctrlPswd']
        ctrlTimeOut = d['ctrlTimeOut']

        hvsrIp_1 = d['hvsrIp_1']
        hvsrPortNum_1 = d['hvsrPortNum_1']
        hvsrName_1 = d['hvsrName_1']
        hvsrIp_2 = d['hvsrIp_2']
        hvsrPortNum_2 = d['hvsrPortNum_2']
        hvsrName_1 = d['hvsrName_1']

        vtepName_1 = d['vtepName_1']
        vtepName_2 = d['vtepName_2']

        vniId_1 = d['vniId_1']
        vniId_2 = d['vniId_2']
    except:
        print ("Failed to get Controller and Node device attributes from Configuration file %s" %f)
        exit(0)

    return d

if __name__ == "__main__":

    vtep_hvsrA = {}
    vtep_hvsrB = {}


    # Read in the controller and overlay configuration
    doo = read_in_ovrly_cfg()

    # Configure VTEP 1 onto Hypervisor 1 and reference this set as vtep_hvsrA
    vtep_hvsrA['hvsrIp'] = doo['hvsrIp_1']
    vtep_hvsrA['hvsrPortNum'] = doo['hvsrPortNum_1']
    vtep_hvsrA['vtepName'] = doo['vtepName_1']
    vtep_hvsrA['hvsrName'] = doo['hvsrName_1']
    vtep_hvsrA['vtep_hvsr_name'] = doo['vtepName_1'] + doo['hvsrName_1']
    vtep_hvsrA['switchName'] = doo['switchName_1'] + doo['hvsrName_1']

    # Configure VTEP 1 onto Hypervisor 1 and reference this set as vtep_hvsrA
    vtep_hvsrB['hvsrIp'] = doo['hvsrIp_2']
    vtep_hvsrB['hvsrPortNum'] = doo['hvsrPortNum_2']
    vtep_hvsrB['vtepName'] = doo['vtepName_2']
    vtep_hvsrB['hvsrName'] = doo['hvsrName_2']
    vtep_hvsrB['vtep_hvsr_name'] = doo['vtepName_1'] + doo['hvsrName_2']
    vtep_hvsrB['switchName'] = doo['switchName_2'] + doo['hvsrName_2']

    # Instantiate the Overlay Manager
    overlay_manager = Ovrly_mgr(doo['ctrlIpAddr'], doo['ctrlPortNum'], doo['ctrlUname'],
                                doo['ctrlPswd'], doo['ctrlTimeOut'])

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to register the first Hypervisor: ")

    # Register the 1st hypervisor
    overlay_manager.register_hypervisor(doo['hvsrIp_1'], doo['hvsrPortNum_1'])

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to register the second Hypervisor: ")

    # Register the 2nd Hypervisor
    overlay_manager.register_hypervisor(doo['hvsrIp_2'], doo['hvsrPortNum_2'])

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to register a VTEP with the first Hypervisor: ")

    # Resister a VTEP with the 1st hypervisor
    overlay_manager.resister_vtep_on_hypervisor(vtep_hvsrA)

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to register a VTEP with the second Hypervisor: ")

    # Resister a VTEP with the 2nd hypervisor
    overlay_manager.resister_vtep_on_hypervisor(vtep_hvsrB)

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to build a tunnel between the VTEP Hypervisors: ")

    # Build a tunnel between the VTEP Hypervisors
    overlay_manager.create_tunnel_between_two_hypervisors( "g2_tunnel", doo['vniId_1'], vtep_hvsrA, vtep_hvsrB)

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to build a tunnel between the VTEP Hypervisors: ")

    # View VTEP Hypervisor #1 details
    overlay_manager.get_hypervisor_details(doo['hvsrIp_1'], doo['hvsrPortNum_1'])

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to build a tunnel between the VTEP Hypervisors: ")

    # View VTEP Hypervisor #2 details
    overlay_manager.get_hypervisor_details(doo['hvsrIp_2'], doo['hvsrPortNum_2'])

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to build a tunnel between the VTEP Hypervisors: ")

    # Delete VTEP Hypervisor #1
    overlay_manager.delete_hypervisor(doo['hvsrIp_1'], doo['hvsrPortNum_1'])

    # wait on input
    print "\n"
    user_input = raw_input("Press any key to build a tunnel between the VTEP Hypervisors: ")

    # Delete VTEP Hypervisor #2
    overlay_manager.delete_hypervisor(doo['hvsrIp_2'], doo['hvsrPortNum_2'])
