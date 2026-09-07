# FastAPI se HTTPException import - errors return karne ke liye
from fastapi import HTTPException
# Farm model import - database table ke saath kaam karne ke liye
from Models.Farm import Farm


# FarmController mein saare farm-related functions hain
class FarmController:

    @staticmethod
    def add_farm(data, database):
        try:
            # Naya farm object banate hain schema se data le kar
            new_farm = Farm(
                Landlord_id=data.Landlord_id,  # Farm kis landlord ka hai
                name=data.name,                 # Farm ka naam
                type=data.type,                 # Farm ki type (e.g., mango)
                province=data.province,         # Province
                city=data.city                  # City
            )

            database.add(new_farm)    # Database mein add karo
            database.commit()         # Save karo
            database.refresh(new_farm)  # ID wapas lo

            return {
                "message": "Farm added successfully",
                "landlord_id": new_farm.Landlord_id,
                "farm_id": new_farm.id
            }

        except Exception as e:
            database.rollback()  # Koi error aya to sab wapas lo
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def get_all_farms(data, database):
        # Landlord ID se saare farms dhundho
        farms = database.query(Farm).filter(
            Farm.Landlord_id == data.landlord_id
        ).all()

        # List of dictionaries return karo
        return [
            {
                "id": farm.id,
                "Landlord_id": farm.Landlord_id,
                "name": farm.name,
                "province": farm.province,
                "city": farm.city,
                "type": farm.type
            }
            for farm in farms
        ]

    @staticmethod
    def get_farmby_id(farm_id, database):
        # Farm ID se ek specific farm dhundho
        farm = database.query(Farm).filter(Farm.id == farm_id).first()

        if not farm:
            raise HTTPException(status_code=404, detail="farm not found")

        return {
            "id": farm.id,
            "Landlord_id": farm.Landlord_id,
            "name": farm.name,
            "province": farm.province,
            "city": farm.city,
            "type": farm.type
        }

    @staticmethod
    def get_farm_by_location(data, database):
        # City ke according farms search karo
        farms = database.query(Farm).filter(Farm.city == data.city).all()

        if not farms:
            return {"message": "farm not found in this city"}

        return [
            {
                "id": farm.id,
                "name": farm.name,
                "type": farm.type,
                "province": farm.province,
                "city": farm.city
            }
            for farm in farms
        ]

    @staticmethod
    def update_farm(farm_id, data, database):
        # Farm ID se farm dhundho
        farm = database.query(Farm).filter(Farm.id == farm_id).first()

        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")

        # Jo field di hai woh update karo (optional)
        if data.name is not None:
            farm.name = data.name
        if data.city is not None:
            farm.city = data.city
        if data.province is not None:
            farm.province = data.province
        if data.type is not None:
            farm.type = data.type

        database.commit()
        return {"message": "Farm updated successfully"}
