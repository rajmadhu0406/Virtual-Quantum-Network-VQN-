from typing import Annotated, List
from pydantic import BaseModel, conint, root_validator


class ChannelList(BaseModel):
    channels: List[conint(ge=1, le=8)]  

    # # Custom validation to check that 4 is not in the list
    # @root_validator(pre=True)
    # def check_for_restricted_channel(cls, values):
    #     numbers = values
    #     if 1 in numbers:
    #         raise ValueError("The channel 1 is not allowed to access")
    #     return values



class ChannelListWithBins(ChannelList):
    n_values: int
    
class ChannelDataForCounter(BaseModel):
    numChannels: int
    n_values: int
    bin_width: int
    
class ChannelDataForCountRate(BaseModel):
    numChannels: int
