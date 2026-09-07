import React from "react";
import { ChevronLeft, Search } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate, useParams,useLocation } from "react-router-dom";

import "./ProductionSummary.css";

const ProductionSummary = () => {
    const navigate = useNavigate();
    const { farmId } = useParams();
    

    const [farmName, setFarmName] = React.useState("Production Summary");
    const [batches, setBatches] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    // Fetch farm name from backend using real farm ID
    React.useEffect(() => {
        const fetchFarmName = async () => {
            if (!farmId) return;
            try {
                const res = await fetch(`/farm/${farmId}`);
                if (res.ok) {
                    const data = await res.json();
                    setFarmName(data.name || "Production Summary");
                }
            } catch (err) {
                console.error("Failed to fetch farm name:", err);
            }
        };
        const handle_weekly_report= async () =>{

        }
        fetchFarmName();
    }, [farmId]);

    React.useEffect(() => {
        const fetchBatches = async () => {
            try {
                const res = await fetch('/batch_report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ farm_id: farmId })//? parseInt(farmId) : null
                });
                const data = await res.json();
                if (res.ok) {
                    setBatches(data);
                } else {
                    console.error("Error fetching batches:", data);
                }
            } catch (err) {
                console.error("Network error fetching batches:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchBatches();
    }, [farmId]);




    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const cardVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { type: "spring", stiffness: 100 }
        }
    };

    return (
        <motion.div
            className="production-summary-container"
            initial="hidden"
            animate="visible"

            variants={containerVariants}
        >
            <header className="production-summary-header">
                <button className="back-btn" onClick={() => navigate("/farm-selection-summary")}>
                    <ChevronLeft size={28} />
                </button>
                <h1>{farmName}</h1>
            </header>


            <header className="production-summary-header">
                
                <h2>weekly report</h2>
            </header>

            <div className="batches-list" style={{ marginTop: "1rem", flex: 1 }}>
                {loading ? (
                    <p style={{ textAlign: "center", color: "#4a4a4a", fontSize: "18px", marginTop: "40px" }}>Loading batch reports...</p>
                ) : (!Array.isArray(batches) || batches.length === 0) ? (
                    <p style={{ textAlign: "center", color: "#4a4a4a", fontSize: "18px", marginTop: "40px" }}>No batches found.</p>
                ) : (
                    batches.map((batch, idx) => (
                        <motion.div
                            key={batch.batch_id || idx}
                            className="batch-card"
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ type: "spring", stiffness: 100, delay: idx * 0.1 }}
                        >
                            <div className="batch-card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <h2>Batch #{batch.batch_id}</h2>
                                <button
                                    onClick={() => navigate(`/batch-images/${batch.batch_id}`)}
                                    style={{
                                        padding: "6px 12px",
                                        backgroundColor: "#0c5c4c",
                                        color: "white",
                                        border: "none",
                                        borderRadius: "6px",
                                        fontSize: "12px",
                                        fontWeight: "600",
                                        cursor: "pointer"
                                    }}
                                >
                                    View Images
                                </button>
                            </div>
                            <div className="batch-card-body">
                                <div className="detail-row">
                                    <span className="detail-label">Fruit type</span>
                                    <span className="detail-value">{batch.fruit_name}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">Date</span>
                                    <span className="detail-value">{batch.timestamp}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">A Quality</span>
                                    <span className="detail-value">{batch.class_A}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">B Quality</span>
                                    <span className="detail-value">{batch.class_B}</span>
                                </div>
                                <div className="detail-row">
                                    <span className="detail-label">C Quality</span>
                                    <span className="detail-value">{batch.class_C}</span>
                                </div>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </motion.div>
    );
};

export default ProductionSummary;
