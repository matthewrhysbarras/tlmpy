def test_imports():
    import tlmpy
    from tlmpy import Grid2D
    from tlmpy.physics import Diffusion2D, ScalarWaveTLM2D

    assert tlmpy.__version__ == "0.1.0"
    assert Grid2D and ScalarWaveTLM2D and Diffusion2D

