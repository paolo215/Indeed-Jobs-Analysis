
class Test():
    pass

class B():
    def __init__(self, test):
        self.b = test


class A():
    def __init__(self):
        self.a = Test()
        self.b = B(self.a)

    def test(self):
        self.a = None

a = A()
print(a.a)
print(a.b)
a.test()
print(a.a)
print(a.b)

