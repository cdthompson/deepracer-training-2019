def some_global_function(a):
  print(type(a))

def some_global_function_with_self(self, a):
  print(type(a))

class Object():
  def __init__(self):
    #self.fp = some_global_function
    self.fp = some_global_function_with_self

  def call(self):
    self.fp('Hello')


if __name__ == "__main__":
  o = Object()
  o.call()
