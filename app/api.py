#Imports

import json, firebase_admin, os

from firebase_admin import firestore, credentials
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, Annotated, Union, List
from .config import settings
from dotenv import load_dotenv

########################################################################################

from .data import ROOT_DIR

load_dotenv()

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
    item_id: Optional[str] = None
    q: Optional[str] = None

class postModel(BaseModel):
    item_id: str
    q: Optional[str] = None

app = FastAPI()

fileName = r'\data.json'
fullPath = ROOT_DIR + fileName

########################################################################################

# Helper Methods:


"""
Asynchronous function that parses data and returns a list of objects
that matches the parameters of the given model. 
"""
async def retrieveData(currData, model: getModel):
    dataset = currData['Items']

    if (len(dataset) == 0):
        raise HTTPException(status_code=404, detail="Item not found")
    
    #Retrieving attributes from the inputed model
    item_id = model.item_id
    q = model.q

    originalSize = len(dataset)

    #Branches for filtering data:

    #Filter based on item ID - Item ID is meant to be unique; hence possible O(1) situation
    if (item_id and (len(item_id) > 0)):

        # O(1) Handling

        if (dataset[-1]['item_id'] == item_id):
            dataset = [dataset[-1]]

        elif (dataset[0]['item_id'] == item_id):
            dataset = [dataset[0]]

        else:

            for i in range(len(dataset)):

                if (dataset[i]['item_id'] == item_id):
                    dataset = [dataset[i]]
                    break

            if (len(dataset) == originalSize):
                raise HTTPException(status_code=404, detail="Item not found")

    #Filter based on q parameter
    if (q and (len(q) > 0)):
        try:
            dataset = [val for val in dataset if ("q" in val) and (val['q'] == q)]

        except:
            raise HTTPException(status_code=404, detail="Item not found")

    if (len(dataset) == 0):
        raise HTTPException(status_code=404, detail="Item not found")
        
    return dataset

async def readData():
    try:
        with (open(fullPath, 'r') as file):
            fileData = json.load(file)
            return fileData
    
    except:
        raise HTTPException(status_code=500, detail="Internal Service Error")
    
async def writeData(currData, data):
    if (data == None):
        return
    
    if (isinstance(data, dict)):
        currData['Items'].append(data)

    elif (isinstance(data, list)):
        for val in data:
            currData['Items'].append(val)

    try:
        with (open(fullPath, 'w') as file):
            json.dump(currData, file)
    
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def deleteData(currData, data: Union[getModel, List[getModel]]):

    try:

        if (isinstance(data, list) and (len(data) == 1)):
            if (currData['Items'][0] == data):
                del currData['Items'][0]

            if (currData['Items'][-1] == data):
                del currData['Items'][-1]

        currData['Items'] = [val for val in currData['Items'] if val not in data]
        
        with (open(fullPath, 'w') as file):
            json.dump(currData, file)

    except IOError:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    except ValueError:
        raise HTTPException(status_code=404, detail="Item not found")

async def updateData(target, currData, data):
    await deleteData(currData, target)
    await writeData(currData, data)


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
    return {"Existing routes": ['items']}

#GET function for default items page
@app.get('/items', response_model=list[getModel])
async def getItem(model: Annotated[getModel, Query()]):

    currData = await readData()

    # Retrieving the data
    return await retrieveData(currData, model)

#POST function for items page
@app.post('/items')
async def postItem(model: Union[postModel, List[postModel]]):

    #Convert inserted model data to JSON
    mainData = await toJSON(model)

    currData = await readData()

    #Write data into file
    await writeData(currData, mainData)

    #Return data
    return mainData


@app.delete('/items', response_model=list[getModel])
async def deleteItem(model: Annotated[getModel, Query()]):

    currData = await readData()

    # Retrieving attributes from the inputed model
    targets = await retrieveData(currData, model)

    # Deleting targeted data
    await deleteData(currData, targets)

    return (targets)

@app.put('/items', response_model=list[getModel])
async def updateItem(model: postModel):

    val = getModel(item_id=model.item_id)
    
    currData = await readData()
    target = await retrieveData(currData, val)
    newData = await toJSON(model)

    await updateData(target, currData, newData)

    return target

