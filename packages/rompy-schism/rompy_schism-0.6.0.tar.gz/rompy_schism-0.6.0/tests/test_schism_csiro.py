from datetime import datetime
from pathlib import Path

import pytest

# Import test utilities
from test_utils.logging import get_test_logger

# Initialize logger
logger = get_test_logger(__name__)

pytest.importorskip("rompy_schism")
from rompy.core.data import DataBlob
from rompy.core.time import TimeRange
from rompy.model import ModelRun
from rompy_schism.config_legacy import Inputs, SchismCSIROConfig
from rompy_schism.grid import SCHISMGrid
from tests.utils import compare_files

here = Path(__file__).parent


@pytest.mark.skip(reason="Needs to be updated")
def test_schism_render(tmpdir):
    """Test the swantemplate function."""
    run_id = "test_schism"
    period = TimeRange(
        start=datetime(2021, 8, 1, 0), end=datetime(2021, 11, 29, 0), interval="15M"
    )
    runtime = ModelRun(
        period=period,
        run_id=run_id,
        output_dir=str(tmpdir),
        config=SchismCSIROConfig(
            grid=SCHISMGrid(
                hgrid=DataBlob(id="hgrid", source=here / "data" / "schism" / "hgrid.gr3"),
                vgrid=DataBlob(id="vgrid", source=here / "data" / "schism" / "vgrid.in"),
                diffmin=DataBlob(
                    id="diffmin", source=here / "data" / "schism" / "diffmin.gr3"
                ),
                diffmax=DataBlob(
                    id="diffmax", source=here / "data" / "schism" / "diffmax.gr3"
                ),
                # drag=DataBlob(id="drag", source=here /
                #               "data" / "schism" / "drag.gr3"),
                manning=DataBlob(
                    id="manning", source=here / "data" / "schism" / "manning.gr3"
                ),
                # rough=DataBlob(id="rough", source=here /
                #                "data" / "schism" / "rough.gr3"),
                # hgridll=DataBlob(
                #     id="hgridll", source=here / "data" / "schism" / "hgridll.gr3"
                # ),
                hgrid_WWM=DataBlob(
                    id="hgrid_WWM", source=here / "data" / "schism" / "hgrid_WWM.gr3"
                ),
                wwmbnd=DataBlob(id="wwmbnd", source=here / "data" / "schism" / "wwmbnd.gr3"),
            ),
            inputs=Inputs(
                filewave=DataBlob(
                    id="filewave",
                    source=here
                    / "data" / "schism"
                    / "schism_bnd_spec_SWAN_500m_use_in_schism_2021Aug-Nov.nc",
                ),
            ),
        ),
    )
    runtime.generate()
    for fname in ["param.nml", "wwminput.nml"]:
        compare_files(
            here / "reference_files" / runtime.run_id / fname,
            tmpdir / runtime.run_id / fname,
        )
        # assert file exists
        for fname in [
            "diffmax.gr3",
            "diffmin.gr3",
            "hgrid.gr3",
            "hgrid_WWM.gr3",
            # "drag.gr3",
            "manning.gr3",
            "schism_bnd_spec_SWAN_500m_use_in_schism_2021Aug-Nov.nc",
            "vgrid.in",
            "wwmbnd.gr3",
        ]:
            assert (tmpdir / runtime.run_id / fname).exists()
