from typing import Any

from libsms.data_model import EcoliExperiment, SimulationRun
from libsms.api import run_simulation, check_simulation_status, get_analysis_manifest

__all__ = ["analysis_manifest", "ecoli_experiment", "simulation_status"]

async def ecoli_experiment(
    config_id: str, max_retries: int = 20, delay_s: float = 1.0, verbose: bool = False, **body: dict[str, Any]
) -> EcoliExperiment | None:
    return await run_simulation(config_id, max_retries, delay_s, verbose, **body)


async def simulation_status(
    experiment: EcoliExperiment, max_retries: int = 20, delay_s: float = 1.0, verbose: bool = False
) -> SimulationRun | None:
    return await check_simulation_status(experiment, max_retries, delay_s, verbose)


async def analysis_manifest(
    experiment: EcoliExperiment, max_retries: int = 20, delay_s: float = 1.0, verbose: bool = False
) -> dict[str, Any] | None | Any:
    return await get_analysis_manifest(experiment, max_retries, delay_s, verbose)
