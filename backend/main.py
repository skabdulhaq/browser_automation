import os
import re
import math
import random
import base64
import smtplib
import paramiko
import requests
from uuid import uuid4
from pydo import Client
from typing import Union
from jose import JWTError, jwt
from dotenv import load_dotenv
from pymongo import MongoClient
from email.mime.text import MIMEText
from datetime import timedelta, datetime
from passlib.context import CryptContext
from email.mime.multipart import MIMEMultipart
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from models import Token, TokenData, Container, ContainerInDB, ContainerOut, User, UserInDB, UserCreate
# from starlette.middleware import Middleware

# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://campusmartz.com",
#     "https://*.campusmartz.com",
# ]
# middleware = [
#     Middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=['*'],
#         allow_headers=['*']
#     )
# ]
load_dotenv()
# load_dotenv("./.env.dev")
# app = FastAPI(title="Cloud OS", description="Cloud OS",version="0.1.0")
app = FastAPI(title="Cloud OS", description="Cloud OS",version="0.1.0", root_path="/api")
app.add_middleware(CORSMiddleware,allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"] )
SECRET_KEY = os.environ.get("SECRET_KEY")
TOKEN = os.getenv('DIGITALOCEAN_AUTH')
DB_URL = os.getenv('DB_URL')
client = Client(token=TOKEN)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30*2*24
ALGORITHM = "HS256"
noreply_email = os.environ.get("EMAIL_HOST_USER")
password_noreply_email = os.environ.get("EMAIL_HOST_PASSWORD")
mail_server = os.environ.get("EMAIL_HOST")
port_number = os.environ.get("EMAIL_PORT")
website_url = os.environ.get("WEBSITE_URL") or "http://0.0.0.0:8000"
web_api = os.environ.get("WEB_API")
delete_interval = os.environ.get("DELETE_INTERVAL")
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Config #

email_verification = None
deployment_server_ready = None

#####
def get_diff_time(initial_time):
    now_utc = datetime.utcnow()
    specific_time = datetime.strptime(initial_time, '%Y-%m-%dT%H:%M:%SZ')
    time_difference = now_utc - specific_time
    return f"{time_difference.days} days {round(time_difference.seconds/3600, 5)} hours"            

def execute_command(command)->str:
    hostname = os.getenv("IP_ADDRESS")
    username = 'root'
    private_key_path = os.getenv("PRIVATE_KEY_PATH")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
        ssh.connect(hostname, username=username, pkey=private_key)
        print("Executing cmd")
        stdin,stdout,stderr = ssh.exec_command(command)
        print("".join(stdout.readlines()))
        ssh.close()
        return hostname
    except paramiko.ssh_exception.NoValidConnectionsError:
        raise "Connection Error"

def is_valid_email(email:str):
    payload = { "email": email }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authkey": os.getenv("MSG_91_AUTH_KEY")
    }
    url = "https://control.msg91.com/api/v5/email/validate"
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data["status"] != "success":
        return "Error while validating email."
    result = data["data"]["result"]
    if result["result"] != "deliverable":
        if result["result"] == "undeliverable":
            return f"{email} doesn't exists, check your email."
        return f'{result["result"]} email, check your email.'
    if result["is_disposable"]:
        return 'Use non disposable mail'
    return True

def generateOTP(lenght: int = 6):
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""
    for _ in range(lenght):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def sendVerificationMail(to_mail:str, link:str):
    msg = MIMEMultipart()
    msg['From'] = noreply_email
    msg['To'] = to_mail
    msg['Subject'] = 'Email Verification.'
    msg.attach(MIMEText("Your verification link is: \n" + f'{website_url}{link}', 'plain'))
    try:
        server = smtplib.SMTP(mail_server,port_number) 
        server.starttls()
        server.login(noreply_email, password_noreply_email)
        server.send_message(msg)
        server.close()
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication Error : {e}")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user_dict = app.database["users"].find_one({"username": username})
    if not user_dict:
        return False
    return UserInDB(**user_dict)

def get_user_by_email(email: str):
    user_dict = app.database["users"].find_one({"email": email})
    if user_dict:
        user_in_db = UserInDB(**user_dict)
        return user_in_db
    else:
        return {}

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def initialize_config():
    app.database["config"].insert_one({"type": "config", "email_verification": False, "deployment_server_ready": False})
    return 
 
@app.on_event("startup")
async def startup_event():
    global email_verification, deployment_server_ready
    try:
        app.mongodb_client = MongoClient(DB_URL)
    except Exception as e:
        raise print(e)
    app.database = app.mongodb_client["cloudos"]
    config = app.database["config"].find({"type": "config"})
    conf = list(config)
    if config.count() == 0:
        initialize_config()
    else:
        if conf["email_verification"]:
            email_verification = conf["email_verification"]
        if conf["deployment_server_ready"]:
            deployment_server_ready = conf["deployment_server_ready"]



@app.on_event("shutdown")
async def shutdown_server():
    app.mongodb_client.close()

   
def remove_container_in_db(container_name: str):
    print("Deleting", container_name)
    current_username = container_name.split("-")[0]
    # print
    app.database["port"].delete_one({"port": int(container_name.split("-")[-1])})
    print("Deleted", container_name)
    app.database["users"].update_one({"username": current_username}, {"$pull": {"containers": {"container_name":container_name}}})
    app.database["users"].update_one({"username": current_username}, {"$inc": {"active_containers": -1}})
    return app.database["users"].find_one({"username": current_username})
def add_container_in_db(container: ContainerInDB, current_user: User):
    app.database["port"].insert_one({"port": container.port})
    app.database["users"].update_one({"username": current_user.username}, {"$push": {"containers": container.dict()}}, upsert=True)
    app.database["users"].update_one({"username": current_user.username}, {"$inc": {"active_containers": 1}})
    return app.database["users"].find_one({"username": current_user.username})

