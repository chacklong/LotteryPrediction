from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta

# 假设这是你的密钥和算法
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # 解码 JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid token payload.")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=403, detail="Could not validate credentials.")
    
    # 验证 token 是否过期
    expire = payload.get("exp")
    if datetime.fromtimestamp(expire) < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Token has expired.")
    
    return {"user_id": user_id, "scopes": payload.get("scopes", [])}
