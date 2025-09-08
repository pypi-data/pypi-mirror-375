__all__ = ['Compile']
import collections
from typing import Any, Generator


def getVar(arr, idx):
    return 0 if idx >= len(arr) else arr[idx]


class _Trie():
    def __init__(self, check, base, fail, output, v, l, codeMap):
        self.check = check
        self.base = base
        self.fail = fail
        self.output = output
        self.v = v
        self.l = l
        self.codemap = codeMap
        self.maxlen = max(self.l)+1

    def _getCode(self, seq):
        seq = str(seq).lower()
        return self.codemap.get(seq, len(self.codemap)+1)

    def parse(self, text) -> Generator[int, int, Any]:
        currentState = 0
        for position, seq in enumerate(text):
            position += 1
            currentState = self._getState(currentState, self._getCode(seq))
            hitArray = self.output[currentState]
            if hitArray is not None:
                for hit in hitArray:
                    yield(position - self.l[hit], position, self.v[hit])

    def parseWithSkip(self, text, skipCall) -> Generator[int, int, Any]:
        currentState = 0
        index_bufer = [-1]*self.maxlen
        index_buffer_pos = 0
        for position, seq in enumerate(text):
            if skipCall(seq):
                continue
            index_bufer[index_buffer_pos % self.maxlen] = position
            index_buffer_pos += 1
            currentState = self._getState(currentState, self._getCode(seq))
            hitArray = self.output[currentState]
            if hitArray is not None:
                for hit in hitArray:
                    pre_index = (index_buffer_pos-self.l[hit]) % self.maxlen
                    yield(index_bufer[pre_index], position+1, self.v[hit])

    def _getState(self, currentState, character):
        newCurrentState = self._transitionWithRoot(currentState, character)
        while newCurrentState == -1:
            currentState = self.fail[currentState]
            newCurrentState = self._transitionWithRoot(currentState, character)
        return newCurrentState

    def _transitionWithRoot(self, nodePos,  c):
        b = getVar(self.base, nodePos)
        p = b + c + 1
        if b != getVar(self.check, p):
            if nodePos == 0:
                return 0
            return -1
        return p


def insertVar(arr, val):
    low, hight = 0, len(arr)-1
    while low <= hight:
        mid = (low + hight) // 2
        if val > arr[mid]:
            low = mid + 1
        elif val == arr[mid]:
            return
        else:
            hight = mid - 1
    arr.insert(low, val)


class _State():
    def __init__(self, depth=0):
        self.depth = depth
        self.failure = None
        self.emits = []
        self.success = {}
        self.index = 0

    def addEmit(self, emit):
        insertVar(self.emits, emit)

    def getLargestValueId(self):
        return self.emits[-1]

    def isAcceptable(self):
        return self.depth > 0 and len(self.emits) > 0

    def setFailure(self, failState, fail):
        self.failure = failState
        fail[self.index] = failState.index

    def nextState(self, character, ignoreRootState=False):
        nextState = self.success.get(character, None)
        if (not ignoreRootState) and (nextState is None) and (self.depth == 0):
            nextState = self
        return nextState

    def addState(self, character):
        nextS = self.nextState(character, True)
        if nextS is None:
            nextS = _State(self.depth + 1)
            self.success[character] = nextS
        return nextS

    def getStates(self):
        return iter(v for (_, v) in sorted(self.success.items(), key=lambda x: x[0]))

    def getTransitions(self):
        return sorted(self.success.keys())

    def clear(self):
        self.emits.clear()
        self.emits = []
        for _, v in self.success.items():
            if v is not None:
                v.clear()
        self.success.clear()
        self.success = {}


