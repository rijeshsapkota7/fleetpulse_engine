from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.model import Users, Deliveries, RiderLocation
from security.security import verify_Ws_connection
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/ws", tags=["Websocket Stream"])

rider_rooms : dict[int, list[WebSocket]] = {}
order_room : dict[int, list[WebSocket]] = {}

@router.websocket("/tracking/{rider_id}")
async def track_rider(rider_id : int,websocket : WebSocket, current_user : Users = Depends(verify_Ws_connection),  db : Session = Depends(get_db)):
    await websocket.accept()
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if not user:
        await websocket.send_text("invalid or expired token")
        await websocket.close()
        return
    if user.role == "rider":
        if user.id != rider_id:
            await websocket.send_text("not authorized")
            await websocket.close()
            return
        if rider_id not in rider_rooms:
            rider_rooms[rider_id] = []
    if user.role == "customer":
        delivery = db.query(Deliveries).filter(Deliveries.customer_id == user.id, Deliveries.rider_id == rider_id, Deliveries.status != "delivered").all()
        if not delivery:
            await websocket.send_text("not authorized")
            await websocket.close()
            return
    
        if rider_id not in rider_rooms:
            rider_rooms[rider_id] = []
        rider_rooms[rider_id].append(websocket)
    if user.role == "dispatcher":
        if rider_id not in rider_rooms:
            rider_rooms[rider_id] = []
        rider_rooms[rider_id].append(websocket)
    try:
        while True:
            if user.role in  ("customer", "dispatcher"):
                await websocket.receive_text()
            if user.role ==  "rider":
                data = await websocket.receive_text()
                try:
                    data_obj = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_text("Invalid JSON format. Send {'lat': ..., 'lng': ...}")
                    continue
                lat = data_obj.get("lat")
                lng = data_obj.get("lng")
                if  lat is None or lng is None:
                    await websocket.send_text("coudln't fetch lat or lang properly")
                else:
                    for customer in rider_rooms[rider_id]:
                        await customer.send_text(data)
                    time = datetime.now(timezone.utc).timestamp()
                    location = RiderLocation(rider_id = user.id, latitude = lat, longitude = lng, timestamp =  str(int(time)))
                    db.add(location)
                    db.commit()
                    db.refresh(location)
                    await websocket.send_text(f"details saved successfully : {location}")
      
    except WebSocketDisconnect:
        if user.role in ("customer", "dispatcher"):
            rider_rooms[rider_id].remove(websocket)
        print("user disconnected clenly")

@router.websocket("/order/{delivery_id}")
async def track_order_status(delivery_id : int, websocket : WebSocket, current_user : Users = Depends(verify_Ws_connection),  db : Session = Depends(get_db)):
    await websocket.accept()
    user = db.query(Users).filter(Users.id == current_user.id).first()
    if user is None:
        await websocket.send_text("invalid or expired token")
        await websocket.close()
        return
    delivery = db.query(Deliveries).filter(Deliveries.id == delivery_id).first()
    if delivery is None:
        await websocket.send_text(f"delivery with id {delivery_id} not found!!")
        await websocket.close()
        return
    if delivery.status == "delivered":
        await websocket.send_text(f"status for the order id {delivery_id} is already delivered")
        await websocket.close()
        return
    if user.role == "rider":
        if delivery.rider_id != user.id:
            await websocket.send_text("only the assigned rider can be entered")
            await websocket.close()
            return
        room = order_room.get(delivery_id)
        if not room:
            order_room[delivery_id] = []
    if user.role in ("customer", "dispatcher"):
        if user.role == "customer" and delivery.customer_id != user.id:
            await websocket.send_text("only the customer of the dlivery can enter!!")
            await websocket.close()
            return
        room = order_room.get(delivery_id)
        if not room:
            order_room[delivery_id] = []
        order_room[delivery_id].append(websocket)
    while True:
        try:
            if user.role == "rider":
                data = await websocket.receive_text()
                for user in order_room[delivery_id]:
                    await user.send_text(data)
            if user.role in ("customer" , "dispatcher"):
                await websocket.receive_text()
        except WebSocketDisconnect:
            if user.role in ("customer", "dispatcher"):
                order_room[delivery_id].remove(websocket)
            print("user cleanly disconnected")
    