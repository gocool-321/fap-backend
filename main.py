from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from random import randint

import face_recognition
import uvicorn
import io
import uuid
import os

def face_attraction_value(image):
  face_landmarks_list = face_recognition.face_landmarks(image)
  middlePoints = []
  for j in range(1,len(face_landmarks_list[0]["left_eyebrow"])+1):
    middlePoints.append(tuple([(face_landmarks_list[0]["left_eyebrow"][-j][i] + face_landmarks_list[0]["right_eyebrow"][j-1][i])//2 for i in range(2)]))
  face_landmarks_list[0]["middle_point"] = middlePoints
  landmarks = {i: face_landmarks_list[0][i] for i in ["chin","top_lip","middle_point"]}
  chin =  tuple([int(i) for i in landmarks["chin"][len(landmarks["chin"])//2]]) # indexing chin from landmarks
  nose =  tuple([int(i) for i in landmarks["top_lip"][3]]) # indexing nose from landmarks
  forehead =  tuple([int(i) for i in landmarks["middle_point"][len(landmarks["middle_point"])//2]]) #indexing forehead from landmarks

  def distance(a,b): #using Euclidean Distance
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5

  c_to_n = distance(chin,nose) #distance from chin to nose
  n_to_f = distance(nose,forehead) #distance from nose to forehead
  print(round((100 - abs((1.618 - ((n_to_f/c_to_n) + 0.4))/1.618)*100),2))
  return {"attraction": round((100 - abs((1.618 + 0.4 - ((n_to_f/c_to_n)))/1.618)*100),2)}

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
def sayHello():
  return {"hello":"world"}


@app.post("/upload")
async def create_upload_file(file: UploadFile):
    try:
      contents = file.file.read()
      filename = f"{uuid.uuid4()}.jpg"
      with open(filename,'wb') as image:
          image.write(contents)
          image.close()
      image = face_recognition.load_image_file(filename)
      result = face_attraction_value(image)
      os.remove(filename)
      return result
    except Exception:
      return {"message":"Something went wrong"}


if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
