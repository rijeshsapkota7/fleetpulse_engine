from fastapi import APIRouter, Depends, HTTPException
from security.security import verify_token
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal
from database.database import get_db
from database.model import Users, Deliveries
from 

class CreateDeliveries(BaseModel):
    pickup_address : str
    dropoff_address : str
    status : Literal["pending"]

class UpdateOrderStatus(BaseModel):
    status : Literal["picked_up", "delivered"]

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])

@router.get("/my")
def fetch_orders(id : int | None = None, db : Session = Depends(get_db), current_users :Users = Depends(verify_token)):
    user = db.query(Users).filter(Users.id == current_users.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="not authorized")
    if id:
        order = db.query(Deliveries).filter(Deliveries.id == id).first()
        if not order:
            raise HTTPException(status_code=404, detail=f"order with id {id} not found")
        if order.customer_id != current_users.id | order.rider_id != current_users.id:
            raise HTTPException(status_code=401, detail="not authorized")
        return {"orders details" : order}
    if current_users.role == "customer":
        all_orders = db.query(Deliveries).filter(Deliveries.customer_id == current_users.id).all()
        return {"orders" : all_orders}
    if current_users.role not in ( "rider" , "dispatcher"):
        all_order = db.query(Deliveries).filter(Deliveries.rider_id == current_users.id).all()
        return {"orders" : all_order}

@router.get("/available-to-pick")
def available_to_pick(db : Session = Depends(get_db), current_user : Users = Depends(verify_token)):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="not authorized")
    if user.role not in ( "rider" , "dispatcher"):
        raise HTTPException(status_code=403, detail="not allowed")
    all_orders = db.query(Deliveries).filter(Deliveries.rider_id == None, Deliveries.status == "pending").all()
    return {"orders" : all_orders}
    

@router.post("/", status_code=201)
def create_order(data : CreateDeliveries, db : Session = Depends(get_db), current_user : Users = Depends(verify_token)):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="not authorized")
    if user.role != "customer":
        raise HTTPException(status_code=403, detail="only customer can create order")
    new_delivery = Deliveries(customer_id=current_user.id, pickup_address=data.pickup_address, dropoff_address=data.dropoff_address, status = data.status)
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return {"Delivery created succesfully" : new_delivery}

@router.patch("/{id}/assign")
def assign_delivery(id : int, db : Session = Depends(get_db), current_user : Users = Depends(verify_token)):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="not authorized")
    if user.role not in  ("rider", "dispatcher"):
        raise HTTPException(status_code=401, detail="not authorized")
    order = db.query(Deliveries).filter(Deliveries.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"order with id {id} not found")
    if order.rider_id is not None:
        raise HTTPException(status_code=401, detail="A rider is already assigned in the delivery")
    order.rider_id = current_user.id
    db.commit()
    db.refresh(order)
    return {"Rider assinged successfully" : order}

@router.patch("/{id}/status")
def update_delivery(data : UpdateOrderStatus, id : int, db : Session = Depends(get_db), current_user : Users = Depends(verify_token)):
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="not authorized")
    if user.role not in ("rider" , "dispatcher"):
        raise HTTPException(status_code=401, detail="not authorized")
    order = db.query(Deliveries).filter(Deliveries.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"order with id {id} not found")
    if order.rider_id is None:
        raise HTTPException(status_code=401, detail="no any rider is assigned to the order yet")
    if order.rider_id != current_user.id:
        raise HTTPException(status_code=401, detail="not authorized")
    if order.status is "delivered":
        raise HTTPException(status_code=402, detail="Order status was already updated to delivered")
    order.status = data.status
    db.commit()
    return {"order status updated succesfully" : order}
    
    
    