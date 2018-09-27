# coding: utf-8

import collections
import os
import traceback

import numpy as np
import onnx
from onnx import helper
from onnx import TensorProto


def _get_trace_str():
    # TODO(hamaji): Use parsing context instead of CH2O codebase.
    skip_names = set(['_get_trace_str', 'addnode', 'calc', 'calc_seq'])
    trace = []
    for stack in reversed(traceback.extract_stack()):
        if stack.name in skip_names:
            continue
        trace.append('%s:%s:%d' %
                     (stack.name,
                      os.path.basename(stack.filename),
                      stack.lineno))
        if len(trace) == 3:
            break
    return ' '.join(trace)


_cnt = 0


def gen_id(prefix):
    global _cnt
    _cnt += 1
    return prefix + str(_cnt)


def new_tensor(dims=['Undefined'], dtype=None):
    if dtype is not None:
        dt = onnx.mapping.NP_TYPE_TO_TENSOR_TYPE[np.dtype(dtype)]
    else:
        # TODO(hamaji): Deprecate this fallback pass.
        dt = onnx.TensorProto.FLOAT
    return helper.make_tensor_value_info(gen_id('T'), dt, dims)


def new_sequence(dtype=None):
    if dtype is not None:
        dt = onnx.mapping.NP_TYPE_TO_TENSOR_TYPE[dtype]
    else:
        # TODO(hamaji): Deprecate this fallback pass.
        dt = onnx.TensorProto.FLOAT
    vi = onnx.ValueInfoProto()
    vi.name = gen_id('S')
    vi.type.sequence_type.elem_type.tensor_type.elem_type = dt
    return vi


def get_dims(tensor):
    dims = tensor.type.tensor_type.shape.dim
    return list(map(lambda x: x.dim_value, dims))


def clip_head(s):
    s = s.split('\n')
    # print(s)
    hs = os.path.commonprefix(list(filter(lambda x: x != '', s)))
    # print('hs',list(map(ord,hs)))
    ls = len(hs)
    s = map(lambda x: x[ls:], s)
    return '\n'.join(s)


class ValueReturn(Exception):
    def __init__(self, value):
        self.value = value


def size2d(x):
    if isinstance(x, collections.Iterable):
        return x
    return x, x


def istensor(x):
    return isinstance(x, onnx.ValueInfoProto)


def totensor(x, env, dtype=None):
    if istensor(x):
        assert dtype is None
        return x

    if type(x) == float or type(x) == int:
        if dtype is not None:
            dt = onnx.mapping.NP_TYPE_TO_TENSOR_TYPE[dtype]
        elif type(x) == float:
            dt = onnx.TensorProto.FLOAT
        else:
            dt = onnx.TensorProto.INT64
        res = env.calc(
            'Constant',
            inputs=[],
            value=onnx.helper.make_tensor(
                name="hoge",
                data_type=dt,
                dims=[],
                vals=[x],
            )
        )
    elif type(x) == tuple or type(x) == list:
        def f(v):
            tv = v.to_tensor(env)
            tw = env.calc(
                'Unsqueeze',
                inputs=[tv.name],
                axes=[0]
            )
            return tw.name

        vs = list(map(f, x))
        # print(vs)
        res = env.calc(
            'Concat',
            inputs=vs,
            axis=0
        )
    else:
        raise Exception("totensor of %s is not implemented yet" % str(x))

    return res


class Env(object):
    def __init__(self, module):
        self.vars = {}
        self.nodes = []
        self.init_tensors = []
        self.restore_funcs = []  # User定義Linkの初期化子を正常化させるやつ
        self.module = module

    def localenv(self, module):
        res = Env(module)
        res.nodes = self.nodes  # こっちはglobalに共通でないといけない
        res.init_tensors = self.init_tensors  # こっちも共通
        res.restore_funcs = self.restore_funcs
        return res

    def addnode(self, *args, **kwargs):
        node = helper.make_node(*args, **kwargs)
        node.doc_string = _get_trace_str()
        self.nodes.append(node)

    def add_init(self, inits, pathname):
        for v in inits:
            # drint('add_init',v,p)
            v.name = pathname + v.name
            self.init_tensors.append(v)

    def calc(self, *args, npdtype=None, **kwargs):
        res = new_tensor(dtype=npdtype)
        assert 'outputs' not in kwargs.keys()
        kwargs['outputs'] = [res.name]
        self.addnode(*args, **kwargs)
        return res

    def calc_seq(self, *args, npdtype=None, **kwargs):
        res = new_sequence(dtype=npdtype)
        assert 'outputs' not in kwargs.keys()
        kwargs['outputs'] = [res.name]
        self.addnode(*args, **kwargs)
        return res