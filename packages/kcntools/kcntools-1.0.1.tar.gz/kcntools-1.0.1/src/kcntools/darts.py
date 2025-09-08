from typing import List


class Atom():
    __slots__ = ('image', 'pos', 'types')

    def __init__(self, image, pos):
        """
        image is any thing you want like str\n
        pos is a tuple (start,end) in ori string index \n
        types is any you want make the tags of this atom
        """
        self.image = image
        self.pos = pos
        self.types = set([])

    def __str__(self):
        return str(self.image)


class WCell():
    __slots__ = ('word', 'pos', 'embedding', 'feature')

    def __init__(self, atom, lpos, embedding=None, feature=0):
        """
        this is a class use for split\n
        atom is Atom, lpos is (start,end) in atom list \n
        embding is a float or float array \n
        feature is a int use by other tag model
        """
        self.word = atom
        self.pos = lpos
        self.embedding = embedding
        self.feature = feature

    def addTypes(self, types):
        self.word.types |= types

    def getTypes(self):
        return self.word.types

    def __str__(self):
        return "<%s|%s|%s>" % (str(self.word), str(self.pos), str(self.word.types))


class CellMap():
    """
    store all the possobal cell for a string
    """
    class _Cursor():
        __slots__ = ('pre', 'val', 'next', 'index')

        def __init__(self, pre, val, nextCur):
            self.pre = pre
            self.val = val
            self.next = nextCur
            self.index = -1

    def __init__(self):
        self.head = CellMap._Cursor(None, WCell(None, (-1, 0)), None)
        self.rownum = 0
        self.colnum = 0
        self.elenum = 0

    def indexMap(self):
        node = self.head
        index = -1
        while node.next is not None:
            node = node.next
            index += 1
            node.index = index

    def iter(self, coursor=None, row=-1):
        coursor = coursor if coursor is not None else self.head
        if row > -1:
            while coursor.next is not None:
                n = coursor.next
                if n.val.pos[0] < row:
                    coursor = n
                    continue
                if n.val.pos[0] != row:
                    break
                yield n
                coursor = n
        else:
            while coursor.next is not None:
                yield coursor.next
                coursor = coursor.next

    def addNext(self, cursor, cell):
        self.rownum = max(self.rownum, cell.pos[0])
        self.colnum = max(self.colnum, cell.pos[1])
        while cursor.next is not None:
            n = cursor.next
            if n.val.pos[0] < cell.pos[0]:
                cursor = n
                continue
            if n.val.pos[0] == cell.pos[0]:
                if n.val.pos[1] < cell.pos[1]:
                    cursor = n
                    continue

                if n.val.pos[1] == cell.pos[1]:
                    n.val.addTypes(cell.getTypes())
                    return n
            m = CellMap._Cursor(cursor, cell, n)
            self.elenum += 1
            cursor.next = m
            n.pre = m
            return m

        cursor.next = CellMap._Cursor(cursor, cell, None)
        self.elenum += 1
        return cursor.next

    def addPre(self, cursor,  cell):
        self.rownum = max(self.rownum, cell.pos[0])
        self.colnum = max(self.colnum, cell.pos[1])
        while cursor.pre != self.head:
            n = cursor.pre
            if n.val.pos[0] > cell.pos[0]:
                cursor = n
                continue
            if n.val.pos[0] == cell.pos[0]:
                if n.val.pos[1] > cell.pos[1]:
                    cursor = n
                    continue
                if n.val.pos[1] == cell.pos[1]:
                    n.val.addTypes(cell.getTypes())
                    return n
            m = CellMap._Cursor(n, cell, cursor)
            self.elenum += 1
            cursor.pre = m
            n.next = m
            return m
        cursor.pre = CellMap._Cursor(self.head, cell, cursor)
        self.elenum += 1
        return cursor.pre

    def addCell(self, cell, coursor=None):
        if coursor is None:
            return self.addNext(self.head, cell)
        if coursor.val.pos[0] < cell.pos[0]:
            return self.addNext(coursor, cell)
        if (coursor.val.pos[0] == cell.pos[0]) and (coursor.val.pos[1] <= cell.pos[1]):
            return self.addNext(coursor, cell)
        return self.addPre(coursor, cell)

    def clear(self):
        """clear memory leak"""
        node = self.head
        while node.next is not None:
            xnode = node.next
            node.pre = None
            node.next = None
            node = xnode


class CellPresenter():
    def embed(self, cmap: CellMap, context) -> None:
        """
        set the cmap val data embeding
        cmap:CellMap
        content: list atom
        """
        raise NotImplementedError()


class CellQuantizer(CellPresenter):

    def distance(self, preW: WCell, nextW: WCell) -> float:
        """
        preW and nextW is WCell
        return the float distance of from pre to next
        """
        raise NotImplementedError()


class CellRecognizer():

    def read(self, content, cmap: CellMap) -> None:
        """
        recognize the word cell from base string and put it into the map
        content:list atom
        cmap:CellMap
        """
        raise NotImplementedError()


