from autolearn_config import * 
import os
import sys
import time

class User_Info:
    def __init__(self, config_filename):
        self.logger = Logging()
        self.config_file = config_filename

        ### groups_info_dict:
        ### {  
        ###     int(group_id_1) : {
        ###                           'ip_list'     : [ip1, ip2, ip3, ...],
        ###                           'rule_info'   : (actoin_type, dest) (see Structure of rule dict member in BcmCommand)
        ###                           'hit_counter' : int(hit counter)
        ###                       },
        ### }  
        self.groups_info_dict = {} 

        ### load_balance_groups:
        ### {  
        ###     int(load_balance_group_id_1) : [group_id_1, group_id_2],
        ###     int(load_balance_group_id_2) : [group_id_3, group_id_5],
        ###     int(load_balance_group_id_3) : [group_id_4,],
        ### }  
        self.sic_load_balance_groups = {} 
        self.iprobe_load_balance_groups = {} 

        self.flag_is_balanced = False


    def __len__(self):
        return len(self.groups_info_dict)


    def __average_load_balance(self, groups):
        sorted_groups = sorted(self.groups_info_dict.keys(), key = lambda x : self.groups_info_dict[x]["hit_counter"])
        sorted_groups.reverse()
        
        index_list = [n for n in range(1, len(sorted_groups)+1)]
        
        load_balance_index_list = [ [] for i in range(groups)]

        for i in index_list:
            load_balance_index_list.sort(key = lambda x : sum(x))
            load_balance_index_list[0].append(i)

        for this_group in load_balance_index_list:
            chunk = []
            for element in this_group:
                chunk.append(sorted_groups[element-1])
            self.sic_load_balance_groups[load_balance_index_list.index(this_group)+1] = chunk


    def __round_robin_load_balance(self, type_Cfg, groups, use_for):
        for i in self.groups_info_dict.keys():
            if self.groups_info_dict[i]["new_group"] == True:
                try:
                    type_Cfg.load_balance_index_list[self.groups_info_dict[i]["number"]%groups].append(i)
                    self.groups_info_dict[i]["new_group"] = False
                except ZeroDivisionError:
                    self.groups_info_dict[i]["new_group"] = False
                    pass
        self.sic_load_balance_groups = {}
        self.iprobe_load_balance_groups = {}
        for this_group in type_Cfg.load_balance_index_list:
            chunk = []
            for element in this_group:
                chunk.append(self.groups_info_dict[element]["ip_list"])
                if use_for == "sic":
                    self.sic_load_balance_groups[type_Cfg.load_balance_index_list.index(this_group)+1 ] = chunk
                if use_for == "iprobe":
                    self.iprobe_load_balance_groups[type_Cfg.load_balance_index_list.index(this_group)+1 ] = chunk

    
    def get_all_ip_list(self):
        all_ip_list = []
        for group in self.groups_info_dict.keys():
            all_ip_list.extend(ip for ip in self.groups_info_dict[group]["ip_list"])
            self.logger.debug("all_ip_list:", all_ip_list)
        return all_ip_list


    def line_append(self, group, group_id = 1):
        group_info = { "ip_list": [], "rule_info":None, "group_id":0, "new_ip_list":[], "delete_ip_list":[] }
        self.logger.debug("line_append group:", group)
        self.logger.debug("line_append group len:", len(group))

        if len(group) > 0:
            self.logger.debug("groups_info_dict keys:", self.groups_info_dict.keys())
            if group_id in self.groups_info_dict.keys():
                group_info = self.groups_info_dict[group_id]

            group_info["new_ip_list"] = []
            splited_infos = group.split(" ")

            for info in splited_infos:
                #one_info = info.split(':')
                one_info = info.split("->")
                try:
                    ipaddress.ip_address(one_info[0])
                    if one_info[0] in group_info["ip_list"]:
                        continue
                    else:
                        group_info["ip_list"].append(one_info[0])
                        group_info["new_ip_list"].append(one_info[0])
                        group_info["group_id"] = int(group_id)
                except ValueError:
                    self.logger.error("Ooops: invalid ip address,", one_info[0])                  

            self.logger.debug("groups_info_dict[%s]:"%(group_id), group_info)
            self.groups_info_dict[group_id] = group_info


    def associate_line_append(self, type_Cfg, group, group_id, mme_group, mme_code):
        flag_is_found = True
        group_info = { 
                       "ip_list": [], "rule_info": None, "group_id": 0, "new_ip_list": [], "delete_ip_list": [],
                       "s1_ip_list": [], "s11_ip_list": [], "s6a_ip_list": [], "sgs_ip_list": [], 
                       "new_group": True, "number": 0, "mme_group": 0, "mme_code": 0
                     }

        if len(group):
            if group_id in self.groups_info_dict.keys():
                group_info["new_group"] = False
                group_info = self.groups_info_dict[group_id]

            group_info["new_ip_list"] = []
            splited_infos = group

            for info in splited_infos:
                flag_is_found = False
                #one_info = info.split(":")
                one_info = info.split()
                try:
                    ipaddress.ip_address(one_info[0])
                    for i in self.groups_info_dict.keys():
                       if one_info[0] in  self.groups_info_dict[i]["ip_list"]:
                           flag_is_found = True
                           break

                    if flag_is_found:
                        if i == group_id:
                            continue
                        else:
                            Gloabal_Var.NEED_UPDATE_CONFIG = True

                            group_info["ip_list"].append(one_info[0])
                            group_info["new_ip_list"].append(one_info[0])
                            group_info["group_id"] = int(group_id)
                            self.groups_info_dict[i]["ip_list"].remove(one_info[0])
                            self.groups_info_dict[i]["delete_ip_list"].remove(one_info[0])

                            if one_info[0] in type_Cfg.s1_mme_ip_list:
                                group_info["s1_ip_list"].append(one_info[0])
                                self.groups_info_dict[i]["s1_ip_list"].remove(one_info[0])
                            if one_info[0] in type_Cfg.s6a_mme_ip_list:
                                group_info["s6a_ip_list"].append(one_info[0])
                                self.groups_info_dict[i]["s6a_ip_list"].remove(one_info[0])
                            if one_info[0] in type_Cfg.s11_mme_ip_list:
                                group_info["s11_ip_list"].append(one_info[0])
                                self.groups_info_dict[i]["s11_ip_list"].remove(one_info[0])
                    else:
                        Gloabal_Var.NEED_UPDATE_CONFIG = True
                        group_info["ip_list"].append(one_info[0])
                        group_info["new_ip_list"].append(one_info[0])
                        group_info["group_id"] = int(group_id)
                        if one_info[0] in type_Cfg.s1_mme_ip_list:
                            group_info["s1_ip_list"].append(one_info[0])
                        if one_info[0] in type_Cfg.s6a_mme_ip_list:
                            group_info["s6a_ip_list"].append(one_info[0])
                        if one_info[0] in type_Cfg.s11_mme_ip_list:
                            group_info["s11_ip_list"].append(one_info[0])
                except ValueError:
                    self.logger.error("Ooops: invalid ip address,", one_info[0])

            if group_info["new_group"]:
                group_info["number"] = len(self.groups_info_dict)
                group_info["mme_group"] = int(mme_group)
                group_info["mme_code"] = int(mme_code) 
                self.groups_info_dict[group_id] = group_info

            self.logger.debug("associate_line_append new_ip_list:",self.groups_info_dict[group_id]["new_ip_list"])
            self.logger.debug("associate_line_append ip_list:",self.groups_info_dict[group_id]["ip_list"])


    def load_balance(self, type_Cfg, groups, use_for, mode = "round-robin"):
        if mode == "round-robin":
            self.__round_robin_load_balance(type_Cfg, groups, use_for)
        elif mode == "average":
            self.__average_load_balance(groups)


    #######FULL MASH######
    def get_ip_info(self, ip):
        for group in self.groups_info_dict.keys():
            if ip in self.groups_info_dict[group]["ip_list"]:
                return self.groups_info_dict[group]["ip_list"]
        return None


    def get_group_rule_info(self, group_id):
        if group_id in self.groups_info_dict.keys():
            return self.groups_info_dict[group_id]["rule_info"]


    def is_ip_configed(self, group):
        if group in self.groups_info_dict.keys():
            if self.groups_info_dict[group] != None:
                return True
        return None

    def sum_of_load_balance_group_hit_counter(self, load_balance_grp_id):
        s = 0 
        for group in self.load_balance_groups[load_balance_grp_id]:
            s += self.groups_info_dict[group]["hit_counter"]
        return s


