from threading import Thread
from ThreadMgr.Pause import Pause

__metaclass__ = type


class Cqsim_sim(Pause, Thread):

    def __init__(self, module, debug=None):
        Thread.__init__(self)
        Pause.__init__(self)

        self.myInfo = "Cqsim Sim"
        self.module = module
        self.debug = debug
        
        self.debug.line(4," ")
        self.debug.line(4,"#")
        self.debug.debug("# "+self.myInfo,1)
        self.debug.line(4,"#")
        
        self.event_seq = []
        self.current_event = None
        self.reserve_job_id = -1
        #obsolete
        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        #obsolete
        self.read_job_buf_size = 100
        self.read_job_pointer = 0 # next position in job list
        self.previous_read_job_time = -1 # lastest read job submit time
        
        self.debug.line(4)
        for module_name in self.module:
            temp_name = self.module[module_name].myInfo
            self.debug.debug(temp_name+" ................... Load",4)
            self.debug.line(4)

        # ************ #
        # Shared Variables to communicate with GymEnvironment.
        # ************ #
        self.simulator_wait_que_indices = []
        self.is_simulation_complete = False

    def run(self) -> None:
        """
        Invoke thread which runs the CqSim.
        :return:
        """
        self.cqsim_sim()

    def reset(self, module=None, debug=None):

        if module:
            self.module = module
        
        if debug:
            self.debug = debug

        self.event_seq = []
        self.current_event = None
        self.reserve_job_id = -1
        # obsolete
        self.job_num = len(self.module['job'].job_info())
        self.currentTime = 0
        # obsolete
        self.read_job_buf_size = 100
        self.read_job_pointer = 0
        self.previous_read_job_time = -1

    def cqsim_sim(self):

        self.import_submit_events()
        self.scan_event()

        self.print_result()

        self.is_simulation_complete = True
        self.release_all()

        self.debug.debug("------ Simulating Done!", 2)
        self.debug.debug(lvl=1)
        return

    def import_submit_events(self):
        # fread jobs to job list and buffer to event_list dynamically
        if self.read_job_pointer < 0:
            return -1
        temp_return = self.module['job'].dyn_import_job_file()
        i = self.read_job_pointer
        #while (i < len(self.module['job'].job_info())):
        while (i < self.module['job'].job_info_len()):
            if (self.module['job'].job_info(i)['o_d'] <= 0):
                if (self.module['job'].job_info(i)['o_d'] == -1):
                    self.debug.debug("####################### on demand job loaded ##########################", 4) 
                self.insert_event(1,self.module['job'].job_info(i)['submit'],2,[1,i])
                self.previous_read_job_time = self.module['job'].job_info(i)['submit']
                self.debug.debug("  "+"Insert job["+"2"+"] "+str(self.module['job'].job_info(i)['submit']),4)
            else:
                self.debug.debug("####################### on demand job notice of " + str(self.module['job'].job_info(i)['o_d'] - 1) + " loaded ##########################", 4)
                # submit a resource prevision event, event type 3, job id received from notice
                self.insert_event(3, self.module['job'].job_info(i)['submit'],2,[3,(self.module['job'].job_info(i)['o_d'] % 2000) - 1])
            i += 1

        if temp_return == None or temp_return < 0 :
            self.read_job_pointer = -1
            return -1
        else:
            self.read_job_pointer = i
            return 0
    
    def insert_event(self, type, time, priority, para = None):
        #self.debug.debug("# "+self.myInfo+" -- insert_event",5) 
        temp_index = -1
        new_event = {"type":type, "time":time, "prio":priority, "para":para}
        if (type == 1 or type ==3):
            #i = self.event_pointer
            i = 0
            if (type == 3):
                self.debug.debug("####################### a notice inserted ##########################", 4)
            while (i<len(self.event_seq)):
                if (self.event_seq[i]['time']==time):
                    if (self.event_seq[i]['prio']>priority):
                        temp_index = i
                        break
                elif (self.event_seq[i]['time']>time):
                    temp_index = i
                    break 
                i += 1
            
        if (temp_index>=len(self.event_seq) or temp_index == -1):
            self.event_seq.append(new_event)
        else:
            self.event_seq.insert(temp_index,new_event)

    def scan_event(self):

        self.debug.line(2, " ")
        self.debug.line(2, "=")
        self.debug.line(2, "=")
        self.current_event = None

        while (len(self.event_seq) > 0 or self.read_job_pointer >= 0):
            if len(self.event_seq) > 0:
                temp_current_event = self.event_seq[0]
                temp_currentTime = temp_current_event['time']
            else:
                temp_current_event = None
                temp_currentTime = -1

            if (len(self.event_seq) == 0 or temp_currentTime >= self.previous_read_job_time) and self.read_job_pointer >= 0:
                self.import_submit_events()
                continue

            self.current_event = temp_current_event
            self.currentTime = temp_currentTime

            if self.current_event['type'] == 1:

                self.debug.line(2, " ")
                self.debug.line(2, ">>>")
                self.debug.line(2, "--")
                self.debug.debug("  Time: "+str(self.currentTime), 2)
                self.debug.debug("   "+str(self.current_event), 2)
                self.debug.line(2, "--")
                self.debug.debug("  Wait: "+str(self.module['job'].wait_list()),2) 
                self.debug.debug("  Run : "+str(self.module['job'].run_list()),2) 
                self.debug.line(2, "--")
                self.debug.debug("  Tot:"+str(self.module['node'].get_tot())+" Idle:"+str(self.module['node'].get_idle())+" Avail:"+str(self.module['node'].get_avail())+" ",2)
                self.debug.line(2, "--")
                
                self.event_job(self.current_event['para'])
            if self.current_event['type'] == 3:
                self.debug.line(2, " ")
                self.debug.line(2, ">>>")
                self.debug.line(2, "--")
                self.debug.debug("  Time: "+str(self.currentTime), 2)
                self.debug.debug("   "+str(self.current_event), 2)
                self.debug.line(2, "--")
                self.debug.debug("  Wait: "+str(self.module['job'].wait_list()),2) 
                self.debug.debug("  Run : "+str(self.module['job'].run_list()),2) 
                self.debug.line(2, "--")
                self.debug.debug("  Tot:"+str(self.module['node'].get_tot())+" Idle:"+str(self.module['node'].get_idle())+" Avail:"+str(self.module['node'].get_avail())+" ",2)
                self.debug.line(2, "--")
                
                self.debug.debug("####################### a notice evented ##########################", 4)
                
                self.event_job(self.current_event['para'])

            self.sys_collect()

            del self.event_seq[0]

        self.debug.line(2,"=")
        self.debug.line(2,"=")
        self.debug.line(2," ")
        return
    
    def event_job(self, para_in = None):

        if (self.current_event['para'][0] == 1):
            if (self.module['job'].job_info(self.current_event['para'][1])['o_d'] == -1):
                self.debug.debug("####################### on demand job " + str(self.current_event['para'][1]) + " submitted", 3)
            self.submit(self.current_event['para'][1])
        elif (self.current_event['para'][0] == 2):
            self.finish(self.current_event['para'][1])
        elif (self.current_event['para'][0] == 3 and self.module['node'].prepared_job == -1 and self.module['node'].preparing_job == -1):
            # if prevision event set successfully
            if(self.set_wait(self.current_event['para'][1])):
                # arrive time
                self.module['node'].prepared_arrive = self.currentTime + 1800
                #'''cua_f only trigger resource collecting
                self.module['node'].preparing_job = self.current_event['para'][1]
                self.module['node'].preparing_node = 0
                #'''
                '''cua will start collecting directly
                if(self.module['node'].node_allocate( 64, # magic number
                                                self.current_event['para'][1], 
                                                self.currentTime, # magic number
                                                self.currentTime + 1800 + 1200)): # magic number
                    # self.debug.debug("####################### reserve resource for job " + str(self.current_event['para'][1]), 4)
                    self.module['node'].prepared_job = self.current_event['para'][1]
                # start node collecting
                else:
                    # self.debug.debug("####################### collected " + str(self.module['node'].avail) + " node for job " + str(self.current_event['para'][1]), 4)
                    self.module['node'].preparing_job = self.current_event['para'][1]
                    self.module['node'].preparing_node = self.module['node'].avail
                    self.module['node'].node_allocate( self.module['node'].avail,
                                                self.current_event['para'][1],\
                                                self.currentTime, # magic number
                                                self.currentTime + 1800 + 1200)# magic number
                '''
        # Obsolete
        # self.score_calculate()
        self.start_scan()
    
    def submit(self, job_index):
        #self.debug.debug("# "+self.myInfo+" -- submit",5) 
        self.debug.debug("[Submit]  "+str(job_index),3)
        self.module['job'].job_submit(job_index)
        return
    
    def set_wait(self, job_index):
        #self.debug.debug("# "+self.myInfo+" -- submit",5) 
        self.debug.debug("[Set wait]  "+str(job_index),3)
        return self.module['job'].job_set_wait(job_index)

    def finish(self, job_index):
        #self.debug.debug("# "+self.myInfo+" -- finish",5) 
        self.debug.debug("[Finish]  "+str(job_index),3)
        self.module['node'].node_release(job_index,self.currentTime)
        # resource collecting or collected job finished
        if (self.module['node'].prepared_job == job_index or self.module['node'].preparing_job == job_index):
            self.module['node'].prepared_job = -1
            self.module['node'].prepared_arrive = -1
            self.module['node'].preparing_job = -1
            self.module['node'].preparing_node = -1
        # collecting resource
        elif (self.module['node'].preparing_job != -1):
            # enough after allocation
            if ((self.module['node'].avail + self.module['node'].preparing_node) >= 64):
                # self.debug.debug("####################### job " + str(self.module['node'].preparing_job) + " collect " + str(64 - self.module['node'].preparing_node) + " and become sufficient.", 4)
                self.module['node'].node_allocate (64 - self.module['node'].preparing_node, # magic number
                                                self.module['node'].preparing_job, # magic number
                                                self.currentTime,
                                                self.currentTime + 1200) # magic number
                self.module['node'].node_extend(self.module['node'].preparing_job, 64, self.currentTime + 1200) # magic number
                self.module['node'].prepared_job = self.module['node'].preparing_job
                self.module['node'].preparing_job = -1
                self.module['node'].preparing_node = -1
            # still need allocation
            else: 
                # self.debug.debug("####################### job " + str(self.module['node'].preparing_job) + " collect " + str(self.module['node'].avail) + " and still need.", 4)
                self.module['node'].preparing_node += self.module['node'].avail
                self.module['node'].node_allocate (self.module['node'].avail,
                                self.module['node'].preparing_job,\
                                self.currentTime,\
                                self.currentTime + 1200) # magic number
                self.module['node'].node_extend(self.module['node'].preparing_job, self.module['node'].preparing_node, self.currentTime + 1200) # magic number
        self.module['job'].job_finish(job_index)
        self.module['output'].print_result(self.module['job'], job_index)
        self.module['job'].remove_job_from_dict(job_index)
        return
    
    def start_job(self, job_index):
        # self.debug.debug("# "+self.myInfo+" -- start",5)
        self.debug.debug("[Start]  "+str(job_index), 3)
        if (self.module['node'].prepared_job != job_index):
            self.module['node'].node_allocate(self.module['job'].job_info(job_index)['reqProc'], job_index,
                                            self.currentTime, self.currentTime +
                                            self.module['job'].job_info(job_index)['reqTime'])
        self.module['job'].job_start(job_index, self.currentTime)
        self.insert_event(1, self.currentTime+self.module['job'].job_info(job_index)['run'], 1, [2, job_index])
        return

    def reorder_queue(self, wait_que):
        """
        This(and only this) function manages thread synchronization and communication with the GymEnvironment.

        :param wait_que: [List[int]] : CqSim WaitQue at current Time.
        :return: [List[int]] : Updated wait_que, with the selected job at the beginning.
        """
        self.simulator_wait_que_indices = wait_que
        self.pause_consumer()
        return self.simulator_wait_que_indices

    def start_scan(self):

        start_max = self.module['win'].start_num()
        temp_wait = self.module['job'].wait_list()
        win_count = start_max

        while temp_wait:
            if win_count >= start_max:
                win_count = 0
                temp_wait = self.start_window(temp_wait)

            # ************ #
            # Communicate with GymEnvironment.
            # ************ #
            print("Wait Queue at StartScan - ", temp_wait)
            temp_job_id = temp_wait[0]
            temp_job = self.module['job'].job_info(temp_job_id)
            if temp_wait[0] != self.reserve_job_id and temp_job['o_d'] != -1:
                temp_wait = self.reorder_queue(temp_wait)

            temp_job_id = temp_wait[0]
            temp_job = self.module['job'].job_info(temp_job_id)
            if self.module['node'].prepared_job == (temp_job['id'] % 2000) - 1:
                self.debug.debug("Job ID " + str((temp_job['id'] % 2000) - 1)+ " use prepared resource", 3)
                self.start_job(temp_job_id)
                temp_wait.pop(0)
            elif self.module['node'].is_available(temp_job['reqProc']):
                # print(f'temp_job_id: {temp_job_id}')
                if self.reserve_job_id == temp_job_id:
                    self.reserve_job_id = -1

                self.start_job(temp_job_id)
                temp_wait.pop(0)
            else:
                temp_wait = self.module['job'].wait_list()
                self.reserve_job_id = temp_wait[0]
                self.backfill(temp_wait)
                break

            win_count += 1
        return
    
    def start_window(self, temp_wait_B):

        win_size = self.module['win'].window_size()
        
        if (len(temp_wait_B)>win_size):
            temp_wait_A = temp_wait_B[0:win_size]
            temp_wait_B = temp_wait_B[win_size:]
        else:
            temp_wait_A = temp_wait_B
            temp_wait_B = []

        temp_wait_info = []
        max_num = len(temp_wait_A)
        i = 0
        while i < max_num:
            temp_job = self.module['job'].job_info(temp_wait_A[i])
            temp_wait_info.append({"index": temp_wait_A[i], "proc": temp_job['reqProc'],
                                   "node": temp_job['reqProc'], "run": temp_job['run'],
                                   "score": temp_job['score']})
            i += 1
            
        temp_wait_A = self.module['win'].start_window(temp_wait_info,{"time":self.currentTime})
        temp_wait_B[0:0] = temp_wait_A
        return temp_wait_B
    
    def backfill(self, temp_wait):
        temp_wait_info = []
        max_num = len(temp_wait)
        i = 0
        while i < max_num:
            temp_job = self.module['job'].job_info(temp_wait[i])
            temp_wait_info.append({"index": temp_wait[i], "proc": temp_job['reqProc'],
                                   "node": temp_job['reqProc'], "run": temp_job['run'], "score": temp_job['score']})
            i += 1

        # ************ #
        # reorder_queue function passed as an argument, to be invoked while selecting back-fill jobs.
        # ************ #
        backfill_list = self.module['backfill'].backfill(temp_wait_info, {'time': self.currentTime,
                                                                          'reorder_queue_function': self.reorder_queue})

        if not backfill_list:
            return 0
        
        for job in backfill_list:
            print('backfill job.')
            self.start_job(job)
        return 1
    
    def sys_collect(self):

        temp_inter = 0
        if (len(self.event_seq) > 1):
            temp_inter = self.event_seq[1]['time'] - self.currentTime
        temp_size = 0
        
        event_code=None
        if (self.event_seq[0]['type'] == 1):
            if (self.event_seq[0]['para'][0] == 1):   
                event_code='S'
            elif(self.event_seq[0]['para'][0] == 2):   
                event_code='E'
        elif (self.event_seq[0]['type'] == 2):
            event_code='Q'
        temp_info = self.module['info'].info_collect(time=self.currentTime, event=event_code,
                                                     uti=(self.module['node'].get_tot() -
                                                          self.module['node'].get_idle()) *
                                                         1.0/self.module['node'].get_tot(),
                                                     waitNum=len(self.module['job'].wait_list()),
                                                     waitSize=self.module['job'].wait_size(), inter=temp_inter)
        self.print_sys_info(temp_info)
        return

    def print_sys_info(self, sys_info):
        self.module['output'].print_sys_info(sys_info)
    
    def print_result(self):
        self.module['output'].print_sys_info()
        self.debug.debug(lvl=1)
        self.module['output'].print_result(self.module['job'])
