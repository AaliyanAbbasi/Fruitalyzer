import React, { useState } from "react";
import { MapPin, Plus, ChevronDown, ChevronLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./FarmDetails.css";

const FarmDetails = ({ addFarm }) => {
    const navigate = useNavigate();
    const [farmName, setFarmName] = useState("");
    const [farmType, setFarmType] = useState("");
    const [province, setProvince] = useState("");
    const [city, setCity] = useState("");
    const [age,setage]=useState("");
    const [hint,sethint]=useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!farmName || !farmType || !province || !city) {
        alert("Please fill all fields");
        return;
    }

    try {
        
        const userId = localStorage.getItem("user_id");

        if (!userId) {
            alert("User not logged in");
            return;
        }
alert('fuck you')
        const response = await fetch('/Add_farm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                Landlord_id: Number(userId),
                name: farmName,
                type: farmType,
                province: province,
                city: city,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            alert("Farm added successfully");
            navigate("/my-farms");
        } else {
            alert(data.error || "Failed to add farm");
        }

    } catch (error) {
        console.error(error);
        alert("Server error");
    }
};
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { duration: 0.5 }
        }
    };

    const cardVariants = {
        hidden: { scale: 0.9, opacity: 0 },
        visible: {
            scale: 1,
            opacity: 1,
            transition: { type: "spring", stiffness: 100 }
        }
    };

    return (
        <motion.div
            className="farm-details-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <motion.div className="farm-details-card" variants={cardVariants}>
                <h1 className="title">Farm Details</h1>

                <div className="input-group">
                    <label>Farm Name</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="Enter Farm Name"
                        value={farmName}
                        onChange={(e) => setFarmName(e.target.value)}
                        required
                    />
                </div>

                <div className="input-group">
                    <label>Farm Type</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="eg. Mango Farm"
                        value={farmType}
                        onChange={(e) => setFarmType(e.target.value)}
                        required
                    />
                </div>
               

                <div className="location-row">
                    <div className="input-group">
                        <label>Enter Province</label>
                        <div className="location-wrapper">
                            <MapPin className="input-icon" size={18} />
                            <input
                                type="text"
                                placeholder="Province"
                                value={province}
                                onChange={(e) => setProvince(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label>Enter City</label>
                        <div className="location-wrapper">
                            <MapPin className="input-icon" size={18} />
                            <select
                                value={city}
                                onChange={(e) => setCity(e.target.value)}
                                required
                            >
                                <option value="" disabled>City</option>
                                <option value="Lahore">Lahore</option>
                                <option value="Multan">Multan</option>
                                <option value="Sargodha">Sargodha</option>
                                <option value="Islamabad">Islamabad</option>
                                <option value="Karachi">Karachi</option>
                                <option value="Karachi">Balochistan</option>
                            </select>
                            <ChevronDown className="chevron-icon" size={18} />
                        </div>
                    </div>
                </div>

                <motion.button
                    className="add-farm-btn"
                    onClick={handleSubmit}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Plus size={20} strokeWidth={3} />
                    <span>Add Farm</span>
                </motion.button>
            </motion.div>
        </motion.div>
    );
};

export default FarmDetails;
