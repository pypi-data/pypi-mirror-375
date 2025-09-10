# from bee.honeyfactory import BF
# from bee.bee_enum import Op
#
# import MyConfig
# from bee.api0 import Suid0
# from entity.Student2 import Student2
#
#
# if __name__ == '__main__':
#     print("start")
#
#     MyConfig.init()
#
#     stu=Student2()
#     # stu.name='张三'
#
#     # suid = BF.suid()
#     suid = Suid0()
#
#     orderList = suid.select(stu)
#
#     # field is null    
#     condition = BF.condition()
#     # condition.op("remark", Op.eq, None)
#     # condition.op("--addr", Op.eq, None)
#     condition.op("addr", Op.eq, None)
#     condition.start(10).size(10)
#     # condition.start(5)
#     orderList = suid.select(stu,condition)
#     for one in orderList: 
#         print(one) 
#
#
#     condition = BF.condition()
#     # condition.op("remark", Op.eq, None)
#     condition.op("addr", Op.eq, None)
#     # condition.start(0).size(10)
#     condition.start(5)
#     orderList = suid.select(stu,condition)
#     for one in orderList: 
#         print(one) 
#
#     condition = BF.condition()
#     # condition.op("remark", Op.eq, None)
#     condition.op("addr", Op.eq, None)
#     # condition.start(0).size(10)
#     # condition.start(5)
#     condition.size(10)
#     orderList = suid.select(stu,condition)
#     for one in orderList: 
#         print(one) 
#
#
#     condition = BF.condition()
#     # condition.op("remark", Op.eq, None)
#     condition.op("addr", Op.eq, None)
#     # condition.start("")
#     condition.size(10)
#     orderList = suid.select(stu,condition)
#     for one in orderList: 
#         print(one)       
#
#     suid = Suid0()
#     print("finished")
