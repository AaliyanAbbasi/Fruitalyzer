import React, { useState, useEffect, useMemo } from "react";
import { ChevronLeft, ChevronRight, Home } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import "./Summary.css";

const Summary = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const farmId = location.state?.farmId || 1;
    const farmName = location.state?.farmName || "Selected Farm";
    const sessionStart = location.state?.sessionStart || null;
    const sessionId = location.state?.sessionId || null;
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentFruitIndex, setCurrentFruitIndex] = useState(0);

    // Fetch temp records for this session on mount
    useEffect(() => {
        const fetchRecords = async () => {
            try {
                // Determine if we need to show a specific batch or temporary records
                const query = new URLSearchParams(window.location.search);
                const batchId = query.get('batch_id');
                let res;
                if (batchId) {
                    // Fetch predictions for a saved batch
                    res = await fetch(`/prediction_by_batch/${batchId}`);
                } else {
                    // Fetch temporary predictions since session started
                    const params = new URLSearchParams();
                    if (sessionStart) params.append('since', sessionStart);
                    res = await fetch(`/get_temp_records?${params.toString()}`);
                }
                if (res.ok) {
                    const data = await res.json();
                    const mappedData = data.map(r => ({ ...r, originalCategory: r.category }));
                    setRecords(mappedData);
                }
            } catch (err) {
                console.error("Error fetching temp records:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchRecords();
    }, [sessionStart]);

    // Clear unsaved temp records for this session when user goes back
    const handleGoBack = async () => {
        // if (!window.confirm("Are you sure you want to go back? Unsaved batch records will be discarded.")) {
        //     return;
        // }
        // try {
        //     await fetch("/clear_temp", { method: "DELETE" });
        // } catch (err) {
        //     console.error("Error clearing temp:", err);
        // }
        navigate("/live-detection");
    };

    const handleCategoryChange = async (recordId, newCategory) => {
        try {
            const res = await fetch(`/update_temp_record/${recordId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category: newCategory })
            });
            if (res.ok) {
                setRecords(prev => prev.map(r => r.id === recordId ? { ...r, category: newCategory, grade: newCategory } : r));
            } else {
                const data = await res.json();
                alert(`Failed to update category: ${data.error || "Unknown error"}`);
            }
        } catch (err) {
            console.error("Error updating category:", err);
            alert("Error updating category.");
        }
    };

    const handleSaveBatch = async () => {
        try {
            const res = await fetch("/save_temp_to_batch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ farm_id: farmId, session_id: sessionId })
            });
            const data = await res.json();
            if (res.ok) {
                alert("saved sucessfully")
                const classA = records.filter(r => (r.grade || r.category) === "A").length;
                const classB = records.filter(r => (r.grade || r.category) === "B").length;
                const classC = records.filter(r => (r.grade || r.category) === "C").length;
                
                // navigate("/prediction-graph", {
                //     state: {
                //         batchData: {
                //             classA,
                //             classB,
                //             classC,
                //             batchId: data.batch_id,
                //             farmId: farmId
                //         }
                //     }
                // });
            } else {
                alert(`Error saving bath: ${data.detail || data.error || "Unknown error"}`);
            }
        } catch (err) {
            console.error("Error saving batch:", err);
            alert("Error saving batch. Please check server connection.");
        }
    };

    // Group records by fruit category (e.g. "green apple", "red apple", "mango")
    const fruitsGrouped = Object.entries(
        records.reduce((groups, r) => {
            const raw = (r.fruit_name || r.fruit_category || "Unknown").trim();
            // Title-case every word: "green apple" → "Green Apple"
            const name = raw
                .split(" ")
                .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
                .join(" ");

            if (!groups[name]) {
                groups[name] = [];
            }
            groups[name].push(r);
            return groups;
        }, {})
    ).map(([name, list]) => ({
        name,
        list,
        classA: list.filter(item => item.grade === "A").length,
        classB: list.filter(item => item.grade === "B").length,
        classC: list.filter(item => item.grade === "C").length,
    }));

    const currentFruit = fruitsGrouped[currentFruitIndex];

    const accuracy = useMemo(() => {
        if (records.length === 0) return 100;
        const correctCount = records.filter(r => r.category === r.originalCategory).length;
        return parseFloat(((correctCount / records.length) * 100).toFixed(1));
    }, [records]);

    if (loading) {
        return (
            <div className="summary-container">
                <div className="summary-card" style={{ justifyContent: "center", minHeight: "400px" }}>
                    <p style={{ fontSize: "1.2rem", color: "#64748b" }}>Loading summary...</p>
                </div>
            </div>
        );
    }

    if (fruitsGrouped.length === 0) {
        return (
            <div className="summary-container">
                <div className="summary-card" style={{ justifyContent: "center", minHeight: "400px" }}>
                    <p style={{ fontSize: "1.2rem", color: "#ef4444", marginBottom: "1rem" }}>
                        No images found. Upload some images first.
                    </p>
                    <button className="summary-go-back-btn" onClick={() => navigate("/live-detection")}>
                        back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            className="summary-container"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        >
            <div className="summary-card">
                {/* Header */}
                <header className="summary-header">
                    <button className="summary-back-btn" onClick={handleGoBack}>
                        <ChevronLeft size={28} />
                    </button>
                    <h1 className="summary-title">Batch Summary</h1>
                </header>

                <div className="accuracy-badge" style={{
                    backgroundColor: accuracy >= 90 ? "#e2fbe8" : accuracy >= 70 ? "#fff3cd" : "#fce8e6",
                    color: accuracy >= 90 ? "#15803d" : accuracy >= 70 ? "#856404" : "#a80c0c",
                    padding: "8px 16px",
                    borderRadius: "20px",
                    fontWeight: "700",
                    fontSize: "14px",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    marginTop: "10px",
                    marginBottom: "16px",
                    border: `1px solid ${accuracy >= 90 ? "#bbf7d0" : accuracy >= 70 ? "#ffeeba" : "#f9c2c2"}`
                }}>
                    <span>Model Prediction Accuracy:</span>
                    <span style={{ fontSize: "16px" }}>{accuracy}%</span>
                </div>

                {/* Fruit Navigation */}
                <div className="fruit-nav-bar">

                    <div className="fruit-nav-info">
                        <span className="fruit-nav-name">{currentFruit.name}</span>
                        <span className="fruit-nav-counter">
                            Fruit {currentFruitIndex + 1} of {fruitsGrouped.length}
                        </span>
                    </div>

                </div>

                {/* Dots */}
                <div className="fruit-dots">
                    {fruitsGrouped.map((_, index) => (
                        <button
                            key={index}
                            className={`fruit-dot ${index === currentFruitIndex ? "active" : ""}`}
                            onClick={() => setCurrentFruitIndex(index)}
                        />
                    ))}
                </div>

                {/* Grade Stats */}
                <div className="grade-stats-bar">
                    <div className="grade-stat">
                        <div className="grade-badge grade-a">A</div>
                        <span className="grade-label">Class A</span>
                        <span className="grade-count">{currentFruit.classA}</span>
                    </div>
                    <div className="grade-stat">
                        <div className="grade-badge grade-b">B</div>
                        <span className="grade-label">Class B</span>
                        <span className="grade-count">{currentFruit.classB}</span>
                    </div>
                    <div className="grade-stat">
                        <div className="grade-badge grade-c">C</div>
                        <span className="grade-label">Class C</span>
                        <span className="grade-count">{currentFruit.classC}</span>
                    </div>
                    <div className="grade-stat">
                        <div className="grade-badge" style={{ backgroundColor: "#64748b" }}>T</div>
                        <span className="grade-label">Total</span>
                        <span className="grade-count">{currentFruit.list.length}</span>
                    </div>
                </div>

                {/* Image Grid */}
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentFruitIndex}
                        className="summary-image-grid"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.25 }}
                    >
                        {currentFruit.list.map((record) => (
                            <div key={record.id} className="summary-image-card">
                                <div className="summary-img-wrapper">
                                    <img
                                        src={`/predict/images/${record.image}`}
                                        alt={`${currentFruit.name}`}
                                        className="summary-img"
                                    />
                                    <span className={`summary-grade-tag grade-tag-${(record.grade || record.category || "a").toLowerCase()}`} style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                                        Class {record.grade || record.category || "?"}
                                        <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                                            {((record.category_confidence || 0) * 100).toFixed(1)}%
                                        </span>
                                    </span>
                                </div>
                                <div className="summary-img-info" style={{ display: "flex", flexDirection: "column", gap: "8px", alignItems: "stretch", width: "100%" }}>
                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                        <span className="summary-img-fruit">{currentFruit.name}</span>
                                        <span className="summary-img-confidence">
                                            {record.confidence}
                                        </span>
                                    </div>
                                    <div style={{ display: "flex", width: "100%" }}>
                                        <select
                                            value={record.category}
                                            onChange={(e) => handleCategoryChange(record.id, e.target.value)}
                                            style={{
                                                width: "100%",
                                                padding: "6px 8px",
                                                borderRadius: "8px",
                                                border: "1px solid #cbd5e1",
                                                backgroundColor: "#f8fafc",
                                                fontSize: "12px",
                                                fontWeight: "600",
                                                color: "#334155",
                                                cursor: "pointer",
                                                outline: "none"
                                            }}
                                        >
                                            <option value="A">Class A</option>
                                            <option value="B">Class B</option>
                                            <option value="C">Class C</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </motion.div>
                </AnimatePresence>

                {/* Bottom Navigation */}
                <div className="summary-bottom-nav">
                    {currentFruitIndex > 0 ? (
                        <button
                            className="summary-nav-btn prev"
                            onClick={() => setCurrentFruitIndex(prev => prev - 1)}
                        >
                            <ChevronLeft size={18} />
                            <span>Previous</span>
                        </button>
                    ) : (
                        <button className="summary-nav-btn prev" onClick={handleGoBack}>
                            <ChevronLeft size={18} />
                            <span>Back</span>
                        </button>
                    )}

                    {currentFruitIndex < fruitsGrouped.length - 1 ? (
                        <button
                            className="summary-nav-btn next"
                            onClick={() => setCurrentFruitIndex(prev => prev + 1)}
                        >
                            <span>Next Fruit</span>
                            <ChevronRight size={18} />
                        </button>
                    ) : (
                        <button className="summary-nav-btn next" onClick={handleSaveBatch} style={{ background: "linear-gradient(135deg, #16a34a 0%, #15803d 100%)", color: "white" }}>
                            <Home size={18} />
                            <span>Save Batch</span>
                        </button>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default Summary;