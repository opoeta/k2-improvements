"""Self-check do BED_MESH_SCALE sem Klipper: python features/mesh_scale/test_k2_mesh_scale.py"""
import importlib.util
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))


class BedMeshError(Exception):
    pass


class FakeZMesh:
    def __init__(self, params, printer):
        self.params = params
        self.probed_matrix = None

    def get_mesh_params(self):
        return self.params

    def build_mesh(self, m):
        self.probed_matrix = m

    def get_z_range(self):
        flat = [z for r in self.probed_matrix for z in r]
        return min(flat), max(flat)


class FakeGcmd:
    error = RuntimeError

    def __init__(self, factor):
        self.factor, self.msgs = factor, []

    def get_float(self, name, default, minval=None, maxval=None):
        return default if self.factor is None else self.factor

    def respond_info(self, m):
        self.msgs.append(m)


class FakeBedMesh:
    def __init__(self, z_mesh):
        self.z_mesh, self.set_to = z_mesh, None

    def set_mesh(self, m):
        self.set_to = m


class FakePrinter:
    def __init__(self, bedmesh):
        self.bedmesh = bedmesh

    def lookup_object(self, name):
        if name == 'bed_mesh':
            return self.bedmesh
        return types.SimpleNamespace(register_command=lambda *a, **k: None)


class FakeConfig:
    def __init__(self, printer):
        self.p = printer

    def get_printer(self):
        return self.p


# pacote falso 'extras' com um bed_mesh falso, pra o 'from . import bed_mesh' resolver
pkg = types.ModuleType('extras')
pkg.__path__ = []
sys.modules['extras'] = pkg
stub = types.ModuleType('extras.bed_mesh')
stub.ZMesh, stub.BedMeshError = FakeZMesh, BedMeshError
sys.modules['extras.bed_mesh'] = stub
pkg.bed_mesh = stub
spec = importlib.util.spec_from_file_location(
    'extras.k2_mesh_scale', os.path.join(HERE, 'k2_mesh_scale.py'))
mod = importlib.util.module_from_spec(spec)
sys.modules['extras.k2_mesh_scale'] = mod
spec.loader.exec_module(mod)


def run(z_mesh, factor):
    bm = FakeBedMesh(z_mesh)
    ext = mod.load_config(FakeConfig(FakePrinter(bm)))
    g = FakeGcmd(factor)
    ext.cmd_BED_MESH_SCALE(g)
    return bm, g


orig = FakeZMesh({'x_count': 2}, None)
orig.probed_matrix = [[0.0, -0.6], [-0.3, -0.66]]

bm, g = run(orig, 0.25)
assert bm.set_to.probed_matrix == [[0.0, -0.15], [-0.075, -0.165]], bm.set_to.probed_matrix
assert orig.probed_matrix == [[0.0, -0.6], [-0.3, -0.66]], 'nao pode alterar o mesh original'
assert bm.set_to.params == {'x_count': 2} and bm.set_to.params is not orig.params

bm, g = run(orig, 1.0)
assert bm.set_to is None, 'FACTOR=1 e no-op'

bm, g = run(FakeZMesh({}, None), 0.5)
assert bm.set_to is None and 'sem mesh' in g.msgs[0], 'sem mesh ativo nao escala'
print('ok')
