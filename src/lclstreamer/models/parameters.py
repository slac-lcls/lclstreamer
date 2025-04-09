from pydantic import BaseModel


class LCLStreamerParameters(BaseModel):
    event_source: str
    processing_pipeline: str
    data_sources: list[str]
