from tlmpy import Grid2D
from tlmpy.physics import ScalarWaveTLM2D

grid = Grid2D((256, 256), (1e-3, 1e-3))
solver = ScalarWaveTLM2D(grid)
solver.run(200)

