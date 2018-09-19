import os
import sys
import time
import itertools
import ipaddress
import configparser
import logging
import logging.config

class Logging:
    init = False
    def __new__(cls, *args, **kw):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logging, cls).__new__(cls, *args, **kw)
        return cls.instance

    def __init__(self):
g       if self.init:
            return

        self.init = True
        self.logger = self.getLogger()

    def getLogger(self):
        logging.config.fileConfig("autolearn.cfg")
        root = logging.getLogger()
        logger = logging.getLogger("autolearn_Logger")
        return logger

    def info(self, *args):
        args_tmp = []
        for i in range(0,len(args)):
            args_tmp.append(str(args[i]))
        msg = "".join(args_tmp)
        self.logger.info(msg)

    def debug(self, *args):
        args_tmp = []
        for i in range(0,len(args)):
            args_tmp.append(str(args[i]))
        msg = "".join(args_tmp)
        self.logger.debug(msg)

    def warning(self, *args):
        args_tmp = []
        for i in range(0,len(args)):
            args_tmp.append(str(args[i]))
        msg = "".join(args_tmp)
        self.logger.warning(msg)
        
    def error(self, *args):
        args_tmp = []
        for i in range(0,len(args)):
            args_tmp.append(str(args[i]))
        msg = "".join(args_tmp)
        self.logger.error(msg)



class Gloabal_Var:
    ###flag
    #FLAG_ALREADLY_CONFIG = False
    NEED_UPDATE_CONFIG = False

    FLAG_LOAD_CONFIG = True 
    NOLOOP = False
    FLAG_ONLY_CHECK = False

    ###switch g06 ip
    FLAG_IP_CONFIG = False
    
    ###load config 
    AUTO_LEARN_CONF_OTHER = r'./autolearn.cfg'
    AUTO_LEARN_CONF_78 = r'/roofs/cup1/autolearn.cfg'

    ###cdr  get  result_file 
    CDR_IP_LIST_DUMP_COMMAND = r'./cdr_ip_list_dump'

    ###result_file
    CHECK_RESULT_FILE = "check_result.csv"
    CHECK_RESULT_FILE_CUR = "check_result.csv.cur"
              
    DEB_CONFIG = r's1_mme.conf' 
    SGS_CONFIG = r'sgs_mme.conf'
    HSS_CONFIG = r's6a_mme.conf'
    SGW_CONFIG = r's11_mme.conf'
    GGSN_C_CONFIG = r'ggsn_c.conf'
    S5S8_C_CONFIG = r's5s8_c.conf'
    SGW_C_CONFIG = r'sgw_c.conf'
    PGW_C_CONFIG = r'pgw_c.conf'
    LOCAL_S5S8_C_CONFIG = r'local_s5s8_c.conf'
    LOCAL_SGSN_C_CONFIG = r'local_sgsn_c.conf'
    S11_AND_S5S8_CONF = r's11_and_s5s8.conf' 
    SGSN_C_CONFIG = r'sgsn_c.conf'
    ASSOCIATE_CONFIG = r'associate.conf'
    ASSOCIATE_SAV= r'associate.sav'
    RC_LOAD_CONF = r'auto_learn_result.cfg'  
    RC_IPV6_LOAD_CONF = r'auto_learn_ipv6_result.cfg'  

    ###count 
    COMMAND_HISTORY = r'./autolearn_stat'
    LOOP_TIMES = 0

    ### 5 seconds
    TIME_DELAY_BASE = 5 
    ### 5 seconds
    TIME_DELAY_STEP = 5

    ###PPS mode
    PPS_PORT = 8080
    PPS_SYSTEM = 1
    PPS_SERVICE = 2

    SIC_CPU1_PORT = 9090
    SIC_CPU2_PORT = 9091
    SIC_SYSTEM = 1
    SIC_SERVICE = 2
    SIC_STAT = 3



