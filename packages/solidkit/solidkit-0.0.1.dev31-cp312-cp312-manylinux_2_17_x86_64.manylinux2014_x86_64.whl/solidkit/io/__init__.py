from ase.io import read, write, Trajectory
from ase.io.formats import define_io_format

__all__ = [
    'read', 'write', 'Trajectory'
]

F = define_io_format
F('bcs', 'Bilbao Crystallographic Server file', '1F',
  module='solidkit.io.bcs', glob='*.bcs', external=True)

F('vesta', 'VESTA file', '1F',
  module='solidkit.io.vesta', glob='*.vesta', external=True)
