from fastapi import APIRouter, status, Depends, HTTPException, Response
import database
from models import Switch as SwitchModel
from models import Channel as ChannelModel
from sqlalchemy.orm import Session
import schemas
from pydantic import parse_obj_as
import traceback

router = APIRouter(
    prefix="/api/switch",
    tags=["switch"],
    responses={404: {"description": "Not found"}},
)

@router.get("/get/all")
def get_all_switches(db: Session = Depends(database.get_db)):
    switches = db.query(SwitchModel).all()
    return switches

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_switch(switch: schemas.Switch, db: Session = Depends(database.get_db)):
    try:
        total_channels = switch.channels_count
        switch_active = switch.active
        
        db_switch = SwitchModel(**switch.dict())
        db.add(db_switch)
        db.commit()
        
        print("here")
        switch_id = db_switch.id
        print("switch id : ", switch_id)
        
        for i in range(total_channels):
        
            c = {
                "channel_number": (i+1),
                "channel_active": False,
                "channel_user": None,
                "switch_id": switch_id
            }
            
            print(str(c))
            
            db_channel = ChannelModel(**c)
            db.add(db_channel)
        
        db.commit()
        
        pydantic_db_switch = parse_obj_as(schemas.DBSwitch, db_switch)

        return pydantic_db_switch

    except Exception as e:
        db.rollback()  # Rollback the transaction in case of error
        traceback.print_exc()  # Print the stack trace
        return {"error" : f"Error occured during Switch Creation in DB : {e}"}
