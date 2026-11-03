# K2 mesh scale: BED_MESH_SCALE FACTOR=0.0..1.0
#
# A celula de carga do bico (PR Touch) mede uma parabola de curvatura da mesa
# centrada no meio (meio de borda ~ -0.33 mm, canto ~ -0.65 mm) MUITO maior que a
# curvatura real: testes de 9 quadrados sem mesh (nov/2026) mostraram os cantos
# precisando de ~0.10-0.25 mm, e os meios de borda ja imprimindo bem. O mesh
# completo sobre-corrige as bordas (peca perto da borda: bico perto demais).
# Este comando multiplica o mesh ATIVO por FACTOR (em torno de 0 = a referencia do
# G28 Z no centro) e o reconstroi pelo mesmo caminho do load_profile do bed_mesh.
#
# Opera no mesh ativo: chamado 2x escala 2x. O START_PRINT chama 1x por impressao,
# logo depois de medir/carregar o mesh (so se mesh_scale < 1.0 no k2_vars.cfg).

from . import bed_mesh


class K2MeshScale:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command(
            'BED_MESH_SCALE', self.cmd_BED_MESH_SCALE,
            desc='Multiplica o mesh ativo por FACTOR (0.0 a 1.0)')

    def cmd_BED_MESH_SCALE(self, gcmd):
        factor = gcmd.get_float('FACTOR', 1.0, minval=0.0, maxval=1.0)
        bedmesh = self.printer.lookup_object('bed_mesh')
        z_mesh = bedmesh.z_mesh
        if z_mesh is None or z_mesh.probed_matrix is None:
            gcmd.respond_info('BED_MESH_SCALE: sem mesh ativo, nada a escalar')
            return
        if factor == 1.0:
            return
        matrix = [[z * factor for z in row] for row in z_mesh.probed_matrix]
        new_mesh = bed_mesh.ZMesh(dict(z_mesh.get_mesh_params()), self.printer)
        try:
            new_mesh.build_mesh(matrix)
        except bed_mesh.BedMeshError as e:
            raise gcmd.error(str(e))
        bedmesh.set_mesh(new_mesh)
        lo, hi = new_mesh.get_z_range()
        gcmd.respond_info(
            'BED_MESH_SCALE: mesh x%.3f aplicado (faixa %.3f a %.3f mm)'
            % (factor, lo, hi))


def load_config(config):
    return K2MeshScale(config)