def _split_content(cmap, quantizer, context):
    """
    split the data from content
    content:list atom
    cmap:CellMap
    quantizer:CellQuantizer
    """
    def buildGraph():
        cmap.indexMap()
        quantizer.embed(cmap, context)
        graph, tmp = {}, []
        for coursor in cmap.iter(None, 0):
            dist = quantizer.distance(None, coursor.val)
            assert dist >= 0.0, 'dist %f must >0' % dist
            tmp.append((coursor.index, dist))
        graph[-1] = tmp
        for pre in cmap.iter():
            tmp = []
            for nextC in cmap.iter(pre, pre.val.pos[1]):
                dist = quantizer.distance(pre.val, nextC.val)
                assert dist >= 0.0, 'dist %f must >0' % dist
                tmp.append((nextC.index, dist))
            if not tmp:
                dist = quantizer.distance(pre.val, None)
                assert dist >= 0.0, 'dist %f must >0' % dist
                tmp.append((cmap.elenum, dist))
            graph[pre.index] = tmp
        return graph

    def selectPath(graph):
        # init
        sz = len(graph)
        dist, prev = [-1.0]*sz, [-2]*sz
        used = set(range(sz))
        visted = set()
        for node, weight in graph[-1]:
            dist[node] = weight
            visted.add(node)
            prev[node] = -1
        # dijkstra
        while (sz-1) in used:
            mindist, u = float('inf'), 0
            for i in (used & visted):
                if dist[i] < mindist:
                    mindist = dist[i]
                    u = i
            if u == sz-1:
                break
            used.remove(u)
            for node, weight in graph[u]:
                if node not in used:
                    continue
                c = dist[u] + weight
                visted.add(node)
                if dist[node] < 0 or c < dist[node]:
                    dist[node] = c
                    prev[node] = u

        # select
        bestPaths = [sz - 1]
        while bestPaths[-1] > -1:
            bestPaths.append(prev[bestPaths[-1]])
        bestPaths.reverse()
        return bestPaths

    nodes_use = set(selectPath(buildGraph()))
    return list(cur.val for cur in cmap.iter() if cur.index in nodes_use)


class SentenceSegment():
    def __init__(self, quantizer):
        self.cellRecognizers = []
        assert (quantizer is not None) and isinstance(quantizer, CellQuantizer)
        self.quantizer = quantizer

    def addCellRecognizer(self, recognizer):
        """
        add a cell recognizer
        """
        assert recognizer is not None and isinstance(recognizer, CellRecognizer)
        self.cellRecognizers.append(recognizer)

    def _buildMap(self, atom_list) -> CellMap:
        cmap = CellMap()
        _coursor = cmap.head
        for i, atom in enumerate(atom_list):
            _coursor = cmap.addNext(_coursor, WCell(atom, (i, i+1)))
        for recognizer in self.cellRecognizers:
            recognizer.read(atom_list, cmap)
        return cmap

    def smartCut(self, atom_list, max_mode=False) -> List[WCell]:
        """
        cut the give data in smart mode,\n
        input must Atom List\n
        if max mode is opened this will return all possable word!\n
        return a Wcell List
        """
        if not atom_list:
            return None
        if len(atom_list) == 1:
            return [WCell(atom_list[0], (0, 1))]
        cmap = self._buildMap(atom_list)
        ret = None
        if max_mode:
            ret = list(cur.val for cur in cmap.iter())
        else:
            ret = _split_content(cmap, self.quantizer, atom_list)
        cmap.clear()
        return ret


class Measurement():
    def join(self, vec1, vec2):
        """
        join two vec to one vec\n
        this return a vec and while using for measure method
        """
        raise NotImplementedError()

    def measure(self, vec1, vec2):
        """
        measure the distance of f1 and f2\n
        return distance must >0
        """
        raise NotImplementedError()


class AtomWordVecDic():
    def dimSize(self):
        """
        the dim of this wordvec\n
        return int
        """
        raise NotImplementedError()

    def wordNum(self):
        """
        word num support\n
        return long
        """
        raise NotImplementedError()

    def hasWord(self, atom):
        """
        if has a word in dict\n
        return boolean
        """
        raise NotImplementedError()

    def embeding(self, atom):
        """
        return float array or float,must be not None
        """
        raise NotImplementedError()


class AtomPresenter():
    """
    embeding a atom list
    """

    def embed(self, context):
        """
        content is atom list \n
        return content vec list that use by  next map method
        """
        raise NotImplementedError()

    def map(self, list_embedings, pos):
        """
        pos=(start,end),list_embeding is embed method return \n
        return a vec 
        """
        raise NotImplementedError()


class SmartCellQuantizer(CellQuantizer):
    """
    embeding a cell use wordvec or nural model
    """

    def __init__(self, measurement, atom_wordvec=None, atom_presenter=None):
        assert (measurement is not None) and isinstance(measurement, Measurement)
        assert (atom_wordvec is not None) or (atom_presenter is not None)
        if atom_wordvec is not None:
            assert isinstance(atom_wordvec, AtomWordVecDic)
        if atom_presenter is not None:
            assert isinstance(atom_presenter, AtomPresenter)
        self.measurement = measurement
        self.vecDic = atom_wordvec
        self.presenter = atom_presenter

    def embed(self, cellmap, context):
        # set embeding by model
        if self.presenter is not None:
            list_vec = self.model.embed(context)
            for cur in cellmap.iter():
                cell = cur.val
                cell.embedding = self.model.map(list_vec, cell.pos)
        # set embeding by word vec
        if self.vecDic is not None:
            for cur in cellmap.iter():
                cell = cur.val
                v = self.vecDic.embeding(cell.word)
                cell.embedding = self.measurement.join(cell.embedding, v)

    def distance(self, pre,  next):
        return self.measurement.measure(pre.embedding, next.embedding)
