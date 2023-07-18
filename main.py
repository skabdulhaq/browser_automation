from typing import Union
from dotenv import load_dotenv
import os, paramiko, asyncio
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi.responses import StreamingResponse
from passlib.context import CryptContext
from pymongo import MongoClient
from models import *
from pydo import Client
from datetime import datetime
from uuid import uuid4
import math, random, base64,smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()
app = FastAPI()
SECRET_KEY = os.environ.get("SECRET_KEY")
db_creds = os.environ.get("DB_CRED")
TOKEN = os.getenv('DIGITALOCEAN_AUTH')
DB_URL = os.getenv('DB_URL')
client = Client(token=TOKEN)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
noreply_email = os.environ.get("EMAIL_HOST_USER")
password_noreply_email = os.environ.get("EMAIL_HOST_PASSWORD")
mail_server = os.environ.get("EMAIL_HOST")
port_number = os.environ.get("EMAIL_PORT")
website_url = os.environ.get("URL")

def get_diff_time(initial_time):
    now_utc = datetime.utcnow()
    specific_time = datetime.strptime(initial_time, '%Y-%m-%dT%H:%M:%SZ')
    time_difference = now_utc - specific_time
    return f"{time_difference.days} days {round(time_difference.seconds/3600, 5)} hours"
         
def get_ipaddress(networks):
    for ipv4_network in networks:
            if ipv4_network["type"] == "public":
                return ipv4_network["ip_address"]
            
def delete_droplet(id, username):
    try:
        response = client.droplets.destroy(droplet_id=id)
        remove_container_in_db(id,username)
    except Exception as e:
        print(e)
    return response

async def creat_new_droplet(name):
    payload = {
        "name": name,
        "region": "BLR1",
        "size": "s-2vcpu-4gb",
        "image": "docker-20-04",
        "backups": False,
        "monitoring": True,
        "ipv6": True,
        "with_droplet_agent": True,
        "ssh_keys": [
            "c7:12:fe:52:cb:7b:86:21:51:a1:aa:96:76:20:11:02"
        ],
        "tags": [
            "kasm:prod"
        ],
    }
    response = client.droplets.create(payload)
    return response

def exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    if stderr:
        error = stderr.read().decode('utf-8')
        print('Error:')
        print(error)
    if stdin:
        print('Output:')
        print(output)

async def execute_command(ipaddress, port, password, image):
    hostname = ipaddress
    username = 'root'
    private_key_path = "./ssh_rsa"
    print(ipaddress)
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
        ssh.connect(hostname, username=username, pkey=private_key)
        exec(ssh,"sudo apt install -y at")
        sftp = ssh.open_sftp()
        sftp.put('./timer.sh', '/root/timer.sh')
        sftp.chmod('/root/timer.sh', 0o777)
        sftp.close()
        command = f'sudo docker run -d -it  -p {port}:6901 -e VNC_PW={password} {image}'
        exec(ssh, command)
        exec(ssh, "/root/timer.sh")
        ssh.close()
        return f"https://{ipaddress}:{port}"
    except paramiko.ssh_exception.NoValidConnectionsError:
        return "Connection Error"

async def get_droplets_details(name):
    data = {}
    droplets_fulldata = (client.droplets.list(name=name))
    data["total"] = droplets_fulldata["meta"]["total"]
    try:
        droplet = droplets_fulldata["droplets"][0]
    except IndexError:
        return data
    data["running-time"] = get_diff_time(droplet['created_at'])
    data["ip-address"] = get_ipaddress(droplet['networks']['v4'])
    data["id"] = droplet["id"]
    data["name"] = droplet["name"]
    data["memory"] = droplet["memory"]
    return data

def generateOTP(lenght: int):
    digits = "0123456789"
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
    server = smtplib.SMTP(mail_server,port_number) 
    server.starttls()
    server.login(noreply_email, password_noreply_email)
    server.send_message(msg)
    server.close()


async def update_container_time(name:str):
    details = await get_droplets_details(name)
    username = name.split("-")[0]
    app.database.update_one({"username": username}, {"$set": {f"containers.{details['id']}.up_time": details["running-time"]}})

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user_dict = app.database.find_one({"username": username})
    if not user_dict:
        return False
    return UserInDB(**user_dict)

def get_user_by_email(email: str):
    user_dict = app.database.find_one({"email": email})
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
    
@app.on_event("startup")
async def startup_event():
    app.mongodb_client = MongoClient(DB_URL)
    app.database = app.mongodb_client["users"]["users"]
    app.state.connected_websockets = []