def get_usable_images(image):
    allowed_images = app.database["allowed_images"].find_one({"image": image}, {"_id": 0})
    if allowed_images:
        return True
    else:
        return False

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def is_password_valid(password):
    pattern = re.compile("^[a-zA-Z0-9]+$")
    if pattern.match(password):
        return True
    else:
        return False
    
def get_free_port():
    result = random.choice(range(9000, 65536))
    live_ports = app.database["port"].find_one({"port": result},{"port": 1, "_id": 0})
    print("liveports", live_ports)
    if live_ports:
        return get_free_port()
    return result

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestFormStrict = Depends()):
    # get_user(form_data.username)
    if "@" in form_data.username:
        user_from_email = get_user_by_email(form_data.username)
        if user_from_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        form_data.username = user_from_email.username
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user", response_model=User)
async def get_user_data(current_user: User = Depends(get_current_active_user)):
    # user = await update_up_time(current_user)
    return current_user

@app.post("/user/container")
async def add_container(container: Container, task_manager: BackgroundTasks, current_user: User = Depends(get_current_active_user))->ContainerOut:
    if current_user.active_containers >= current_user.max_containers:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum containers reached please use your own instance",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not get_usable_images(container.container_image):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="This image is not allowed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # server_name = current_user.username+"-"+ uuid4().hex
    if not is_password_valid(container.password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Password should only contain numbers and alphabets",
            headers={"WWW-Authenticate": "Bearer"},
        )
    port_value = get_free_port()
    container_name = f"{current_user.username}-{uuid4().hex}-{port_value}"
    del_key = os.environ.get('delete_key')
    command = f'sudo docker run --rm -d --name={container_name} --health-interval={delete_interval}s --health-cmd="curl -f {web_api}/delete/container/{container_name}/{del_key}" --health-timeout=5s --health-retries=3 -it --shm-size=512m -p {port_value}:6901 -e VNC_PW={container.password} {container.container_image}'
    print(command)
    try:
        url_service = f"https://{execute_command(command)}:{port_value}"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error when creating {container_name}",headers={"WWW-Authenticate": "Bearer"},)
    container_in_db = ContainerInDB(port=port_value, password=get_password_hash(container.password), container_image=container.container_image, container_name=container_name, service_url=url_service, down_time=datetime.utcnow()+timedelta(hours=1), status="Live")
    add_container_in_db(container_in_db, current_user)
    return container_in_db

def delete_container(container_name: str):
    try:
        remove_container_in_db(container_name)
        command = f"sudo docker stop {container_name}"
        print(command)
        if execute_command(command):
            return "success"
    except Exception as e:
        print(e)
        print("Error in delete_container")
        return False

@app.get("/delete/container/{container_name}/{delete_key}")
def delete_container_key(container_name: str, delete_key: str):
    if delete_key == os.environ.get("delete_key"):
        if delete_container(container_name):
            return {"Success": "Container Deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error when deleting {container_name}",headers={"WWW-Authenticate": "Bearer"})
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Admin Key",headers={"WWW-Authenticate": "Bearer"})


@app.delete("/user/container")
async def delete_user_container(container_name: str, current_user: User = Depends(get_current_active_user))->list[ContainerOut]:
    if delete_container(container_name):
        current_user = get_user(current_user.username)
        containers = current_user.containers
        return containers
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error when deleting {container_name}",headers={"WWW-Authenticate": "Bearer"})

@app.get("/user/containers")
async def get_containers(current_user: User = Depends(get_current_active_user))->list[ContainerOut]:
    # print(current_user)
    return current_user.containers


@app.get("/verify/{otp}/{email}")
def verify_email(email: str, otp: str):
    email = base64.b64decode(email).decode()
    otp = base64.b64decode(otp).decode()
    user = get_user_by_email(email)
    if user and user.otp == otp:
        app.database["users"].update_one({"email": email}, {"$set": {"disabled": False}})
        return {"Success": "Email Verified"}
    else:
        return {"Error": "Invalid OTP"}

@app.get("/list/images")
def get_available_images()->list[str]:
    pipeline = [
    {
        '$project': {
            '_id': 0,
            'image': 1
        }
    },
    {
        '$group': {
            '_id': None,
            'images': {'$push': '$image'}
        }
    },
    {
        '$project': {
            '_id': 0,
            'result': '$images'
        }
    }
    ]
    result = list(app.database["allowed_images"].aggregate(pipeline))[0]["result"]
    return result

@app.post("/register" , response_model=User)
async def register(user: UserCreate, verification_email: BackgroundTasks):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=409 ,detail="User already exists.")
    if get_user(user.username):
        raise HTTPException(status_code=409 ,detail="Username is already taken.")
    if not is_password_valid(user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail="Only alphabets and numbers are allowed in username.") 
    details = is_valid_email(user.email)
    if not details :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail=details)
    if len(user.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail="Password should be atleast 8 characters long.")
    otp = generateOTP()
    if email_verification:
        db_user = UserInDB(**user.dict(), hashed_password=get_password_hash(user.password), otp=str(otp))
        link = f"/verify/{base64.b64encode(otp.encode()).decode()}/{base64.b64encode(db_user.email.encode()).decode()}"
        verification_email.add_task(sendVerificationMail, db_user.email, link)
        app.database["users"].insert_one(db_user.dict())
    else:
        db_user = UserInDB(**user.dict(), hashed_password=get_password_hash(user.password), otp=str(otp), disabled=False)
        app.database["users"].insert_one(db_user.dict())
    return db_user
