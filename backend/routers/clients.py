"""Client CRUD routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import User, Client, Session
from schemas import ClientCreate, ClientUpdate, ClientResponse
from auth import get_current_user

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all clients for the current coach."""
    clients = (
        db.query(Client)
        .filter(Client.coach_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for client in clients:
        session_count = db.query(Session).filter(Session.client_id == client.id).count()
        client_data = ClientResponse.model_validate(client)
        client_data.session_count = session_count
        result.append(client_data)
    return result


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new client."""
    client = Client(
        coach_id=current_user.id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        notes=data.notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return ClientResponse.model_validate(client)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single client by ID."""
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.coach_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    session_count = db.query(Session).filter(Session.client_id == client.id).count()
    client_data = ClientResponse.model_validate(client)
    client_data.session_count = session_count
    return client_data


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    data: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a client."""
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.coach_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if data.full_name is not None:
        client.full_name = data.full_name
    if data.email is not None:
        client.email = data.email
    if data.phone is not None:
        client.phone = data.phone
    if data.notes is not None:
        client.notes = data.notes

    db.commit()
    db.refresh(client)
    return ClientResponse.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a client and all their sessions."""
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.coach_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    db.delete(client)
    db.commit()
    return None