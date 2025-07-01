#Imports

import json, firebase_admin, os

from firebase_admin import firestore, credentials
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, Annotated, Union, List
from .config import settings

########################################################################################

from .data import ROOT_DIR


FIREBASE_CRED = {
  "type": settings.type,
  "project_id": settings.project_id,
  "private_key_id": settings.private_key_id,
  "private_key": settings.private_key,
  "client_email": settings.client_email,
  "client_id": settings.client_id,
  "auth_uri": settings.auth_uri,
  "token_uri": settings.token_uri,
  "auth_provider_x509_cert_url": settings.auth_provider_x509_cert_url,
  "client_x509_cert_url": settings.client_x509_cert_url,
  "universe_domain": settings.universe_domain
}

cred = credentials.Certificate(FIREBASE_CRED)
firebase_admin.initialize_app(cred)
db = firestore.client()

class getModel(BaseModel):
    equipment: str
    type: Optional[str] = None
    destroyed: Optional[int] = None
    damaged: Optional[int] = None
    abandoned: Optional[int] = None
    captured: Optional[int] = None

class postModel(BaseModel):
    equipment: str
    type: str
    destroyed: Optional[int] = 0
    damaged: Optional[int] = 0
    abandoned: Optional[int] = 0
    captured: Optional[int] = 0

app = FastAPI()

fileName = r'\data.json'
fullPath = ROOT_DIR + fileName

########################################################################################

# Helper Methods:

async def retrieveData(data):
    group = data.equipment
    elemType = data.type

    try:

        if (elemType):
            return db.collection(group).document(elemType).get().to_dict()

        else:
            return [val.to_dict() for val in db.collection(group).stream()]

    except:
        raise HTTPException(status_code=404, detail="Error, data not found")

async def toJSON(model: Union[postModel, List[postModel]]):

    if (isinstance(model, postModel)):
        jsonObj = json.loads(model.model_dump_json())

    elif (isinstance(model, list)):
        jsonObj = [json.loads(val.model_dump_json()) for val in model]

    return jsonObj

########################################################################################

# Main API methods:

#GET function for main default page
@app.get('/')
async def mainPage():
    return "Main API Front Page"

#GET function for default items page
@app.get('/items')
async def getItem(model: Annotated[getModel, Query()]):

    ref = await retrieveData(model)

    return ref

#POST function for items page
@app.post('/items')
async def postItem(model: Union[postModel, List[postModel]]):

    #Convert inserted model data to dict
    mainData = model.model_dump()

    try:
        if (isinstance(model, postModel)):
            group = model.equipment
            db.collection(group).add(document_data=mainData, document_id=mainData['type'])

        elif (isinstance(model, list)):
            for item in mainData:
                group = item.equipment
                db.collection(group).add(document_data=mainData, document_id=mainData['type'])

    except:
        raise HTTPException(status_code=500, detail="Internal Server Failure")

    #Return data
    return mainData


@app.delete('/items', response_model=list[getModel])
async def deleteItem(model: Annotated[getModel, Query()]):

    return 

@app.put('/items', response_model=list[getModel])
async def updateItem(model: postModel):

    return 

