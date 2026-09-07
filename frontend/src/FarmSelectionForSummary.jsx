import React, { useState, useEffect } from "react";
import { ChevronLeft, UserCircle, Search, MapPin, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate,useLocation } from "react-router-dom";
import "./FarmSelectionForSummary.css";

const FarmSelectionForSummary = () => {

    const navigate = useNavigate();
    const location = useLocation();
    const [farms, setFarms] = useState([]);
    useEffect(() => {
        const fetchFarms = async () => {
            try {
                const userId = localStorage.getItem("user_id");

                const res = await fetch("/get_all_farms_of_landlord", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        landlord_id: userId
                    }),
                });

                const data = await res.json();

                if (res.ok) {
                    setFarms(data);
                }
            } catch (err) {
                // Ignore errors
            }
        };

        fetchFarms();
    }, []);
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const cardVariants = {
        hidden: { x: -20, opacity: 0 },
        visible: {
            x: 0,
            opacity: 1,
            transition: { type: "spring", stiffness: 100 }
        }
    };

    return (
        <motion.div
            className="farm-selection-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <header className="farm-selection-header">
                <button className="back-btn" onClick={() => navigate("/home")}>
                    <ChevronLeft size={28} />
                </button>
                <h1>Select Farm</h1>
                <button className="profile-btn" onClick={() => navigate("/account")}>
                    <UserCircle size={28} />
                </button>
            </header>

            <div className="search-container">
                <Search className="search-icon" size={20} />
                <input type="text" className="search-bar" placeholder="Search Farms" />
            </div>

            <div className="farms-list">
                {farms.map((farm) => (
                    <motion.div
                        key={farm.id}
                        className="farm-card selectable"
                        variants={cardVariants}
                        initial="hidden"
                        animate="visible"
                        onClick={() => navigate(`/production-summary/${farm.id}`)}
                    >

                        <div className="farm-info">
                            <h3>{farm.name}</h3>
                            <p className="farm-type">Type: {farm.type}</p>
                            <div className="farm-location">
                                <MapPin size={14} />
                                <span>{farm.city}, {farm.province}</span>
                            </div>
                        </div>
                        <motion.div
                            className="forward-btn"
                            whileTap={{ scale: 0.9 }}
                        >
                            <ChevronRight size={20} />
                        </motion.div>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
};

export default FarmSelectionForSummary;
