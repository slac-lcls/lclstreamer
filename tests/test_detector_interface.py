from psana import DataSource
from lclstreamer.backend.psana2.data_sources import Psana2DetectorInterface
from lclstreamer.models.parameters import DataSourceParameters, DetectorDataParameters
from typing import Any, cast, Generator
import numpy


def test_detector_interface() -> None:

    parameters = DataSourceParameters(type="Detector_data")

    # Psana2AreaDetector
    exp = "mfx100852324"
    run = 355

    source_identifier: str = f"exp={exp},run={run}"
    ds: Any = DataSource(exp=exp,run=run)
    psana_run: Any = next(ds.runs())

    event_source: Any = cast(Generator[Any, None, None], psana_run.events())
    event = next(event_source)
    name = "Psana2AreaDetector"
    parameters.__pydantic_extra__ = {
        "type":"Psana2DetectorInterface",
        "psana_name":"jungfrau",
        "psana_fields":"raw.raw"
    }
    Psana2AreaDetector = Psana2DetectorInterface(
                            name=name,
                            parameters=parameters,
                            additional_info={
                                "run": psana_run,
                                "source_identifier": source_identifier,
                            },)
    Psana2AreaDetector_func = Psana2AreaDetector.get_data(event)
    Psana2AreaDetector_raw = psana_run.Detector("jungfrau").raw.raw(event)
    assert numpy.array_equal(
        Psana2AreaDetector_func,
        Psana2AreaDetector_raw
        )

    # Psana2AssembledAreaDetector
    name = "Psana2AssembledAreaDetector"
    parameters.__pydantic_extra__ = {
        "type":"Psana2DetectorInterface",
        "psana_name":"jungfrau",
        "psana_fields":"raw.image"
    }
    Psana2AssembledAreaDetector = Psana2DetectorInterface(
                            name=name,
                            parameters=parameters,
                            additional_info={
                                "run": psana_run,
                                "source_identifier": source_identifier,
                            },)
    Psana2AssembledAreaDetector_func = Psana2AssembledAreaDetector.get_data(event)
    Psana2AssembledAreaDetector_raw = psana_run.Detector("jungfrau").raw.image(event)
    assert numpy.array_equal(
        Psana2AssembledAreaDetector_func,
        Psana2AssembledAreaDetector_raw
    )

    # Psana2PV
    name = "Psana2PV"
    parameters.__pydantic_extra__ = {
        "type":"Psana2DetectorInterface",
        "psana_name": "SIOC:SYS0:ML00:AO192"
    }
    Psana2PV = Psana2DetectorInterface(
                            name=name,
                            parameters=parameters,
                            additional_info={
                                "run": psana_run,
                                "source_identifier": source_identifier,
                            },)
    Psana2PV_func = Psana2PV.get_data(event)
    Psana2PV_raw = psana_run.Detector("SIOC:SYS0:ML00:AO192")(event)
    assert numpy.array_equal(
        Psana2PV_func,
        Psana2PV_raw
    )


    # Psana2EBeam
    name = "Psana2EBeam"
    parameters.__pydantic_extra__ = {
        "type":"Psana2DetectorInterface",
        "psana_name": "ebeamh",
        "psana_fields": "raw.ebeamL3Energy"
    }
    Psana2EBeam = Psana2DetectorInterface(
                            name=name,
                            parameters=parameters,
                            additional_info={
                                "run": psana_run,
                                "source_identifier": source_identifier,
                            },)
    Psana2EBeam_func = Psana2EBeam.get_data(event)
    Psana2EBeam_raw = psana_run.Detector("ebeamh").raw.ebeamL3Energy(event)
    assert numpy.array_equal(
        Psana2EBeam_func,
        Psana2EBeam_raw
    )

    # Psana2Gmd
    exp = "tmox1016823"
    run = 44

    source_identifier: str = f"exp={exp},run={run}"
    ds: Any = DataSource(exp=exp,run=run)
    psana_run: Any = next(ds.runs())

    event_source: Any = cast(Generator[Any, None, None], psana_run.events())
    event = next(event_source)
    name = "Psana2Gmd"
    parameters.__pydantic_extra__ = {
        "type":"Psana2DetectorInterface",
        "psana_name": "gmd",
        "psana_fields": "raw.milliJoulesPerPulse"
    }
    Psana2Gmd = Psana2DetectorInterface(
                            name=name,
                            parameters=parameters,
                            additional_info={
                                "run": psana_run,
                                "source_identifier": source_identifier,
                            },)
    Psana2Gmd_func = Psana2Gmd.get_data(event)
    Psana2Gmd_raw = psana_run.Detector("gmd").raw.milliJoulesPerPulse(event)
    assert numpy.array_equal(
        Psana2Gmd_func,
        Psana2Gmd_raw
    )

    # Psana2Camera
    name = "Psana2Camera"
    parameters.__pydantic_extra__ = {
        "type":"Psana2DetectorInterface",
        "psana_name": "tmo_fzppiranha",
        "psana_fields": "raw.raw"
    }
    Psana2Camera = Psana2DetectorInterface(
                            name=name,
                            parameters=parameters,
                            additional_info={
                                "run": psana_run,
                                "source_identifier": source_identifier,
                            },)
    Psana2Camera_func = Psana2Camera.get_data(event)
    Psana2Camera_raw = psana_run.Detector("tmo_fzppiranha").raw.raw(event)
    assert numpy.array_equal(
        Psana2Camera_func,
        Psana2Camera_raw
    )