class Base_Cfg:
    ######protect value
    ######Please change here when necessary
    ######Defalut config is G33 
    #type_supports_ipv6
    _flag_ipv6 = False
    _ipv6_rule_min_id = 50
    _ipv6_rule_max_id = 1500

    _ipv4_rule_min_id = 50
    _ipv4_rule_max_id = 1500

    _pf_rule_min_id = 50
    _pf_rule_max_id = 1500

    _pf_ipv6_rule_min_id = 1
    _pf_ipv6_rule_max_id = 128

    ###bulid action 
    _action_id_base = 500
    _action_no_modeid_id_base = _action_id_base + 40

    ###ipv6 vlan id
    _vlan_id_base = 500

    ###init local command
    _localhost_ip = '127.0.0.1'
    _rule_id_local = 2048
    _action_id_local = 93
    _autolearn_to_cpu_port = ""

    ###init command
    _lag_sic = 1000 
    _lag_autolearn = 999
    _mirror_lag_action_id = 1000

    _sp_dp_port = 2123  
    _proto = 132 

    _lag_sic_ctrl_egress = 998
    ######

    local_modeid = 0
    dev_plat = ""

    pf_rule_id_queue = [i for i in range(_pf_rule_min_id, _pf_rule_max_id)]
    pf_rule_ipv6_id_queue = [i for i in range(_pf_ipv6_rule_min_id, _pf_ipv6_rule_max_id)]
    ipv4_rule_id_queue = [i for i in range(_ipv4_rule_min_id, _ipv4_rule_max_id)]
    ipv6_rule_id_queue = [i for i in range(_ipv6_rule_min_id, _ipv6_rule_max_id)]

    phy_l4_srcport_rule_id = 0
    phy_l4_dstport_rule_id = 0
    phy_l3_protocol_rule_id = 0
    phy_l4_srcport_rule_ipv6_id = 0
    phy_l4_dstport_rule_ipv6_id = 0
    phy_l3_protocol_rule_ipv6_id = 0

    pf_rule_id_dict = {}
    pf_rule_ipv6_id_dict = {}

    rule_id_dict = {}
    rule_ipv6_id_dict = {}

    remote_rule_id_dict = {}
    remote_rule_ipv6_id_dict = {}

    autolearn_rules = []
    autolearn_ipv6_rules = []
    #not autolean rule id and id in autolearn id range 
    other_rules = []
    other_ipv6_rules = []
   
    sic_ingress_ports = ""
    autolearn_ingress_ports = ""
    sic_ctrl_string = ""
    sic_ctrl_egress = ""
    pps_ip = ""

    gn_load_balance = False
    pps_ingress_ports = ""
    sic_stcp_default_egress = ""
    sic_s11_default_egress = ""
    pps_to_autolearn_port = ""
    autolearn_to_pps_port = ""
    pps_port_num = 0

    load_balance_index_list = []
    s1_mme_ip_list = []
    msc_ip_list = []
    s61_mme_ip_list = []
    sgw_ip_list = []
    s11_mme_ip_list = []
    s11_s5s8_ip_list = []

    local_sgsn_c_ip_list = []
    sgsn_c_ip_list = []
    local_s5s8_c_ip_list = []
    s5s8_c_ip_list = []

    #log 
    logger = Logging()

    def _get_autolearn_config(self):
        try:
            f = open(Gloabal_Var.RC_LOAD_CONF, mode = "rt", encoding = "utf-8")
            lines = f.readlines()
            for line in lines:
                word = line.split(" ")
                if word[0] == "bind":
                    ###full_mash
                    if word[4] == "tuple":
                        self.autolearn_rules.append(int(word[8]))
                    ###full_mash
                    elif word[4] == "ipset":
                        self.autolearn_rules.append(int(word[6]))
                    ###other
                    else:
                        self.autolearn_rules.append(int(word[4]))
            f.close()
        except Exception as e:
            self.logger.error(e)

        try:
            f = open(Gloabal_Var.RC_IPV6_LOAD_CONF, mode= "rt", encoding = "utf-8")
            lines = f.readlines()
            for line in lines:
                word = line.split(" ")
                if word[0] == "bind":
                    if word[4] == "tuplev6":
                        self.autolearn_ipv6_rules.append(int(word[8]))
            f.close()
        except Exception as e:
            self.logger.error(e)

    

    def _pf_rule_get_id(self):
        if len(self.pf_rule_id_queue) == 0:
            return None
        else:
            return self.pf_rule_id_queue.pop()

    def _pf_ipv6_rule_get_id(self):
        if len(self.pf_rule_ipv6_id_queue) == 0:
            return None
        else:
            return self.pf_rule_id_queue.pop()
    
    def _ipv4_rule_get_id(self):
        if len(self.ipv4_rule_id_queue) == 0:
            return None
        else:
            return self.ipv4_rule_id_queue.pop()

    def _ipv6_rule_get_id(self):
        if len(self.ipv6_rule_id_queue) == 0:
            return None
        else:
            return self.ipv6_rule_id_queue.pop()


    def _pf_rule_put_id(self, ruleid):
        if ruleid not in self.pf_rule_id_queue:
            self.pf_rule_id_queue.append(ruleid)
            self.pf_rule_id_queue.sort()

    def _pf_ipv6_rule_put_id(self, ruleid):
        if ruleid not in self.pf_rule_id_queue:
            self.pf_rule_ipv6_id_queue.append(ruleid)
            self.pf_rule_ipv6_id_queue.sort()

    def _ipv4_rule_put_id(self, ruleid):
        if ruleid not in self.ipv4_rule_id_queue:
            self.ipv4_rule_id_queue.append(ruleid)
            self.ipv4_rule_id_queue.sort()


    def _ipv6_rule_put_id(self, ruleid):
        if ruleid not in self.ipv6_rule_id_queue:
            self.ipv6_rule_id_queue.append(ruleid)
            self.ipv6_rule_id_queue.sort()


    def _get_local_modeid(self):
        os.system("./rpcc {0} {1} {2} 'show mymodid' 10 > ./modeid".format(self.pps_ip, Gloabal_Var.PPS_PORT, Gloabal_Var.PPS_SYSTEM))
        with open("./modeid", "rt", encoding = "utf-8") as f:
            lines = f.readlines()
            for line in lines:
                modeid = line.split()
                self.logger.debug(modeid)
                if modeid[0] == "My":
                    self.local_modeid = modeid[3] 
                    break


    #pbmp is port
    def _build_pf_pbmp_action_str(self, port_action_id, modeid = ""):
        if modeid == "":
            action_id = int(port_action_id) + self._action_no_modeid_id_base
            return "set action_id {0} forward port {1}".format(action_id, port_action_id), action_id
        else:
            #debug
            self.logger.debug(port_action_id)

            action_id = int(port_action_id) + ( int(modeid)*2 + self._action_id_base )
            return "set action_id {0} forward port {1} modid {2}".format(action_id, port_action_id, modeid), action_id


    #trunk is lag
    def _build_pf_trunk_action_str(self, lag_action_id):
        return "set action_id {0} forward lag {1}".format(lag_action_id, lag_action_id)

    #Determine whether IP is ipv4 or ipv6
    def _determine_ip_type(self, a_ip, b_ip, ip_type = None):
        if ip_type == None:
            type_str = "ipv4"
            if self._flag_ipv6 == False:
                return type_str
            ###Use the ipv4 rule when there is no IP
            if a_ip == "" and b_ip == "":
                return type_str
            if a_ip.find(".") >= 0 and b_ip.find(".") >= 0 :
                type_str = "ipv4"
            elif a_ip.find(":") >= 0 or b_ip.find(":") >= 0:
                type_str = "ipv6"
        else:
            type_str = ip_type
        return type_str

    def _build_pf_rule_command(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid):
        ip_type = self._determine_ip_type(srcip, dstip)
        self.logger.debug("%s%s ip_type is "%(srcip,dstip), ip_type)
        if ip_type == "ipv4":
            base_rule_str = "set rule %s vlan outervlan any "%str(rule_id)
        elif ip_type == "ipv6":
            base_rule_str = "set rule_ipv6 %s vlan any "%str(rule_id)

        if srcip != "":
            base_rule_str = base_rule_str + "sip %s "%srcip
        else:
            base_rule_str = base_rule_str + "sip any "
        if dstip != "":
            base_rule_str = base_rule_str + "dip %s "%dstip
        else:
            base_rule_str = base_rule_str + "dip any "
        if l4srcport != "":
            base_rule_str = base_rule_str + "sp %s "%str(l4srcport)
        else:
            base_rule_str = base_rule_str + "sp any "
        if l4dstport != "":
            base_rule_str = base_rule_str + "dp %s "%str(l4dstport)
        else:
            base_rule_str = base_rule_str + "dp any "
        if ipprotocol != "":
            base_rule_str = base_rule_str + "proto %s "%str(ipprotocol)
        else:
            base_rule_str = base_rule_str + "proto any "
        if prio != "":
       	    base_rule_str = base_rule_str + "priority %s"%str(prio)
       	else:
       	    base_rule_str = base_rule_str + "priority any "

        action_str = ""
        if port_action_id != "":
            action_str,action_id = self._build_pf_pbmp_action_str(port_action_id, modeid)
            cmd = [
                    "unbind port {0} rule {1}\n".format(inports, rule_id),
                    "delete rule {0}\n".format(rule_id),
                    "{0}\n".format(action_str),
                    "{0}\n".format(base_rule_str),
                  ]
            if ip_type == "ipv4":
                cmd.append("bind port {0} rule {1} action_id {2}\n".format(inports, rule_id, action_id))
            elif ip_type == "ipv6":
                cmd.append("bind port {0} rule_ipv6 {1} action_id {2}\n".format(inports, rule_id, action_id))
        elif lag_action_id != "":
            action_str,action_id= self._build_pf_trunk_action_str(lag_action_id)
            cmd = [
                    "unbind port {0} rule {1}\n".format(inports, rule_id),
                    "delete rule {0}\n".format(rule_id),
                    "{0}\n".format(action_str),
                    "{0}\n".format(base_rule_str),
                  ]
            if ip_type == "ipv4":
                cmd.append("bind port {0} rule {1} action_id {2}\n".format(inports, rule_id, action_id))
            elif ip_type == "ipv6":
                cmd.append("bind port {0} rule_ipv6 {1} action_id {2}\n".format(inports, rule_id, action_id))
        return cmd

    def _build_fp_rule_command_ipv4(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid):
        #sf-sic
        base_rule_str = "set access-list tuple group default rule %s "%str(rule_id)
        if srcip != "":
            base_rule_str = base_rule_str + "sip %s "%srcip
        else:
            base_rule_str = base_rule_str + "sip any "
        if dstip != "":
            base_rule_str = base_rule_str + "dip %s "%dstip
        else:
            base_rule_str = base_rule_str + "dip any "
        if l4srcport != "":
            base_rule_str = base_rule_str + "sp %s "%str(l4srcport)
        else:
            base_rule_str = base_rule_str + "sp any "
        if l4dstport != "":
            base_rule_str = base_rule_str + "dp %s "%str(l4dstport)
        else:
            base_rule_str = base_rule_str + "dp any "
        if ipprotocol != "":
            base_rule_str = base_rule_str + "proto %s "%str(ipprotocol)
        else:
            base_rule_str = base_rule_str + "proto any "
        base_rule_str = base_rule_str + "vlan any "

        cmd = []
        if port_action_id != "":
            #sf-sic
            #sic_ingress_ports
            if inports == self.sic_ingress_ports:
                ingress_interface = 3
                action_id = self._sf_action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}".format( action_id, vlan_id )
                cmd = [
                        #"set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} port {1}\n".format( vlan_id, ingress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n",
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build remote cmd for sf-sic:", cmd)
            #autolearn_ingress_ports
            elif inports == self.autolearn_ingress_ports:
                ingress_interface = 2 
                action_id = self._sf_action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}\n".format( action_id, vlan_id )
                cmd = [
                        #"set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} port {1}\n".format( vlan_id, ingress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n",
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build autolearn cmd for sf-sic:", cmd)

            #Controlled device PF
            pf_cmd = ["vlan create {0} ports {1} untag {1}\n".format( vlan_id, port_action_id)]
            self.send_command(pf_cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        if lag_action_id != "":
            #sf-sic
            #sic_ingress_ports
            if lag_action_id == self._lag_sic_ctrl_egress:
                ingress_interface = 3
                action_id = self._sf_action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}".format( action_id, vlan_id )
                cmd = [
                        #"set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} port {1}\n".format( vlan_id, ingress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n",
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build remote cmd for sf-sic user lag:", cmd)
            #debug
            self.logger.debug("build remote pf lags ports:", self.sic_ctrl_egress)
            #Controlled device PF
            pf_cmd = ["vlan create {0} ports {1} untag {1}\n".format( vlan_id, self.sic_ctrl_egress)]
            self.send_command(pf_cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        return cmd


    def _build_fp_rule_command_ipv6(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid):
        #sf-sic
        base_rule_str = "set access-list tuplev6 group default rule %s "%str(rule_id)
        if srcip != "":
            base_rule_str = base_rule_str + "sip %s "%srcip
        else:
            base_rule_str = base_rule_str + "sip any "
        if dstip != "":
            base_rule_str = base_rule_str + "dip %s "%dstip
        else:
            base_rule_str = base_rule_str + "dip any "
        if l4srcport != "":
            base_rule_str = base_rule_str + "sp %s "%str(l4srcport)
        else:
            base_rule_str = base_rule_str + "sp any "
        if l4dstport != "":
            base_rule_str = base_rule_str + "dp %s "%str(l4dstport)
        else:
            base_rule_str = base_rule_str + "dp any "
        if ipprotocol != "":
            base_rule_str = base_rule_str + "proto %s "%str(ipprotocol)
        else:
            base_rule_str = base_rule_str + "proto any "
        base_rule_str = base_rule_str + "vlan any "

        cmd = []
        if port_action_id != "":
            #sf-sic
            #sic_ingress_ports
            if inports == self.sic_ingress_ports:
                ingress_interface = 3
                action_id = self._sf_action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}".format( action_id, vlan_id )
                cmd = [
                        #"set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} port {1}\n".format( vlan_id, ingress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n",
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build remote cmd for sf-sic:", cmd)
            #autolearn_ingress_ports
            elif inports == self.autolearn_ingress_ports:
                ingress_interface = 2 
                action_id = self._sf_action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}\n".format( action_id, vlan_id )
                cmd = [
                        #"set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} port {1}\n".format( vlan_id, ingress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n",
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build autolearn cmd for sf-sic:", cmd)

            #Controlled device PF
            pf_cmd = ["vlan create {0} ports {1} untag {1}\n".format( vlan_id, port_action_id)]
            self.send_command(pf_cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        if lag_action_id != "":
            #sf-sic
            #sic_ingress_ports
            if lag_action_id == self._lag_sic_ctrl_egress:
                ingress_interface = 3
                action_id = self._sf_action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}".format( action_id, vlan_id )
                cmd = [
                        #"set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} port {1}\n".format( vlan_id, ingress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n",
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build remote cmd for sf-sic user lag:", cmd)
            #debug
            self.logger.debug("build remote pf lags ports:", self.sic_ctrl_egress)
            #Controlled device PF
            pf_cmd = ["vlan create {0} ports {1} untag {1}\n".format( vlan_id, self.sic_ctrl_egress)]
            self.send_command(pf_cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        return cmd


    def _build_fp_rule_command(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid):
        ip_type = self._determine_ip_type(srcip, dstip)
        self.logger.debug("%s%s ip_type is "%(srcip,dstip), ip_type)
        if ip_type == "ipv4":
            cmd = self._build_fp_rule_command_ipv4(inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
        elif ip_type == "ipv6":
            cmd = self._build_fp_rule_command_ipv6(inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
        return cmd


    def send_command(self, commands_list, ip, type, *port):
        if len(commands_list):
            for cmd in commands_list:
                cmd = cmd.strip("\n")
                if len(port) != 0:
                    this_cmd = "./rpcc %s %s %s '%s' 10"%(ip, str(port[0]), str(type), cmd)
                else:
                    this_cmd = "./rpcc %s 8080 %s '%s' 10"%(ip, str(type), cmd)

                #debug
                self.logger.debug(this_cmd)

                flag = os.system(this_cmd)
                while(True):
                    if flag == 0 or flag == 65280:
                        self.logger.debug("send command success!")
                        break;
                    else:
                        self.logger.error("send command failed!",this_cmd)
                        time.sleep(2)
                        flag = os.system(this_cmd)
        

    def build_remote_cmd(self, inports = "", srcip = "", dstip = "", l4srcport = "", l4dstport = "", ipprotocol = "", port_action_id = "", lag_action_id = "", rule_id = None, prio = None):
        #ipv4 or ipv6
        ip_type = self._determine_ip_type(srcip, dstip)
        if rule_id == None:
            if ip_type == "ipv4":
                rule_id = self._ipv4_rule_get_id()
            elif ip_type == "ipv6":
                rule_id = self._ipv6_rule_get_id()
        if prio == None:
            prio = rule_id
        modeid = self.local_modeid
        cmd = self._build_fp_rule_command(inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
        if len(cmd):
            if ip_type == "ipv4":
                self.remote_rule_id_dict[rule_id] = (inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
            elif ip_type == "ipv6":
                self.remote_rule_ipv6_id_dict[rule_id] = (inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
            return (rule_id, ip_type)
        else:
            return None


    def do_install_pf_rule(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id = None, prio = None, ip_type = None):
        #ipv4 or ipv6 
        ip_type = self._determine_ip_type(srcip, dstip, ip_type)
        if rule_id == None:
            if ip_type == "ipv4":
                rule_id = self._pf_rule_get_id()
            elif ip_type == "ipv6":
                rule_id = self._pf_ipv6_rule_get_id()
        if prio == None:
            prio = rule_id
        modeid = self.local_modeid
        cmd = self._build_pf_rule_command(inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
        if len(cmd):
            if ip_type == "ipv4":
                self.send_command(cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE) 
                self.pf_rule_id_dict[rule_id] = (inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
            elif ip_type == "ipv6":
                self.send_command(cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE) 
                self.pf_rule_ipv6_id_dict[rule_id] = (inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
            return (rule_id, ip_type)
        else:
            return None

    def do_install_fp_rule(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id = None, prio = None):
        #ipv4 or ipv6 
        ip_type = self._determine_ip_type(srcip, dstip)
        if rule_id == None:
            if ip_type == "ipv4":
                rule_id = self._ipv4_rule_get_id()
            elif ip_type == "ipv6":
                rule_id = self._ipv6_rule_get_id()
        if prio == None:
            prio = rule_id
        modeid = self.local_modeid
        cmd = self._build_fp_rule_command(inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
        if len(cmd):
            if ip_type == "ipv4":
                self.send_command(cmd, self.pps_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT) 
                self.rule_id_dict[rule_id] = (inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
            elif ip_type == "ipv6":
                self.send_command(cmd, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT) 
                self.rule_ipv6_id_dict[rule_id] = (inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid)
            return (rule_id, ip_type)
        else:
            return None


    def do_destory_pf_rule(self, inports, rule_id):
        cmd = [
               "unbind port {0} rule {1}\n".format(inports, rule_id),
               "delete rule {0}\n".format(rule_id)
              ]
        self.send_command(cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        del self.pf_rule_id_dict[rule_id]
        self._pf_rule_put_id(rule_id)

    def do_destory_pf_ipv6_rule(self, inports, rule_id):
        cmd = [
               "unbind port {0} rule_ipv6 {1}\n".format(inports, rule_id),
               "delete rule_ipv6 {0}\n".format(rule_id)
              ]
        self.send_command(cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        del self.pf_rule_ipv6_id_dict[rule_id]
        self._pf_ipv6_rule_put_id(rule_id)

    def do_destory_fp_rule(self, inports, rule_id):
        if inports == self.autolearn_ingress_ports:
            cmd = [
                   "unbind ingress-interface {0} access-list tuple group default rule {1}\n".format(1, rule_id),
                   "delete access-list tuple group default rule {0}\n".format(rule_id),
                   "sync\n"
                  ]
        self.send_command(cmd, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
        del self.rule_id_dict[rule_id]
        self._ipv4_rule_put_id(rule_id)


    def do_destory_ipv6_rule(self, inports, rule_id):
        if inports == self.autolearn_ingress_ports:
            cmd = [
                   "unbind ingress-interface {0} access-list tuplev6 group default rule {1}\n".format(1, rule_id),
                   "delete access-list tuplev6 group default rule {0}\n".format(rule_id),
                   "sync\n"
                  ]
        self.send_command(cmd, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
        del self.rule_ipv6_id_dict[rule_id]
        self._ipv6_rule_put_id(rule_id)


    def do_destory_remote_fp_rule(self, inports, rule_id):
        if inports == self.sic_ingress_ports:
            cmd = [
                   "unbind ingress-interface {0} access-list tuple group default rule {1}\n".format(2, rule_id),
                   "delete access-list tuplev6 group default rule {0}\n".format(rule_id),
                   "sync\n"
                  ]
        self.send_command(cmd, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
        del self.remote_rule_id_dict[rule_id]
        self._ipv6_rule_put_id(rule_id)


    def do_destory_remote_ipv6_rule(self, inports, rule_id):
        if inports == self.sic_ingress_ports:
            cmd = [
                   "unbind ingress-interface {0} access-list tuplev6 group default rule {1}\n".format(2, rule_id),
                   "delete access-list tuplev6 group default rule {0}\n".format(rule_id),
                   "sync\n"
                  ]
        self.send_command(cmd, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
        del self.remote_rule_ipv6_id_dict[rule_id]
        self._ipv6_rule_put_id(rule_id)


    def install_fp_l3_protocol_rule(self, protocol, rule_id = None, prio = None):
        if rule_id == None:
            rule_id = self._pf_rule_get_id()
        self.phy_l3_protocol_rule_id = rule_id
        return self.do_install_pf_rule(inports = self.autolearn_ingress_ports, \
                                       srcip = "", dstip = "", l4srcport = "", l4dstport = "" , \
                                       ipprotocol = protocol, \
                                       port_action_id = self.pps_to_autolearn_port, \
                                       lag_action_id = "", rule_id = rule_id, prio = prio)

    def install_fp_l3_protocol_rule_ipv6(self, protocol, rule_id = None, prio = None):
        if rule_id == None:
            rule_id = self._pf_ipv6_rule_get_id()
        self.phy_l3_protocol_rule_ipv6_id = rule_id
        return self.do_install_pf_rule(inports = self.autolearn_ingress_ports, \
                                       srcip = "", dstip = "", l4srcport = "", l4dstport = "" , \
                                       ipprotocol = protocol, \
                                       port_action_id = self.pps_to_autolearn_port, \
                                       lag_action_id = "", rule_id = rule_id, prio = prio, ip_type = "ipv6")


    def install_fp_srcport_rule(self, l4srcport, rule_id = None, prio = None):
        if rule_id == None:
            rule_id = self._pf_rule_get_id()
        self.phy_l4_srcport_rule_id = rule_id
        return self.do_install_pf_rule(inports = self.autolearn_ingress_ports, \
                                       srcip = "", dstip = "", l4srcport = l4srcport, l4dstport = "", \
                                       ipprotocol = "", \
                                       port_action_id = self.pps_to_autolearn_port, \
                                       lag_action_id = "", rule_id = rule_id, prio = prio)

    def install_fp_srcport_rule_ipv6(self, l4srcport, rule_id = None, prio = None):
        if rule_id == None:
            rule_id = self._pf_ipv6_rule_get_id()
        self.phy_l4_srcport_rule_ipv6_id = rule_id
        return self.do_install_pf_rule(inports = self.autolearn_ingress_ports, \
                                       srcip = "", dstip = "", l4srcport = l4srcport, l4dstport = "", \
                                       ipprotocol = "", \
                                       port_action_id = self.pps_to_autolearn_port, \
                                       lag_action_id = "", rule_id = rule_id, prio = prio, ip_type = "ipv6")


    def install_fp_dstport_rule(self, l4dstport, rule_id = None, prio = None):
        if rule_id == None:
            rule_id = self._pf_rule_get_id()
        self.phy_l4_dstport_rule_id = rule_id
        return self.do_install_pf_rule(inports = self.autolearn_ingress_ports, \
                                       srcip = "", dstip = "", l4srcport = "", l4dstport = l4dstport, \
                                       ipprotocol = "", \
                                       port_action_id = self.pps_to_autolearn_port, \
                                       lag_action_id = "", rule_id = rule_id, prio = prio)

    def install_fp_dstport_rule_ipv6(self, l4dstport, rule_id = None, prio = None):
        if rule_id == None:
            rule_id = self._pf_ipv6_rule_get_id()
        self.phy_l4_dstport_rule_ipv6_id = rule_id
        return self.do_install_pf_rule(inports = self.autolearn_ingress_ports, \
                                       srcip = "", dstip = "", l4srcport = "", l4dstport = l4dstport, \
                                       ipprotocol = "", \
                                       port_action_id = self.pps_to_autolearn_port, \
                                       lag_action_id = "", rule_id = rule_id, prio = prio, ip_type = "ipv6")

            
    def install_fp_ip_rule(self, ip, rule_id = None, prio = None):
        srcip_rule_info = self.do_install_fp_rule(inports = self.autolearn_ingress_ports, \
                                               srcip = ip, dstip = "", l4srcport = "", l4dstport = "", \
                                               ipprotocol = "", \
                                               port_action_id = self.pps_to_autolearn_port, \
                                               lag_action_id = "", rule_id = rule_id, prio = prio)

        dstip_rule_info = self.do_install_fp_rule(inports = self.autolearn_ingress_ports, \
                                               srcip = "", dstip = ip, l4srcport = "", l4dstport = "", \
                                               ipprotocol = "", \
                                               port_action_id = self.pps_to_autolearn_port, \
                                               lag_action_id = "", rule_id = rule_id, prio = prio)
        return (srcip_rule_info, dstip_rule_info)
    

    def install_surplus_cmd(self, port_action_id = "", lag_action_id = "", port = "", proto = ""):
        cmd = []
        if port_action_id != "":
            action = "set action_id 10 copy ports {0},{1}".format(port_action_id, self.pps_to_autolearn_port)
        if lag_action_id != "":
            action = "set action_id 10 copy lag {0},{1}".format(lag_action_id, 10)
            cmd.append("set lag 10 ports {0}".format(self.pps_to_autolearn_port))
        cmd.append(action)

        if port != "":
            self.phy_l4_srcport_rule_id = self._pf_rule_get_id()
            self.phy_l4_srcport_rule_ipv6_id = self._pf_ipv6_rule_get_id()
            cmd.append("set rule {0} vlan outervlan any sip any dip any sp {1} dp any proto any priority {0}".format(self.phy_l4_srcport_rule_id, port))
            cmd.append("set rule_ipv6 {0} vlan  any sip any dip any sp {1} dp any proto any".format(self.phy_l4_srcport_rule_ipv6_id, port))
            self.phy_l4_dstport_rule_id = self._pf_rule_get_id()
            self.phy_l4_dstport_rule_ipv6_id = self._pf_ipv6_rule_get_id()
            cmd.append("set rule {0} vlan outervlan any sip any dip any sp any dp {1} proto any priority {0}".format(self.phy_l4_dstport_rule_id, port))
            cmd.append("set rule_ipv6 {0} vlan  any sip any dip any sp {1} dp any proto any".format(self.phy_l4_dstport_rule_ipv6_id, port))

            cmd.append("bind port {0} rule {1},{2} action_id {3}".format(self.sic_ingress_ports , self.phy_l4_srcport_rule_id, self.phy_l4_dstport_rule_id, 10))
            cmd.append("bind port {0} rule_ipv6 {1},{2} action_id {3}".format(self.sic_ingress_ports , self.phy_l4_srcport_rule_ipv6_id, self.phy_l4_dstport_rule_ipv6_id, 10))
            self.pf_rule_id_dict[self.phy_l4_srcport_rule_id] = (self.sic_ingress_ports, "", "", port, "", "", port_action_id, lag_action_id, self.phy_l4_srcport_rule_id)
            self.pf_rule_id_dict[self.phy_l4_dstport_rule_id] = (self.sic_ingress_ports, "", "", "", port, "", port_action_id, lag_action_id, self.phy_l4_dstport_rule_id)
            self.pf_rule_ipv6_id_dict[self.phy_l4_srcport_rule_ipv6_id] = (self.sic_ingress_ports, "", "", port, "", "", port_action_id, lag_action_id, self.phy_l4_srcport_rule_ipv6_id)
            self.pf_rule_ipv6_id_dict[self.phy_l4_dstport_rule_ipv6_id] = (self.sic_ingress_ports, "", "", "", port, "", port_action_id, lag_action_id, self.phy_l4_dstport_rule_ipv6_id)
        if proto != "":
            self.phy_l3_protocol_rule_id = self._pf_rule_get_id()
            self.phy_l3_protocol_rule_ipv6_id = self._pf_ipv6_rule_get_id()
            cmd.append("set rule {0} vlan outervlan any sip any dip any sp any dp any proto {1} priority {0}".format(self.phy_l3_protocol_rule_id, proto))
            cmd.append("set rule_ipv6 {0} vlan any sip any dip any sp any dp any proto {1}".format(self.phy_l3_protocol_rule_ipv6_id, proto))
            cmd.append("bind port {0} rule {1} action_id {2}".format(self.sic_ingress_ports , self.phy_l3_protocol_rule_id, 10))
            cmd.append("bind port {0} rule {1} action_id {2}".format(self.sic_ingress_ports , self.phy_l3_protocol_rule_ipv6_id, 10))
            self.pf_rule_id_dict[self.phy_l3_protocol_rule_id] = (self.sic_ingress_ports, "", "", "", "", proto, port_action_id, lag_action_id, self.phy_l3_protocol_rule_id)

        self.send_command(cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        

    def remove_old_rule_in_dict(self):
        for rule_id in list(self.remote_rule_id_dict):
            self.do_destory_remote_fp_rule(self.remote_rule_id_dict[rule_id][0],rule_id)
        for rule_id in list(self.remote_rule_ipv6_id_dict):
            self.do_destory_remote_ipv6_rule(self.remote_rule_ipv6_id_dict[rule_id][0],rule_id)


    def save_61_config(self, new_info):
        from autolearn_handler import User_Info
        if new_info == None:
            return None
        if not isinstance(new_info,User_Info):
            self.logger.error("arg 2 must be Class User_Info!")
        f = open(Gloabal_Var.ASSOCIATE_SAV, mode = "w", encoding = "utf-8")
        for item  in sorted(new_info.groups_info_dict.keys(), key = lambda x : new_info.groups_info_dict[x]["number"]):
            f.write("{0} {1} ".format(str(new_info.groups_info_dict[item]["mme_group"]), str(new_info.groups_info_dict[item]["mme_code"])))
            for ip in new_info.groups_info_dict[item]["ip_list"]:
                f.write(str(ip) + " ")
            f.write("\n")
        f.close()
        if self.dev_plat == "g06_68":
            os.system("tftp -pr /rootfs/autolearn/associate.conf -l /rootfs/associate.sav %s"%self.pps_ip)
        elif self.dev_plat == "g06_78":
            os.system("tftp -pr /rootfs/associate.sav -l /rootfs/autolearn/associate.conf %s"%self.pps_ip)


    def _show_running_config(self, ip, model = Gloabal_Var.PPS_SERVICE, port = Gloabal_Var.PPS_PORT):
        show_result_path = "port_bits"
        show_result_path_tmp = "port_bits_tmp"
        while(True):
            flag = os.system("./rpcc {0} {1} {2} 'show running_config' 10 > {3}".format(self.pps_ip, port, model, show_result_path))
            self.logger.debug("./rpcc {0} {1} {2} 'show running_config' 10 > {3}".format(self.pps_ip, port, model, show_result_path))
            if flag == 0:
                self.logger.debug("show running_config success")
                break
            else:
                self.logger.error("show running_config failed")
                time.sleep(2)
        if port != Gloabal_Var.PPS_PORT:
            cmd = "cat {0} | grep bind | grep rule | awk '{2}' > {1} ; cat {1} > {0} ; rm {1}".format(show_result_path, show_result_path_tmp, "{print $5,$9}")
        else:
            cmd = "cat {0} | grep bind | grep rule | awk '{2}' > {1} ; cat {1} > {0} ; rm {1}".format(show_result_path, show_result_path_tmp, "{print $4,$5}")

        self.logger.debug(cmd)
        os.system(cmd)
        with open(show_result_path, mode = "r", encoding = "utf-8") as show_result:
            result = show_result.readlines()
            self.logger.debug(result)
        return result


    def _merge_id(self, rule_id_list):
        ###Eg: [1,2,3,4,5,7,8,9,20,21,22,26]
        ###    [1-5, 7-9, 20-22, 26]
        tmp = []
        if len(rule_id_list):
            begin = rule_id_list[0]
            for i in range(1,len(rule_id_list)):
                if rule_id_list[i]-rule_id_list[i-1] != 1:
                    end = rule_id_list[i-1]
                    if begin != end: 
                        tmp.append("{0}-{1}".format(begin, end))
                    else:
                        tmp.append("{0}".format(begin))
                    begin = rule_id_list[i]                                                                                                                                                                                                                                        
            end  = rule_id_list[len(rule_id_list)-1]
            if begin != end:
                tmp.append("{0}-{1}".format(begin, end))
            else:
                tmp.append("{0}".format(begin))
        return tmp 


    ###### The function overridden in a subclass
    def _fp_init(self):
        #####
        self.logger.debug("_fp_init function need overridden")


    ###### The function overridden in a subclass
    def load_config(self):
        ##### The debugging parameters are given
        self.logger.debug("pps_ip:", self.pps_ip)
        self.logger.debug("sic_ctrl_egress:", self.sic_ctrl_egress)
        self.logger.debug("sic_stcp_default_egress:", self.sic_stcp_default_egress)
        self.logger.debug("sic_s11_default_egress:", self.sic_s11_default_egress)
        self.logger.debug("pps_port_num:", self.pps_port_num)
        self.logger.debug("autolearn_ingress_ports", self.autolearn_ingress_ports)
        self.logger.debug("sic_ingress_ports:", self.sic_ingress_ports)
        self.logger.debug("pps_ingress_ports:", self.pps_ingress_ports)
        self.logger.debug("pps_to_autolearn_port:", self.pps_to_autolearn_port)
        self.logger.debug("autolearn_to_pps_port:", self.autolearn_to_pps_port)


        
class G33_Cfg(Base_Cfg):
    ######
    ### G33 autolearn configuration 
    ### Base_Cfg Class contained functions that support G33:
    ###         _fp_init()
    ###         build_remote_cmd()
    ######

    ###### protect value
    ### When sic has residual traffic
    _sf_action_id_base = 10
    _remain_sic_to_autolearn_port = ""
    _autolearn_remain_sic_to_port = ""

    def __init__(self):
        self.dev_plat = "g33"

        #Creat history or Delete old history before writes
        with open(Gloabal_Var.COMMAND_HISTORY, "wt", encoding = "utf-8"):
            pass

        self.load_config()

        self.pf_rule_id_queue = [i for i in range(self._pf_rule_min_id, self._pf_rule_max_id)]
        self.pf_rule_ipv6_id_queue = [i for i in range(_pf_ipv6_rule_min_id, _pf_ipv6_rule_max_id)]
        self.ipv4_rule_id_queue = [i for i in range(self._ipv4_rule_min_id, self._ipv4_rule_max_id)]
        self.ipv6_rule_id_queue = [i for i in range(self._ipv6_rule_min_id, self._ipv6_rule_max_id)]

        self._get_autolearn_config()
        self._fp_init()
        self._get_local_modeid()


    def load_config(self):
        is_init_load_balance_list_flag = False
        try:
            sic_ctrl_egress_list = []
            used_ports_list = []

            g33_config = configparser.ConfigParser()
            g33_config.read(Gloabal_Var.AUTO_LEARN_CONF_OTHER, encoding = "utf-8")

            if g33_config.has_section(self.dev_plat):
                options_list = g33_config.options(self.dev_plat)
                for option in options_list:
                    if option == "pps_ip":
                        self.pps_ip = g33_config.get(self.dev_plat, option)

                    elif option == "sic_ctrl_egress":
                        sic_ctrl_string_value = g33_config.get(self.dev_plat, option)
                        if self.sic_ctrl_string != sic_ctrl_string_value:
                            self.sic_ctrl_string = sic_ctrl_string_value 
                            is_init_load_balance_list_flag = True
                        for port in sic_ctrl_string_value.split(","):
                            sic_ctrl_egress_list.append(port)
                        self.sic_stcp_default_egress = sic_ctrl_string_value.split(",")[-1]
                        self.sic_s11_default_egress = sic_ctrl_string_value.split(",")[-1]

                    elif option == "lag_sic_ctrl_egress":
                        self._lag_sic_ctrl_egress = g33_config.get(self.dev_plat, option)

                    elif option == "pps_port_num":
                        self.pps_port_num = g33_config.get(self.dev_plat, option)

                    elif option == "autolearn_ingress_ports":
                        self.autolearn_ingress_ports = g33_config.get(self.dev_plat, option)
                        for port_autolearn in self.autolearn_ingress_ports.split(","):
                            used_ports_list.append(int(port_autolearn))

                    elif option == "sic_ingress_ports":
                        self.sic_ingress_ports = g33_config.get(self.dev_plat, option)
                        for port_sic in self.sic_ingress_ports.split(","):
                            used_ports_list.append(int(port_sic))

                    elif option == "remain_sic_to_autolearn_port":
                        self._remain_sic_to_autolearn_port = g33_config.get(self.dev_plat, option)
                        for port_sic_remain in self._remain_sic_to_autolearn_port.split(","):
                            used_ports_list.append(int(port_sic_remain))

                    elif option == "autolearn_remain_sic_to_port":
                        self._autolearn_remain_sic_to_port = g33_config.get(self.dev_plat, option)

                    elif option == "lag_autolearn":
                        self._lag_autolearn = g33_config.get(self.dev_plat, option)

                    elif option == "lag_sic":
                        self._lag_sic = g33_config.get(self.dev_plat, option)

                    elif option == "loopback_ports":
                        self.loopback_ports = g33_config.get(self.dev_plat, option)

                    elif option == "pps_to_autolearn_port":
                        self.pps_to_autolearn_port = g33_config.get(self.dev_plat, option)
                        for port_pps in self.pps_to_autolearn_port.split(","):
                            used_ports_list.append(int(port_pps))

                    elif option == "autolearn_to_pps_port":
                        self.autolearn_to_pps_port = g33_config.get(self.dev_plat, option)

                    elif option == "autolearn_to_cpu":
                        self._autolearn_to_cpu_port = g33_config.get(self.dev_plat, option)

                    elif option == "autolearn_gn_to_last_dev":
                        if g33_config.getboolean(self.dev_plat, option):
                            self.sic_ctrl_egress = tuple(sic_ctrl_egress_list[0:-1])
                            if self.gn_load_balance == True:
                                Gloabal_Var.NEED_UPDATE_CONFIG = True
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]
                            self.gn_load_balance = False
                            if is_init_load_balance_list_flag == True:
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]
                        
                        else:
                            self.sic_ctrl_egress = tuple(sic_ctrl_egress_list)
                            if self.gn_load_balance == False:
                                Gloabal_Var.NEED_UPDATE_CONFIG = True
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]
                            self.gn_load_balance = True
                            if is_init_load_balance_list_flag == True:
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]

                    elif option == "rule_pf_id":
                        self._pf_ipv6_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._pf_ipv6_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "rule_ipv6_pf_id":
                        self._pf_ipv6_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._pf_ipv6_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "rule_ipv4_id":
                        self._ipv4_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._ipv4_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "rule_ipv6_id":
                        self._ipv6_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._ipv6_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "local_rule_id":
                        self._rule_id_local = int(g33_config.get(self.dev_plat, option))

                    elif option == "action_id":
                        self._action_id_base = g33_config.getint(self.dev_plat, option)

                    elif option == "vlan_id":
                        self._vlan_id_base = g33_config.getint(self.dev_plat, option)

                    elif option == "flag_ipv6":
                        self._flag_ipv6 = g33_config.getboolean(self.dev_plat, option)


                    self.pps_ingress_ports = ",".join([str(i) for i in range(1,int(self.pps_port_num)+1) if i not in used_ports_list])

            else:
                self.logger.error("Configuration file exception!")

            self.logger.debug("pps_ip:", self.pps_ip)
            self.logger.debug("sic_ctrl_egress_list:", sic_ctrl_egress_list)
            self.logger.debug("sic_ctrl_egress:", self.sic_ctrl_egress)
            self.logger.debug("sic_stcp_default_egress:", self.sic_stcp_default_egress)
            self.logger.debug("sic_s11_default_egress:", self.sic_s11_default_egress)
            self.logger.debug("pps_port_num:", self.pps_port_num)
            self.logger.debug("autolearn_ingress_ports", self.autolearn_ingress_ports)
            self.logger.debug("sic_ingress_ports:", self.sic_ingress_ports)
            self.logger.debug("pps_ingress_ports:", self.pps_ingress_ports)
            self.logger.debug("pps_to_autolearn_port:", self.pps_to_autolearn_port)
            self.logger.debug("autolearn_to_pps_port:", self.autolearn_to_pps_port)

        except configparser.Error as e:
            self.logger.error(e)
            exit()

    def _fp_init(self):
        ####################### 1 #########################
        ######## init autolearn device pps
        #autolearn  local pps  config  of sf3000
        init_localhost_commands = [
                                    "delete lag {0}".format(self._lag_autolearn),
                                    "set lag {0} port {1},{2}".format(self._lag_autolearn, self._autolearn_to_cpu_port, int(self._autolearn_to_cpu_port)+1)
                                    "delete rule {0} force".format(self._rule_id_local),
                                    "delete action_id {0}".format(self._action_id_local),
                                    #default autolearn to cpu port 1-2
                                    "set rule {0} any".format(self._rule_id_local),
                                    "set action_id {0} forward port {1} ".format(self._action_id_local, self._lag_autolearn),
                                    "bind port {0} rule {1} action_id {2}".format(self.autolearn_to_pps_port, self._rule_id_local, self._action_id_local),

                                    "delete rule {0} force".format(self._rule_id_local-1),
                                    "delete action_id {0}".format(self._action_id_local+1),
                                    #remain sic to cpu port 3
                                    "set action_id {0} forward port {1} ".format(self._action_id_local+1, int(self._autolearn_to_cpu_port)+2),
                                    "set rule {0} any".format(self._rule_id_local-1),
                                    "bind port {0} rule {1} action_id {2}".format(self._autolearn_remain_sic_to_port, self._rule_id_local-1, self._action_id_local+1)
                                    
                                    "set rule {0} any".format(self._rule_id_local)

                                  ]        

        self.send_command(init_localhost_commands, self._localhost_ip, Gloabal_Var.PPS_SERVICE)

        

        ####################### 2 #########################
        ######## init autolearn device sic 
        ###exist rule id and in autolearn rule range and not in autolearn rule
        init_sf_commands = []
        if Gloabal_Var.FLAG_ONLY_CHECK == True:
            for rule_id in range(self._ipv4_rule_min_id, self._ipv4_rule_max_id):
                if rule_id  in self.autolearn_rules:
                    self.ipv4_rule_id_queue.remove(rule_id)
            tmp = self._merge_id(self.ipv4_rule_id_queue)
            #ipv6
            for rule_id in range(self._ipv6_rule_min_id, self._ipv6_rule_max_id):
                if rule_id  in self.autolearn_ipv6_rules:
                    self.ipv6_rule_id_queue.remove(rule_id)
            tmp_ipv6 = self._merge_id(self.ipv6_rule_id_queue)

            init_sf_commands.append("unbind ingress-interface {0} access-list tuple group default rule {1}".format( 1, ",".join(tmp)))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuple group default rule {1}".format( 2, ",".join(tmp)))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuple group default rule {1}".format( 3, ",".join(tmp)))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule {1}".format( 1, ",".join(tmp_ipv6)))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule {1}".format( 2, ",".join(tmp_ipv6)))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule {1}".format( 3, ",".join(tmp_ipv6)))
            init_sf_commands.append("delete access-list tuplev6 group default rule {0}".format(",".join(tmp_ipv6)))
            init_sf_commands.append("sync")
            init_sf_commands.append("delete ingress-interface all")
            init_sf_commands.append("set ingress-interface 1 add port 1-2 vlan {0}".format(self._autolearn_to_cpu + self._vlan_id_base))
            init_sf_commands.append("set ingress-interface 1 learn-only enable")
            init_sf_commands.append("set ingress-interface 2 add port 1-2 vlan not-care")
            init_sf_commands.append("set ingress-interface 2 l3-goto-acl enable")
            init_sf_commands.append("set ingress-interface 3 add port 3 vlan not-care")
            init_sf_commands.append("set ingress-interface 3 l3-goto-acl enable")
            init_sf_commands.append("set switch s1-cdr disable")
            init_sf_commands.append("set switch s1-tmsi-info disable")
            init_sf_commands.append("set switch nas_decrypt enable")
            init_sf_commands.append("set switch gtpv2-cdr-proc disable")
            init_sf_commands.append("set switch sgw-uinfo disable")
            init_sf_commands.append("set switch ggsn-uinfo disable")
            init_sf_commands.append("set switch learn-associate-ip enable")

        else:
            init_sf_commands.append("unbind ingress-interface {0} access-list tuple group default rule all".format(1))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuple group default rule all".format(2))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuple group default rule all".format(3))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule all".format(1))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule all".format(2))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule all".format(3))
            init_sf_commands.append("delete access-list tuplev6 group default rule all")
            init_sf_commands.append("sync")
            init_sf_commands.append("delete ingress-interface all")
            init_sf_commands.append("set ingress-interface 1 add port 1-2 vlan {0}".format(self._autolearn_to_cpu + self._vlan_id_base))
            init_sf_commands.append("set ingress-interface 1 learn-only enable")
            init_sf_commands.append("set ingress-interface 2 add port 2 vlan not-care")
            init_sf_commands.append("set ingress-interface 2 l3-goto-acl enable")
            init_sf_commands.append("set ingress-interface 3 add port 3 vlan not-care")
            init_sf_commands.append("set ingress-interface 3 l3-goto-acl enable")
            init_sf_commands.append("set switch s1-cdr disable")
            init_sf_commands.append("set switch s1-tmsi-info disable")
            init_sf_commands.append("set switch nas_decrypt enable")
            init_sf_commands.append("set switch gtpv2-cdr-proc disable")
            init_sf_commands.append("set switch sgw-uinfo disable")
            init_sf_commands.append("set switch ggsn-uinfo disable")
            init_sf_commands.append("set switch learn-associate-ip enable")

        self.send_command(init_sf_commands, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)

        ####################### 3 #########################
        ######## configparse controlled device pps
        init_commands = []
        sp_rule_id = self._pf_rule_get_id()
        dp_rule_id = self._pf_rule_get_id()
        proto_rule_id = self._pf_rule_get_id()
        ipv6_sp_rule_id = self._pf_ipv6_rule_get_id()
        ipv6_dp_rule_id = self._pf_ipv6_rule_get_id()
        ipv6_proto_rule_id = self._pf_ipv6_rule_get_id()
        init_commands = [
                          "delete rule {0}-{1} force".format(self._pf_rule_min_id, self._pf_rule_max_id),
                          "delete rule_ipv6 {0}-{1} force".format(self._pf_ipv6_rule_min_id, self._pf_ipv6_rule_max_id),
                          "delete action_id {0}".format(self._mirror_lag_action_id),
                          "delete lag {0}".format(self._lag_sic),
                          "delete lag {0}".format(self._lag_autolearn),

                          #pf to sf deal with ipv6
                          "delete rule 1 force",
                          "delete rule_ipv6 1 force",
                          "set rule 1 vlan outervlan any sip any dip any sp any dp any proto any priority 1",
                          "set rule_ipv6  1 vlan any sip any dip any sp any dp any proto any ",
                          "set action_id 1 forward port {0}".format(self._remain_sic_to_autolearn_port),
                          "bind port {0} rule {1} action_id {2}".format(self.sic_ingress_ports, 1, 1),

                          "set lag {0} ports {1}".format(self._lag_sic, self.sic_ingress_ports),
                          "set lag {0} ports {1}".format(self._lag_autolearn, self.autolearn_ingress_ports),
                          "set port {0},{1} loopback enable".format(self.sic_ingress_ports, self.autolearn_ingress_ports),
                          "set action_id {0} copy lag {1},{2}".format(self._mirror_lag_action_id, self._lag_sic, self._lag_autolearn),
                          "set rule {0} vlan outervlan any sip any dip any sp {1} dp any proto any priority {0}".format(sp_rule_id, self._sp_dp_port),
                          "set rule {0} vlan outervlan any sip any dip any sp any dp {1} proto any priority {0}".format(dp_rule_id, self._sp_dp_port),
                          "set rule {0} vlan outervlan any sip any dip any sp any dp any proto {1} priority {0}".format(proto_rule_id, self._proto),
                          "set rule_ipv6 {0} vlan any sip any dip any sp {1} dp any proto any".format(ipv6_sp_rule_id, self._sp_dp_port),
                          "set rule_ipv6 {0} vlan any sip any dip any sp any dp {1} proto any".format(ipv6_dp_rule_id, self._sp_dp_port),
                          "set rule_ipv6 {0} vlan any sip any dip any sp any dp any proto {1}".format(ipv6_proto_rule_id, self._proto),
                          "bind port {0} rule {1},{2},{3},{4},{5},{6} action_id {7}".format(self.pps_ingress_ports, sp_rule_id, dp_rule_id, proto_rule_id, ipv6_sp_rule_id, ipv6_dp_rule_id, ipv6_proto_rule_id, self._mirror_lag_action_id)
                        ]
        init_commands.append("set port {0} dtag none".format(self._remain_sic_to_autolearn_port))
        init_commands.append("set port {0} discard none".format(self._remain_sic_to_autolearn_port))

        init_commands.append("set port {0} dtag none".format(self.pps_to_autolearn_port))
        init_commands.append("set port {0} discard none".format(self.pps_to_autolearn_port))

        ###vlan broadcast
        init_commands.append("vlan creat {0} ports {1}".format( (int(self._vlan_id_base)+int(self._autolearn_to_cpu_port)), self.pps_to_autolearn_port))
        init_commands.append("vlan creat {0} ports {1}".format( (int(self._vlan_id_base)+int(self._autolearn_to_cpu_port)+ 2), self._remain_sic_to_autolearn_port))
                                                                
        self.send_command(init_commands, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        if self.gn_load_balance == True:
     	    if len(self.sic_ctrl_egress) > 0:
                init_commands = ["set lag {1} ports {0}".format(",".join([i for i in self.sic_ctrl_egress]), self._lag_sic_ctrl_egress)]
                self.send_command(init_commands, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        
class G33_78_Cfg(Base_Cfg):
    #####
    ### G33_78 is sf8000 autolearn configuration
    #####

    #####protect value
    ### When sic has residual traffic
    _remain_sic_to_autolearn_port = ""
    _autolearn_remain_sic_to_port = ""

    def __init__(self):
        self.dev_plat = "g33_78"

        #Creat history or Delete old history before writes
        with open(Gloabal_Var.COMMAND_HISTORY, "wt", encoding = "utf-8"):
            pass

        self.load_config()

        self.pf_rule_id_queue = [i for i in range(self._pf_rule_min_id, self._pf_rule_max_id)]
        self.pf_rule_ipv6_id_queue = [i for i in range(_pf_ipv6_rule_min_id, _pf_ipv6_rule_max_id)]
        self.ipv4_rule_id_queue = [i for i in range(self._ipv4_rule_min_id, self._ipv4_rule_max_id)]
        self.ipv6_rule_id_queue = [i for i in range(self._ipv6_rule_min_id, self._ipv6_rule_max_id)]

        self._get_autolearn_config()
        self._fp_init()
        self._get_local_modeid()
    

    def load_config(self):
        is_init_load_balance_list_flag = False
        try:
            sic_ctrl_egress_list = []
            used_ports_list = []

            g33_config = configparser.ConfigParser()
            g33_config.read(Gloabal_Var.AUTO_LEARN_CONF_OTHER, encoding = "utf-8")

            if g33_config.has_section(self.dev_plat):
                options_list = g33_config.options(self.dev_plat)
                for option in options_list:
                    if option == "pps_ip":
                        self.pps_ip = g33_config.get(self.dev_plat, option)

                    elif option == "sic_ctrl_egress":
                        sic_ctrl_string_value = g33_config.get(self.dev_plat, option)
                        if self.sic_ctrl_string != sic_ctrl_string_value:
                            self.sic_ctrl_string = sic_ctrl_string_value 
                            is_init_load_balance_list_flag = True
                        for port in sic_ctrl_string_value.split(","):
                            sic_ctrl_egress_list.append(port)
                        self.sic_stcp_default_egress = sic_ctrl_string_value.split(",")[-1]
                        self.sic_s11_default_egress = sic_ctrl_string_value.split(",")[-1]

                    elif option == "lag_sic_ctrl_egress":
                        self._lag_sic_ctrl_egress = g33_config.get(self.dev_plat, option)

                    elif option == "pps_port_num":
                        self.pps_port_num = g33_config.get(self.dev_plat, option)

                    elif option == "autolearn_ingress_ports":
                        self.autolearn_ingress_ports = g33_config.get(self.dev_plat, option)
                        for port_autolearn in self.autolearn_ingress_ports.split(","):
                            used_ports_list.append(int(port_autolearn))

                    elif option == "sic_ingress_ports":
                        self.sic_ingress_ports = g33_config.get(self.dev_plat, option)
                        for port_sic in self.sic_ingress_ports.split(","):
                            used_ports_list.append(int(port_sic))

                    elif option == "remain_sic_to_autolearn_port":
                        self._remain_sic_to_autolearn_port = g33_config.get(self.dev_plat, option)
                        for port_sic_remain in self._remain_sic_to_autolearn_port.split(","):
                            used_ports_list.append(int(port_sic_remain))

                    elif option == "autolearn_remain_sic_to_port":
                        self._autolearn_remain_sic_to_port = g33_config.get(self.dev_plat, option)

                    elif option == "lag_autolearn":
                        self._lag_autolearn = g33_config.get(self.dev_plat, option)

                    elif option == "lag_sic":
                        self._lag_sic = g33_config.get(self.dev_plat, option)

                    elif option == "loopback_ports":
                        self.loopback_ports = g33_config.get(self.dev_plat, option)

                    elif option == "pps_to_autolearn_port":
                        self.pps_to_autolearn_port = g33_config.get(self.dev_plat, option)
                        for port_pps in self.pps_to_autolearn_port.split(","):
                            used_ports_list.append(int(port_pps))

                    elif option == "autolearn_to_pps_port":
                        self.autolearn_to_pps_port = g33_config.get(self.dev_plat, option)

                    elif option == "autolearn_gn_to_last_dev":
                        if g33_config.getboolean(self.dev_plat, option):
                            self.sic_ctrl_egress = tuple(sic_ctrl_egress_list[0:-1])
                            if self.gn_load_balance == True:
                                Gloabal_Var.NEED_UPDATE_CONFIG = True
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]
                            self.gn_load_balance = False
                            if is_init_load_balance_list_flag == True:
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]
                        
                        else:
                            self.sic_ctrl_egress = tuple(sic_ctrl_egress_list)
                            if self.gn_load_balance == False:
                                Gloabal_Var.NEED_UPDATE_CONFIG = True
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]
                            self.gn_load_balance = True
                            if is_init_load_balance_list_flag == True:
                                self.load_balance_index_list = [[] for i in range(len(self.sic_ctrl_egress))]

                    elif option == "rule_pf_id":
                        self._pf_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._pf_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "rule_ipv6_pf_id":
                        self._pf_ipv6_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._pf_ipv6_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "rule_ipv4_id":
                        self._ipv4_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._ipv4_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "rule_ipv6_id":
                        self._ipv6_rule_min_id = int(g33_config.get(self.dev_plat, option).split("-")[0])
                        self._ipv6_rule_max_id = int(g33_config.get(self.dev_plat, option).split("-")[1])

                    elif option == "local_rule_id":
                        self._rule_id_local = int(g33_config.get(self.dev_plat, option))

                    elif option == "action_id":
                        self._action_id_base = g33_config.getint(self.dev_plat, option)

                    elif option == "vlan_id":
                        self._vlan_id_base = g33_config.getint(self.dev_plat, option)

                    elif option == "flag_ipv6":
                        self._flag_ipv6 = g33_config.getboolean(self.dev_plat, option)

                    elif option == "autolearn_to_cpu":
                        self._autolearn_to_cpu_port = g33_config.get(self.dev_plat, option)
                    elif option == "sic_acl_to_cpu":
                        self._sic_acl_to_cpu = g33_config.get(self.dev_plat, option)


                    self.pps_ingress_ports = ",".join([str(i) for i in range(1,int(self.pps_port_num)+1) if i not in used_ports_list])

            else:
                self.logger.error("Configuration file exception!")

            self.logger.debug("pps_ip:", self.pps_ip)
            self.logger.debug("sic_ctrl_egress_list:", sic_ctrl_egress_list)
            self.logger.debug("sic_ctrl_egress:", self.sic_ctrl_egress)
            self.logger.debug("sic_stcp_default_egress:", self.sic_stcp_default_egress)
            self.logger.debug("sic_s11_default_egress:", self.sic_s11_default_egress)
            self.logger.debug("pps_port_num:", self.pps_port_num)
            self.logger.debug("autolearn_ingress_ports", self.autolearn_ingress_ports)
            self.logger.debug("sic_ingress_ports:", self.sic_ingress_ports)
            self.logger.debug("pps_ingress_ports:", self.pps_ingress_ports)
            self.logger.debug("pps_to_autolearn_port:", self.pps_to_autolearn_port)
            self.logger.debug("autolearn_to_pps_port:", self.autolearn_to_pps_port)

        except configparser.Error as e:
            self.logger.error(e)
            exit()


    def _build_fp_rule_command_ipv6(self, inports, srcip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modeid):
        #sf-sic
        base_rule_str = "set access-list tuplev6 group default rule %s "%str(rule_id)
        if srcip != "":
            base_rule_str = base_rule_str + "sip %s "%srcip
        else:
            base_rule_str = base_rule_str + "sip any "
        if dstip != "":
            base_rule_str = base_rule_str + "dip %s "%dstip
        else:
            base_rule_str = base_rule_str + "dip any "
        if l4srcport != "":
            base_rule_str = base_rule_str + "sp %s "%str(l4srcport)
        else:
            base_rule_str = base_rule_str + "sp any "
        if l4dstport != "":
            base_rule_str = base_rule_str + "dp %s "%str(l4dstport)
        else:
            base_rule_str = base_rule_str + "dp any "
        if ipprotocol != "":
            base_rule_str = base_rule_str + "proto %s "%str(ipprotocol)
        else:
            base_rule_str = base_rule_str + "proto any "
        base_rule_str = base_rule_str + "vlan any "

        cmd = []
        if port_action_id != "":
            #sf-sic
            #sic_ingress_ports
            if inports == self.sic_ingress_ports:
                ingress_interface = 2
                egress_interface = self._autolearn_remain_sic_to_port
                action_id = self._action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}".format( action_id, vlan_id )
                cmd = [
                        "set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} ports {1}\n".format( vlan_id, egress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n"
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build remote cmd for sf-sic:", cmd)
            #autolearn_ingress_ports
            elif inports == self.autolearn_ingress_ports:
                ingress_interface = 1
                egress_interface = self.autolearn_to_pps_port
                action_id = self._action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}\n".format( action_id, vlan_id )
                cmd = [
                        "set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} ports {1}\n".format( vlan_id, egress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n"
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build autolearn cmd for sf-sic:", cmd)

            #Controlled device PF
            pf_cmd = [
                        "vlan create {0} ports {1} untag {1}\n".format( vlan_id, port_action_id)
                     ]
            self.send_command(pf_cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
            #autolearn device PF
            auto_pf_cmd = [
                            "vlan create {0} ports {1} untag {1}\n".format( vlan_id, self.autolearn_remain_sic_to_port)
                          ]
            self.send_command(auto_pf_cmd, self._localhost_ip, Gloabal_Var.PPS_SERVICE)

        if lag_action_id != "":
            #sf-sic
            #sic_ingress_ports
            if lag_action_id == self._lag_sic_ctrl_egress:
                ingress_interface = 2 
                egress_interface = self._autolearn_remain_sic_to_port
                action_id = self._action_id_base+int(port_action_id)
                vlan_id = self._vlan_id_base+int(port_action_id)
                action_str = "set action {0} forward egress-vlan {1}".format( action_id, vlan_id )
                cmd = [
                        "set ingress-interface {0} add port {0} vlan not-care\n".format(ingress_interface),
                        "set egress-vlan {0} ports {1}\n".format( vlan_id, egress_interface),
                        "{0}\n".format(action_str),
                        "{0}\n".format(base_rule_str),
                        "sync\n"
                        "bind ingress-interface {0} access-list tuplev6 group default rule {1} action {2}\n".format( ingress_interface, rule_id, action_id)
                      ]
                #debug
                self.logger.debug("build remote cmd for sf-sic user lag:", cmd)
            #debug
            self.logger.debug("build remote pf lags ports:", self.sic_ctrl_egress)
            #Controlled device PF
            pf_cmd = ["vlan create {0} ports {1} untag {1}\n".format( vlan_id, self.sic_ctrl_egress)]
            self.send_command(pf_cmd, self.pps_ip, Gloabal_Var.PPS_SERVICE)
            #autolearn device PF
            auto_pf_cmd = [
                            "vlan create {0} ports {1} untag {1}\n".format( vlan_id, self.autolearn_remain_sic_to_port)
                          ]
            self.send_command(auto_pf_cmd, self._localhost_ip, Gloabal_Var.PPS_SERVICE)
        return cmd


    def _fp_init(self):
        ####################### 1 #########################
        ######## init autolearn device sic 
        ### 
        init_commands = []
        init_sf_commands = []
        if Gloabal_Var.FLAG_ONLY_CHECK == True:
            for rule_id in range(self._ipv4_rule_min_id, self._ipv4_rule_max_id):
                if rule_id  in self.autolearn_rules:
                    self.ipv4_rule_id_queue.remove(rule_id)
            tmp = self._merge_id(self.ipv4_rule_id_queue)
            #ipv6
            for rule_id in range(self._ipv6_rule_min_id, self._ipv6_rule_max_id):
                if rule_id  in self.autolearn_ipv6_rules:
                    self.ipv6_rule_id_queue.remove(rule_id)
            tmp_ipv6 = self._merge_id(self.ipv6_rule_id_queue)
            #debug
            self.logger.debug("merge_id", tmp)

            init_commands.append("delete rule {0} force".format(",".join(tmp)))

            init_sf_commands.append("set ingress-interface 1 add port 1-2 vlan {0}".format( int(self._autolearn_to_cpu_port)+1 ))
            init_sf_commands.append("set ingress-interface 1 learn-only enable")
            init_sf_commands.append("set ingress-interface 2 add port 1-2 vlan not-care")
            init_sf_commands.append("set ingress-interface 2 l3-goto-acl enable")
            init_sf_commands.append("set ingress-interface 3 add port 3 vlan not-care")
            init_sf_commands.append("set ingress-interface 3 l3-goto-acl enable")
            init_sf_commands.append("set switch s1-cdr disable")
            init_sf_commands.append("set switch s1-tmsi-info disable")
            init_sf_commands.append("set switch nas_decrypt enable")
            init_sf_commands.append("set switch gtpv2-cdr-proc disable")
            init_sf_commands.append("set switch sgw-uinfo disable")
            init_sf_commands.append("set switch ggsn-uinfo disable")
            init_sf_commands.append("set switch learn-associate-ip enable")
        else:
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule all".format(1))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule all".format(2))
            init_sf_commands.append("unbind ingress-interface {0} access-list tuplev6 group default rule all".format(3))
            init_sf_commands.append("delete access-list tuplev6 group default rule all")
            init_sf_commands.append("sync")
            init_sf_commands.append("delete ingress-interface all")
            init_sf_commands.append("set ingress-interface 1 add port 1-2 vlan {0}".format( int(self._autolearn_to_cpu_port)+1 ))
            init_sf_commands.append("set ingress-interface 1 learn-only enable")
            init_sf_commands.append("set ingress-interface 2 add port 1-2 vlan not-care")
            init_sf_commands.append("set ingress-interface 2 l3-goto-acl enable")
            init_sf_commands.append("set ingress-interface 3 add port 3 vlan not-care")
            init_sf_commands.append("set ingress-interface 3 l3-goto-acl enable")
            init_sf_commands.append("set switch s1-cdr disable")
            init_sf_commands.append("set switch s1-tmsi-info disable")
            init_sf_commands.append("set switch nas_decrypt enable")
            init_sf_commands.append("set switch gtpv2-cdr-proc disable")
            init_sf_commands.append("set switch sgw-uinfo disable")
            init_sf_commands.append("set switch ggsn-uinfo disable")
            init_sf_commands.append("set switch learn-associate-ip enable")

        self.send_command(init_sf_commands, self._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)

        ####################### 2 #########################
        ######## init contorlled device pps 
        sp_rule_id = self._pf_rule_get_id()
        dp_rule_id = self._pf_rule_get_id()
        proto_rule_id = self._pf_rule_get_id()

        sp_rule_ipv6_id = self._pf_ipv6_rule_get_id()
        dp_rule_ipv6_id = self._pf_ipv6_rule_get_id()
        proto_rule_ipv6_id = self._pf_ipv6_rule_get_id()
        sic_mirror_action_id = int(self._remain_sic_to_autolearn_port)+500
        init_commands = [
                    "delete rule {0} force".format(sp_rule_id),
                    "delete rule {0} force".format(dp_rule_id),
                    "delete rule {0} force".format(proto_rule_id),
                    "delete rule_ipv6 {0} force".format(sp_rule_ipv6_id),
                    "delete rule_ipv6 {0} force".format(dp_rule_ipv6_id),
                    "delete rule_ipv6 {0} force".format(proto_rule_ipv6_id),
                    "delete action_id {0}".format(self._mirror_lag_action_id),
                    "delete action_id {0}".format(sic_mirror_action_id),
                    "delete lag {0}".format(self._lag_sic),
                    "delete lag {0}".format(self._lag_autolearn),

                    "set port {0} loop_back enable".format(self.autolearn_ingress_ports),
                    "set lag {0} ports {1}".format(self._lag_sic, self._remain_sic_to_autolearn_port),
                    "set lag {0} ports {1}".format(self._lag_autolearn, self.autolearn_ingress_ports),
                    "set action_id {0} forward lag {1}".format(sic_mirror_action_id, self._lag_sic),
                    "set action_id {0} forward lag {1}".format(self._mirror_lag_action_id),
                    "set rule {0} vlan outervlan any sip any dip any sp 2123 dp any proto any priority 1024".format(sp_rule_id),
                    "set rule {0} vlan outervlan any sip any dip any sp any dp 2123 proto any priority 1024".format(dp_rule_id),
                    "set rule {0} vlan outervlan any sip any dip any sp any dp any proto 132 priority 1024".format(proto_rule_id),
                    "set rule_ipv6 {0} vlan any sip any dip any sp 2123 dp any proto any".format(sp_rule_ipv6_id),
                    "set rule_ipv6 {0} vlan any sip any dip any sp any dp 2123 proto any".format(dp_rule_ipv6_id),
                    "set rule_ipv6 {0} vlan any sip any dip any sp any dp any proto 132".format(proto_rule_ipv6_id),
                    "bind port {0} rule {1}-{2} action_id {3}".format(self.pps_ingress_ports, sp_rule_id, proto_rule_id, self._mirror_lag_action_id),
                    "bind port {0} rule_ipv6 {1}-{2} action_id {3}".format(self.pps_ingress_ports, sp_rule_ipv6_id, proto_rule_ipv6_id, self._mirror_lag_action_id),
                    "bind port {0} mirror action_id {1}".format(self.pps_ingress_ports, sic_mirror_action_id),
                    "set port {0} pvlan 4095".format(self._remain_sic_to_autolearn_port),
                ]
        for port in range(1, int(self.pps_port_num)-int(self.loopback_ports)+1):
            vlan_id = port + 500
            init_commands.append("vlan create {0} ports {1} untag {2}".format(vlan_id, port, port))
        
        self.send_command(init_commands, self.pps_ip, Gloabal_Var.PPS_SERVICE)
        if self.gn_load_balance == True:
     	    if len(self.sic_ctrl_egress) > 0:
                init_commands = ["set lag {1} ports {0}".format(",".join([i for i in self.sic_ctrl_egress]), self._lag_sic_ctrl_egress)]
                self.send_command(init_commands, self.pps_ip, Gloabal_Var.PPS_SERVICE)

