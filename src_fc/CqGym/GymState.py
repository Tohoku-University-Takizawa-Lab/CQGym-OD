import numpy as np


class GymState:

    _job_cols_ = 2
    _window_size_ = 50

    def __init__(self):
        # Variable to maintain the info received
        self.current_time = None
        self.wait_que = None
        self.wait_que_size = 0
        self.job_info = {}
        self.on_demand_arrive = None
        self.preparing_node = None
        self.preparing_status = None

        self.job_vector = []
        self.node_vector = []
        self.total_nodes = 0
        self.idle_nodes = 0
        self.feature_vector = []

    def define_state(self, current_time, wait_que_indices, job_info_dict, node_info_list, idle_nodes_count):
        """
        :param wait_que_indices: List[Integer] - indices of the jobs in wait que, List size limited.
        :param job_info_dict: Dict{Integer: Info} - Information of all the jobs from simulator
        :param node_info_list: List[Node Info] - Information of all the nodes from simulator
        :return: State parsable by the RL Model in use - Eg. Numpy Array
        """
        self.current_time = current_time
        self.wait_que = wait_que_indices[:]
        self.wait_que_size = len(self.wait_que)
        self.job_info = job_info_dict

        self.wait_job = [job_info_dict[ind] for ind in wait_que_indices]

        wait_job_input = self.preprocessing_queued_jobs(
            self.wait_job, current_time)
        system_status_input = self.preprocessing_system_status(
            node_info_list, current_time)
        self.feature_vector = self.make_feature_vector(
            wait_job_input, system_status_input)

        def vector_reshape(vec):
            return vec.reshape(tuple([1]) + vec.shape)
        self.feature_vector = vector_reshape(self.feature_vector)

        self.total_nodes = len(node_info_list)
        self.idle_nodes = idle_nodes_count

    def define_state_on_demand(self, current_time, wait_que_indices, job_info_dict, node_info_list, idle_nodes_count, on_demand_arrive, preparing_node, preparing_status):
        """
        :param wait_que_indices: List[Integer] - indices of the jobs in wait que, List size limited.
        :param job_info_dict: Dict{Integer: Info} - Information of all the jobs from simulator
        :param node_info_list: List[Node Info] - Information of all the nodes from simulator
        :return: State parsable by the RL Model in use - Eg. Numpy Array
        """
        self.current_time = current_time
        self.wait_que = wait_que_indices[:]
        self.wait_que_size = len(self.wait_que)
        self.job_info = job_info_dict
        self.on_demand_arrive = on_demand_arrive
        self.preparing_node = preparing_node
        self.preparing_status = preparing_status

        print("------------------------- " + str(self.on_demand_arrive) + " " + str(self.preparing_node) + " " + str(self.preparing_status) + " -------------------------")

        self.wait_job = [job_info_dict[ind] for ind in wait_que_indices]

        wait_job_input = self.preprocessing_queued_jobs(
            self.wait_job, current_time)
        system_status_input = self.preprocessing_system_status(
            node_info_list, current_time)
        self.feature_vector = self.make_feature_vector(
            wait_job_input, system_status_input)

        def vector_reshape(vec):
            return vec.reshape(tuple([1]) + vec.shape)
        self.feature_vector = vector_reshape(self.feature_vector)

        self.total_nodes = len(node_info_list)
        self.idle_nodes = idle_nodes_count

    def preprocessing_queued_jobs(self, wait_job, currentTime):
        job_info_list = []
        for job in wait_job:
            s = float(job['submit'])
            t = float(job['reqTime'])
            n = float(job['reqProc'])
            w = int(currentTime - s)
            # award 1: high priority; 0: low priority
            # a = int(wait_job[i]['award'])
            info = [[n, t], [0, w]]
            # info = [[n, t], [a, w]]
            job_info_list.append(info)
        return job_info_list

    def preprocessing_system_status(self, node_struc, currentTime):
        node_info_list = []
        # Each element format - [Availbility, time to be available] [1, 0] - Node is available
        for node in node_struc:
            info = []
            # avabile 1, not available 0
            if node['state'] < 0:
                info.append(1)
                info.append(0)
            else:
                info.append(0)
                info.append(node['end'] - currentTime)
                # Next available node time.

            node_info_list.append(info)
        return node_info_list

    def make_feature_vector(self, jobs, system_status):
        # Remove hard coded part !
        job_cols = self._job_cols_
        window_size = self._window_size_
        input_dim = [len(system_status) + window_size *
                     job_cols, len(system_status[0])]

        fv = np.zeros((1, input_dim[0], input_dim[1]))
        i = 0
        for idx, job in enumerate(jobs):
            fv[0, idx * job_cols:(idx + 1) * job_cols, :] = job
            i += 1
            if i == window_size:
                break
        fv[0, job_cols * window_size:, :] = system_status
        return fv

    def get_max_wait_time_in_queue(self):
        job_cnt = 0
        max_wait_time_in_que = 0
        max_job_size_in_que = 0
        total_wait_time = 0
        total_wait_core_seconds = 0
        for job_id in self.job_info:
            job_cnt += 1
            job = self.job_info[job_id]
            if job_cnt <= self._window_size_:
                max_wait_time_in_que = max(
                    max_wait_time_in_que, self.current_time - job['submit'])
                max_job_size_in_que = max(max_job_size_in_que, job['reqProc'])
            total_wait_time += job['reqTime']
            total_wait_core_seconds += job['reqTime'] * job['reqProc']
        return max_wait_time_in_que, max_job_size_in_que, total_wait_time, total_wait_core_seconds, job_cnt

    def get_reward(self, selected_job):

        max_wait_time_in_que, max_job_size_in_que, total_wait_time, total_wait_core_seconds, total_wait_size = self.get_max_wait_time_in_queue()

        tmp_reward = 0
        running = self.total_nodes - self.idle_nodes
        selected_job_info = self.job_info[selected_job]
        selected_job_requested_nodes = selected_job_info['reqProc']
        selected_job_wait_time = self.current_time - \
            selected_job_info['submit']

        selected_job_priority = selected_job_requested_nodes / self.total_nodes
        w1, w2, w3 = 1 / 3, 1 / 3, 1 / 3

        if self.idle_nodes < selected_job_requested_nodes:
            tmp_reward += running / self.total_nodes * w1
        else:
            tmp_reward += (selected_job_requested_nodes +
                           running) / self.total_nodes * w1

        if max_wait_time_in_que >= 21600:
            tmp_reward += selected_job_wait_time / max_wait_time_in_que * w2
        else:
            tmp_reward += selected_job_wait_time / 21600 * w2

        tmp_reward += selected_job_priority * w3

       # tmp_reward = selected_job_requested_nodes / max_job_size_in_que

        return tmp_reward

    def get_reward_o_d(self, selected_job):

        max_wait_time_in_que, max_job_size_in_que, total_wait_time, total_wait_core_seconds, total_wait_size = self.get_max_wait_time_in_queue()

        tmp_reward = 0
        running = self.total_nodes - self.idle_nodes
        selected_job_info = self.job_info[selected_job]
        selected_job_requested_nodes = selected_job_info['reqProc']
        selected_job_wait_time = self.current_time - \
            selected_job_info['submit']
        if selected_job_info['o_d'] == 0:
            print("######################################## rigid ########################################")
            o_d_job_bonus_time = 0
        if selected_job_info['o_d'] == -1:
            print("######################################## on-demand ########################################")
            if ( selected_job_wait_time > 3600 ):
                o_d_job_bonus_time = 0
            else:
                o_d_job_bonus_time = selected_job_wait_time

        selected_job_priority = selected_job_requested_nodes / self.total_nodes
        w1, w2, w3, w4 = 1 / 3, 1 / 3, 1 / 3, 1

        if self.idle_nodes < selected_job_requested_nodes:
            tmp_reward += running / self.total_nodes * w1
        else:
            tmp_reward += (selected_job_requested_nodes +
                           running) / self.total_nodes * w1

        if max_wait_time_in_que >= 21600:
            tmp_reward += selected_job_wait_time / max_wait_time_in_que * w2
        else:
            tmp_reward += selected_job_wait_time / 21600 * w2

        tmp_reward += selected_job_priority * w3

        if o_d_job_bonus_time > 0:
            tmp_reward += o_d_job_bonus_time / 3600 * w4

       # tmp_reward = selected_job_requested_nodes / max_job_size_in_que

        return tmp_reward
    
    def get_reward_on_demand(self, selected_job):

        max_wait_time_in_que, max_job_size_in_que, total_wait_time, total_wait_core_seconds, total_wait_size = self.get_max_wait_time_in_queue()

        tmp_reward = 0
        running = self.total_nodes - self.idle_nodes
        selected_job_info = self.job_info[selected_job]
        selected_job_requested_nodes = selected_job_info['reqProc']
        selected_job_wait_time = self.current_time - \
            selected_job_info['submit']

        selected_job_priority = selected_job_requested_nodes / self.total_nodes
        w1, w2, w3 = 1 / 3, 1 / 3, 1 / 3

        # node
        if self.idle_nodes < selected_job_requested_nodes:
            tmp_reward += running / self.total_nodes * w1
        else:
            tmp_reward += (selected_job_requested_nodes +
                           running) / self.total_nodes * w1

        # wait time
        if max_wait_time_in_que >= 21600:
            tmp_reward += selected_job_wait_time / max_wait_time_in_que * w2
        else:
            tmp_reward += selected_job_wait_time / 21600 * w2

        # priority (node)
        tmp_reward += selected_job_priority * w3

       # tmp_reward = selected_job_requested_nodes / max_job_size_in_que

       # on demand reward calculation
        if (self.preparing_status) :
            print("arrive time and current time ", self.on_demand_arrive, self.current_time)
            print("prepared node ", self.preparing_node)
            tmp_reward = 0
            if (selected_job_info['run'] + self.current_time > self.on_demand_arrive): 
                print("punish")
                tmp_reward -= (selected_job_info['reqProc'] / 128) / 2
                tmp_reward -= ((self.current_time + selected_job_info['run'] - self.on_demand_arrive) / selected_job_info['run']) / 2
            else:
                print("reward")
                tmp_reward += (selected_job_info['reqProc'] / 128) / 2
                tmp_reward += (selected_job_info['run'] / (self.on_demand_arrive - self.current_time)) / 2

        return tmp_reward