class Autolearn_tools:
    config_file_to_info_obj_dict = {}
    #max ip input cpu number
    #IP corresponds to two rules , so one_time_input_cpu_num*2 < (autolearning can use rule range)
    #default = 500   if  default  number of rules is not provisional
    one_time_input_cpu_num = 500  
    time_start = 0
    time_end = 0
    logger = Logging()


    @classmethod
    def user_info_config_parse(cls, config_file):
        new_info = None
        try:
            f = open(config_file, mode = "rt", encoding = "utf-8")

            if config_file not in cls.config_file_to_info_obj_dict.keys():
                new_info = User_Info(config_file)
                cls.config_file_to_info_obj_dict[config_file] = new_info
            else:
                new_info = cls.config_file_to_info_obj_dict[config_file]

            group_id = 1 
            for line in f.readlines():
                cls.logger.debug(config_file,":",line)
                new_info.line_append(line.rstrip(), group_id)
                group_id +=1
            if len(new_info) == 0 :
                del new_info
                new_info = None
            f.close()
        except FileNotFoundError:
            cls.logger.error("No such file or directory:", config_file)

        return new_info


    @classmethod
    def associate_config_parse(cls, type_Cfg, config_file):
        new_info = None
        try:
            f = open(config_file, mode = "rt", encoding = "utf-8")

            if config_file not in cls.config_file_to_info_obj_dict.keys():
                new_info = User_Info(config_file)
                cls.config_file_to_info_obj_dict[config_file] = new_info
            else:
                new_info =cls.config_file_to_info_obj_dict[config_file]

            group_id = 0
            for line in f.readlines():
                line_info = line.split()
                group_id = int(line_info[0])*65535 + int(line_info[1])/2
                ip_line = line_info[2:]
                new_info.associate_line_append(type_Cfg, ip_line, group_id, line_info[0], line_info[1])

            if len(new_info) == 0:
                del new_info
                new_info = None

            f.close()
        except FileNotFoundError:
            cls.logger.error("No such file or directory:", config_file)
        except IndexError:
            cls.logger.error("%s file is NULL"%config_file)

        return new_info

    @classmethod
    def write_rc(cls, type_Cfg, rule_id_dict, rule_ipv6_id_dict):
        f = open(Gloabal_Var.RC_LOAD_CONF, 'w', encoding = 'utf-8')
        for i in list(rule_id_dict.keys()):
            inports = rule_id_dict[i][0]
            sicip = rule_id_dict[i][1]
            dstip = rule_id_dict[i][2]
            l4srcport = rule_id_dict[i][3]
            l4dstport = rule_id_dict[i][4]
            ipprotocol = rule_id_dict[i][5]
            port_action_id = rule_id_dict[i][6]
            lag_action_id = rule_id_dict[i][7]
            rule_id = rule_id_dict[i][8]
            prio = rule_id_dict[i][9]
            modid = rule_id_dict[i][10]

            cmd = type_Cfg._build_fp_rule_command(inports, sicip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modid)
            for j in cmd:
                f.write(j)
        f.close()

        f = open(Gloabal_Var.RC_IPV6_LOAD_CONF, 'w', encoding = 'utf-8')
        for i in list(rule_ipv6_id_dict.keys()):
            inports = rule_ipv6_id_dict[i][0]
            sicip = rule_ipv6_id_dict[i][1]
            dstip = rule_ipv6_id_dict[i][2]
            l4srcport = rule_ipv6_id_dict[i][3]
            l4dstport = rule_ipv6_id_dict[i][4]
            ipprotocol = rule_ipv6_id_dict[i][5]
            port_action_id = rule_ipv6_id_dict[i][6]
            lag_action_id = rule_ipv6_id_dict[i][7]
            rule_id = rule_ipv6_id_dict[i][8]
            prio = rule_ipv6_id_dict[i][9]
            modid = rule_ipv6_id_dict[i][10]

            cmd = type_Cfg._build_fp_rule_command(inports, sicip, dstip, l4srcport, l4dstport, ipprotocol, port_action_id, lag_action_id, rule_id, prio, modid)
            for j in cmd:
                f.write(j)
        f.close()


    @classmethod
    def put_config_remote_from_rc(cls, type_Cfg):
        try:
            #ipv4
            f =  open(Gloabal_Var.RC_LOAD_CONF, "rt", encoding = "utf-8")
            lines = f.readlines()
            type_Cfg.send_command(lines, type_Cfg.pps_ip, Gloabal_Var.PPS_SERVICE)
            f.close()
        except FileNotFoundError:
            cls.logger.error("No such file or directory:", Gloabal_Var.RC_LOAD_CONF)
        try:
            #ipv6
            f =  open(Gloabal_Var.RC_IPV6_LOAD_CONF, "rt", encoding = "utf-8")
            lines = f.readlines()
            type_Cfg.send_command(lines, type_Cfg._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
            f.close()
        except FileNotFoundError:
            cls.logger.error("No such file or directory:", Gloabal_Var.RC_IPV6_LOAD_CONF)


    @classmethod
    def do_install_combined_rule(cls, type_Cfg, ip):
        src_rule_info = None
        dst_rule_info = None
        src_rule_info, dst_rule_info = type_Cfg.install_fp_ip_rule(ip, rule_id = None, prio = None)
        return (src_rule_info, dst_rule_info)

    
    @classmethod
    def do_uninstall_combined_rule(cls, type_Cfg, src_rule_info, dst_rule_info):
        if src_rule_info[1] == "ipv4":
            type_Cfg.do_destory_fp_rule(type_Cfg.autolearn_ingress_ports, src_rule_info[0])
        elif src_rule_info[1] == "ipv6":
            type_Cfg.do_destory_ipv6_rule(type_Cfg.autolearn_ingress_ports, src_rule_info[0])
        if dst_rule_info[1] == "ipv4":
            type_Cfg.do_destory_fp_rule(type_Cfg.autolearn_ingress_ports, dst_rule_info[0])
        elif dst_rule_info[1] == "ipv6":
            type_Cfg.do_destory_ipv6_rule(type_Cfg.autolearn_ingress_ports, dst_rule_info[0])


    ###Relational learning base func
    @classmethod
    def do_combined_rule(cls, type_Cfg, a_ip_list, b_ip_list):
        
        #Calculate the number of available rules
        cls.one_time_input_cpu_num = int(len(type_Cfg.fp_rule_id_queue)/2)
        #debug
        cls.logger.debug("one_time_input_cpu_num:",cls.one_time_input_cpu_num)
        cls.logger.debug("a_ip_list:", a_ip_list)
        cls.logger.debug("b_ip_list:", b_ip_list)

        combined_iter = itertools.product(a_ip_list, b_ip_list)
        ###a_ip_list = [ip1] , b_ip_list = [ip2, ip3]
        ###eg:cdr_ip_list = [(ip1,ip2),[ip1,ip3]]
        cdr_ip_list = []
        for ips in combined_iter:
            cdr_ip_list.append(sorted(ips))
        cdr_ip_list_bak =[]

        #debug
        cls.logger.debug("before cdr_ip_list:", cdr_ip_list)

        ###List removal duplication
        for i in cdr_ip_list:
            if i not in cdr_ip_list_bak:
                cdr_ip_list_bak.append(i)
        cdr_ip_list = cdr_ip_list_bak

        #debug
        cls.logger.debug("after cdr_ip_list:", cdr_ip_list)

        begin = 0
        if cls.one_time_input_cpu_num >= len(cdr_ip_list):
            end = len(cdr_ip_list)
        else:
            end = begin + cls.one_time_input_cpu_num

        tmp_ip_list_old = []
        while True:
            tmp_ip_list = []
            tmp_ip_rule_dict = {}
            for i in range(begin, end):
                for j in cdr_ip_list[i]:
                    tmp_ip_list.append(j)
            tmp_ip_list = list(set(tmp_ip_list))
            tmp_ip_list.sort()
            ###Whether the same IP list already exists
            if tmp_ip_list not in tmp_ip_list_old:
                tmp_ip_list_old.append(tmp_ip_list)
                for aip in tmp_ip_list:
                    result = cls.do_install_combined_rule(type_Cfg, aip)
                    tmp_ip_rule_dict[aip] = result
                if len(tmp_ip_list) >0:
                    time.sleep(60)
            else:
                pass

            for aip in tmp_ip_rule_dict.keys():
                cls.do_uninstall_combined_rule(type_Cfg, tmp_ip_rule_dict[aip][0], tmp_ip_rule_dict[aip][1])
            
            begin = end
            if (end + cls.one_time_input_cpu_num) >= len(cdr_ip_list):
                end = len(cdr_ip_list)
            else:
                end = end + cls.one_time_input_cpu_num
            if begin == len(cdr_ip_list):
                break
            

    @classmethod
    def load_all_ip(cls, type_Cfg):
        stage_config_file = (Gloabal_Var.PGW_C_CONFIG, Gloabal_Var.GGSN_C_CONFIG, Gloabal_Var.S11_AND_S5S8_CONF, 
                             Gloabal_Var.DEB_CONFIG, Gloabal_Var.SGS_CONFIG, Gloabal_Var.HSS_CONFIG,
                             Gloabal_Var.SGW_CONFIG, Gloabal_Var.LOCAL_SGSN_C_CONFIG, Gloabal_Var.SGSN_C_CONFIG,
                             Gloabal_Var.LOCAL_S5S8_C_CONFIG, Gloabal_Var.S5S8_C_CONFIG, Gloabal_Var.SGW_C_CONFIG)

        for filename in stage_config_file:
            cls.user_info_config_parse(filename)
        
        s11_and_s5s8_info = cls.config_file_to_info_obj_dict[Gloabal_Var.S11_AND_S5S8_CONF]
        type_Cfg.s11_s5s8_ip_list = s11_and_s5s8_info.get_all_ip_list()

        cls.logger.debug("s11_s5s8_ip_list:", type_Cfg.s11_s5s8_ip_list)

        local_sgsn_info = cls.config_file_to_info_obj_dict[Gloabal_Var.LOCAL_SGSN_C_CONFIG]
        type_Cfg.local_sgsn_c_ip_list = local_sgsn_info.get_all_ip_list()

        cls.logger.debug("local_sgsn_c_ip_list:", type_Cfg.local_sgsn_c_ip_list)

        s5s8_c_info = cls.config_file_to_info_obj_dict[Gloabal_Var.S5S8_C_CONFIG]
        type_Cfg.s5s8_c_ip_list = s5s8_c_info.get_all_ip_list()

        cls.logger.debug("s5s8_c_ip_list:", type_Cfg.s5s8_c_ip_list)

        local_s5s8_info = cls.config_file_to_info_obj_dict[Gloabal_Var.LOCAL_S5S8_C_CONFIG]
        type_Cfg.local_s5s8_c_ip_list = local_s5s8_info.get_all_ip_list()

        cls.logger.debug("local_s5s8_c_ip_list:", type_Cfg.local_s5s8_c_ip_list)

        sgw_info = cls.config_file_to_info_obj_dict[Gloabal_Var.SGW_CONFIG]
        type_Cfg.s11_mme_ip_list = sgw_info.get_all_ip_list()

        cls.logger.debug("s11_mme_ip_list:", type_Cfg.s11_mme_ip_list)

        sgw_c_info = cls.config_file_to_info_obj_dict[Gloabal_Var.SGW_C_CONFIG]
        type_Cfg.sgw_ip_list = sgw_c_info.get_all_ip_list()

        cls.logger.debug("sgw_ip_list:", type_Cfg.sgw_ip_list)

        hss_info = cls.config_file_to_info_obj_dict[Gloabal_Var.HSS_CONFIG]
        type_Cfg.s6a_mme_ip_list = hss_info.get_all_ip_list()

        cls.logger.debug("s6a_mme_ip_list:", type_Cfg.s6a_mme_ip_list)

        enobe_info = cls.config_file_to_info_obj_dict[Gloabal_Var.DEB_CONFIG]
        type_Cfg.s1_mme_ip_list = enobe_info.get_all_ip_list()

        cls.logger.debug("s1_mme_ip_list:", type_Cfg.s1_mme_ip_list)
        

    @classmethod
    def save_loop_times(cls, loop_times):
        f = open(Gloabal_Var.COMMAND_HISTORY, "w", encoding = "utf-8")
        f.write("loop_times: %s\n"%str(loop_times))
        f.close()


    @classmethod 
    def read_se_commend_memory(cls, stage):
        stage1_config_file = {
                                Gloabal_Var.LOCAL_SGSN_C_CONFIG : "local-sgsn-gnc"
                             }

        stage2_1_config_file = {
                                Gloabal_Var.DEB_CONFIG : "mme-s1", Gloabal_Var.SGS_CONFIG : "mme-sgs", Gloabal_Var.HSS_CONFIG : "mme-s6a", Gloabal_Var.SGW_CONFIG : "mme-s11"
                                }

        stage_remain_config_file = {
                                Gloabal_Var.LOCAL_S5S8_C_CONFIG : "local-sgw-s5s8c", Gloabal_Var.S5S8_C_CONFIG : "sgw-s5s8c", Gloabal_Var.SGW_C_CONFIG : "sgw-s11"
                                    }

        stage_associate_ip_file = {
                                    Gloabal_Var.S11_AND_S5S8_CONF : "sgw-s11-s5s8", Gloabal_Var.ASSOCIATE_CONFIG : "mme"
                                  }
        ###switch stage
        os.system("./rpcc {0} {1} {2} 'set autolearn-stage {3}' 10".format("127.0.0.1", Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT, stage))


        ###read conf file
        for conf in stage1_config_file.keys():
            read_cmd = "show learn-dev-ip {0} write /rootfs/autolearn/{1}".format(stage1_config_file[conf], conf)
            #debug
            cls.logger.debug(read_cmd)
            cmd = "./rpcc {0} {1} {2} '{3}' 10".format("127.0.0.1", Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, read_cmd)
            os.system(cmd)
        if stage == 1:
            return    
        for conf in stage2_1_config_file.keys():
            read_cmd = "show learn-dev-ip {0} write /rootfs/autolearn/{1}".format(stage2_1_config_file[conf], conf)
            #debug
            cls.logger.debug(read_cmd)
            cmd = "./rpcc {0} {1} {2} '{3}' 10".format("127.0.0.1", Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, read_cmd)
            os.system(cmd)
        if stage == 2:
            return 
        for conf in stage_remain_config_file.keys():
            read_cmd = "show learn-dev-ip {0} write /rootfs/autolearn/{1}".format(stage_remain_config_file[conf], conf)
            #debug
            cls.logger.debug(read_cmd)
            cmd = "./rpcc {0} {1} {2} '{3}' 10".format("127.0.0.1", Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, read_cmd)
            os.system(cmd)
        for conf in stage_associate_ip_file.keys():
            read_cmd = "show learn-associate-ip {0} write /rootfs/autolearn/{1}".format(stage_associate_ip_file[conf], conf)
            #debug
            cls.logger.debug(read_cmd)
            cmd = "./rpcc {0} {1} {2} '{3}' 10".format("127.0.0.1", Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, read_cmd)
            os.system(cmd)

    @classmethod
    def read_se_shared_memory(cls, stage):
        conf_file = [
                    "associate.conf", "ggsn_c.conf", "ggsn_u.conf", "local_s5s8_c.conf", "local_sgsn_c.conf",
                    "pgw_c.conf", "s11_and_s5s8.conf", "s11_c_for_s5s8.conf", "s11_mme.conf",
                    "s1_mme.conf", "s5s8_c.conf", "s5s8_c_ip_for_s11.conf", "s6a_mme.conf", 
                    "sgs_mme.conf", "sgsn_c.conf", "sgsn_u.conf", "sgw_c.conf", "sgw_u.conf"
                    ]
        for conf in conf_file:
            os.system("echo > {0}".format(conf))
        #os.system("{0} {1}".format(Gloabal_Var.CDR_IP_LIST_DUMP_COMMAND,stage))
        #cls.logger.debug("cdr_ip_list_dump:", "{0} {1}".format(Gloabal_Var.CDR_IP_LIST_DUMP_COMMAND,stage))

    ######Learn the IP , s11 on the mme side
    @classmethod
    def autolearn_stage_1(cls, type_Cfg):
        cls.time_start = time.time()
        cls.logger.debug("::::::Stage 1:::::::")
        cls.read_se_shared_memory("stage1")
        ######
        ### first time
        if Gloabal_Var.LOOP_TIMES == 0:
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###creat rule sp dp 2123 and send 
                type_Cfg.install_fp_srcport_rule(2123)
                type_Cfg.install_fp_dstport_rule(2123)

                type_Cfg.install_fp_srcport_rule_ipv6(2123)
                type_Cfg.install_fp_dstport_rule_ipv6(2123)

            for times in range(5):
                ###new
                cls.read_se_commend_memory(1)
                time.sleep(Gloabal_Var.TIME_DELAY_BASE)
                #debug
                cls.logger.debug("stage1 read shared memory times:", times)

            ###old
            #stage_1_config_files = (Gloabal_Var.PGW_C_CONFIG, Gloabal_Var.GGSN_C_CONFIG, Gloabal_Var.S11_AND_S5S8_CONF, 
            #                        Gloabal_Var.LOCAL_SGSN_C_CONFIG, Gloabal_Var.SGSN_C_CONFIG)
            ###new
            stage_1_config_files = ( Gloabal_Var.LOCAL_SGSN_C_CONFIG, Gloabal_Var.S11_AND_S5S8_CONF )

            for filename in stage_1_config_files:
                new_info  = cls.user_info_config_parse(filename)
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###destory rule         
                type_Cfg.do_destory_pf_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.phy_l4_srcport_rule_id)
                type_Cfg.do_destory_pf_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.phy_l4_dstport_rule_id)
                type_Cfg.do_destory_pf_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.phy_l4_srcport_rule_ipv6_id)
                type_Cfg.do_destory_pf_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.phy_l4_dstport_rule_ipv6_id)
        ######
        ### later time
        else:
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###close all flow    open default flow
                type_Cfg.send_command(["vlan remove 100 ports {0}".format(self.autolearn_ingress_ports)], self.pps_ip, Gloabal_Var.PPS_SERVICE)
                ###creat rule sp dp 2123 and send 
                if type_Cfg.gn_load_balance == False:
                    #type_Cfg.install_surplus_cmd(port_action_id = type_Cfg.sic_s11_default_egress, port = "2123")
                    #use vlan send
                else:
                    type_Cfg.install_surplus_cmd(lag_action_id = type_Cfg._lag_sic_ctrl_egress, port = "2123")

            for times in range(5):
                ###new
                cls.read_se_commend_memory(1)
                ###old
                #cls.read_se_shared_memory("stage1")

                time.sleep(Gloabal_Var.TIME_DELAY_BASE)
                #debug
                cls.logger.debug("stage1 read shared memory times:", times)

            ###old
            #stage_1_config_files = (Gloabal_Var.PGW_C_CONFIG, Gloabal_Var.GGSN_C_CONFIG, Gloabal_Var.S11_AND_S5S8_CONF, 
            #                        Gloabal_Var.LOCAL_SGSN_C_CONFIG, Gloabal_Var.SGSN_C_CONFIG)
            ###new
            stage_1_config_files = ( Gloabal_Var.LOCAL_SGSN_C_CONFIG, Gloabal_Var.S11_AND_S5S8_CONF )

            for filename in stage_1_config_files:
                new_info  = cls.user_info_config_parse(filename)
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###destory rule         
                type_Cfg.do_destory_fp_rule(type_Cfg.sic_ingress_ports, type_Cfg.phy_l4_srcport_rule_id)
                type_Cfg.do_destory_fp_rule(type_Cfg.sic_ingress_ports, type_Cfg.phy_l4_dstport_rule_id)

        

    ######Learn the IP , s1,s6a,sgs on the mme side
    @classmethod
    def autolearn_stage_2_1(cls, type_Cfg):
        cls.logger.debug("::::::Stage 2.1 ::::::")
        if (Gloabal_Var.LOOP_TIMES+1)%3 == 1:
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###creat rule proto 132 and send
                type_Cfg.install_fp_l3_protocol_rule(132)
                type_Cfg.install_fp_l3_protocol_rule_ipv6(132)

            for times in range(5):
                ###new
                cls.read_se_commend_memory(2)
                ###old
                #cls.read_se_shared_memory("stage2.1")

                time.sleep(Gloabal_Var.TIME_DELAY_BASE)
                #debug 
                cls.logger.debug("stage2.1 read shared memory times:", times)

            stage_2_1_config_files = (Gloabal_Var.DEB_CONFIG, Gloabal_Var.SGS_CONFIG, Gloabal_Var.HSS_CONFIG,Gloabal_Var.SGW_CONFIG)
            for filename in stage_2_1_config_files:
                new_info  = cls.user_info_config_parse(filename)
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###destory rule
                type_Cfg.do_destory_pf_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.phy_l3_protocol_rule_id)
                type_Cfg.do_destory_pf_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.phy_l3_protocol_rule_ipv6_id)
        else:
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                if type_Cfg.gn_load_balance == False:
                    type_Cfg.install_surplus_cmd(port_action_id = type_Cfg.sic_stcp_default_egress, proto = "132")
                else:
                    type_Cfg.install_surplus_cmd(lag_action_id = type_Cfg._lag_sic_ctrl_egress, proto = "132")

            for times in range(5):
                ###new
                cls.read_se_commend_memory(2)
                ###old
                #cls.read_se_shared_memory("stage2.1")

                time.sleep(Gloabal_Var.TIME_DELAY_BASE)
                #debug 
                cls.logger.debug("stage2.1 read shared memory times:", times)


            stage_2_1_config_files = (Gloabal_Var.DEB_CONFIG, Gloabal_Var.SGS_CONFIG, Gloabal_Var.HSS_CONFIG,Gloabal_Var.SGW_CONFIG)
            for filename in stage_2_1_config_files:
                new_info  = cls.user_info_config_parse(filename)
            if Gloabal_Var.FLAG_LOAD_CONFIG == False:
                ###destory rule
                type_Cfg.do_destory_pf_rule(type_Cfg.sic_ingress_ports, type_Cfg.phy_l3_protocol_rule_id)
                type_Cfg.do_destory_pf_ipv6_rule(type_Cfg.sic_ingress_ports, type_Cfg.phy_l3_protocol_rule_ipv6_id)


    ######Relationship learn, s1-s1  s1-s11 s1-s6a s1-sgs
    @classmethod
    def autolearn_stage_2_2(cls, type_Cfg):
        if Gloabal_Var.FLAG_LOAD_CONFIG == False:
            cls.logger.debug("::::::Stage 2.2 ::::::")

            #need if first
            type_Cfg.send_command(["vlan add 100 ports {0} untag {0}".format(self.autolearn_ingress_ports)], self.pps_ip, Gloabal_Var.PPS_SERVICE)
            ###Unlimit stage2.1 on se side
            ###new
            cls.read_se_commend_memory(3)

            ###old
            #cls.read_se_shared_memory("stage2.2")


            ######Combinded ip and send IP rules based on the result 
            #s1 s1
            s1_mme_ip_info = cls.config_file_to_info_obj_dict[Gloabal_Var.DEB_CONFIG]
            type_Cfg.s1_mme_ip_list = s1_mme_ip_info.get_all_ip_list()

            cls.logger.debug("s1_mme_ip_list:", type_Cfg.s1_mme_ip_list)

            cls.do_combined_rule(type_Cfg, type_Cfg.s1_mme_ip_list, type_Cfg.s1_mme_ip_list) 

            #sgs
            #msc_ip_info = cls.config_file_to_info_obj_dict[Gloabal_Var.SGS_CONFIG]
            #type_Cfg.msc_ip_list = msc_ip_info.get_all_ip_list()

            #cls.logger.debug("msc_ip_list:", type_Cfg.msc_ip_list)

            #cls.do_combined_rule(type_Cfg, type_Cfg.msc_ip_list, type_Cfg.msc_ip_list)


            ###Filter the IP learned by s6a
            '''
                When the IP of s6a has no mme group and mme code, need remain ip there hasn't mme group and mme code combinded s1 ip
            '''
            cmd = ["show learn-associate-ip mme write /rootfs/autolearn/associate.conf"]
            type_Cfg.send_command(cmd, type_Cfg._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
            new_info  = cls.associate_config_parse(type_Cfg, Gloabal_Var.ASSOCIATE_CONFIG)

            groups_info_dict_tmp = new_info.groups_info_dict
            learned_s6a_ip_list = []
            for group_id in list(groups_info_dict_tmp.keys()):
                learned_s6a_ip_list.extend(groups_info_dict_tmp[group_id]["s6a_ip_list"])

            #s6a s1
            s6a_mme_ip_info = cls.config_file_to_info_obj_dict[Gloabal_Var.HSS_CONFIG]
            type_Cfg.s6a_mme_ip_list = s6a_mme_ip_info.get_all_ip_list()

            cls.logger.debug("s6a_mme_ip_list:", type_Cfg.s6a_mme_ip_list)
            filter_s6a_ip_list = [ip for ip in type_Cfg.s6a_mme_ip_list if ip not in learned_s6a_ip_list]
            cls.logger.debug("filter_s6a_ip_list:", filter_s6a_ip_list)

            cls.do_combined_rule(type_Cfg, type_Cfg.s1_mme_ip_list, filter_s6a_ip_list)
            
            #s11 s1
            s11_mme_ip_info = cls.config_file_to_info_obj_dict[Gloabal_Var.SGW_CONFIG]
            type_Cfg.s11_mme_ip_list = s11_mme_ip_info.get_all_ip_list()

            cls.logger.debug("s11_mme_ip_list:", type_Cfg.s11_mme_ip_list)

            cls.do_combined_rule(type_Cfg, type_Cfg.s1_mme_ip_list, type_Cfg.s11_mme_ip_list)
            
            #s6a s11
            cls.do_combined_rule(type_Cfg, type_Cfg.s11_mme_ip_list, type_Cfg.s6a_mme_ip_list)
        else:
            cls.logger.debug("flag_alreadly config is true!")
            cls.logger.debug("::::::Stage 2.2 skiped ::::::")


    @classmethod
    ######Based on the learning NE, send traffic flow
    def autolearn_stage_3(cls, type_Cfg):
        cls.logger.debug("::::::Stage 3 ::::::")
        if Gloabal_Var.FLAG_LOAD_CONFIG == False:
            ###Unlimit stage2.1 on se side
            ###new
            cls.read_se_commend_memory(3)
            ###old
            #cls.read_se_shared_memory("stage2.2")
        else:
            if type_Cfg.dev_plat == "g06_68":           
                os.system("tftp -gr /rootfs/autolearn/associate.conf -l /rootfs/associate.conf %s"%type_Cfg.pps_ip)
            elif type_Cfg.dev_plat == "g06_78":
                os.system("tftp -gr /rootfs/associate.conf -l /rootfs/autolearn/associate.conf %s"%type_Cfg.pps_ip)
            else:
                os.system("cp {0} {1}".format(Gloabal_Var.ASSOCIATE_SAV, Gloabal_Var.ASSOCIATE_CONFIG))

        type_Cfg.load_config()
        cls.load_all_ip(type_Cfg)

        cmd = ["show learn-associate-ip mme write /rootfs/autolearn/associate.conf"]
        type_Cfg.send_command(cmd, type_Cfg._localhost_ip, Gloabal_Var.SIC_SERVICE, Gloabal_Var.SIC_CPU1_PORT)
        new_info  = cls.associate_config_parse(type_Cfg, Gloabal_Var.ASSOCIATE_CONFIG)
        cls.logger.debug("associate_config_parse  new_info:", new_info)

        if Gloabal_Var.NEED_UPDATE_CONFIG == True and Gloabal_Var.FLAG_ONLY_CHECK == False: 
            ###destory old rule dict
            type_Cfg.remove_old_rule_in_dict()

            ###no support iprobe
            sic_egress_for_ctrl_iter = iter(type_Cfg.sic_ctrl_egress)

            if new_info:
                new_info.load_balance(type_Cfg, len(type_Cfg.sic_ctrl_egress), "sic")
                if len(new_info.sic_load_balance_groups):
                    for groups in new_info.sic_load_balance_groups.keys():
                        egress = next(sic_egress_for_ctrl_iter)
                        for group in new_info.sic_load_balance_groups[groups]:
                            for ip in group:
                                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, ip, "", "", "", "", egress, "")
                                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", ip, "", "", "", egress, "")
            
            if type_Cfg.gn_load_balance == False:
                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", "", 2123, "", "", type_Cfg.sic_s11_default_egress, "", prio = 10)
                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", "", "", 2123, "", type_Cfg.sic_s11_default_egress, "", prio = 10)
                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", "", "", "", 132, type_Cfg.sic_stcp_default_egress, "", prio = 10)
            else:
                ###lag_id = lag_sic_ctrl_egress
                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", "", 2123, "", "", "", type_Cfg._lag_sic_ctrl_egress, prio = 10)
                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", "", "", 2123, "", "", type_Cfg._lag_sic_ctrl_egress, prio = 10)
                type_Cfg.build_remote_cmd(type_Cfg.sic_ingress_ports, "", "", "", "", 132, "", type_Cfg._lag_sic_ctrl_egress, prio = 10)
            ###support iprobe
            if Gloabal_Var.FLAG_IP_CONFIG == True:
                ip_egress_for_ctrl_iter = iter(type_Cfg.ip_ctrl_egress)
                
                if new_info:
                    new_info.load_balance(type_Cfg, len(ip_ctrl_egress), "iprobe")
                    if len(new_info.iprobe_load_balance_groups):
                        for groups in new_info.iprobe_load_balance_groups.keys():
                                egress = next(ip_egress_for_ctrl_iter)
                                for group in new_info.iprobe_load_balance_groups[groups]:
                                    for ip in group:
                                        type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, ip, "", "", "", "", egress, "")
                                        type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", ip, "", "", "", egress, "")
                if type_Cfg.gn_load_balance == False:
                    type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", "", 2123, "", "", type_Cfg.ip_s11_default_egress, "", prio = 10)
                    type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", "", "", 2123, "", type_Cfg.ip_s11_default_egress, "", prio = 10)
                    type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", "", "", "", 132, type_Cfg.ip_stcp_default_egress, "", prio = 10)
                else:
                    ###trunk_id = lag_ip_ctrl_egress
                    type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", "", 2123, "", "", "", type_Cfg._lag_ip_ctrl_egress, prio = 10)
                    type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", "", "", 2123, "", "", type_Cfg._lag_ip_ctrl_egress, prio = 10)
                    type_Cfg.build_remote_cmd(type_Cfg.ip_ingress_ports, "", "", "", "", 132, "", type_Cfg._lag_ip_ctrl_egress, prio = 10)
            
        if Gloabal_Var.FLAG_LOAD_CONFIG == True:
            cls.logger.debug("::: Reload old ip table from share memory complete")
            Gloabal_Var.FLAG_LOAD_CONFIG = False

            ###only check
            if Gloabal_Var.FLAG_ONLY_CHECK == True:
                ###check path quality
                Check_path_quality_tools.check_path_quality_result(type_Cfg, new_info)
                exit()

            if Gloabal_Var.NEED_UPDATE_CONFIG == True:
                cls.write_rc(type_Cfg, type_Cfg.remote_rule_id_dict, type_Cfg.remote_rule_ipv6_id_dict)
                cls.put_config_remote_from_rc(type_Cfg)
        else:
            Gloabal_Var.LOOP_TIMES += 1
            cls.save_loop_times(Gloabal_Var.LOOP_TIMES)
            
            ###add time delay 
            Gloabal_Var.TIME_DELAY_BASE += Gloabal_Var.TIME_DELAY_STEP

            if Gloabal_Var.NEED_UPDATE_CONFIG == True:
                cls.write_rc(type_Cfg, type_Cfg.remote_rule_id_dict, type_Cfg.remote_rule_ipv6_id_dict)
                cls.put_config_remote_from_rc(type_Cfg)
                type_Cfg.save_61_config(new_info)

            ###recording time
            cls.time_end = time.time()
            cls.logger.debug("==============times:  {0}".format(cls.time_end-cls.time_start))

            if Gloabal_Var.NOLOOP == True:
                exit()


        if Gloabal_Var.LOOP_TIMES%3 ==0 and Gloabal_Var.LOOP_TIMES !=0:
            Gloabal_Var.TIME_DELAY_BASE = Gloabal_Var.TIME_DELAY_STEP
            ###check path quality
            Check_path_quality_tools.check_path_quality_result(type_Cfg, new_info)


