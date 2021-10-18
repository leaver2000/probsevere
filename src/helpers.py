from datetime import datetime

class Object:
    pass

class ReduceObject:

    def __init__(self, obj, delete=None):
        # print(obj)
        if obj is not None:
            for key in obj.keys():
                if key == 'validTime':
                    # print(key)
                    time = Object()
                    b = datetime.strptime(obj[key][:-4], '%Y%m%d_%H%M%S')
                    
                    # print(b)
                    self.validTime = b
                elif key == delete:
                    # print(feature[key])
                    del feature[key]


                else:
                    setattr(self,key,obj[key])
        pass
