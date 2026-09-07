import React from "react";
import { ChevronLeft, CheckCircle2, Home, BarChart2 } from "lucide-react";
import { motion } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import "./PredictionGraph.css";

const PredictionGraph = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const batchData = location.state?.batchData;

    const classA = batchData?.classA || 0;
    const classB = batchData?.classB || 0;
    const classC = batchData?.classC || 0;
    const farmId = batchData?.farmId || 1;

    // Use actual batch counts or fallback mock data
    const totalCount = classA + classB + classC || 100;
    
    const items = [
        { label: "Quality A", subtitle: "Export Quality", count: classA, color: "#16a34a" },
        { label: "Quality B", subtitle: "Local / Average", count: classB, color: "#eab308" },
        { label: "Quality C", subtitle: "Rotten / Low Quality", count: classC, color: "#ef4444" }
    ];

    // Calculate angles for Conic Gradient pie chart
    let currentAngle = 0;
    const slices = items.map(item => {
        const percentage = totalCount > 0 ? ((item.count / totalCount) * 100).toFixed(1) : 0;
        const startAngle = currentAngle;
        const sliceAngle = totalCount > 0 ? (item.count / totalCount) * 360 : 0;
        currentAngle += sliceAngle;
        return {
            ...item,
            percentage,
            startAngle,
            endAngle: currentAngle
        };
    });

    const gradientString = slices.length > 0 && (classA > 0 || classB > 0 || classC > 0)
        ? `conic-gradient(${slices.map(s => `${s.color} ${s.startAngle}deg ${s.endAngle}deg`).join(", ")})`
        : `conic-gradient(#cbd5e1 0deg 360deg)`;

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
            className="prediction-graph-container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <div className="prediction-graph-card">
                <header className="prediction-graph-header">
                    <button className="back-btn" onClick={() => navigate("/live-detection")}>
                        <ChevronLeft size={28} />
                    </button>
                </header>

                <motion.div className="success-banner" variants={itemVariants}>
                    <div className="title-row">
                        <CheckCircle2 size={28} className="check-icon" />
                        <h1>Prediction Result Graph</h1>
                    </div>
                    <p className="success-text">AI Detection Completed & Saved</p>
                </motion.div>

                <motion.div className="graph-section" variants={itemVariants}>
                    <h2 className="graph-title">Overall Quality Classification</h2>
                    
                    {/* Donut / Pie Chart Render */}
                    <div className="pie-chart-wrapper">
                        <div 
                            className="pie-chart-donut"
                            style={{ background: gradientString }}
                        >
                            <div className="pie-chart-center">
                                <span className="total-num">{totalCount}</span>
                                <span className="total-label">Total Fruits</span>
                            </div>
                        </div>
                    </div>

                    {/* Legend / Breakdown */}
                    <div className="pie-legend">
                        {slices.map((item, index) => (
                            <div key={index} className="legend-item">
                                <div className="legend-header">
                                    <span className="legend-dot" style={{ backgroundColor: item.color }}></span>
                                    <span className="legend-title">{item.label}</span>
                                    <span className="legend-sub">({item.subtitle})</span>
                                </div>
                                <div className="legend-values">
                                    <span className="legend-count">{item.count} items</span>
                                    <span className="legend-percent">{item.percentage}%</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>

                <motion.div className="actions-container" variants={itemVariants}>
                    <motion.button
                        className="action-btn view-batch-btn"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => navigate(`/production-summary/${farmId}`)}
                    >
                        <BarChart2 size={20} />
                        <span>see weekly report</span>
                    </motion.button>
                    <motion.button
                        className="action-btn back-home-btn"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => navigate("/home")}
                    >
                        <Home size={20} />
                        <span>Back To Home</span>
                    </motion.button>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default PredictionGraph;
