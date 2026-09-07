
import React, { useState, useEffect } from "react";
import { ChevronLeft, UserCircle, Search, MapPin, Edit3, Trash2, PlusCircle } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import "./MyFarms.css";

const MyFarms = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const [farms, setFarms] = useState([]);
    const [farmToDelete, setFarmToDelete] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [isSearching, setIsSearching] = useState(false);
    
    // Store original farms to revert when search is cleared
    const [originalFarms, setOriginalFarms] = useState([]);

    const fetchFarms = async () => {
        try {
            const userId = Number(localStorage.getItem("user_id"));
            const res = await fetch("/get_all_farms_of_landlord", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ landlord_id: userId }),
            });
            const data = await res.json();
            if (res.ok) {
                setFarms(data);
                setOriginalFarms(data);
            }
        } catch (err) {
            console.error("Fetch farms error:", err);
        }
    };

    useEffect(() => {
        fetchFarms();
    }, [location.key]);

    useEffect(() => {
        const searchLocation = async () => {
            if (searchQuery.trim() === "") {
                setFarms(originalFarms);
                return;
            }

            setIsSearching(true);
            try {
                const res = await fetch("/farm_location", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ city: searchQuery }),
                });
                const data = await res.json();
                
                if (res.ok && Array.isArray(data)) {
                    // Filter to only show farms belonging to THIS landlord if necessary
                    // For now, showing what the API returns as per user request
                    setFarms(data);
                } else if (data.message === "farm not found in this city") {
                    setFarms([]);
                }
            } catch (err) {
                console.error("Search error:", err);
            } 
            
            
            finally {
                setIsSearching(false);
            }
        };

        const timeoutId = setTimeout(searchLocation, 500); // Debounce
        return () => clearTimeout(timeoutId);
    }, [searchQuery, originalFarms]);

    const confirmDelete = () => {
        if (farmToDelete) {
            setFarms((prev) => prev.filter((f) => f.id !== farmToDelete));
            setFarmToDelete(null);
        }
    };

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
            className="my-farms-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <header className="my-farms-header">
                <button className="back-btn" onClick={() => navigate("/home")}>
                    <ChevronLeft size={28} />
                </button>
                <h1>My Farms</h1>
                <button className="profile-btn" onClick={() => navigate("/account")}>
                    <UserCircle size={28} />
                </button>
            </header>

            <div className="search-container">
                <Search className="search-icon" size={20} />
                <input 
                    type="text" 
                    className="search-bar" 
                    placeholder="Search by City (e.g. Multan)" 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                {isSearching && <span className="search-loader">...</span>}
            </div>

            <div className="farms-list">
                {farms.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px", color: "#64748b" }}>
                        <h3>No farms found for this account.</h3>
                        <p>If you just added a farm, please verify you are logged into the correct account.</p>
                    </div>
                ) : (
                    farms.map((farm) => (
                        <motion.div
                            key={farm.id}
                            className="farm-card"
                            variants={cardVariants}
                            initial="hidden"
                            animate="visible"
                        >
                            <div className="farm-info">
                                <h3>{farm.name}</h3>
                                <p className="farm-type">Type: {farm.type}</p>
                                <div className="farm-location">
                                    <MapPin size={14} />
                                    <span>{farm.city}, {farm.province}</span>
                                </div>
                            </div>
                            <motion.button
                                className="edit-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    navigate(`/edit-farm/${farm.id}`);
                                }}
                                whileTap={{ scale: 0.9 }}
                                type="button"
                            >
                                <Edit3 size={20} />
                            </motion.button>
                            <motion.button
                                className="delete-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setFarmToDelete(farm.id);
                                }}
                                whileTap={{ scale: 0.9 }}
                                type="button"
                            >
                                <Trash2 size={20} />
                            </motion.button>

                        </motion.div>
                    ))
                )}
            </div>

            <motion.div className="add-more-container" variants={cardVariants}>
                <button className="add-more-btn" onClick={() => navigate("/farm-details")}>
                    <PlusCircle size={20} />
                    <span>Add More Farms</span>
                </button>
            </motion.div>

            {farmToDelete && (
                <div className="modal-overlay">
                    <motion.div
                        className="modal-content"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                    >
                        <h3>Delete Farm</h3>
                        <p>Are you sure you want to delete this farm? This action cannot be undone.</p>
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={() => setFarmToDelete(null)}>Cancel</button>
                            <button className="confirm-btn" onClick={confirmDelete}>Delete</button>
                        </div>
                    </motion.div>
                </div>
            )}
        </motion.div>
    );
};

export default MyFarms;