class Check_path_quality_tools:
    remote_s5s8_c_info_need  = False
    remote_sgsn_c_info_need  = False
    local_s5s8_c_info_need  = True
    local_sgsn_c_info_need  = True
    PORT_BITS_PATH = "port_bits"

    time_start = 0
    time_end = 0

    logger = Logging()

    @classmethod
    def get_teminal_output(cls, command):
        os.system("{0} > {1}".format(command, cls.PORT_BITS_PATH))
        with open(cls.PORT_BITS_PATH, mode = "r", encoding = "utf-8") as cpu_engress_bits:
            output =  cpu_engress_bits.readlines()
        return output


    @classmethod
    def get_port_bits(cls, type_Cfg, pps_to_autolearn_port):
        ###delay times because  wait  port stat update
        time.sleep(3)
        pps_ip = type_Cfg.pps_ip
        rpcc_port = Gloabal_Var.PPS_PORT
        mode = Gloabal_Var.PPS_SERVICE
        cmd = "show port_stat all"
        time_out = 10

        rpcc_cmd = "./rpcc %s %s %s '%s' %s |awk '{if($1==\"%s\"){print $9}}'"%(pps_ip, rpcc_port, mode, cmd, time_out, pps_to_autolearn_port)

        cls.logger.debug(":::get_port_bits:", rpcc_cmd)

        return cls.get_teminal_output(rpcc_cmd)


    @classmethod
    def stat_path_of_chain(cls, file, stat_time, filter_str):
        os.system("./rpcc localhost 9090 2 'clean learn-associate-stat' 10")
        time.sleep(stat_time)
        bits = ""
        cmd = "show learn-associate-stat all"
        if filter_str != "":
            rpcc_cmd = "./rpcc localhost {0} {1} '{2}' 10 | grep 'cdr\|dl\|ul\|s1 auth' | grep -v 'switch' | sed 's/ : /,/g' | sed 's/^\s*//g' | grep '{3}' | awk -F , '{4}'".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, filter_str, "{printf(\"%s,\\n\",$2)}")
            for line in cls.get_teminal_output(rpcc_cmd):
                file.write(line)
                file.flush()
        else:
            rpcc_cmds = [
                    "./rpcc localhost {0} {1} '{2}' 10 | grep '{3}' | sed 's/ : /,/g' |sed 's/^\s*//g' | awk -F , '{5}' >  {4}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, "initial cdr", cls.PORT_BITS_PATH, "{printf(\"%s,\",$2)}") , 
                    "./rpcc localhost {0} {1} '{2}' 10 | grep '{3}' | sed 's/ : /,/g' |sed 's/^\s*//g' | awk -F , '{5}' >> {4}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, "s11 cdr", cls.PORT_BITS_PATH, "{printf(\"%s,\",$2)}") , 
                    "./rpcc localhost {0} {1} '{2}' 10 | grep '{3}' | sed 's/ : /,/g' |sed 's/^\s*//g' | awk -F , '{5}' >> {4}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, "s6a auth cdr create", cls.PORT_BITS_PATH, "{printf(\"%s,\",$2)}"),
                    "./rpcc localhost {0} {1} '{2}' 10 | grep '{3}' | sed 's/ : /,/g' |sed 's/^\s*//g' | awk -F , '{5}' >> {4}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, "learn user bear ul create", cls.PORT_BITS_PATH, "{printf(\"%s,\",$2)}"),
                    "./rpcc localhost {0} {1} '{2}' 10 | grep '{3}' | sed 's/ : /,/g' |sed 's/^\s*//g' | awk -F , '{5}' >> {4}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, "learn user bear ul create", cls.PORT_BITS_PATH, "{printf(\"%s,\",$2)}"),
                    "./rpcc localhost {0} {1} '{2}' 10 | grep '{3}' | sed 's/ : /,/g' |sed 's/^\s*//g' | awk -F , '{5}' >> {4}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_SERVICE, cmd, "s1 auth find s6a count", cls.PORT_BITS_PATH, "{printf(\"%s\\n\",$2)}")
                        ]
            for cmd in rpcc_cmds:
                os.system(cmd)
            with open(cls.PORT_BITS_PATH, mode = "r", encoding = "utf-8") as cpu_engress_bits:
                output =  cpu_engress_bits.readlines()
            for line in output: 
                file.write(line)
                file.flush()


    @classmethod
    def check_do_install_rule(cls, type_Cfg, ip):
        srcip_rule_info = type_Cfg.do_install_fp_rule(type_Cfg.autolearn_ingress_ports, ip, "", "", "", "", type_Cfg.pps_to_autolearn_port, "")
        dstip_rule_info = type_Cfg.do_install_fp_rule(type_Cfg.autolearn_ingress_ports, "", ip, "", "", "", type_Cfg.pps_to_autolearn_port, "")
        if srcip_rule_info[1] == "ipv4":
            type_Cfg.rule_id_dict[srcip_rule_info[0]] = (type_Cfg.autolearn_ingress_ports, ip, "", "", "", "", type_Cfg.pps_to_autolearn_port, "", srcip_rule_info[0], srcip_rule_info[0])
        elif srcip_rule_info[1] == "ipv6":
            type_Cfg.rule_ipv6_id_dict[srcip_rule_info[0]] = (type_Cfg.autolearn_ingress_ports, ip, "", "", "", "", type_Cfg.pps_to_autolearn_port, "", srcip_rule_info[0], srcip_rule_info[0])
        if dstip_rule_info[1] == "ipv4":
            type_Cfg.rule_id_dict[dstip_rule_info[0]] = (type_Cfg.autolearn_ingress_ports, "", ip, "", "", "", type_Cfg.pps_to_autolearn_port, "", dstip_rule_info[0], dstip_rule_info[0])
        elif dstip_rule_info[1] == "ipv6":
            type_Cfg.rule_ipv6_id_dict[dstip_rule_info[0]] = (type_Cfg.autolearn_ingress_ports, "", ip, "", "", "", type_Cfg.pps_to_autolearn_port, "", dstip_rule_info[0], dstip_rule_info[0])

    
    @classmethod
    def write_mme_quality(cls, result_info, type_Cfg, ip_title, ip_list):
        if len(ip_list) > 0:
            for ip in ip_list:
                cls.check_do_install_rule(type_Cfg, ip)
                if ip_title != "MME total bits,":
                    result_info.write(ip + " ")
                    result_info.flush()

            bits = ""
            bits = cls.get_port_bits(type_Cfg, type_Cfg.pps_to_autolearn_port)[0].rstrip()

            cls.logger.debug(":::write_mme_qulity:", bits)

            result_info.write("(%sM),"%bits)
            result_info.flush()
            if ip_title == "MME total bits,":
                cls.stat_path_of_chain(result_info, 60, "")
            #ipv4
            cls.logger.debug("rule_id_dict:", type_Cfg.rule_id_dict)
            for i in list(type_Cfg.rule_id_dict.keys()):
                cls.logger.debug("rule_id_dict[{0}]:".format(i), type_Cfg.rule_id_dict[i][8])
                type_Cfg.do_destory_fp_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_id_dict[i][8])
            #ipv6
            cls.logger.debug("rule_ipv6_id_dict:", type_Cfg.rule_ipv6_id_dict)
            for i in list(type_Cfg.rule_ipv6_id_dict.keys()):
                cls.logger.debug("rule_ipv6_id_dict[{0}]:".format(i), type_Cfg.rule_ipv6_id_dict[i][8])
                type_Cfg.do_destory_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_ipv6_id_dict[i][8])


    @classmethod
    def get_lte_ip_info(cls, type_Cfg, ip_lost_mme, file, filter_str, autolearn_ingress_ports, pps_to_autolearn_port):
        if len(ip_lost_mme) > 0:
            cls.logger.debug("get_lte_ip_info === ip_list_mme:", ip_lost_mme )
            for ip in ip_lost_mme:
                cls.check_do_install_rule(type_Cfg, ip)

                bits = ""
                bits = cls.get_port_bits(type_Cfg, type_Cfg.pps_to_autolearn_port)[0].rstrip()
                file.write("%s(%sM),"%(ip, bits))
                file.flush()
                cls.stat_path_of_chain(file, 10, filter_str)
                #ipv4
                for i in list(type_Cfg.rule_id_dict):
                    type_Cfg.do_destory_fp_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_id_dict[i][8])
                #ipv6
                for i in list(type_Cfg.rule_ipv6_id_dict):
                    type_Cfg.do_destory_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_ipv6_id_dict[i][8])
            file.write("\n")
            file.flush()


    @classmethod 
    def get_gtpv1_quality(cls):
        cmd = "show gtpv1-info cdr"
        awk = "awk 'BEGIN{a=4}{if($1==\"create\"||($1==\"update\"&&$2==\"pdp\"&&$3==\"cdr\")){print $0;a=0}else if (a<2){print$0;a++}}'"
        rpcc_cmd = "./rpcc localhost {0} {1} '{2}' 10 | {3}".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_STAT, cmd, awk)
        ###Eg:this is result
        ### create pdp cdr create : 0
        ### delete : 0
        ### timeout : 0
        ### update pdp cdr create : 0
        ### delete : 0
        ### timeout : 0
        return cls.get_teminal_output(rpcc_cmd)


    @classmethod
    def get_sgsnc_ip_res_rate(cls, type_Cfg, ip_lost_mme, file, autolearn_ingress_ports, pps_to_autolearn_port):
        if len(ip_lost_mme) > 0:
            cls.logger.debug("get_sgsnc_ip_res_rate === ip_list_mme:", ip_lost_mme )
            for ip in ip_lost_mme:
                os.system("./rpcc localhost {0} {1} 'clean learn-associate-stat' 10".format(Gloabal_Var.SIC_CPU1_PORT, Gloabal_Var.SIC_STAT))

                cls.check_do_install_rule(type_Cfg, ip)
                time.sleep(10)

                bits = ""
                bits = cls.get_gtpv1_quality()

                #debug
                cls.logger.debug("Gtpv1_quality:\n",bits)

                total_create = int(bits[0].split(":")[1].strip()) + int(bits[3].split(":")[1].strip())
                total_match = int(bits[1].split(":")[1].strip()) + int(bits[4].split(":")[1].strip())

                if total_create != 0:
                    #debug
                    cls.logger.debug(str(format(float(total_match*100)/float(total_create),".2f")))
                    
                    file.write("{0}/{1}({2}%)\n".format(str(total_create), str(total_match), str(format(float(total_match*100)/float(total_create), ".2f")) ))
                    file.flush()
                else:
                    file.write("0/0(0.00%)\n")
                    file.flush()

                
    @classmethod
    def check_path_quality_send_rule(cls, type_Cfg, new_info, result_file):
        cls.logger.debug("::: check_path_quality_send_rule ::::")
        if new_info != None:
            groups_info_dict = {}
            group_keys_list = []
            one_line_ip = []
            groups_info_dict = new_info.groups_info_dict

            result_file.write("mme group id,mme code id,S1-MME IP,S11-MME IP,S6a-MME IP,MME total bits,S1-MME inner match,S11-MME inner match,S6a-MME inner match,S1-MME match S11-MME,S11-MME match S1-MME,S6a-MME match S1-MME,\n")

            cls.logger.debug("groups_info_dict", groups_info_dict)
            for group_id in groups_info_dict.keys():
                ###delete autolearn rule
                cls.logger.debug("check_path_quality_send_rule### rule_id_dict:", type_Cfg.rule_id_dict)
                cls.logger.debug("check_path_quality_send_rule### rule_ipv6_id_dict:", type_Cfg.rule_ipv6_id_dict)
                #ipv4
                for rule_id in list(type_Cfg.rule_id_dict.keys()):
                    type_Cfg.do_destory_fp_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_id_dict[rule_id][8])
                #ipv6
                for rule_id in list(type_Cfg.rule_ipv6_id_dict.keys()):
                    type_Cfg.do_destory_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_ipv6_id_dict[rule_id][8])

                result_file.write("{0},{1},".format(groups_info_dict[group_id]["mme_group"], groups_info_dict[group_id]["mme_code"]))
                cls.write_mme_quality(result_file, type_Cfg, "S1-MME IP,", groups_info_dict[group_id]["s1_ip_list"])                
                cls.write_mme_quality(result_file, type_Cfg, "S11-MME IP,", groups_info_dict[group_id]["s11_ip_list"])                
                cls.write_mme_quality(result_file, type_Cfg, "S6a-MME IP,", groups_info_dict[group_id]["s6a_ip_list"])   
                cls.write_mme_quality(result_file, type_Cfg, "MME total bits,", groups_info_dict[group_id]["ip_list"])                


    @classmethod
    def check_path_quality_send_rule_g06(cls, type_Cfg, new_info):
        ###Test if the default process is appropriate
        pass
        

    
    @classmethod
    def check_path_quality_result(cls, type_Cfg, new_info):
        cls.time_start = time.time()

        cls.logger.debug(":::::::::check_path_quality_result::::::::::")

        with open(Gloabal_Var.CHECK_RESULT_FILE_CUR, mode = "wt", encoding = "utf-8") as result_file:
            curr_time = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))
            result_file.write(curr_time + "\n")
            result_file.flush()

        result_file = open(Gloabal_Var.CHECK_RESULT_FILE_CUR, mode = "at", encoding = "utf-8")

        cls.check_path_quality_send_rule(type_Cfg, new_info, result_file)

        s11_ip_lost_mme = []
        s1_ip_lost_mme = []
        s6a_ip_lost_mme = []

        cls.logger.debug("new_info----groups_info_dict:", new_info.groups_info_dict)
        ###s1
        for enobe_ip in type_Cfg.s1_mme_ip_list:
            isfind = False
            if new_info != None:
                for associate_ips in new_info.groups_info_dict:
                    if enobe_ip in new_info.groups_info_dict[associate_ips]["ip_list"]:
                        isfind = True
            if isfind == False:
                if enobe_ip not in s1_ip_lost_mme:
                    s1_ip_lost_mme.append(enobe_ip)

        cls.logger.debug("s1_ip_lost_mme:", s1_ip_lost_mme)
        if len(s1_ip_lost_mme) > 0:
            result_file.write("S1-MME IP don't find mme, S1 IP inner match\n")
            result_file.flush()
            cls.get_lte_ip_info(type_Cfg, s1_ip_lost_mme, result_file, "initial cdr", type_Cfg.autolearn_ingress_ports, type_Cfg.pps_to_autolearn_port)
                
        ###s11
        for sgw_ip in type_Cfg.s11_mme_ip_list:
            isfind = False
            if new_info != None:
                for associate_ips in new_info.groups_info_dict:
                    if sgw_ip in new_info.groups_info_dict[associate_ips]["ip_list"]:
                        isfind = True
            if isfind == False:
                if sgw_ip not in s11_ip_lost_mme:
                    s11_ip_lost_mme.append(sgw_ip)

        cls.logger.debug("s11_ip_lost_mme:", s11_ip_lost_mme)
        if len(s11_ip_lost_mme) > 0:
            result_file.write("S11-MME IP don't find mme, S11 IP inner match\n")
            result_file.flush()
            cls.get_lte_ip_info(type_Cfg, s11_ip_lost_mme, result_file, "s11 cdr", type_Cfg.autolearn_ingress_ports, type_Cfg.pps_to_autolearn_port)

        ###s6a
        for s6a_ip in type_Cfg.s6a_mme_ip_list:
            isfind = False
            if new_info != None:
                for associate_ips in new_info.groups_info_dict:
                    if s6a_ip  in new_info.groups_info_dict[associate_ips]["ip_list"]:
                        isfind = True
            if isfind == False:
                if s6a_ip not in s6a_ip_lost_mme:
                    s6a_ip_lost_mme.append(s6a_ip)

        cls.logger.debug("s6a_ip_lost_mme:", s6a_ip_lost_mme)
        if len(s6a_ip_lost_mme) > 0:
            result_file.write("S6A-MME IP don't find mme, S6A IP inner match\n")
            result_file.flush()
            cls.get_lte_ip_info(type_Cfg, s6a_ip_lost_mme, result_file, "s6a auth cdr", type_Cfg.autolearn_ingress_ports, type_Cfg.pps_to_autolearn_port)
        
        remote_s5s8_c_ip = []
        remote_sgsn_c_ip = []

        ###local_sgsn_c
        if cls.local_sgsn_c_info_need == True:
            result_file.write("local GN_SGSN IP, local GN-SGSN IP inner match\n")
            result_file.flush()

            cls.logger.debug("local_sgsn_c_ip_list:", type_Cfg.local_sgsn_c_ip_list)

            cls.get_sgsnc_ip_res_rate(type_Cfg, type_Cfg.local_sgsn_c_ip_list, result_file, type_Cfg.autolearn_ingress_ports, type_Cfg.pps_to_autolearn_port)

        result_file.write("\n")
        result_file.flush()

        ###local_s5s8
        if cls.local_s5s8_c_info_need == True:
            result_file.write("S11-SGW IP, local S5S8-SGW IP, S11-SGW inner match, local S5S8-SGW inner match, local S5S8-SGW quality with S11-SGW\n")
            result_file.flush()

            s11_and_s5s8_info = Autolearn_tools.config_file_to_info_obj_dict[Gloabal_Var.S11_AND_S5S8_CONF]
            for group in s11_and_s5s8_info.groups_info_dict.keys():
                s11_ip = []
                s5s8_ip = []
                for ip in s11_and_s5s8_info.groups_info_dict[group]["ip_list"]:
                    if ip != "":
                        ###ip in s11
                        if ip in type_Cfg.sgw_ip_list:
                            s11_ip.append(ip)
                        ###ip only in s5s8 
                        else:
                            s5s8_ip.append(ip)

                cls.logger.debug("local_s5s8-----s11_ip:", s11_ip)
                cls.logger.debug("local_s5s8-----s5s8_ip:", s5s8_ip)

                cls.write_mme_quality(result_file, type_Cfg, "SGW IP", s11_ip)
                cls.write_mme_quality(result_file, type_Cfg, "S5S8", s5s8_ip)

                for ip in s11_and_s5s8_info.groups_info_dict[group]["ip_list"]:
                    if ip != "":
                        cls.check_do_install_rule(type_Cfg, ip)
                os.system("./rpcc localhost 9090 2 'clean learn-associate-stat' 10")
                ###with date update
                time.sleep(100)

                bits = cls.get_teminal_output("./rpcc localhost 9090 2 'show learn-associate-stat all' 10 |grep 's11 cdr'|sed 's/ : /,/g'|sed 's/^\s*//g'|awk -F , '{printf(\"%s,\",$2)}'")
                result_file.write(''.join(bits))
                result_file.flush()

                bits = cls.get_teminal_output("./rpcc localhost 9090 2 'show learn-associate-stat all' 10 |grep 's5s8 cdr'|sed 's/ : /,/g'|sed 's/^\s*//g'|awk -F , '{printf(\"%s,\",$2)}'")
                result_file.write(''.join(bits))
                result_file.flush()

                bits = cls.get_teminal_output("./rpcc localhost 9090 2 'show learn-associate-stat all' 10 |grep 's11 find s5s8 count'|sed 's/ : /,/g'|sed 's/^\s*//g'|awk -F , '{printf(\"%s,\",$2)}'")
                result_file.write(''.join(bits)+"\n")
                result_file.flush()
                #ipv4
                for i in list(type_Cfg.rule_id_dict.keys()):
                    type_Cfg.do_destory_fp_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_id_dict[i][8])
                #ipv6
                for i in list(type_Cfg.rule_ipv6_id_dict.keys()):
                    type_Cfg.do_destory_ipv6_rule(type_Cfg.autolearn_ingress_ports, type_Cfg.rule_ipv6_id_dict[i][8])
        
        result_file.write("\n")
        result_file.flush()

        ###remote_sgsn_c
        if cls.remote_sgsn_c_info_need == True:
            for sgsn_c_ip in type_Cfg.sgsn_c_ip_list:
                for local_sgsn_c_ip in type_Cfg.local_sgsn_c_ip_list:
                    if sgsn_c_ip != local_sgsn_c_ip:
                        remote_sgsn_c_ip.append(sgsn_c_ip)

        cls.logger.debug("remote_sgsn_c_ip:", remote_sgsn_c_ip)

        if len(remote_sgsn_c_ip) > 0:
            result_file.write("remote GN-SGSN IP, remote GN-SGSN IP inner match\n")
            result_file.flush()
            cls.get_sgsnc_ip_res_rate(type_Cfg, remote_sgsn_c_ip, result_file, type_Cfg.autolearn_ingress_ports, type_Cfg.pps_to_autolearn_port)

        result_file.write("\n")
        result_file.flush()

        ###remote_s5s8_c
        if cls.remote_s5s8_c_info_need == True:
            for s5s8_c_ip in type_Cfg.s5s8_c_ip_list:
                if s5s8_c_ip != local_sgsn_c_ip:
                    remote_s5s8_c_ip.append(s5s8_c_ip)

        cls.logger.debug("remote_s5s8_c_ip:", remote_s5s8_c_ip)
        if len(remote_s5s8_c_ip) > 0:
            result_file.write("remote S5S8-SGW IP, remote S5S8-SGW IP inner match\n")
            result_file.flush()
            cls.get_lte_ip_info(type_Cfg, remote_s5s8_c_ip, result_file, "s5s8 cdr", type_Cfg.autolearn_ingress_ports, type_Cfg.pps_to_autolearn_port)

        result_file.write("\n")
        result_file.flush()

        os.system("mv {0} {1}".format(Gloabal_Var.CHECK_RESULT_FILE_CUR, Gloabal_Var.CHECK_RESULT_FILE))
        cls.time_end = time.time()
        cls.logger.debug("================times:  {0}".format(cls.time_end-cls.time_start))


