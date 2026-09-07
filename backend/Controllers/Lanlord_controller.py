# FastAPI se HTTPException import - ye errors return karne ke liye hai
from fastapi import HTTPException
# Landlord model import - database table ke saath interact karne ke liye
from Models.Landlord import Landlord


# LandlordController class mein saare user-related functions hain
class LandlordController:
    @staticmethod
    def sign_up(data, database):
        # Check karo agar email already exist karta hai to error do
        existing = database.query(Landlord).filter(Landlord.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="email already exist")

        # Naya user create karo
        new_user = Landlord(
            name=data.name,
            email=data.email,
            password=data.password,  # Note: password plain text mein save ho raha hai (hash nahi)
        )

        database.add(new_user)   # Database mein add karo
        database.commit()        # Changes save karo
        database.refresh(new_user)  # Naya ID wapas lo database se

        return {'message': 'Signup successful', 'user_id': new_user.id}

    @staticmethod
    def login(data, database):
        # Email se user dhundho
        user = database.query(Landlord).filter(Landlord.email == data.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="email not found")

        # Password check karo (plain text comparison - secure nahi hai)
        if user.password != data.password:
            raise HTTPException(status_code=401, detail="incorrect password")

        return {'message': 'Login successful', 'user_id': user.id}

    @staticmethod
    def update_profile(id, data, database):
        # ID se user dhundho
        landlord = database.query(Landlord).filter(Landlord.id == id).first()
        if not landlord:
            raise HTTPException(status_code=404, detail="user not found")

        # Jo field di hai woh update karo (optional fields)
        if "name" in data:
            landlord.name = data.name
        if "city" in data:
            landlord.location = data.city
        if "phone_number" in data:
            landlord.phone_number = data.phone_number
        if "email" in data:
            landlord.email = data.email
        if "password" in data:
            landlord.password = data.password

        database.commit()
        return {'message': 'Profile updated successfully'}

    @staticmethod
    def get_landlord_by_id(l_id, database):
        # ID se user dhundho
        landlord = database.query(Landlord).filter(Landlord.id == l_id).first()
        if not landlord:
            raise HTTPException(status_code=404, detail="user not found")

        return {
            "id": landlord.id,
            "name": landlord.name,
            "email": landlord.email
        }
