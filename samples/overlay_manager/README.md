Requirements
0. To install pip
        - On Linux
            $ sudo apt-get install python-pip
        - On Windows
            - Download https://raw.github.com/pypa/pip/master/contrib/get-pip.py being careful to save it 
              as a .py file rather than .txt. 
            - Then, run it from the command prompt.
            $ python get-pip.py
                
1. To install globally with pip (if you have pip 1.3 or greater installed globally):
        $ sudo pip install virtualenv

2. Create your local virtual environment
        $ virtualenv <give-it-a-name>
        $ cd <your-name-dir>
        $ source bin/activate
        - You will see the name of the directory in you command prompt
        
                
3. To install pysdn # which contains the sample ovrly_manager_script
        $ git clone https://github.com/brocade/pysdn.git
        
4. To setup the script for your environment
        $ cd /pysdn/samples/overlay_manager/
        $ chmod +x ovrly_mgr_script.py

        - Edit the following file /pysdnc/samples/overlay_manager/ovrly_mgr.yml

            # Controller
            ctrlIpAddr: <env-ip-addr>
            ctrlPortNum: 8181
            ctrlUname: "admin"
            ctrlPswd: "admin"
            ctrlTimeOut: "5"
            
            # Hypervisors
            hvsrIp_1: <env-hypervisor_ip-addr-1>
            hvsrPortNum_1: 16640
            hvsrName_1: "Hypervisor1"  # you can change this name 
            switchName_1: "Switch1"    # you can change this name
            
            hvsrIp_2: <env-hypervisor_ip-addr-2>
            hvsrPortNum_2: 16640
            hvsrName_2: "Hypervisor2"  # you can change this name
            switchName_2: "Switch2"    # you can change this name
            
            # VTEPs
            vtepName_1: "vtep1"        # you can change this name
            vtepName_2: "vtep2"        # you can change this name
            
            # VXLAN Identifiers
            vniId_1: 100               # you can change this id number
            vniId_2: 200               # you can change this id number

5. To run the script        
        - From terminal type, 
            $ ./ovly_mgr_script.py
            
            Results:
            - The "ovrly_mgr_script will run the following operations in order...
                1. Register the first hypervisor (#1)
                2. Register the second hypervisor (#2)
                3. Register vtep #1 on the first hypervisor (#1)
                4. Register vtep #2 on the second hypervisor (#2)
                5. Build a tunnel between the two VTEPs
                6. Get details of the first hypervisor (#1)
                7. Get details of the second hypervisor (#2)
                8. Delete the first hypervisor (#1)
                9. Delete the second hypervisor (#2)
            - The user will be prompted to enter any key to initiate each operation before running it
            - The user will see RESTCONF response codes, as well as some RESTCONF parameters displayed 
        
        
        
        