class _Builder():
    def __init__(self):
        self.rootState = _State()
        self.used = []
        self.base = []
        self.check = []
        self.v = None
        self.codemap = {}
        self.l = None
        self.allocSize = 0
        self.progress = 0
        self.nextCheckPos = 0
        self.size = 0

    def build(self, kvs, strKey):
        max_code = self._addAllKeyword(kvs, strKey)
        # build double array tire base on tire
        self._buildDoubleArrayTrie(max_code)
        self.used = None
        # build failure table and merge output table
        self._constructFailureStates()
        self.rootState.clear()
        self.rootState = None
        self.zipWeight()
        return _Trie(self.check, self.base, self.fail, self.output, self.v, self.l, self.codemap)

    def resize(self, newSize):
        base2 = [0]*newSize
        check2 = [0]*newSize
        used2 = [False]*newSize
        if self.allocSize > 0:
            base2[:self.allocSize] = self.base[:self.allocSize]
            check2[:self.allocSize] = self.check[:self.allocSize]
            used2[:self.allocSize] = self.used[:self.allocSize]

        self.base = base2
        self.check = check2
        self.used = used2
        self.allocSize = newSize
        return self.allocSize

    def _addAllKeyword(self, kvs, strKey):
        max_code = 0
        self.l = []
        self.v = []
        for index, kv in enumerate(kvs):
            currentState = self.rootState
            lens = 0
            for seq in kv[0]:
                seq = strKey(seq)
                if seq is None:
                    continue
                lens += 1
                _seq = str(seq).lower()
                _code = self.codemap.get(_seq, len(self.codemap)+1)
                self.codemap[_seq] = _code
                currentState = currentState.addState(_code)
            if lens < 1:
                continue
            currentState.addEmit(index)
            self.l.append(lens)
            max_code += lens
            self.v.append(kv[1])
        return int((max_code+len(self.codemap))/1.5) + 1

    def _fetch(self, parent):
        siblings = []
        if parent.isAcceptable():
            fakeNode = _State(-(parent.depth + 1))
            fakeNode.addEmit(parent.getLargestValueId())
            siblings.append((0, fakeNode))
        for (k, v) in sorted(parent.success.items(), key=lambda x: x[0]):
            siblings.append((k + 1, v))
        return siblings

    def _insert(self, queue):
        value, siblings = queue.popleft()
        begin = 0
        pos = max(siblings[0][0] + 1, self.nextCheckPos) - 1
        nonzero_num = 0
        first = 0
        if self.allocSize <= pos:
            self.resize(pos + 1)
        while True:
            pos += 1
            if self.allocSize <= pos:
                self.resize(pos + pos//2+1)
            if self.check[pos] != 0:
                nonzero_num += 1
                continue
            elif first == 0:
                self.nextCheckPos = pos
                first = 1

            begin = pos - siblings[0][0]
            if self.allocSize <= (begin + siblings[-1][0]):
                self.resize(begin + siblings[-1][0]+100)
            if self.used[begin]:
                continue
            if all(self.check[begin + kv[0]] == 0 for kv in siblings):
                break

        if 1.0 * nonzero_num/(pos - self.nextCheckPos + 1) >= 0.95:
            self.nextCheckPos = pos
        self.used[begin] = True

        if self.size < begin + siblings[-1][0] + 1:
            self.size = begin + siblings[-1][0] + 1

        for kv in siblings:
            self.check[begin + kv[0]] = begin

        for kv in siblings:
            new_siblings = self._fetch(kv[1])
            if not new_siblings:
                self.base[begin + kv[0]] = -(kv[1].getLargestValueId()+1)
            else:
                queue.append((begin + kv[0], new_siblings))
            kv[1].index = begin + kv[0]
        if value >= 0:
            self.base[value] = begin

    def _buildDoubleArrayTrie(self, max_code):
        self.resize(max_code+10)
        self.base[0] = 1
        self.nextCheckPos = 0
        root_node = self.rootState
        siblings = self._fetch(root_node)
        if not siblings:
            return
        queue = collections.deque()
        queue.append((-1, siblings))
        while len(queue) > 0:
            self._insert(queue)

    def _constructFailureStates(self):
        self.fail = [0]*(self.size+1)
        self.output = [None]*(self.size+1)
        queue = collections.deque()

        for depthOneState in self.rootState.getStates():
            depthOneState.setFailure(self.rootState, self.fail)
            queue.append(depthOneState)
            self._constructOutput(depthOneState)

        while len(queue) > 0:
            currentState = queue.popleft()
            for transition in currentState.getTransitions():
                targetState = currentState.nextState(transition)
                queue.append(targetState)
                traceFailureState = currentState.failure
                while traceFailureState.nextState(transition) is None:
                    traceFailureState = traceFailureState.failure
                newFailureState = traceFailureState.nextState(transition)
                targetState.setFailure(newFailureState, self.fail)
                for e in newFailureState.emits:
                    targetState.addEmit(e)
                self._constructOutput(targetState)

    def _constructOutput(self, targetState):
        emit = targetState.emits
        if (emit is None) or len(emit) == 0:
            return
        self.output[targetState.index] = list(emit)

    def zipWeight(self):
        self.base = self.base[:self.size]
        self.check = self.check[:self.size]


def Compile(kv_iter, strKey=None):
    if strKey is None:
        def strKey(x): return x
    return _Builder().build(kv_iter, strKey)
