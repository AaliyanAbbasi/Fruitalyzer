import React, { useState, useEffect, useMemo } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate, useParams } from "react-router-dom";
import "./BatchImages.css";

const BatchImages = () => {
    const navigate = useNavigate();
    const { batchId } = useParams();
    const [images, setImages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchImages = async () => {
            try {
                const res = await fetch(`/batch_images/${batchId}`);
                if (res.ok) {
                    const data = await res.json();
                    setImages(data);
                } else {
                    setError("Failed to load batch images.");
                }
            } catch (err) {
                console.error("Error fetching batch images:", err);
                setError("Error connecting to server.");
            } finally {
                setLoading(false);
            }
        };
        fetchImages();
    }, [batchId]);

    // Group images by fruit name
    const fruitsGrouped = useMemo(() => {
        return Object.entries(
            images.reduce((groups, r) => {
                const name = ( r.category || "Unknown").trim();
                const capitalized = name
                .split(" ")
                .map(w =>w.  charAt(0).toUpperCase() + w.slice(1).toLowerCase())
                .join(" ");
                if (!groups[capitalized]) {
                    groups[capitalized] = [];
                }
                groups[capitalized].push(r);
                return groups;
            }, {})
        ).map(([name, list]) => ({
            name,
            list,
            classA: list.filter(item => item.grade === "A").length,
            classB: list.filter(item => item.grade === "B").length,
            classC: list.filter(item => item.grade === "C").length,
        }));
    }, [images]);

    const [currentFruitIndex, setCurrentFruitIndex] = useState(0);
    const currentFruit = fruitsGrouped[currentFruitIndex];

    if (loading) {
        return (
            <div className="bi-container">
                <div className="bi-card" style={{ justifyContent: "center", minHeight: "400px" }}>
                    <p style={{ fontSize: "1.2rem", color: "#64748b" }}>Loading images...</p>
                </div>
            </div>
        );
    }

    if (error || images.length === 0) {
        return (
            <div className="bi-container">
                <div className="bi-card" style={{ justifyContent: "center", minHeight: "400px" }}>
                    <p style={{ fontSize: "1.2rem", color: "#ef4444", marginBottom: "1rem" }}>
                        {error || "No images found for this batch."}
                    </p>
                    <button className="bi-back-btn" onClick={() => navigate(-1)}>Go Back</button>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            className="bi-container"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        >
            <div className="bi-card">
                {/* Header */}
                <header className="bi-header">
                    <button className="bi-back-icon-btn" onClick={() => navigate(-1)}>
                        <ChevronLeft size={28} />
                    </button>
                    <h1 className="bi-title">Batch #{batchId} Images</h1>
                </header>

                {/* Fruit dots navigation if there are multiple fruits */}
                {fruitsGrouped.length > 1 && (
                    <div className="fruit-dots" style={{ display: "flex", gap: "8px", marginBottom: "16px", justifyContent: "center" }}>
                        {fruitsGrouped.map((_, index) => (
                            <button
                                key={index}
                                className={`fruit-dot ${index === currentFruitIndex ? "active" : ""}`}
                                onClick={() => setCurrentFruitIndex(index)}
                                style={{
                                    width: "10px",
                                    height: "10px",
                                    borderRadius: "50%",
                                    background: index === currentFruitIndex ? "#0c5c4c" : "#cbd5e1",
                                    border: "none",
                                    cursor: "pointer",
                                    transition: "all 0.2s",
                                    transform: index === currentFruitIndex ? "scale(1.2)" : "scale(1)"
                                }}
                            />
                        ))}
                    </div>
                )}

                {/* Fruit name bar with Next / Prev buttons */}
                {currentFruit && (
                    <div className="bi-fruit-bar" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        {/* Prev Button */}
                        {fruitsGrouped.length > 1 && (
                            <button
                                onClick={() => setCurrentFruitIndex(prev => (prev - 1 + fruitsGrouped.length) % fruitsGrouped.length)}
                                style={{ background: "none", border: "none", color: "white", cursor: "pointer", display: "flex", alignItems: "center", padding: "4px" }}
                            >
                                <ChevronLeft size={24} />
                            </button>
                        )}

                        {/* Centered Fruit Info */}
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
                            <span className="bi-fruit-name" style={{ textTransform: "capitalize" }}>{currentFruit.name}</span>
                            <span className="bi-fruit-total" style={{ color: "rgba(255, 255, 255, 0.8)", fontSize: "12px", marginTop: "2px" }}>
                                Fruit {currentFruitIndex + 1} of {fruitsGrouped.length} ({currentFruit.list.length} fruits)
                            </span>
                        </div>

                        {/* Next Button */}
                        {fruitsGrouped.length > 1 && (
                            <button
                                onClick={() => setCurrentFruitIndex(prev => (prev + 1) % fruitsGrouped.length)}
                                style={{ background: "none", border: "none", color: "white", cursor: "pointer", display: "flex", alignItems: "center", padding: "4px" }}
                            >
                                <ChevronRight size={24} />
                            </button>
                        )}
                    </div>
                )}


                {/* Grade Stats for current selected fruit */}
                {currentFruit && (
                    <div className="bi-stats-bar">
                        <div className="bi-stat">
                            <div className="bi-badge grade-a">A</div>
                            <span className="bi-stat-label">Class A</span>
                            <span className="bi-stat-count">{currentFruit.classA}</span>
                        </div>
                        <div className="bi-stat">
                            <div className="bi-badge grade-b">B</div>
                            <span className="bi-stat-label">Class B</span>
                            <span className="bi-stat-count">{currentFruit.classB}</span>
                        </div>
                        <div className="bi-stat">
                            <div className="bi-badge grade-c">C</div>
                            <span className="bi-stat-label">Class C</span>
                            <span className="bi-stat-count">{currentFruit.classC}</span>
                        </div>
                        <div className="bi-stat">
                            <div className="bi-badge grade-total">T</div>
                            <span className="bi-stat-label">Total</span>
                            <span className="bi-stat-count">{currentFruit.list.length}</span>
                        </div>
                    </div>
                )}

                {/* Image Grid for current selected fruit */}
                {currentFruit && (
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentFruitIndex}
                            className="bi-image-grid"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.25 }}
                            style={{ width: "100%" }}
                        >
                            {currentFruit.list.map((record, idx) => (
                                <motion.div
                                    key={record.id}
                                    className="bi-image-card"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: idx * 0.04 }}
                                >
                                    <div className="bi-img-wrapper">
                                        <img
                                            src={`/predict/images/${record.image}`}
                                            alt={record.fruit_name}
                                            className="bi-img"
                                        />
                                        <span className={`bi-grade-tag bi-grade-${record.category.toLowerCase()}`}>
                                            Class {record.category}
                                        </span>
                                    </div>
                                    <div className="bi-img-info">
                                        <span className="bi-img-fruit">
                                            {record.fruit_name.charAt(0).toUpperCase() + record.fruit_name.slice(1)}
                                        </span>
                                        <span className="bi-img-confidence">
                                            {(record.confidence * 100).toFixed(1)}%
                                        </span>
                                        <span className="bi-img-confidence">
                                            {(record.grade)}
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                        </motion.div>
                    </AnimatePresence>
                )}
            </div>
        </motion.div>
    );
};

export default BatchImages;
