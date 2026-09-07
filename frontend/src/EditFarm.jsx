import React, { useState, useEffect } from "react";
import { ChevronLeft, Save } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate, useParams } from "react-router-dom";
import "./EditFarm.css";

const EditFarm = ({ farms, updateFarm }) => {
    const navigate = useNavigate();
    const { id } = useParams();

    const [farmData, setFarmData] = useState({
        name: "",
        type: "Apple farm",
        location: ""
    });

    // 🔥 Load farm data from backend
    useEffect(() => {
        const fetchFarm = async () => {
            try {
                const userId = Number(localStorage.getItem("user_id"));
                const res = await fetch("/get_all_farms_of_landlord", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ landlord_id: userId }),
                });

                if (res.ok) {
                    const data = await res.json();
                    const farm = data.find(f => f.id === parseInt(id));
                    if (farm) {
                        setFarmData({
                            name: farm.name || "",
                            type: farm.type || "Apple farm",
                            location: farm.city || ""
                        });
                    }
                }
            } catch (err) {
                console.error("Failed to fetch farm data", err);
            }
        };

        fetchFarm();
    }, [id]);

    // 🔥 Handle input change
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFarmData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // 🔥 API CALL (UPDATE FARM)
    const handleUpdate = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch(`/update_farm/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: farmData.name,
                    type: farmData.type,
                    city: farmData.location   // 🔥 backend expects this
                }),
            });

            const data = await res.json();

            if (res.ok) {
                alert("Farm updated successfully");
                navigate("/my-farms");
            } else {
                alert(data.error || "Update failed");
            }

        } catch (err) {
            console.log(err);
            alert("Server error");
        }
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { type: "spring", stiffness: 100 }
        }
    };

    return (
        <motion.div
            className="edit-farm-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <header className="edit-farm-header">
                <button className="back-btn" onClick={() => navigate("/my-farms")}>
                    <ChevronLeft size={32} />
                </button>
                <h1>Edit Farm</h1>
            </header>

            <motion.form
                className="edit-farm-form"
                variants={itemVariants}
                onSubmit={handleUpdate}
            >
                <div className="form-group">
                    <label>Farm Name</label>
                    <input
                        type="text"
                        name="name"
                        value={farmData.name}
                        onChange={handleChange}
                        placeholder="e.g. Green Pastures"
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Farm Type</label>
                    <select
                        name="type"
                        value={farmData.type}
                        onChange={handleChange}
                        required
                    >
                        <option value="Apple farm">Apple farm</option>
                        <option value="Mango farm">Mango farm</option>
                        <option value="Strawberry farm">Strawberry farm</option>
                        <option value="Orange farm">Orange farm</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Location</label>
                    <input
                        type="text"
                        name="location"
                        value={farmData.location}
                        onChange={handleChange}
                        placeholder="e.g. City, Country"
                        required
                    />
                </div>

                <div className="form-actions">
                    <motion.button
                        type="submit"
                        className="update-btn"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        Update Farm
                    </motion.button>
                    <motion.button
                        type="button"
                        className="cancel-btn"
                        onClick={() => navigate("/my-farms")}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        Cancel
                    </motion.button>
                </div>
            </motion.form>
        </motion.div>
    );
};

export default EditFarm;