@app.on_event("shutdown")
async def shutdown_server():
    app.mongodb_client.close()

async def update_up_time(current_user: User):
    containers = current_user.containers
    for container_id in containers:
        container_details = containers[container_id]
        await update_container_time(container_details["server_name"])
    return current_user
    
def remove_container_in_db(container_id: int, current_user: str):
    app.database.update_one({"username": current_user}, {"$unset": {f"containers.{str(container_id)}": ""}})
    app.database.update_one({"username": current_user}, {"$inc": {"active_containers": -1}})
    return app.database.find_one({"username": current_user})

async def add_container_in_db(container: ContainerInDB, current_user: User, container_id: int):
    app.database.update_one({"username": current_user.username}, {"$set": {f"containers.{str(container_id)}": container.dict()}}, upsert=True)
    app.database.update_one({"username": current_user.username}, {"$inc": {"active_containers": 1}})
    return app.database.find_one({"username": current_user.username})

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestFormStrict = Depends()):
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
    user = await update_up_time(current_user)
    return user

@app.post("/users/container")
async def add_container(container: Container, task_manager: BackgroundTasks, current_user: User = Depends(get_current_active_user)):
    if current_user.active_containers >= current_user.max_containers:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum containers reached upgrade your plan",
            headers={"WWW-Authenticate": "Bearer"},
        )
    server_name = current_user.username+"-"+ uuid4().hex
    async def create_server(server_name):
        yield b"Server creation initiated."
        await creat_new_droplet(server_name)
        droplet_details = await get_droplets_details(server_name)
        yield f"Recieved server id {droplet_details['id']} .".encode()
        print(droplet_details)
        while True:
            droplet_details = await get_droplets_details(server_name)
            ip_address = droplet_details["ip-address"]
            if ip_address:
                break
            yield "Waiting for IP address...".encode()
            await asyncio.sleep(1)
        
        yield f"Got IP address {ip_address}...".encode()
        
        service_link = await execute_command(ipaddress=droplet_details["ip-address"], password = container.password, port=container.port, image=container.container_image)
        for _ in range(5):
            if service_link == "Connection Error":
                await asyncio.sleep(5)
                yield "Connection error. Retrying...".encode()
                print("connection error")
                service_link = await execute_command(ipaddress=droplet_details["ip-address"], password = container.password, port=container.port, image=container.container_image)
            else:
                yield f"Service link generated {service_link}...".encode()
                break
        else:
            task_manager.add_task(delete_droplet, droplet_details["id"], current_user.username)
            yield "Connection Error. retry after some time".encode()
            return
        yield "Adding server detains in db.".encode()
        
        container_in_db = ContainerInDB(
            container_image=container.container_image,
            server_name=server_name,
            server_ip=droplet_details["ip-address"],
            status="Running",
            up_time=droplet_details["running-time"],
            service_url=service_link
            )
        container_id = droplet_details["id"]
        await add_container_in_db(container_in_db, current_user, container_id)
        yield "Server added in db successfully.".encode()
        yield "Container created successfully.".encode()
    return StreamingResponse(create_server(server_name))


@app.delete("/users/container ")
async def delete_container(container_id: int, task_manager: BackgroundTasks, current_user: User = Depends(get_current_active_user)):
    task_manager.add_task(delete_droplet, container_id, current_user.username)
    containers = current_user.containers
    containers.pop(str(container_id))
    return containers

@app.get("/users/containers")
async def get_containers(current_user: User = Depends(get_current_active_user)):
    user = await update_up_time(current_user)
    return user.containers

@app.delete("/container/{name}")
async def delete_server(name: str, delete_key:str, task_manager: BackgroundTasks):
    if os.environ.get("delete_key") != delete_key:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Admin Key",
        headers={"WWW-Authenticate": "Bearer"},
    )
    details = await get_droplets_details(name)
    print(details)
    details_id = details["id"]
    task_manager.add_task(delete_droplet,details_id, name.split("-")[0])
    return {"Success": "Container Deleted"}

@app.post("/register" , response_model=User)
async def register(user: UserCreate, verification_email: BackgroundTasks):
    if get_user_by_email(user.email) or get_user(user.username):
        raise HTTPException(status_code=409 ,detail="User already exists")
    else:
        otp = generateOTP(5)
        db_user = UserInDB(**user.dict(), hashed_password=get_password_hash(user.password))
        app.database.insert_one(db_user.dict())
        # sample_string.encode("ascii")
        link = f"/verify/{base64.b64encode(db_user.email.encode()).decode()}/?code={otp}"
        verification_email.add_task(sendVerificationMail, db_user.email, link)
        return db_user
