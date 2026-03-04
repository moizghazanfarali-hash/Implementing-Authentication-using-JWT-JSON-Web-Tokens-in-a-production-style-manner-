from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr
from database import load_data, save_data
from dependencies import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    text: str

@router.get("/users")
def get_users(
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
    sort: str = Query("asc"),
    current_user: str = Depends(get_current_user)  
):
    data = load_data()
    users = data["users"]

    if sort not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort value")

    sorted_users = sorted(users, key=lambda x: x["user_id"], reverse=(sort == "desc"))
    total = len(sorted_users)
    paginated = [] if offset >= total else sorted_users[offset: offset + limit]

    return {"total": total, "limit": limit, "offset": offset, "data": paginated}


@router.get("/users/{user_id}")
def get_user(user_id: str, current_user: str = Depends(get_current_user)):
    data = load_data()
    for user in data["users"]:
        if user.get("user_id") == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@router.put("/users/{user_id}")
def update_user(user_id: str, updated_user: UserUpdate, current_user: str = Depends(get_current_user)):
    data = load_data()
    for user in data["users"]:
        if user.get("user_id") == user_id:
            user["name"] = updated_user.name
            user["email"] = updated_user.email
            user["text"] = updated_user.text
            save_data(data)
            return {"message": "User updated successfully", "user": user}
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/users/{user_id}")
def delete_user(user_id: str, current_user: str = Depends(get_current_user)):
    data = load_data()
    for user in data["users"]:
        if user.get("user_id") == user_id:
            data["users"].remove(user)
            save_data(data)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/analyze/{user_id}")
def analyze_text(user_id: str, current_user: str = Depends(get_current_user)):
    data = load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    text = user.get("text", "")
    if len(text) > 200:
        raise HTTPException(status_code=400, detail="Text exceeds 200 characters")

    analysis = {
        "analysis_id": len(data["analyses"]) + 1,
        "user_id": user_id,
        "word_count": len(text.split()),
        "char_count": len(text),
        "special_char_count": sum(1 for c in text if not c.isalnum() and not c.isspace()),
        "uppercase_count": sum(1 for c in text if c.isupper()),
        "lowercase_count": sum(1 for c in text if c.islower())
    }

    data["analyses"].append(analysis)
    save_data(data)
    return analysis


@router.get("/users/{user_id}/analyses")
def get_user_analyses(
    user_id: str,
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
    sort: str = Query("asc"),
    min_words: int | None = Query(None, ge=0),
    current_user: str = Depends(get_current_user)
):
    data = load_data()
    user_exists = any(u["user_id"] == user_id for u in data["users"])
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    analyses = [a for a in data["analyses"] if a["user_id"] == user_id]
    if min_words is not None:
        analyses = [a for a in analyses if a["word_count"] >= min_words]

    if sort not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort value")

    sorted_analyses = sorted(analyses, key=lambda x: x["analysis_id"], reverse=(sort == "desc"))
    total = len(sorted_analyses)
    paginated = [] if offset >= total else sorted_analyses[offset: offset + limit]


    return {"total": total, "limit": limit, "offset": offset, "data": paginated}
