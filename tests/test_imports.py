def test_imports():
    import tlmpy
    from tlmpy import Grid2D
    from tlmpy._version import __version__
    from tlmpy.physics import Diffusion2D, ScalarWaveTLM2D

    assert tlmpy.__version__ == __version__
    assert Grid2D and ScalarWaveTLM2D and Diffusion2D
