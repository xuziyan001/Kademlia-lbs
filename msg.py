__author__ = 'X'
PING = 0
STORE = 1
FIND_NODE = 2
FIND_VALUE = 3
REGISTER = 4

PONG = 11
FIND_NODE_RETURN = 22
FIND_VALUE_RETURN = 33


class Msg:
    def __init__(self, rpc_type, target_id, target_port, source_id, source_port, key, value, status, info):
        """
        :param rpc_type: int
        :param target_id:  long
        :param target_port:  int
        :param source_id:  long
        :param source_port:  int
        :param key:  long
        :param value:  str
        :param status:  bool
        :param info:  dict
        :return: no
        """
        self.rpc = rpc_type
        self.target_id = target_id
        self.target_port = target_port
        self.source_id = source_id
        self.source_port = source_port
        self.key = key
        self.value = value
        self.status = status
        self.info = info

    def __str__(self):
        return "Msg. rpc:%s, target:%s, source:%s, key/value:%s, status:%s info:%s." % \
                    (self.rpc, [self.target_id,self.target_port], [self.source_id,self.source_port], [self.key,self.value], self.status, self.info)







