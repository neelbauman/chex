from collections import deque


class queue(deque):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def enque(self, elm):
        super().appendleft(elm)

    def deque(self):
        return super().pop()

    def isEmpty(self):
        return len(self) == 0
    

class stack(deque):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def push(self, elm):
        super().append(elm)

    def pop(self):
        return super().pop()

    def isEmpty(self):
        return len(self) == 0
